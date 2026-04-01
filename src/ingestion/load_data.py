import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)


# -----------------------------------
# 1. NORMALIZE COLUMN NAMES
# -----------------------------------
def normalize_columns(df):
    df.columns = df.columns.str.upper()
    return df


# -----------------------------------
# 2. LOAD CSV FILE (SAFE LOADING)
# -----------------------------------
def load_csv(path, nrows=None):
    logging.info(f"Loading {path}...")
    df = pd.read_csv(path, nrows=nrows)
    df = normalize_columns(df)
    return df


# -----------------------------------
# 3. LOAD ALL DATASETS
# -----------------------------------
def load_data(base_path="data/raw/", sample=True):
    """
    sample=True → loads limited rows (faster for development)
    sample=False → loads full dataset
    """

    nrows = 100000 if sample else None

    # Core tables
    patients = load_csv(base_path + "PATIENTS.csv")
    admissions = load_csv(base_path + "ADMISSIONS.csv")
    icustays = load_csv(base_path + "ICUSTAYS.csv")

    # Large tables (limit rows initially)
    chartevents = load_csv(base_path + "CHARTEVENTS.csv", nrows=nrows)

    # Additional tables (for advanced features)
    diagnoses = load_csv(base_path + "DIAGNOSES_ICD.csv", nrows=nrows)
    medications = load_csv(base_path + "PRESCRIPTIONS.csv", nrows=nrows)

    logging.info("All datasets loaded successfully!")

    return (
        patients,
        admissions,
        icustays,
        chartevents,
        diagnoses,
        medications
    )