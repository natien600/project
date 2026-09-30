from reportlab.pdfgen import canvas
S = {
"alice_data_scientist": "Alice Rao. Data Scientist. 4 years building NLP pipelines in Python with spaCy and scikit-learn. Built TF-IDF and text classification models, deployed REST APIs with Flask, SQL for analytics. Led resume parsing project. Git, Docker.",
"bikram_backend_dev": "Bikram Shah. Backend Developer. 5 years Java and Spring Boot, microservices, PostgreSQL, Kubernetes. Some Python scripting and Flask for internal tools. AWS, CI/CD.",
"chitra_ml_engineer": "Chitra Nair. Machine Learning Engineer. Python, scikit-learn, pandas, NLP text mining, named entity recognition with spaCy. Flask model serving, SQL, Docker. Published TF-IDF search relevance work.",
"dev_designer": "Dev Kulkarni. Graphic Designer. Photoshop, Illustrator, Figma, branding, typography, print layout. 6 years in agency work. Basic HTML and CSS.",
}
for n, t in S.items():
    c = canvas.Canvas(f"sample_resumes/{n}.pdf"); y = 800
    for i in range(0, len(t), 90): c.drawString(50, y, t[i:i+90]); y -= 16
    c.save()
