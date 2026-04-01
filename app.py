#app.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import joblib

app = FastAPI(title="ICU Risk Prediction API")

# -----------------------------------
# LOAD MLFLOW MODEL (for prediction) and removed  the mlflow dependency from requirements.txt to avoid issues with mlflow in production
# -----------------------------------
model = joblib.load("models/model.pkl")

# -----------------------------------
# LOAD RAW MODEL (for probability 🔥)
# -----------------------------------
raw_model = joblib.load("models/xgb_model.pkl")

# Load features
feature_cols = joblib.load("models/feature_columns.pkl")


# -----------------------------------
# INPUT SCHEMA
# -----------------------------------
class PatientData(BaseModel):
    age: float
    LOS: float
    num_diagnoses: int
    unique_diseases: int
    num_meds: int
    vasopressor_flag: int
    antibiotic_flag: int

    mean_temperature: float
    max_temperature: float
    min_temperature: float

    trend: float
    rolling_mean: float

    mean_spo2: float
    min_spo2: float
    spo2_low_flag: int

    max_systolic_bp: float
    min_systolic_bp: float
    mean_systolic_bp: float

    mean_resp_rate: float
    max_resp_rate: float
    std_resp_rate: float

    mean_heart_rate: float
    min_heart_rate: float
    std_heart_rate: float


# -----------------------------------
# ROOT
# -----------------------------------
@app.get("/")
def home():
    return {"message": "ICU Risk Prediction API Running 🚀"}


# -----------------------------------
# PREDICT
# -----------------------------------
@app.post("/predict")
def predict(data: PatientData):
    try:
        df = pd.DataFrame([data.dict()])

        # Align features
        df = df.reindex(columns=feature_cols, fill_value=0)

        # Prediction (MLflow model)
        prediction = model.predict(df)[0]

        # 🔥 Probability (raw model)
        probability = raw_model.predict_proba(df)[0][1]

        return {
            "prediction": int(prediction),
            "risk_probability": float(probability),
            "status": "success"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))