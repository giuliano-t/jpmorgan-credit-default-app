from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import numpy as np
import pickle
import os

app = FastAPI()

# Mount static files (CSS/JS)
app.mount("/static", StaticFiles(directory="../static"), name="static")


# Serve the form at "/"
@app.get("/", response_class=FileResponse)
def serve_index():
    return FileResponse("static/index.html")

# Health check
@app.get("/health")
def health():
    return {"status": "healthy", "model": "credit_default_xgboost_v1"}

# Load the model
model_path = os.path.join("models", "xgboost_model.pkl")
with open(model_path, "rb") as f:
    model = pickle.load(f)

# Input schema
class InputData(BaseModel):
    credit_lines_outstanding: float
    loan_amt_outstanding: float
    total_debt_outstanding: float
    income: float
    years_employed: float
    fico_score: float

# Predict endpoint
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
