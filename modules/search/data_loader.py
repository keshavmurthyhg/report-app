import pandas as pd

# -------------------------------
# NORMALIZE COLUMN NAMES
# -------------------------------
def norm(df):
    df.columns = df.columns.astype(str).str.strip().str.lower()
    return df


# -------------------------------
# SAFE COLUMN FETCH
# -------------------------------
def col(df, *names):
    for n in names:
        if n in df.columns:
            return df[n]
    return None


# -------------------------------
# DATE PARSER (FIXED)
# -------------------------------
def parse_mixed_date(val):
    if pd.isna(val):
        return pd.NaT

    val = str(val).strip()

    try:
        # 🔥 Let pandas auto-detect + enforce day-first
        return pd.to_datetime(val, dayfirst=True, errors="coerce")
    except:
        return pd.NaT

# -------------------------------
# AZURE
# -------------------------------
def build_azure(df):
    return pd.DataFrame({
        "Number": col(df, "id"),
        "Description": col(df, "title"),
        "Priority": col(df, "release_windchill"),
        "Status": col(df, "state"),
        "Created By": col(df, "created by"),
        "Created Date": col(df, "created date"),
        "Assigned To": col(df, "assigned to"),
        "Resolved Date": col(df, "resolved date"),
        "Source": "AZURE"
    })


# -------------------------------
# SNOW
# -------------------------------
def build_snow(df):
    return pd.DataFrame({
        "Number": col(df, "number"),
        "Description": col(df, "short description", "description"),
        "Priority": col(df, "priority"),
        "Status": col(df, "incident state"),
        "Created By": col(df, "opened by", "created by"),
        "Created Date": col(df, "created", "date"),
        "Assigned To": col(df, "assigned to"),
        "Resolved Date": col(df, "resolved"),
        "Source": "SNOW"
    })


# -------------------------------
# PTC
# -------------------------------
def build_ptc(df):
    return pd.DataFrame({
        "Number": col(df, "case number"),
        "Description": col(df, "subject"),
        "Priority": col(df, "severity"),
        "Status": col(df, "status"),
        "Created By": col(df, "case contact"),
        "Created Date": col(df, "created date"),
        "Assigned To": col(df, "case assignee"),
        "Resolved Date": col(df, "resolved date"),
        "Source": "PTC"
    })


# -------------------------------
# LOAD DATA
# -------------------------------
def load_data():

    try:
        azure = pd.read_csv("data/Azure.csv")

        snow = pd.read_excel(
            "data/Snow.xlsx",
            engine="openpyxl"
        )

        ptc = pd.read_csv(
            "data/Ptc.csv",
            index_col=False,
            engine="python"
        )

        ptc = ptc.reset_index(drop=True)

    except Exception as e:
        print(f"Data load failed: {e}")
        return pd.DataFrame(), {}

    azure = norm(azure)
    snow = norm(snow)
    ptc = norm(ptc)

    df = pd.concat([
        build_azure(azure),
        build_snow(snow),
        build_ptc(ptc)
    ], ignore_index=True)

    df = df.reset_index(drop=True)

    # ---------- DATE NORMALIZATION ----------
    for col_name in ["Created Date", "Resolved Date"]:
        if col_name in df.columns:
            df[col_name] = df[col_name].apply(parse_mixed_date)

    df = df.fillna("")

    from datetime import datetime
    info = datetime.now().strftime("%d-%b-%Y %H:%M")

    return df, info
