from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import numpy as np

app = FastAPI(title="ORL IA API", version="0.1.0")

# Charger modèle
model = joblib.load("model.pkl")


class Patient(BaseModel):
    age: int
    larynx: int
    parotide: int
    ethmoide: int


@app.get("/")
def home():
    return {"message": "ORL API is running"}


@app.post("/predict")
def predict(patient: Patient):
    X = np.array([[patient.age, patient.larynx, patient.parotide, patient.ethmoide]])
    pred = model.predict(X)[0]
    proba = model.predict_proba(X)[0].tolist()

    return {
        "prediction": int(pred),
        "probabilities": proba
    }