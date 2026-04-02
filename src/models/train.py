import pandas as pd
import joblib
import os

from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, roc_auc_score
from xgboost import XGBClassifier

# -----------------------------------
# 1. LOAD DATA
# -----------------------------------
def load_data():
    print("\n[STEP 1] Loading dataset...")

    df = pd.read_csv("data/processed/icu_features_final.csv")

    print(f"Dataset shape: {df.shape}")
    return df


# -----------------------------------
# 2. PREPARE DATA
# -----------------------------------
def prepare_data(df):
    print("\n[STEP 2] Preparing data...")

    df = df.dropna()
    print(f"After dropping NA: {df.shape}")

    # -----------------------------------
    # TARGET
    # -----------------------------------
    y = df["mortality"].astype(int)

    # -----------------------------------
    # 🔥 SELECT ONLY API FEATURES (IMPORTANT)
    # -----------------------------------
    feature_cols = [
        "age", "LOS", "num_diagnoses", "unique_diseases", "num_meds",
        "vasopressor_flag", "antibiotic_flag",
        "mean_temperature", "max_temperature", "min_temperature",
        "trend", "rolling_mean",
        "mean_spo2", "min_spo2", "spo2_low_flag",
        "max_systolic_bp", "min_systolic_bp", "mean_systolic_bp",
        "mean_resp_rate", "max_resp_rate", "std_resp_rate",
        "mean_heart_rate", "min_heart_rate", "std_heart_rate"
    ]

    # -----------------------------------
    # SELECT FEATURES
    # -----------------------------------
    X = df[feature_cols]

    print(f"Selected features shape: {X.shape}")

    # -----------------------------------
    # SAVE FEATURE COLUMNS
    # -----------------------------------
    os.makedirs("models", exist_ok=True)
    joblib.dump(feature_cols, "models/feature_columns.pkl")
    print("✅ Feature columns saved!")

    # -----------------------------------
    # SPLIT
    # -----------------------------------
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    print(f"Train: {X_train.shape}, Test: {X_test.shape}")

    return X_train, X_test, y_train, y_test


# -----------------------------------
# 3. TRAIN MODEL
# -----------------------------------
def train_model(X_train, X_test, y_train, y_test):

    print("\n[STEP 3] Training XGBoost model...")

    model = XGBClassifier(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        n_jobs=-1,
        random_state=42
    )

    model.fit(X_train, y_train)

    # -----------------------------------
    # EVALUATION
    # -----------------------------------
    preds = model.predict(X_test)
    probs = model.predict_proba(X_test)[:, 1]

    acc = accuracy_score(y_test, preds)
    roc = roc_auc_score(y_test, probs)

    print(f"Accuracy: {acc:.4f}")
    print(f"ROC-AUC: {roc:.4f}")

    # -----------------------------------
    # SAVE MODEL
    # -----------------------------------
    os.makedirs("models", exist_ok=True)

    joblib.dump(model, "models/model.pkl")
    joblib.dump(model, "models/xgb_model.pkl")

    print("✅ Model saved successfully!")

    return model


# -----------------------------------
# 4. MAIN
# -----------------------------------
def main():
    print("🚀 Starting Training Pipeline...")

    df = load_data()
    X_train, X_test, y_train, y_test = prepare_data(df)

    train_model(X_train, X_test, y_train, y_test)

    print("\n🎉 Training completed successfully!")


# -----------------------------------
# ENTRY POINT
# -----------------------------------
if __name__ == "__main__":
    main()