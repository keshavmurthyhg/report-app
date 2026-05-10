/* -------------------------
   PROGRESS FUNCTIONS
------------------------- */

function showProgress(message) {
    document.getElementById("progressWrapper")
        .classList.remove("hidden");

    document.getElementById("progressFill")
        .style.width = "20%";

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
}


/* -------------------------
   GENERATE
------------------------- */

function generateBulkReports() {
    const incidents = window.filteredIncidents
        ? window.filteredIncidents.join(", ")
        : document.getElementById("bulk_incidents").value.trim();

    const outputType =
        document.getElementById("bulk_output_type").value;

    if (!incidents) {
        alert("Enter incident numbers");
        return;
    }

    const incidentList = incidents
        .split(",")
        .map(i => i.trim())
        .filter(i => i !== "");

    showProgress("Starting bulk generation...");

    setTimeout(() => {
        updateProgress(40, "Fetching incident data...");

        setTimeout(() => {
            updateProgress(75, "Publishing reports...");

            setTimeout(() => {

                let rows = "";
                let successCount = 0;
                let failedCount = 0;

                incidentList.forEach((incident, index) => {

                    // Mock failure for every 3rd record
                    let status =
                        (index + 1) % 3 === 0
                            ? "Failed"
                            : "Successful";

                    if (status === "Successful") {
                        successCount++;
                    } else {
                        failedCount++;
                    }

                    rows += `
                        <tr data-status="${status.toLowerCase()}">
                            <td>${new Date().toLocaleDateString()}</td>
                            <td>${incident}</td>
                            <td>${outputType.toUpperCase()}</td>
                            <td class="${
                                status === "Successful"
                                    ? "status-success"
                                    : "status-failed"
                            }">
                                ${status}
                            </td>
                        </tr>
                    `;
                });

                document.getElementById(
                    "bulkResultsContainer"
                ).innerHTML = `
                    <div class="results-toolbar">

                        <div class="table-filter-bar">
                            <button onclick="filterResults('all')">
                                All
                            </button>

                            <button onclick="filterResults('successful')">
                                Successful
                            </button>

                            <button onclick="filterResults('failed')">
                                Failed
                            </button>
                        </div>

                        <button class="resend-btn"
                                onclick="resendFailedJobs()">
                            Resend Failed Jobs
                        </button>

                    </div>

                    <table class="results-table"
                        id="bulkResultsTable">

                        <thead>
                            <tr>
                                <th>Date</th>
                                <th>Incident Number</th>
                                <th>Output Type</th>
                                <th>Status</th>
                            </tr>
                        </thead>

                        <tbody>
                            ${rows}
                        </tbody>
                    </table>
                `;

                document.getElementById("totalJobs").innerText =
                    incidentList.length;

                document.getElementById("successJobs").innerText =
                    successCount;

                document.getElementById("failedJobs").innerText =
                    failedCount;

                completeProgress("Bulk generation completed");

            }, 1200);

        }, 1000);

    }, 1000);
}

function filterResults(type) {
    const rows =
        document.querySelectorAll("#bulkResultsTable tbody tr");

    rows.forEach(row => {
        const status =
            row.cells[3].innerText.toLowerCase();

        if (type === "all") {
            row.style.display = "";
        }
        else if (type === "success") {
            row.style.display =
                status.includes("successful")
                ? ""
                : "none";
        }
        else if (type === "failed") {
            row.style.display =
                status.includes("failed")
                ? ""
                : "none";
        }
    });
}

/* -------------------------
   DOWNLOAD
------------------------- */

function downloadBulkZip() {
    const incidents =
        document.getElementById("bulk_incidents").value.trim();

    if (!incidents) {
        alert("No incidents available for download");
        return;
    }

    fetch("/bulk/download-zip", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            incidents: incidents
        })
    })
    .then(response => response.blob())
    .then(blob => {
        const url = window.URL.createObjectURL(blob);

        const a = document.createElement("a");
        a.href = url;
        a.download = "bulk_reports.zip";

        document.body.appendChild(a);
        a.click();
        a.remove();

        document.getElementById("statusMessage").innerText =
            "ZIP downloaded successfully";
    })
    .catch(error => {
        console.error(error);
    });
}


function downloadFailedReport() {
    const failedRows =
        document.querySelectorAll(
            '.status-failed'
        );

    let failedIncidents = [];

    failedRows.forEach(row => {
        const tr = row.closest("tr");

        if (tr) {
            const incident =
                tr.children[1].innerText.trim();

            failedIncidents.push(incident);
        }
    });

    if (failedIncidents.length === 0) {
        alert("No failed incidents found");
        return;
    }

    fetch("/bulk/download-failed-report", {
        method: "POST",
        headers: {
            "Content-Type":
                "application/json"
        },
        body: JSON.stringify({
            failed_incidents:
                failedIncidents
        })
    })
    .then(response => response.blob())
    .then(blob => {
        const url =
            window.URL.createObjectURL(blob);

        const a =
            document.createElement("a");

        a.href = url;
        a.download =
            "failed_incidents.csv";

        a.click();

        completeProgress(
            "Failed report downloaded"
        );
    })
    .catch(error => {
        console.error(error);

        document.getElementById(
            "statusMessage"
        ).innerText =
            "Failed report download error";
    });
}


/* -------------------------
   RESEND FAILED
------------------------- */

function resendFailedJobs() {
    alert("Retrying failed jobs...");
}


/* -------------------------
   FILTERS
------------------------- */

function applyBulkFilters() {
    const priority =
        document.getElementById("bulk_priority_filter").value;

    const preset =
        document.getElementById("bulk_preset_date_filter").value;

    const year =
        document.getElementById("bulk_year_filter").value;

    const fromDate =
        document.getElementById("bulk_from_date").value;

    const toDate =
        document.getElementById("bulk_to_date").value;

    showProgress("Fetching incidents...");

    fetch("/bulk/filter-incidents", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            priority: priority,
            preset: preset,
            year: year,
            from_date: fromDate,
            to_date: toDate
        })
    })
    .then(res => res.json())
    .then(data => {

        if (data.success) {

            const incidentText =
                data.incidents.join(", ");

            // update textarea
            document.getElementById("bulk_incidents").value =
                incidentText;

            // store latest filtered incidents globally
            window.filteredIncidents =
                data.incidents;

            completeProgress(
                `${data.incidents.length} incidents fetched`
            );
        }
        else {
            document.getElementById(
                "statusMessage"
            ).innerText = "Filter failed";
        }
    })
    .catch(err => {
        console.error(err);

        document.getElementById(
            "statusMessage"
        ).innerText = "Error fetching incidents";
    });
}

/* -------------------------
   OUTPUT TYPE
------------------------- */

function setBulkOutputType(type) {
    document.getElementById("bulk_output_type").value = type;

    document.getElementById("statusMessage")
        .innerText = `${type.toUpperCase()} selected`;
}


/* -------------------------
   CLEAR
------------------------- */

function clearBulkWorkspace() {
    document.getElementById("bulk_incidents").value = "";
    document.getElementById("bulkResultsContainer").innerHTML =
        "No reports generated yet";

    document.getElementById("totalJobs").innerText = 0;
    document.getElementById("successJobs").innerText = 0;
    document.getElementById("failedJobs").innerText = 0;

    document.getElementById("statusMessage").innerText = "Ready";

    document.getElementById("progressWrapper")
        .classList.add("hidden");
}


/* -------------------------
   ACCORDION
------------------------- */

function toggleSidebarSection(header) {
    const parent = header.parentElement;
    parent.classList.toggle("active");
}


/* -------------------------
   HOME
------------------------- */

function goHome() {
    window.location.href = "/";
}