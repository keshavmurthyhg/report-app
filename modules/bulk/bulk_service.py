import logging
import pandas as pd

# IMPORTANT:
# use existing working generator
from modules.report.bulk_generator import (
    build_bulk_reports,
    generate_bulk_zip
)

logger = logging.getLogger(__name__)


# ------------------------------
# LOAD SNOW DATA
# ------------------------------
def load_snow_data():
    try:
        df = pd.read_excel("data/snow.xlsx")

        df.columns = [
            str(col).strip().lower()
            for col in df.columns
        ]

        logger.info(f"Loaded {len(df)} records")
        logger.info(f"Columns: {df.columns.tolist()}")

        return df

    except Exception as e:
        logger.exception("snow.xlsx load failed")
        raise e


# ------------------------------
# FILTER INCIDENTS
# ------------------------------
def filter_incidents(
    priority=None,
    year=None,
    from_date=None,
    to_date=None
):
    try:
        df = load_snow_data()

        # Priority filter
        if priority and priority != "All Priorities":
            df = df[df["priority"] == priority]

        # Year filter
        if year and year != "Select":
            df = df[
                pd.to_datetime(df["created"]).dt.year
                == int(year)
            ]

        # Custom from date
        if from_date:
            df = df[
                pd.to_datetime(df["created"])
                >= pd.to_datetime(from_date)
            ]

        # Custom to date
        if to_date:
            df = df[
                pd.to_datetime(df["created"])
                <= pd.to_datetime(to_date)
            ]

        incidents = (
            df["number"]
            .dropna()
            .astype(str)
            .tolist()
        )

        logger.info(
            f"Filtered incidents: {incidents}"
        )

        return incidents

    except Exception as e:
        logger.exception("Incident filtering failed")
        raise e


# ------------------------------
# GENERATE BULK ZIP
# ------------------------------
def generate_bulk_zip_file(
    incident_numbers
):
    try:
        df = load_snow_data()

        logger.info(
            f"Generating reports for {incident_numbers}"
        )

        reports = build_bulk_reports(
            df=df,
            incident_list=incident_numbers
        )

        logger.info(
            f"Generated {len(reports)} reports"
        )

        zip_buffer = generate_bulk_zip(
            reports
        )

        return zip_buffer

    except Exception as e:
        logger.exception(
            "Bulk zip generation failed"
        )
        raise e