"""Resume ranking: PDF text -> preprocessing -> TF-IDF -> keyword scoring -> rank."""
import re
import pdfplumber
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# --- preprocessing (SpaCy if installed, regex fallback otherwise) -------------
try:
    import spacy
    _nlp = spacy.load("en_core_web_sm", disable=["ner", "parser"])
except Exception:
    _nlp = None

_STOP = set("a an the and or of to in for with on at by is are was were be as from that this it its".split())


def extract_text(pdf_file) -> str:
    with pdfplumber.open(pdf_file) as pdf:
        return "\n".join((p.extract_text() or "") for p in pdf.pages)


def preprocess(text: str) -> str:
    """Lowercase, lemmatize, drop stop words/punctuation."""
    text = re.sub(r"[^\w\s+#.]", " ", text)
    if _nlp:
        return " ".join(t.lemma_.lower() for t in _nlp(text)
                        if not (t.is_stop or t.is_punct or t.is_space) and len(t.text) > 1)
    return " ".join(w for w in text.lower().split() if w not in _STOP and len(w) > 1)


def extract_keywords(jd: str, n: int = 15) -> list[str]:
    """Auto-pick the JD's most distinctive terms when no keywords are supplied."""
    vec = TfidfVectorizer(ngram_range=(1, 2), max_features=200)
    scores = vec.fit_transform([preprocess(jd)]).toarray()[0]
    terms = vec.get_feature_names_out()
    return [terms[i] for i in scores.argsort()[::-1][:n]]


# --- scoring ------------------------------------------------------------------
W_TFIDF, W_KEYWORD = 0.4, 0.6   # final score = 40% semantic overlap + 60% keyword coverage


def keyword_score(clean_resume: str, keywords: list[str]):
    """Weighted coverage: earlier keywords (higher priority) count more."""
    hits, total, got = [], 0.0, 0.0
    for i, kw in enumerate(keywords):
        w = 1.0 + 0.5 * (1 - i / max(len(keywords), 1))
        total += w
        if re.search(rf"(?<!\w){re.escape(preprocess(kw))}(?!\w)", clean_resume):
            got += w
            hits.append(kw)
    return (got / total if total else 0.0), hits


def rank(resumes: dict[str, str], job_description: str, keywords: list[str] | None = None):
    """resumes: {filename: raw_text}. Returns list of dicts sorted best-first."""
    keywords = keywords or extract_keywords(job_description)
    clean = {k: preprocess(v) for k, v in resumes.items()}
    jd_clean = preprocess(job_description)
    vec = TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True)
    mat = vec.fit_transform([jd_clean] + list(clean.values()))
    sims = cosine_similarity(mat[0:1], mat[1:])[0]
    out = []
    for (name, text), sim in zip(clean.items(), sims):
        kw, hits = keyword_score(text, keywords)
        score = 100 * (W_TFIDF * sim + W_KEYWORD * kw)
        out.append({"name": name, "score": round(score, 1), "similarity": round(100 * sim, 1),
                    "keyword_pct": round(100 * kw, 1), "matched": hits,
                    "missing": [k for k in keywords if k not in hits]})
    out.sort(key=lambda r: r["score"], reverse=True)
    for i, r in enumerate(out, 1):
        r["rank"] = i
    return out, keywords
