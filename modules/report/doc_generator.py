from datetime import datetime

from modules.report.renderers.pdf_renderer import generate_pdf_doc
from modules.report.renderers.word_renderer import generate_word_doc
from modules.common.utils.text_cleaner import format_description
from modules.common.utils.parsers import extract_azure_id

# RCA service
from modules.report.services.rca_service import build_rca


def enrich_data(data):
    """
    Common enrichment layer for:
    - Single PDF
    - Single Word
    - Bulk PDF
    - Bulk Word
    """

    safe_data = data.copy()

    # -----------------------------------
    # AZURE BUG FIX
    # Strictly extract only from resolution notes
    # -----------------------------------
    azure_value = extract_azure_id(
        str(
            safe_data.get(
                "resolution notes",
                ""
            )
        )
    )

    safe_data["azure_bug"] = (
        azure_value if azure_value else "-"
    )
    # -----------------------------------
    # PTC CASE FIX
    # -----------------------------------
    ptc_value = (
        safe_data.get("ptc_case")
        or safe_data.get("vendor ticket")
        or safe_data.get("ptc case")
    )

    safe_data["ptc_case"] = ptc_value if ptc_value else "-"

    return safe_data


def prepare_data(data):
    """
    Single source of truth for:
    UI preview
    PDF
    Word
    Bulk PDF
    Bulk Word
    """

    safe_data = enrich_data(data)

    # Keep description formatting
    safe_data["description"] = format_description(
        safe_data.get("description")
    )

    # RCA generation
    rca = build_rca(safe_data)

    safe_data["problem"] = rca.get(
        "problem_statement",
        ""
    )

    safe_data["analysis"] = rca.get(
        "root_cause",
        ""
    )

    safe_data["resolution"] = rca.get(
        "resolution",
        ""
    )

    return safe_data


def get_download_filename(data, extension):
    """
    Generates filename format:
    INC109720389_24Apr2026.pdf
    INC109720389_24Apr2026.docx
    """

    incident_number = str(
        data.get("number", "incident_report")
    ).strip()

    # DDMMMYYYY format
    current_date = datetime.now().strftime("%d%b%Y")

    return f"{incident_number}_{current_date}.{extension}"


# -----------------------------------
# PDF
# -----------------------------------
def generate_pdf(
    data,
    root=None,
    l2=None,
    res=None,
    images=None
):
    prepared = prepare_data(data)

    pdf_buffer = generate_pdf_doc(
        data=prepared,
        root=prepared.get("problem"),
        l2=prepared.get("analysis"),
        res=prepared.get("resolution"),
        images=images or {}
    )

    return pdf_buffer


# -----------------------------------
# WORD
# -----------------------------------
def generate_word_doc_wrapper(
    data,
    root=None,
    l2=None,
    res=None,
    images=None,
    ppt_data=None
):
    prepared = prepare_data(data)

    word_buffer = generate_word_doc(
        data=prepared,
        root=prepared.get("problem"),
        l2=prepared.get("analysis"),
        res=prepared.get("resolution"),
        images=images or {},
        ppt_data=ppt_data
    )

    return word_buffer
