def render_download_buttons(incident_number):

    return f"""
    <div class="download-section">

        <h3>Download</h3>

        <div class="btn-group">

            <form action="/generate-report" method="POST">
                <input type="hidden" name="incident_number" value="{incident_number}">
                <input type="hidden" name="report_type" value="word">
                <button class="btn">Word</button>
            </form>

            <form action="/generate-report" method="POST">
                <input type="hidden" name="incident_number" value="{incident_number}">
                <input type="hidden" name="report_type" value="pdf">
                <button class="btn">PDF</button>
            </form>

            <form action="/generate-bulk" method="POST">
                <input type="hidden" name="incident_numbers" value="{incident_number}">
                <input type="hidden" name="report_type" value="word">
                <button class="btn">ZIP</button>
            </form>

        </div>

    </div>
    """