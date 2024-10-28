# credit_score_api.py
import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from datetime import datetime
import random
from typing import Optional
import logging

# Function to check if the app is running inside Docker
def is_running_in_docker():
    """Check if the app is running inside Docker by checking for specific Docker indicators."""
    return os.path.exists('/.dockerenv') or os.getenv("DOCKER") == "true"

# Example usage of the function to set paths
if is_running_in_docker():
    static_dir = "/app/static"
    template_dir = "/app/templates"
else:
    static_dir = "./static"
    template_dir = "./templates"

print(f"Running in Docker: {is_running_in_docker()}")
print(f"Static directory: {static_dir}")
print(f"Template directory: {template_dir}")

# Initialize FastAPI and templates
app = FastAPI()

# Set up Jinja2 templates and static files
templates = Jinja2Templates(directory=template_dir)
app.mount("/static", StaticFiles(directory=static_dir), name="static")


# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("credit_score_api")

# Model for Transaction data
class Transaction(BaseModel):
    account_type: str
    amount: float
    state: Optional[str] = None
    type: str

# In-memory storage for recent transactions
transactions = []

def calculate_risk_score(account_type: str, amount: float, state: Optional[str], tx_type: str) -> int:
    risk_score = random.randint(1, 50)
    if account_type == "LOAN":
        risk_score += 20
    elif account_type == "CHECKING":
        risk_score += 10
    elif account_type == "SAVINGS":
        risk_score += 5
    if tx_type == "DEBIT" and amount > 1000:
        risk_score += 15
    elif tx_type == "CREDIT" and amount < 100:
        risk_score -= 10
    high_risk_states = ["CA", "NY", "TX", "FL", "NV", "MD", "MO", "AK", "NC", "IL", "WA", "MA", "AZ", "MI", "NJ"]
    if state in high_risk_states:
        risk_score += 10
    return min(max(risk_score, 1), 100)

@app.post("/calculate-risk-score")
async def calculate_risk_score_endpoint(transaction: Transaction):
    try:
        risk_score = calculate_risk_score(
            transaction.account_type,
            transaction.amount,
            transaction.state,
            transaction.type
        )
        transaction_data = transaction.dict()
        transaction_data["risk_score"] = risk_score
        transaction_data["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        transactions.append(transaction_data)
        if len(transactions) > 1000:
            transactions.pop(0)
        logger.info(f"Processed transaction: {transaction_data}")
        return {"risk_score_value": risk_score, "risk_score_algo_version": "a25-27"}
    except Exception as e:
        logger.error(f"Error processing transaction: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/dashboard-data")
async def get_dashboard_data():
    """Provide data for the dashboard."""
    logger.info("Received request for dashboard data.")
    risk_below_50 = sum(1 for t in transactions if t["risk_score"] < 50)
    risk_above_50 = len(transactions) - risk_below_50

    logger.debug(f"Calculated risk_below_50: {risk_below_50}, risk_above_50: {risk_above_50}.")
    logger.debug(f"Last records in transactions: {transactions}")

    response = {
        "risk_below_50": risk_below_50,
        "risk_above_50": risk_above_50,
        "last_records": transactions
    }

    logger.info("Sending dashboard data response.")
    return response

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

