from modules.common.ui.styles import get_table_style
from modules.common.utils.formatters import (
    format_description,
    format_date,
    safe_text
)


def _val(x):
    return safe_text(x)


def _link(value, type_):
    value = safe_text(value)

    if value == "-":
        return "-"

    if type_ == "incident":
        url = f"https://volvoitsm.service-now.com/nav_to.do?uri=incident.do?sysparm_query=number={value}"
    elif type_ == "azure":
        url = f"https://dev.azure.com/VolvoGroup-DVP/VCEWindchillPLM/_workitems/edit/{value}"
    elif type_ == "ptc":
        url = f"https://support.ptc.com/appserver/cs/view/solution.jsp?n={value}"
    else:
        return value

    return f'<a href="{url}" target="_blank">{value}</a>'


def render_preview_html(
    data,
    root=None,
    l2=None,
    resolution=None,
    show_rca=True
):
    """
    Flask-compatible HTML preview renderer
    """

    if not data:
        return "<h3>No data available for preview</h3>"

    style = get_table_style()

    table1 = f"""
    <table class="tbl">
        <tr>
            <td class="hdr">INCIDENT</td>
            <td>{_link(data.get("number"), "incident")}</td>
            <td class="hdr">CREATED BY</td>
            <td>{_val(data.get("created_by"))}</td>
        </tr>
        <tr>
            <td class="hdr">AZURE BUG</td>
            <td>{_link(data.get("azure_bug"), "azure")}</td>
            <td class="hdr">CREATED DATE</td>
            <td>{_val(format_date(data.get("created_date")))}</td>
        </tr>
        <tr>
            <td class="hdr">PTC CASE</td>
            <td>{_link(data.get("ptc_case"), "ptc")}</td>
            <td class="hdr">ASSIGNED TO</td>
            <td>{_val(data.get("assigned_to"))}</td>
        </tr>
        <tr>
            <td class="hdr">PRIORITY</td>
            <td>{_val(data.get("priority"))}</td>
            <td class="hdr">RESOLVED DATE</td>
            <td>{_val(format_date(data.get("resolved_date")))}</td>
        </tr>
    </table>
    """

    table2 = f"""
    <table class="tbl">
        <tr>
            <td class="hdr">SHORT DESCRIPTION</td>
            <td class="hdr">DESCRIPTION</td>
        </tr>
        <tr>
            <td>{_val(data.get("short_description"))}</td>
            <td>{_val(format_description(data.get("description")))}</td>
        </tr>
    </table>
    """

    html = f"""
    <div class="container">
        <h2>Preview</h2>
        {style}
        {table1}
        <br>
        {table2}
    """

    # RCA section
    if show_rca:
        html += f"""
        <br>
        <table class="tbl">
            <tr>
                <td class="hdr">PROBLEM STATEMENT</td>
                <td>{_val(root or data.get("problem"))}</td>
            </tr>
            <tr>
                <td class="hdr">ROOT CAUSE</td>
                <td>{_val(l2 or data.get("analysis"))}</td>
            </tr>
            <tr>
                <td class="hdr">RESOLUTION</td>
                <td>{_val(resolution or data.get("resolution"))}</td>
            </tr>
        </table>
        """

    html += "</div>"

    return html