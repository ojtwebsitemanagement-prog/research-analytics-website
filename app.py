from flask import Flask, render_template, request, redirect, flash, url_for
from werkzeug.utils import secure_filename
from flask_mail import Mail, Message
import os
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "temporary-secret-key")
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = os.environ.get("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.environ.get("MAIL_PASSWORD")
app.config["MAIL_DEFAULT_SENDER"] = os.environ.get("MAIL_USERNAME")

mail = Mail(app)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/submission")
def submission():
    return render_template("submission.html")
@app.route("/submit-manuscript", methods=["POST"])
def submit_manuscript():

    author_name = request.form.get("author_name")
    email = request.form.get("email")
    phone = request.form.get("phone")
    institution = request.form.get("institution")
    manuscript_title = request.form.get("manuscript_title")

    manuscript = request.files.get("manuscript")

    if not manuscript or manuscript.filename == "":
        flash("Please upload your manuscript.")
        return redirect(url_for("submission"))

    allowed_extensions = (".doc", ".docx")

    if not manuscript.filename.lower().endswith(allowed_extensions):
        flash("Only Word documents are allowed.")
        return redirect(url_for("submission"))

    msg = Message(
        subject=f"New Manuscript Submission: {manuscript_title}",
        recipients=[os.environ.get("RECEIVER_EMAIL")]
    )

    msg.body = f"""
New Manuscript Submission

Author Name: {author_name}
Email: {email}
Phone: {phone}
Institution: {institution}
Manuscript Title: {manuscript_title}
"""

    msg.attach(
        secure_filename(manuscript.filename),
        manuscript.mimetype or
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        manuscript.read()
    )

    try:
        mail.send(msg)
        return "Manuscript submitted successfully!"
    except Exception:
        app.logger.exception("Email delivery failed")
        return "Unable to send submission. Please try again later.", 500

if __name__ == "__main__":
    app.run(debug=True)