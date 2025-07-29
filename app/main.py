from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import numpy as np
import pickle
import os

app = FastAPI()

# Serve static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Serve the HTML form
@app.get("/form", response_class=HTMLResponse)
def get_form():
    with open("app/static/index.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content, status_code=200, media_type="text/html")

# Load model
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
    return {
        "Will it default?": label
    }

@app.get("/")
def health_check():
    return {"status": "healthy", "model": "credit_default_xgboost_v1"}
