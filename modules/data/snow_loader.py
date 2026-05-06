import pandas as pd
import os

def load_snow_data():

    file_path = os.path.join("data", "Snow.xlsx")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    df = pd.read_excel(file_path)

    # normalize column names
    df.columns = df.columns.str.strip().str.lower()

    return df
