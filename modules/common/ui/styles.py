TABLE_STYLE = "width:100%; border-collapse: collapse; font-size:14px; border:2px solid black;"
CELL_STYLE = "border:1px solid black; padding:6px;"
HEADER_CELL_STYLE = "border:1px solid black; padding:6px; font-weight:bold;"

def get_table_style():
    return """
    <style>
    .tbl {
        width: 100%;
        border-collapse: collapse;
        font-family: Arial;
        font-size: 14px;
        margin-bottom: 20px;
    }
    .tbl td {
        border: 1px solid black;
        padding: 8px;
    }
    .hdr {
        font-weight: bold;
        background: #f2f2f2;
        width: 20%;
    }
    </style>
    """
