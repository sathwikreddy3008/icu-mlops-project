from src.ingestion.load_data import load_data
from src.features.build_features import (
    get_icu_base,
    extract_vitals,
    create_stat_features,
    create_time_features,
    merge_all,
    add_age,
    add_diagnosis_features,
    add_medication_features,
    add_clinical_features,
    add_interaction_features,
    add_target,
    handle_missing,
    save_data
)


def run_pipeline():
    print("🚀 Starting ICU Feature Pipeline...")

    # -----------------------------------
    # 1. LOAD DATA
    # -----------------------------------
    print("\n[STEP 1] Loading data...")
    (
        patients,
        admissions,
        icustays,
        chartevents,
        diagnoses,
        medications
    ) = load_data()

    print("✅ Data loaded successfully!")

    # -----------------------------------
    # 2. BASE DATASET
    # -----------------------------------
    print("\n[STEP 2] Building base dataset...")
    base_df = get_icu_base(patients, admissions, icustays)
    print(f"Base dataset shape: {base_df.shape}")

    # -----------------------------------
    # 3. AGE FEATURE
    # -----------------------------------
    print("\n[STEP 3] Adding age feature...")
    base_df = add_age(base_df)

    # -----------------------------------
    # 4. VITAL FEATURES
    # -----------------------------------
    print("\n[STEP 4] Extracting vitals...")
    vitals_df = extract_vitals(chartevents)
    print(f"Vitals data shape: {vitals_df.shape}")

    print("Creating statistical features (mean, min, max, std)...")
    stat_features = create_stat_features(vitals_df)

    print("Creating time-series features (trend, rolling mean)...")
    time_features = create_time_features(vitals_df)

    # -----------------------------------
    # 5. MERGE CORE FEATURES
    # -----------------------------------
    print("\n[STEP 5] Merging core features...")
    df = merge_all(base_df, stat_features, time_features)
    print(f"After merge shape: {df.shape}")

    # -----------------------------------
    # 6. DIAGNOSIS FEATURES
    # -----------------------------------
    print("\n[STEP 6] Adding diagnosis features...")
    df = add_diagnosis_features(df, diagnoses)

    # -----------------------------------
    # 7. MEDICATION FEATURES
    # -----------------------------------
    print("\n[STEP 7] Adding medication features...")
    df = add_medication_features(df, medications)

    # -----------------------------------
    # 8. CLINICAL FEATURES
    # -----------------------------------
    print("\n[STEP 8] Adding clinical derived features...")
    df = add_clinical_features(df)

    # -----------------------------------
    # 9. INTERACTION FEATURES (FIXED 🔥)
    # -----------------------------------
    print("\n[STEP 9] Adding interaction features...")
    df = add_interaction_features(df)

    # -----------------------------------
    # 10. HANDLE MISSING
    # -----------------------------------
    print("\n[STEP 10] Handling missing values...")
    df = handle_missing(df)

    # -----------------------------------
    # 11. TARGET
    # -----------------------------------
    print("\n[STEP 11] Adding target variable...")
    df = add_target(df)

    # -----------------------------------
    # 12. FINAL CHECK
    # -----------------------------------
    print("\n[STEP 12] Final dataset info:")
    print(df.shape)
    print("Columns:", len(df.columns))

    # -----------------------------------
    # 13. SAVE DATA
    # -----------------------------------
    print("\n[STEP 13] Saving dataset...")
    save_data(df)

    print("\n✅ Pipeline completed successfully!")


# -----------------------------------
# ENTRY POINT
# -----------------------------------
if __name__ == "__main__":
    run_pipeline()