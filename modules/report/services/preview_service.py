from modules.report.report_service import load_incident_data
from modules.report.doc_generator import prepare_data


def get_preview_data(incident_number):
    """
    Returns fully prepared data including RCA
    for UI preview/edit
    """

    raw_data = load_incident_data(incident_number)

    prepared = prepare_data(raw_data)

    return prepared