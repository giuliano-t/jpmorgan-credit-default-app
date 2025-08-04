from fastapi import FastAPI, Response
from pydantic import BaseModel
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
import pickle
import os

app = FastAPI()

# CORS middleware allowing all origins and methods
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],            # Change to your domain in production
    allow_credentials=True,
    allow_methods=["*"],            # Allow all HTTP methods including OPTIONS
    allow_headers=["*"],
)

# Paths setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "..", "static")
MODEL_PATH = os.path.join(BASE_DIR, "..", "models", "xgboost_model.pkl")

# Mount static directory
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Serve index.html at root
@app.get("/", response_class=FileResponse)
def serve_index():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))

# Health check endpoint
@app.get("/health")
def health():
    return {"status": "healthy", "model": "credit_default_xgboost_v1"}

# Explicitly handle OPTIONS preflight for /predict
@app.options("/predict")
def options_predict():
    return Response(status_code=200)

# Load the model
with open(MODEL_PATH, "rb") as f:
    model = pickle.load(f)

# Input schema
class InputData(BaseModel):
    credit_lines_outstanding: float
    loan_amt_outstanding: float
    total_debt_outstanding: float
    income: float
    years_employed: float
    fico_score: float

# Prediction endpoint
@app.post("/predict")
def predict_default(data: InputData):
    input_array = np.array([[ 
        data.credit_lines_outstanding,
        data.loan_amt_outstanding,
        data.total_debt_outstanding,
        data.income,
        data.years_employed,
        data.fico_score
    ]])
    prediction = model.predict_proba(input_array)[0][1]
    label = "Yes" if prediction > 0.75 else "No"
    return {"will_default": label}
