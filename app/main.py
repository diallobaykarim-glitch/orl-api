from fastapi import FastAPI
from database import SessionLocal, engine, Base
from models import Patient
from schemas import PatientData
import math

Base.metadata.create_all(bind=engine)

app = FastAPI(title="ORL IA PRODUCTION", version="1.0.0")


@app.get("/")
def root():
    return {
        "message": "ORL IA API",
        "version": "1.0.0",
        "endpoints": {
            "docs": "/docs",
            "predict": "/predict (POST)",
            "patients": "/patients (GET)"
        }
    }


def sigmoid(x):
    return 1 / (1 + math.exp(-x))


@app.post("/predict")
def predict(data: PatientData):

    score = (
        data.age * 0.015 +
        data.smoking * 2 +
        data.alcohol * 1.5 +
        data.dysphonia * 2 +
        data.dysphagia * 1.5 +
        data.imaging_suspicious * 3 +
        data.duration_months * 0.1 +
        data.pain_scale * 0.2
    )

    prob = sigmoid(score / 10)

    level = "Faible"
    if prob > 0.6:
        level = "Élevé"
    elif prob > 0.4:
        level = "Modéré"

    db = SessionLocal()

    patient = Patient(
        age=data.age,
        sex=data.sex,
        smoking=data.smoking,
        alcohol=data.alcohol,
        risk_probability=prob,
        risk_level=level
    )

    db.add(patient)
    db.commit()
    db.close()

    return {
        "probability": round(prob, 3),
        "risk_level": level
    }


@app.get("/patients")
def patients():

    db = SessionLocal()
    data = db.query(Patient).all()
    db.close()

    return data
