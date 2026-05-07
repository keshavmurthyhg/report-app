from flask import Flask, render_template, request, send_file, jsonify, session
from flask import send_from_directory

import uuid
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
app.secret_key = "report_app_secret"
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
# Serve uploaded images
# -----------------------------
@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory("uploads", filename)


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
# Get RCA data
# -----------------------------
@app.route("/get-rca-data", methods=["POST"])
def get_rca_data():
    incident_number = request.form.get("incident_number")
    data = get_preview_data(incident_number)

    return jsonify({
        "problem": data.get("problem"),
        "analysis": data.get("analysis"),
        "resolution": data.get("resolution")
    })

# -----------------------------
# Update Preview data
# -----------------------------
@app.route("/update-preview", methods=["POST"])
def update_preview():

    incident_number = request.form.get("incident_number")
    data = get_preview_data(incident_number)

    # preserve edited values
    final_problem = request.form.get("problem") or data.get("problem")
    final_analysis = request.form.get("analysis") or data.get("analysis")
    final_resolution = request.form.get("resolution") or data.get("resolution")

    data["problem"] = final_problem
    data["analysis"] = final_analysis
    data["resolution"] = final_resolution

    saved_problem_images = []
    saved_root_images = []
    saved_resolution_images = []

    os.makedirs("uploads", exist_ok=True)

    # save problem images
    for file in request.files.getlist("problem_images"):
        if file.filename:
            filename = f"{uuid.uuid4()}_{file.filename}"
            filepath = os.path.join("uploads", filename)
            file.save(filepath)
            saved_problem_images.append(filepath)

    # save root images
    for file in request.files.getlist("root_images"):
        if file.filename:
            filename = f"{uuid.uuid4()}_{file.filename}"
            filepath = os.path.join("uploads", filename)
            file.save(filepath)
            saved_root_images.append(filepath)

    # save resolution images
    for file in request.files.getlist("resolution_images"):
        if file.filename:
            filename = f"{uuid.uuid4()}_{file.filename}"
            filepath = os.path.join("uploads", filename)
            file.save(filepath)
            saved_resolution_images.append(filepath)

    # store edited content for final download
    session["edited_data"] = {
        "incident_number": incident_number,
        "problem": final_problem,
        "analysis": final_analysis,
        "resolution": final_resolution,
        "problem_images": saved_problem_images,
        "root_images": saved_root_images,
        "resolution_images": saved_resolution_images
    }

    preview_html = render_preview_html(
        data,
        root=final_problem,
        l2=final_analysis,
        resolution=final_resolution,
        problem_images=saved_problem_images,
        root_images=saved_root_images,
        resolution_images=saved_resolution_images
    )

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

        data = load_incident_data(incident_number)

        edited_data = session.get("edited_data", {})

        data["problem"] = edited_data.get(
            "problem",
            data.get("problem")
        )

        data["analysis"] = edited_data.get(
            "analysis",
            data.get("analysis")
        )

        data["resolution"] = edited_data.get(
            "resolution",
            data.get("resolution")
        )

        images = {
            "root": edited_data.get("problem_images", []),
            "l2": edited_data.get("root_images", []),
            "res": edited_data.get("resolution_images", [])
        }

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