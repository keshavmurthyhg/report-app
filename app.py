from flask import Flask, render_template, request, send_file
import os

# -----------------------------
# REPORT MODULE
# -----------------------------
from modules.report.report_service import (
    generate_incident_report,
    load_incident_data
)

from modules.report.ui.buttons_ui import render_download_buttons
from modules.report.bulk_service import generate_bulk_reports
from modules.report.services.preview_service import get_preview_data

from modules.report.doc_generator import (
    generate_pdf,
    generate_word_doc_wrapper
)

# -----------------------------
# COMMON UI
# -----------------------------
from modules.common.ui.preview_ui import render_preview_html


app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["OUTPUT_FOLDER"] = OUTPUT_FOLDER


# -----------------------------
# HOME
# -----------------------------
@app.route("/")
def home():
    return render_template("index.html")


# -----------------------------
# REPORT PAGE
# -----------------------------
@app.route("/report")
def report_page():
    return render_template("report.html")


# -----------------------------
# PREVIEW REPORT
# -----------------------------
@app.route("/preview-report", methods=["POST"])
def preview_report():

    incident_number = request.form.get("incident_number")

    data = get_preview_data(incident_number)

    preview_html = render_preview_html(data)

    return preview_html


# -----------------------------
# GENERATE REPORT (DIRECT)
# -----------------------------
@app.route("/generate-report", methods=["POST"])
def generate_report():
    try:
        incident_number = request.form.get("incident_number").strip()
        report_type = request.form.get("report_type")

        output_path = generate_incident_report(
            incident_number,
            report_type
        )

        return send_file(output_path, as_attachment=True)

    except Exception as e:
        return str(e)


# -----------------------------
# FINAL GENERATE (FROM PREVIEW)
# -----------------------------
@app.route("/generate-report-final", methods=["POST"])
def generate_report_final():
    try:
        incident_number = request.form.get("incident_number")
        report_type = request.form.get("report_type")

        # reload base data
        data = load_incident_data(incident_number)

        # override RCA from UI
        data["problem"] = request.form.get("problem")
        data["analysis"] = request.form.get("analysis")
        data["resolution"] = request.form.get("resolution")

        # -----------------------------
        # IMAGE HANDLING
        # -----------------------------
        images = {"root": [], "l2": [], "res": []}

        files = request.files.getlist("images")

        for f in files:
            if f.filename:
                path = os.path.join("uploads", f.filename)
                f.save(path)

                # currently attach to resolution
                images["res"].append(path)

        # -----------------------------
        # GENERATE
        # -----------------------------
        if report_type == "pdf":
            buffer = generate_pdf(
                data,
                root=data["problem"],
                l2=data["analysis"],
                res=data["resolution"],
                images=images
            )
            filename = f"{incident_number}.pdf"

        else:
            buffer = generate_word_doc_wrapper(
                data,
                root=data["problem"],
                l2=data["analysis"],
                res=data["resolution"],
                images=images
            )
            filename = f"{incident_number}.docx"

        output_path = os.path.join("outputs", filename)

        with open(output_path, "wb") as f:
            f.write(buffer)

        return send_file(output_path, as_attachment=True)

    except Exception as e:
        return str(e)


# -----------------------------
# BULK PAGE
# -----------------------------
@app.route("/bulk")
def bulk_page():
    return render_template("bulk.html")


# -----------------------------
# GENERATE BULK
# -----------------------------
@app.route("/generate-bulk", methods=["POST"])
def generate_bulk():
    try:
        incidents_raw = request.form.get("incident_numbers")
        report_type = request.form.get("report_type")

        incident_numbers = [
            x.strip()
            for x in incidents_raw.split(",")
        ]

        zip_path = generate_bulk_reports(
            incident_numbers,
            report_type
        )

        return send_file(zip_path, as_attachment=True)

    except Exception as e:
        return str(e)


# -----------------------------
# CONVERTER
# -----------------------------
@app.route("/converter")
def converter_page():
    return render_template("converter.html")


# -----------------------------
# WORD COMPARE
# -----------------------------
@app.route("/compare")
def compare_page():
    return render_template("compare.html")


# -----------------------------
# RUN
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)