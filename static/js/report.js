let uploadedFiles = {
    problem: [],
    root: [],
    resolution: []
};


/* -----------------------------------
   PROGRESS FUNCTIONS
----------------------------------- */
function showProgress(message) {
    document.getElementById("progressWrapper")
        .classList.remove("hidden");

    document.getElementById("progressFill")
        .style.width = "20%";

    document.getElementById("progressFill")
        .style.background = "#4caf50";

    document.getElementById("progressText")
        .innerText = message;

    document.getElementById("statusMessage")
        .innerText = "Processing...";
}


function updateProgress(percent, message) {
    document.getElementById("progressFill")
        .style.width = percent + "%";

    document.getElementById("progressText")
        .innerText = message;
}


function completeProgress(message) {
    document.getElementById("progressFill")
        .style.width = "100%";

    document.getElementById("progressText")
        .innerText = "Completed";

    document.getElementById("statusMessage")
        .innerText = message;

    setTimeout(() => {
        document.getElementById("progressWrapper")
            .classList.add("hidden");

        document.getElementById("progressFill")
            .style.width = "0%";
    }, 2000);
}


function failProgress(message) {
    document.getElementById("progressFill")
        .style.width = "100%";

    document.getElementById("progressFill")
        .style.background = "#e74c3c";

    document.getElementById("progressText")
        .innerText = "Failed";

    document.getElementById("statusMessage")
        .innerText = message;

    setTimeout(() => {
        document.getElementById("progressWrapper")
            .classList.add("hidden");

        document.getElementById("progressFill")
            .style.width = "0%";

        document.getElementById("progressFill")
            .style.background = "#4caf50";
    }, 3000);
}


/* -----------------------------------
   LOAD INITIAL PREVIEW
----------------------------------- */
async function loadPreview() {
    const incidentNumber =
        document.getElementById("incident_number").value.trim();

    const priority =
        document.getElementById("priority_filter").value;

    const vendor =
        document.getElementById("vendor_filter").value;

    if (!incidentNumber) {
        alert("Enter Incident Number");
        return;
    }

    showProgress("Loading incident data...");

    try {
        updateProgress(50, "Generating preview...");

        const response = await fetch("/get-rca-data", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                incident_number: incidentNumber,
                priority: priority,
                vendor: vendor
            })
        });

        const data = await response.json();

        if (data.error) {
            failProgress(data.error);
            alert(data.error);
            return;
        }

        if (data.preview_html) {
            document.getElementById("previewContainer").innerHTML =
                data.preview_html;

            document.getElementById("problem_statement").value =
                data.problem_statement || "";

            document.getElementById("root_cause").value =
                data.root_cause || "";

            document.getElementById("resolution_text").value =
                data.resolution || "";

            document.getElementById("downloadMessage").style.display = "none";
            document.getElementById("downloadButtons")
                .classList.remove("hidden");
        }

        completeProgress("Preview generated successfully");

    } catch (error) {
        console.error(error);
        failProgress("Preview generation failed");
        alert("Failed to load preview");
    }
}


/* -----------------------------------
   FILE UPLOAD SETUP
----------------------------------- */
function setupFileUpload(inputId, type, previewId) {
    const input = document.getElementById(inputId);

    input.addEventListener("change", function () {
        const files = Array.from(input.files);

        files.forEach(file => {
            uploadedFiles[type].push(file);
        });

        renderFilePreview(type, previewId);
        input.value = "";
    });
}


/* -----------------------------------
   RENDER FILE CHIPS
----------------------------------- */
function renderFilePreview(type, previewId) {
    const previewContainer =
        document.getElementById(previewId);

    previewContainer.innerHTML = "";

    uploadedFiles[type].forEach((file, index) => {
        const chip = document.createElement("div");

        chip.className = "file-chip";

        chip.innerHTML = `
            ${file.name}
            <span onclick="removeFile('${type}', ${index}, '${previewId}')">
                ×
            </span>
        `;

        previewContainer.appendChild(chip);
    });
}


/* -----------------------------------
   REMOVE FILE
----------------------------------- */
function removeFile(type, index, previewId) {
    uploadedFiles[type].splice(index, 1);
    renderFilePreview(type, previewId);
}


/* -----------------------------------
   UPDATE PREVIEW
----------------------------------- */
async function updatePreview() {
    const incidentNumber =
        document.getElementById("incident_number").value.trim();

    if (!incidentNumber) {
        alert("Load incident first");
        return;
    }

    showProgress("Preparing updates...");

    const formData = new FormData();

    formData.append("incident_number", incidentNumber);
    formData.append(
        "problem",
        document.getElementById("problem_statement").value
    );
    formData.append(
        "analysis",
        document.getElementById("root_cause").value
    );
    formData.append(
        "resolution",
        document.getElementById("resolution_text").value
    );

    uploadedFiles.problem.forEach(file => {
        formData.append("problem_images", file);
    });

    uploadedFiles.root.forEach(file => {
        formData.append("root_images", file);
    });

    uploadedFiles.resolution.forEach(file => {
        formData.append("resolution_images", file);
    });

    try {
        updateProgress(60, "Updating preview...");

        const response = await fetch("/update-preview", {
            method: "POST",
            body: formData
        });

        const html = await response.text();

        document.getElementById("previewContainer").innerHTML = html;

        completeProgress("Preview updated successfully");

    } catch (error) {
        console.error(error);
        failProgress("Preview update failed");
        alert("Preview update failed");
    }
}


/* -----------------------------------
   DOWNLOAD REPORT
----------------------------------- */
async function downloadReport(type) {
    const incidentNumber =
        document.getElementById("incident_number").value.trim();

    if (!incidentNumber) {
        alert("Load incident first");
        return;
    }

    showProgress("Preparing download...");

    const formData = new FormData();

    formData.append("incident_number", incidentNumber);
    formData.append(
        "problem_statement",
        document.getElementById("problem_statement").value
    );
    formData.append(
        "root_cause",
        document.getElementById("root_cause").value
    );
    formData.append(
        "resolution",
        document.getElementById("resolution_text").value
    );

    uploadedFiles.problem.forEach(file => {
        formData.append("problem_images", file);
    });

    uploadedFiles.root.forEach(file => {
        formData.append("root_images", file);
    });

    uploadedFiles.resolution.forEach(file => {
        formData.append("resolution_images", file);
    });

    try {
        updateProgress(70, "Generating document...");

        const response = await fetch(`/download/${type}`, {
            method: "POST",
            body: formData
        });

        if (!response.ok) {
            failProgress("Download failed");
            alert("Download failed");
            return;
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);

        const a = document.createElement("a");
        a.href = url;

        if (type === "word") {
            a.download = `${incidentNumber}.docx`;
        } else if (type === "pdf") {
            a.download = `${incidentNumber}.pdf`;
        } else {
            a.download = `${incidentNumber}.zip`;
        }

        document.body.appendChild(a);
        a.click();
        a.remove();

        completeProgress(
            `${type.toUpperCase()} download completed successfully`
        );

    } catch (error) {
        console.error(error);
        failProgress("Document generation failed");
        alert("Download failed");
    }
}


/* -----------------------------------
   CLEAR PAGE
----------------------------------- */
function clearPreview() {
    document.getElementById("incident_number").value = "";

    document.getElementById("previewContainer").innerHTML =
        "Preview will appear here";

    document.getElementById("problem_statement").value = "";
    document.getElementById("root_cause").value = "";
    document.getElementById("resolution_text").value = "";

    uploadedFiles = {
        problem: [],
        root: [],
        resolution: []
    };

    document.getElementById("problem_preview_files").innerHTML = "";
    document.getElementById("root_preview_files").innerHTML = "";
    document.getElementById("resolution_preview_files").innerHTML = "";

    document.getElementById("downloadButtons")
        .classList.add("hidden");

    document.getElementById("downloadMessage")
        .style.display = "block";

    document.getElementById("statusMessage")
        .innerText = "Ready";
}


/* -----------------------------------
   INIT
----------------------------------- */
document.addEventListener("DOMContentLoaded", function () {
    setupFileUpload(
        "problem_images",
        "problem",
        "problem_preview_files"
    );

    setupFileUpload(
        "root_images",
        "root",
        "root_preview_files"
    );

    setupFileUpload(
        "resolution_images",
        "resolution",
        "resolution_preview_files"
    );
});


/* -----------------------------------
   SIDEBAR ACCORDION
----------------------------------- */
function toggleSidebarSection(header) {
    const parent = header.parentElement;
    parent.classList.toggle("active");
}

/* -----------------------------------
   HOME NAVIGATION
----------------------------------- */
function goHome() {
    window.location.href = "/";
}