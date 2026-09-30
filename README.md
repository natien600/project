# AI-Powered Resume Ranker

Ranks PDF resumes against a job description using NLP (SpaCy, TF-IDF) and a keyword-coverage score. Flask web UI with CSV/PDF report download.

## Setup
```
pip install -r requirements.txt
python -m spacy download en_core_web_sm
python app.py
```
Open http://127.0.0.1:5000

## Scoring
score = 100 x (0.4 x TF-IDF cosine similarity + 0.6 x weighted keyword coverage)

## Files
- `app.py` - Flask routes and report downloads
- `ranker.py` - text extraction, preprocessing, scoring, ranking
- `templates/index.html` - UI
- `sample_resumes/`, `sample_jd.txt`, `sample_output.csv` - sample data and results
