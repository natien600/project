import csv, io
from flask import Flask, render_template, request, send_file
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from ranker import extract_text, rank

app = Flask(__name__)
LAST = {"results": [], "keywords": []}   # simple in-memory store for report downloads


@app.route("/", methods=["GET", "POST"])
def index():
    error = None
    if request.method == "POST":
        jd = request.form.get("job_description", "").strip()
        kws = [k.strip() for k in request.form.get("keywords", "").split(",") if k.strip()]
        files = [f for f in request.files.getlist("resumes") if f.filename.lower().endswith(".pdf")]
        if not jd or not files:
            error = "Add a job description and at least one PDF resume."
        else:
            texts = {f.filename: extract_text(f) for f in files}
            LAST["results"], LAST["keywords"] = rank(texts, jd, kws)
    return render_template("index.html", results=LAST["results"] if request.method == "POST" and not error else [],
                           keywords=LAST["keywords"], error=error)


@app.route("/report.csv")
def report_csv():
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["Rank", "Resume", "Score", "TF-IDF similarity %", "Keyword coverage %", "Matched", "Missing"])
    for r in LAST["results"]:
        w.writerow([r["rank"], r["name"], r["score"], r["similarity"], r["keyword_pct"],
                    "; ".join(r["matched"]), "; ".join(r["missing"])])
    return send_file(io.BytesIO(buf.getvalue().encode()), mimetype="text/csv",
                     as_attachment=True, download_name="resume_ranking.csv")


@app.route("/report.pdf")
def report_pdf():
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    y = 800
    c.setFont("Helvetica-Bold", 14); c.drawString(50, y, "Resume Ranking Report"); y -= 22
    c.setFont("Helvetica", 9); c.drawString(50, y, "Keywords: " + ", ".join(LAST["keywords"])[:110]); y -= 26
    for r in LAST["results"]:
        if y < 90: c.showPage(); y = 800
        c.setFont("Helvetica-Bold", 10); c.drawString(50, y, f"#{r['rank']}  {r['name']}   score {r['score']}"); y -= 14
        c.setFont("Helvetica", 9)
        c.drawString(60, y, f"Similarity {r['similarity']}%  |  Keyword coverage {r['keyword_pct']}%"); y -= 12
        c.drawString(60, y, "Matched: " + ", ".join(r["matched"])[:100]); y -= 12
        c.drawString(60, y, "Missing: " + ", ".join(r["missing"])[:100]); y -= 22
    c.save(); buf.seek(0)
    return send_file(buf, mimetype="application/pdf", as_attachment=True, download_name="resume_ranking.pdf")


if __name__ == "__main__":
    app.run(debug=True)
