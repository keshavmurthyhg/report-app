import re


def extract_azure_id(text):
    """
    Extract Azure work item ID ONLY from valid Azure DevOps URLs.

    Example:
    https://dev.azure.com/VolvoGroup-DVP/VCEWindchillPLM/_workitems/edit/123456
    """

    if not text:
        return ""

    text = str(text)

    match = re.search(
        r"dev\.azure\.com/VolvoGroup-DVP/VCEWindchillPLM/_workitems/edit/(\d{6})",
        text,
        re.IGNORECASE
    )

    if match:
        return match.group(1)

    return ""
