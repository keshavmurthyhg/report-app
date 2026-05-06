import os
from modules.converter.ppt_to_doc import ppt_to_word


def convert_ppt(ppt_path, output_folder):
    """
    Only converts PPT -> DOCX
    Keep PDF generation separate
    """

    base = os.path.splitext(
        os.path.basename(ppt_path)
    )[0]

    docx_path = os.path.join(
        output_folder,
        f"{base}.docx"
    )

    ppt_to_word(
        ppt_path,
        docx_path
    )

    return docx_path
