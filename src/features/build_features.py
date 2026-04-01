import pandas as pd
import numpy as np


# -----------------------------------
# 1. BASE
# -----------------------------------
def get_icu_base(patients, admissions, icustays):
    df = patients.merge(admissions, on="SUBJECT_ID", how="inner")
    df = df.merge(icustays, on="SUBJECT_ID", how="inner")
    return df


# -----------------------------------
# 2. UPDATED ITEM IDS 🔥
# -----------------------------------
ITEM_IDS = {
    "heart_rate": [211, 220045],
    "systolic_bp": [51, 455, 220179],
    "spo2": [646, 220277],
    "resp_rate": [618, 220210],
    "temperature": [223761, 678],
    "lactate": [50813, 50960]
}


# -----------------------------------
# 3. EXTRACT VITALS
# -----------------------------------
def extract_vitals(chartevents):
    chartevents = chartevents[
        ["SUBJECT_ID", "ITEMID", "VALUENUM", "CHARTTIME"]
    ].dropna(subset=["VALUENUM"])

    chartevents["CHARTTIME"] = pd.to_datetime(chartevents["CHARTTIME"])

    vitals_list = []

    for name, ids in ITEM_IDS.items():
        temp = chartevents[chartevents["ITEMID"].isin(ids)].copy()
        temp["feature"] = name
        vitals_list.append(temp)

    return pd.concat(vitals_list)


# -----------------------------------
# 4. STAT FEATURES
# -----------------------------------
def create_stat_features(vitals_df):
    features = vitals_df.pivot_table(
        index="SUBJECT_ID",
        columns="feature",
        values="VALUENUM",
        aggfunc=["mean", "min", "max", "std"]
    )

    features.columns = [
        f"{stat}_{feat}" for stat, feat in features.columns
    ]

    return features.reset_index()


# -----------------------------------
# 5. TIME FEATURES
# -----------------------------------
def create_time_features(vitals_df):
    vitals_df = vitals_df.sort_values(["SUBJECT_ID", "feature", "CHARTTIME"])

    vitals_df["trend"] = vitals_df.groupby(
        ["SUBJECT_ID", "feature"]
    )["VALUENUM"].diff()

    vitals_df["rolling_mean"] = vitals_df.groupby(
        ["SUBJECT_ID", "feature"]
    )["VALUENUM"].transform(lambda x: x.rolling(5, min_periods=1).mean())

    return vitals_df.groupby("SUBJECT_ID").agg({
        "trend": "mean",
        "rolling_mean": "mean"
    }).reset_index()


# -----------------------------------
# 6. SAFE AGE
# -----------------------------------
def add_age(df):
    df["DOB"] = pd.to_datetime(df["DOB"], errors="coerce")
    df["ADMITTIME"] = pd.to_datetime(df["ADMITTIME"], errors="coerce")

    def calc(row):
        try:
            age = (row["ADMITTIME"] - row["DOB"]).days / 365.25
            if age < 0 or age > 120:
                return 90
            return age
        except:
            return np.nan

    df["age"] = df.apply(calc, axis=1)
    return df


# -----------------------------------
# 7. DIAGNOSIS
# -----------------------------------
def add_diagnosis_features(df, diagnoses):
    diag_count = diagnoses.groupby("SUBJECT_ID").size().reset_index(name="num_diagnoses")

    unique_diag = diagnoses.groupby("SUBJECT_ID")["ICD9_CODE"].nunique().reset_index(
        name="unique_diseases"
    )

    df = df.merge(diag_count, on="SUBJECT_ID", how="left")
    df = df.merge(unique_diag, on="SUBJECT_ID", how="left")

    df["high_comorbidity"] = (df["num_diagnoses"] > 5).astype(int)

    return df


# -----------------------------------
# 8. MEDS
# -----------------------------------
def add_medication_features(df, meds):
    med_count = meds.groupby("SUBJECT_ID").size().reset_index(name="num_meds")

    meds["vasopressor_flag"] = meds["DRUG"].str.contains(
        "norepinephrine|dopamine|epinephrine", case=False, na=False
    ).astype(int)

    meds["antibiotic_flag"] = meds["DRUG"].str.contains(
        "cef|penicillin|vancomycin", case=False, na=False
    ).astype(int)

    med_flags = meds.groupby("SUBJECT_ID").agg({
        "vasopressor_flag": "max",
        "antibiotic_flag": "max"
    }).reset_index()

    df = df.merge(med_count, on="SUBJECT_ID", how="left")
    df = df.merge(med_flags, on="SUBJECT_ID", how="left")

    df["polypharmacy_flag"] = (df["num_meds"] > 5).astype(int)

    return df


# -----------------------------------
# 9. CLINICAL
# -----------------------------------
def add_clinical_features(df):

    if "mean_heart_rate" in df.columns and "mean_systolic_bp" in df.columns:
        df["shock_index"] = df["mean_heart_rate"] / (df["mean_systolic_bp"] + 1)

    if "min_spo2" in df.columns:
        df["spo2_low_flag"] = (df["min_spo2"] < 90).astype(int)

    if "max_heart_rate" in df.columns:
        df["hr_high_flag"] = (df["max_heart_rate"] > 100).astype(int)

    if "min_systolic_bp" in df.columns:
        df["low_bp_flag"] = (df["min_systolic_bp"] < 90).astype(int)

    if "max_lactate" in df.columns:
        df["lactate_high_flag"] = (df["max_lactate"] > 2).astype(int)

    return df


# -----------------------------------
# 10. INTERACTION
# -----------------------------------
def add_interaction_features(df):

    if "mean_heart_rate" in df.columns and "mean_spo2" in df.columns:
        df["oxygen_stress"] = df["mean_heart_rate"] / (df["mean_spo2"] + 1)

    if "mean_systolic_bp" in df.columns and "mean_spo2" in df.columns:
        df["perfusion_index"] = df["mean_spo2"] / (df["mean_systolic_bp"] + 1)

    return df


# -----------------------------------
# 11. MERGE
# -----------------------------------
def merge_all(base_df, stat_features, time_features):
    df = base_df.copy()
    df = df.merge(stat_features, on="SUBJECT_ID", how="left")
    df = df.merge(time_features, on="SUBJECT_ID", how="left")
    return df


# -----------------------------------
# 12. TARGET
# -----------------------------------
def add_target(df):
    df["mortality"] = df["HOSPITAL_EXPIRE_FLAG"]
    return df


# -----------------------------------
# 13. CLEAN
# -----------------------------------
def handle_missing(df):
    df.fillna(0, inplace=True)
    return df


# -----------------------------------
# 14. SAVE
# -----------------------------------
def save_data(df, path="data/processed/icu_features_final.csv"):
    df.to_csv(path, index=False)