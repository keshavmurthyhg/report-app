from flask import (
    Flask,
    render_template,
    request,
    send_file,
    jsonify,
    session,
    send_from_directory
)

import uuid
import os
import zipfile
from io import BytesIO
from flask import send_file
from modules.report.report_service import (
    generate_incident_report,
    load_incident_data
)

from modules.bulk.bulk_service import (
    filter_incidents,
    generate_bulk_zip_file
)

from modules.report.services.preview_service import get_preview_data

from modules.report.doc_generator import (
    generate_pdf,
    generate_word_doc_wrapper
)

from modules.common.ui.preview_ui import render_preview_html


app = Flask(__name__)
app.secret_key = "report_app_secret"


# -----------------------------
# FOLDERS
# -----------------------------
UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["OUTPUT_FOLDER"] = OUTPUT_FOLDER


# -----------------------------
# HOME
# -----------------------------
@app.route("/")
def home():
    return render_template("index.html")


# -----------------------------
# SERVE UPLOADED IMAGES
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
# PREVIEW + FILTER LOAD
# Called from new toolbar Preview button
# -----------------------------
@app.route("/get-rca-data", methods=["POST"])
def get_rca_data():
    try:
        data = request.get_json()

        incident_number = data.get("incident_number")
        priority = data.get("priority")
        vendor = data.get("vendor")

        if not incident_number:
            return jsonify({
                "error": "Incident number required"
            })

        incident_data = get_preview_data(incident_number)

        if not incident_data:
            return jsonify({
                "error": "Incident not found"
            })

        # Optional filter validation
        if priority and priority != "All":
            if incident_data.get("priority") != priority:
                return jsonify({
                    "error": "No incidents found for selected priority"
                })

        if vendor and vendor != "All":
            if incident_data.get("vendor") != vendor:
                return jsonify({
                    "error": "No incidents found for selected vendor"
                })

        preview_html = render_preview_html(incident_data)

        return jsonify({
            "preview_html": preview_html,
            "problem_statement": incident_data.get("problem", ""),
            "root_cause": incident_data.get("analysis", ""),
            "resolution": incident_data.get("resolution", "")
        })

    except Exception as e:
        return jsonify({
            "error": str(e)
        })


# -----------------------------
# UPDATE PREVIEW AFTER EDITS
# -----------------------------
@app.route("/update-preview", methods=["POST"])
def update_preview():
    try:
        incident_number = request.form.get("incident_number")

        data = get_preview_data(incident_number)

        final_problem = request.form.get("problem")
        final_analysis = request.form.get("analysis")
        final_resolution = request.form.get("resolution")

        data["problem"] = final_problem
        data["analysis"] = final_analysis
        data["resolution"] = final_resolution

        saved_problem_images = []
        saved_root_images = []
        saved_resolution_images = []

        # -----------------------------
        # Problem images
        # -----------------------------
        for file in request.files.getlist("problem_images"):
            if file.filename:
                filename = f"{uuid.uuid4()}_{file.filename}"
                path = os.path.join(UPLOAD_FOLDER, filename)
                file.save(path)
                saved_problem_images.append(path)

        # -----------------------------
        # Root images
        # -----------------------------
        for file in request.files.getlist("root_images"):
            if file.filename:
                filename = f"{uuid.uuid4()}_{file.filename}"
                path = os.path.join(UPLOAD_FOLDER, filename)
                file.save(path)
                saved_root_images.append(path)

        # -----------------------------
        # Resolution images
        # -----------------------------
        for file in request.files.getlist("resolution_images"):
            if file.filename:
                filename = f"{uuid.uuid4()}_{file.filename}"
                path = os.path.join(UPLOAD_FOLDER, filename)
                file.save(path)
                saved_resolution_images.append(path)

        # Save edited data in session
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

    except Exception as e:
        return str(e)


# -----------------------------
# WORD DOWNLOAD
# -----------------------------
@app.route("/download/word", methods=["POST"])
def download_word():
    incident_number = request.form.get("incident_number")

    problem = request.form.get("problem_statement")
    root = request.form.get("root_cause")
    resolution = request.form.get("resolution")

    edited_data = session.get("edited_data", {})

    incident_data = get_preview_data(incident_number)

    images = {
        "problem": edited_data.get("problem_images", []),
        "root": edited_data.get("root_images", []),
        "resolution": edited_data.get("resolution_images", [])
    }

    word_bytes = generate_word_doc_wrapper(
        data=incident_data,
        root=problem,
        l2=root,
        res=resolution,
        images=images
    )

    return send_file(
        BytesIO(word_bytes),
        as_attachment=True,
        download_name=f"{incident_number}.docx",
        mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )


# -----------------------------
# PDF DOWNLOAD
# -----------------------------
@app.route("/download/pdf", methods=["POST"])
def download_pdf():
    incident_number = request.form.get("incident_number")

    problem = request.form.get("problem_statement")
    root = request.form.get("root_cause")
    resolution = request.form.get("resolution")

    edited_data = session.get("edited_data", {})

    incident_data = get_preview_data(incident_number)

    images = {
        "problem": edited_data.get("problem_images", []),
        "root": edited_data.get("root_images", []),
        "resolution": edited_data.get("resolution_images", [])
    }

    pdf_bytes = generate_pdf(
        data=incident_data,
        root=problem,
        l2=root,
        res=resolution,
        images=images
    )

    return send_file(
        BytesIO(pdf_bytes),
        as_attachment=True,
        download_name=f"{incident_number}.pdf",
        mimetype="application/pdf"
    )

# -----------------------------
# ZIP DOWNLOAD
# (optional placeholder)
# -----------------------------
@app.route("/download/zip", methods=["POST"])
def download_zip():
    incident_number = request.form.get("incident_number")

    problem = request.form.get("problem_statement")
    root = request.form.get("root_cause")
    resolution = request.form.get("resolution")

    edited_data = session.get("edited_data", {})

    incident_data = get_preview_data(incident_number)

    images = {
        "problem": edited_data.get("problem_images", []),
        "root": edited_data.get("root_images", []),
        "resolution": edited_data.get("resolution_images", [])
    }

    pdf_bytes = generate_pdf(
        data=incident_data,
        root=problem,
        l2=root,
        res=resolution,
        images=images
    )

    word_bytes = generate_word_doc_wrapper(
        data=incident_data,
        root=problem,
        l2=root,
        res=resolution,
        images=images
    )

    zip_buffer = BytesIO()

    with zipfile.ZipFile(
        zip_buffer,
        "w",
        zipfile.ZIP_DEFLATED
    ) as z:
        z.writestr(
            f"{incident_number}.pdf",
            pdf_bytes
        )

        z.writestr(
            f"{incident_number}.docx",
            word_bytes
        )

    zip_buffer.seek(0)

    return send_file(
        zip_buffer,
        as_attachment=True,
        download_name=f"{incident_number}.zip",
        mimetype="application/zip"
    )

@app.route("/bulk/filter-incidents", methods=["POST"])
def bulk_filter_route():
    try:
        data = request.json

        incidents = filter_incidents(
            priority=data.get("priority"),
            year=data.get("year"),
            from_date=data.get("from_date"),
            to_date=data.get("to_date")
        )

        return jsonify({
            "success": True,
            "incidents": incidents
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        })

@app.route("/bulk/download-zip", methods=["POST"])
def bulk_download_zip_route():
    try:
        data = request.json

        incident_text = data.get(
            "incidents",
            ""
        )

        incident_numbers = [
            x.strip()
            for x in incident_text.split(",")
            if x.strip()
        ]

        zip_buffer = generate_bulk_zip_file(
            incident_numbers
        )

        return send_file(
            zip_buffer,
            as_attachment=True,
            download_name="bulk_reports.zip",
            mimetype="application/zip"
        )

    except Exception as e:
        return str(e)


@app.route("/bulk/download-failed-report", methods=["POST"])
def bulk_failed_report():
    try:
        data = request.json
        failed_incidents = data.get("failed_incidents", [])

        if not failed_incidents:
            return jsonify({
                "success": False,
                "message": "No failed incidents found"
            })

        csv_buffer = BytesIO()

        import pandas as pd

        df = pd.DataFrame({
            "Incident Number": failed_incidents
        })

        df.to_csv(
            csv_buffer,
            index=False
        )

        csv_buffer.seek(0)

        return send_file(
            csv_buffer,
            as_attachment=True,
            download_name="failed_incidents.csv",
            mimetype="text/csv"
        )

    except Exception as e:
        return str(e)


# -----------------------------
# FINAL REPORT GENERATOR
# -----------------------------
def generate_final_report(report_type):
    try:
        edited_data = session.get("edited_data", {})

        incident_number = edited_data.get("incident_number")

        if not incident_number:
            return "No report generated yet"

        data = load_incident_data(incident_number)

        final_problem = edited_data.get("problem")
        final_analysis = edited_data.get("analysis")
        final_resolution = edited_data.get("resolution")

        images = {
            "root": edited_data.get("problem_images", []),
            "l2": edited_data.get("root_images", []),
            "res": edited_data.get("resolution_images", [])
        }

        if report_type == "pdf":
            buffer = generate_pdf(
                data=data,
                root=final_problem,
                l2=final_analysis,
                res=final_resolution,
                images=images
            )
            extension = "pdf"

        else:
            buffer = generate_word_doc_wrapper(
                data=data,
                root=final_problem,
                l2=final_analysis,
                res=final_resolution,
                images=images
            )
            extension = "docx"

        filename = f"{incident_number}.{extension}"
        output_path = os.path.join(OUTPUT_FOLDER, filename)

        with open(output_path, "wb") as f:
            f.write(buffer)

        return send_file(
            output_path,
            as_attachment=True
        )

    except Exception as e:
        return str(e)


# -----------------------------
# OTHER MODULES
# -----------------------------
@app.route("/bulk")
def bulk_page():
    return render_template("bulk.html")


@app.route("/converter")
def converter_page():
    return render_template("converter.html")


@app.route("/compare")
def compare_page():
    return render_template("compare.html")


# -----------------------------
# RUN APP
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)