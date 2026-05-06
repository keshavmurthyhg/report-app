from reportlab.platypus import Paragraph, Spacer
from modules.common.utils.text_cleaner import clean_text
from modules.common.utils.formatters import safe_pdf_text


def build_sections(
    elements,
    root,
    l2,
    res,
    styles,
    bullet_style,
    add_images_pdf,
    images
):
    """
    Match PDF RCA layout with Word output
    """

    def add_bullets(text):
        text = safe_pdf_text(text)

        if str(text).lower() in [
            "nan",
            "none",
            "nat",
            ""
        ]:
            text = "-"

        for line in text.split("\n"):
            line = line.strip()

            if not line:
                continue

            if line.startswith("-"):
                line = line[1:].strip()

            line = clean_text(line)

            if line:
                elements.append(
                    Paragraph(
                        f"• {line}",
                        bullet_style
                    )
                )

    def section(title, content, imgs):
        elements.append(
            Paragraph(
                f"<b>{title}</b>",
                styles["Heading2"]
            )
        )

        elements.append(
            Spacer(1, 6)
        )

        add_bullets(content)

        elements.append(
            Spacer(1, 10)
        )

        if imgs:
            add_images_pdf(
                elements,
                imgs
            )

    section(
        "PROBLEM STATEMENT",
        root,
        images.get("root")
    )

    section(
        "ROOT CAUSE",
        l2,
        images.get("l2")
    )

    section(
        "RESOLUTION & RECOMMENDATION",
        res,
        images.get("res")
    )