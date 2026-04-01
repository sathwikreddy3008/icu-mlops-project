import pandas as pd
import joblib
import os

from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, roc_auc_score
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier

import mlflow
import mlflow.xgboost
import mlflow.sklearn


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

    # Target
    y = df["mortality"].astype(int)

    # Features
    X = df.copy()

    # -----------------------------------
    # REMOVE LEAKAGE + IDs
    # -----------------------------------
    print("Removing leakage columns...")

    drop_patterns = [
        "HOSPITAL_EXPIRE_FLAG",
        "DEATHTIME",
        "DOD",
        "DISCHARGE_LOCATION",
        "ROW_ID",
        "SUBJECT_ID",
        "HADM_ID",
        "ICUSTAY_ID",
        "WARDID",
        "DOB",
        "ADMITTIME",
        "EXPIRE_FLAG",
        "HAS_CHARTEVENTS_DATA"
    ]

    for pattern in drop_patterns:
        X = X.loc[:, ~X.columns.str.contains(pattern, case=False)]

    # Drop target
    X = X.drop(columns=["mortality"], errors="ignore")

    print(f"After cleanup: {X.shape}")

    # -----------------------------------
    # ENCODING
    # -----------------------------------
    print("Encoding categorical features...")

    X = pd.get_dummies(X, drop_first=True)
    X = X.select_dtypes(include=["number"])

    print(f"Final features: {X.shape}")

    # -----------------------------------
    # 🔥 SAVE FEATURE COLUMNS
    # -----------------------------------
    os.makedirs("models", exist_ok=True)

    joblib.dump(X.columns.tolist(), "models/feature_columns.pkl")
    print("✅ Feature columns saved!")

    # -----------------------------------
    # SPLIT
    # -----------------------------------
    print("Splitting data...")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    print(f"Train: {X_train.shape}, Test: {X_test.shape}")

    return X_train, X_test, y_train, y_test


# -----------------------------------
# 3. TRAIN + LOG + REGISTER + SAVE
# -----------------------------------
def train_and_register_model(model, model_name, params,
                             X_train, X_test, y_train, y_test):

    print(f"\n[TRAINING] {model_name}")

    with mlflow.start_run(run_name=model_name):

        # -----------------------------------
        # SET PARAMETERS
        # -----------------------------------
        model.set_params(**params)

        # -----------------------------------
        # TRAIN MODEL
        # -----------------------------------
        print("Training model...")
        model.fit(X_train, y_train)

        # -----------------------------------
        # PREDICTIONS
        # -----------------------------------
        preds = model.predict(X_test)
        probs = model.predict_proba(X_test)[:, 1]

        # -----------------------------------
        # METRICS
        # -----------------------------------
        acc = accuracy_score(y_test, preds)
        roc = roc_auc_score(y_test, probs)

        print(f"{model_name} Accuracy: {acc:.4f}")
        print(f"{model_name} ROC-AUC: {roc:.4f}")

        # -----------------------------------
        # LOG TO MLFLOW
        # -----------------------------------
        print("Logging to MLflow...")

        mlflow.log_param("model_name", model_name)
        mlflow.log_params(params)
        mlflow.log_metric("accuracy", acc)
        mlflow.log_metric("roc_auc", roc)

        # -----------------------------------
        # REGISTER MODEL
        # -----------------------------------
        print("Registering model in MLflow...")

        if model_name == "XGBoost":
            mlflow.xgboost.log_model(
                model,
                artifact_path="model",
                registered_model_name="icu_risk_model"
            )
        else:
            mlflow.sklearn.log_model(
                model,
                artifact_path="model",
                registered_model_name="icu_risk_model"
            )

        # -----------------------------------
        # 🔥 SAVE RAW MODEL (IMPORTANT FOR PROBABILITY)
        # -----------------------------------
        print("Saving raw model locally...")

        os.makedirs("models", exist_ok=True)

        if model_name == "XGBoost":
            joblib.dump(model, "models/xgb_model.pkl")
        elif model_name == "RandomForest":
            joblib.dump(model, "models/rf_model.pkl")

        print(f"✅ {model_name} saved + registered!")

        return acc, roc


# -----------------------------------
# 4. MAIN PIPELINE
# -----------------------------------
def main():
    print("🚀 Starting Full Training Pipeline...")

    # Step 1
    df = load_data()

    # Step 2
    X_train, X_test, y_train, y_test = prepare_data(df)

    # -----------------------------------
    # MODEL 1: XGBOOST
    # -----------------------------------
    print("\n[STEP 3A] XGBoost")

    xgb_params = {
        "n_estimators": 200,
        "max_depth": 6,
        "learning_rate": 0.1,
        "subsample": 0.8,
        "colsample_bytree": 0.8,
        "n_jobs": -1,
        "random_state": 42
    }

    train_and_register_model(
        model=XGBClassifier(),
        model_name="XGBoost",
        params=xgb_params,
        X_train=X_train,
        X_test=X_test,
        y_train=y_train,
        y_test=y_test
    )

    # -----------------------------------
    # MODEL 2: RANDOM FOREST
    # -----------------------------------
    print("\n[STEP 3B] RandomForest")

    rf_params = {
        "n_estimators": 150,
        "max_depth": 10,
        "n_jobs": -1,
        "random_state": 42
    }

    train_and_register_model(
        model=RandomForestClassifier(),
        model_name="RandomForest",
        params=rf_params,
        X_train=X_train,
        X_test=X_test,
        y_train=y_train,
        y_test=y_test
    )

    print("\n🎉 Training pipeline completed successfully!")


# -----------------------------------
# ENTRY POINT
# -----------------------------------
if __name__ == "__main__":
    main()