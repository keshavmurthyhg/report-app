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

from modules.report.report_service import (
    generate_incident_report,
    load_incident_data
)

from modules.report.services.preview_service import get_preview_data

from modules.report.doc_generator import (
    generate_pdf,
    generate_word_doc_wrapper
)

from modules.common.ui.preview_ui import render_preview_html

app = Flask(__name__)
app.secret_key = "report_app_secret"

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["OUTPUT_FOLDER"] = OUTPUT_FOLDER


@app.route("/")
def home():
    return render_template("index.html")


@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory("uploads", filename)


@app.route("/report")
def report_page():
    return render_template("report.html")


# -----------------------------------
# Preview
# -----------------------------------
@app.route("/preview-report", methods=["POST"])
def preview_report():
    incident_number = request.form.get("incident_number")

    data = get_preview_data(incident_number)

    preview_html = render_preview_html(data)

    return preview_html


# -----------------------------------
# Load editable RCA
# -----------------------------------
@app.route("/get-rca-data", methods=["POST"])
def get_rca_data():
    incident_number = request.form.get("incident_number")
    data = get_preview_data(incident_number)

    return jsonify({
        "problem": data.get("problem"),
        "analysis": data.get("analysis"),
        "resolution": data.get("resolution")
    })


# -----------------------------------
# Update Preview
# -----------------------------------
@app.route("/update-preview", methods=["POST"])
def update_preview():

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

    # problem images
    for file in request.files.getlist("problem_images"):
        if file.filename:
            filename = f"{uuid.uuid4()}_{file.filename}"
            path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(path)
            saved_problem_images.append(path)

    # root images
    for file in request.files.getlist("root_images"):
        if file.filename:
            filename = f"{uuid.uuid4()}_{file.filename}"
            path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(path)
            saved_root_images.append(path)

    # resolution images
    for file in request.files.getlist("resolution_images"):
        if file.filename:
            filename = f"{uuid.uuid4()}_{file.filename}"
            path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(path)
            saved_resolution_images.append(path)

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


# -----------------------------------
# Final download
# -----------------------------------
@app.route("/generate-report-final", methods=["POST"])
def generate_report_final():
    try:
        incident_number = request.form.get("incident_number")
        report_type = request.form.get("report_type")

        data = load_incident_data(incident_number)

        edited_data = session.get("edited_data", {})

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


@app.route("/bulk")
def bulk_page():
    return render_template("bulk.html")


@app.route("/converter")
def converter_page():
    return render_template("converter.html")


@app.route("/compare")
def compare_page():
    return render_template("compare.html")


if __name__ == "__main__":
    app.run(debug=True)