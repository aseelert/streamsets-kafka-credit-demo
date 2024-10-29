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
    """
    Calculate a risk score between 1 and 100 based on transaction data.
    This score reflects the risk associated with different account types, transaction types, amounts, and states.

    Parameters:
    - account_type (str): Type of the account ('LOAN', 'CHECKING', 'SAVINGS').
    - amount (float): Amount of the transaction.
    - state (Optional[str]): State associated with the transaction.
    - tx_type (str): Type of the transaction ('DEBIT', 'CREDIT').

    Returns:
    - int: Risk score, with 1 being the lowest risk and 100 being the highest.
    """

    # Start with a base risk score
    risk_score = random.randint(1, 50)

    # Adjust risk based on account type
    if account_type == "LOAN":
        risk_score += 25  # LOAN accounts imply debt and add significant risk
    elif account_type == "CHECKING":
        risk_score += 10  # CHECKING accounts add moderate risk
    elif account_type == "SAVINGS":
        risk_score += 5   # SAVINGS accounts are low risk

    # Adjust risk based on transaction type and amount
    if tx_type == "DEBIT":
        if amount > 1000:
            risk_score += 20  # Large debits imply significant spending, adding risk
        else:
            risk_score += 5   # Smaller debits add slight risk
    elif tx_type == "CREDIT":
        if amount < 100:
            risk_score -= 10  # Small credits reduce risk slightly
        else:
            risk_score += 5   # Other credits add moderate risk

    # Adjust risk based on state, grouped by risk levels

    # High-risk states: Economic volatility or high industry risks
    high_risk_states = {
        "CA": "California - Significant risk due to reliance on technology and entertainment industries.",
        "NY": "New York - High risk due to economic volatility and high unemployment rates in certain areas.",
        "TX": "Texas - High exposure to oil and gas industry, leading to economic instability.",
        "FL": "Florida - Tourism dependence and housing market volatility increase risk.",
        "NV": "Nevada - Heavy reliance on tourism and gambling industries, leading to economic fluctuations.",
        "IL": "Illinois - Financial difficulties and high debt levels add significant risk."
    }

    # Medium-risk states: Moderate risk due to industry-specific dependencies
    medium_risk_states = {
        "OH": "Ohio - Risk due to reliance on manufacturing, especially automotive.",
        "MI": "Michigan - Moderate risk from auto industry dependency and past economic downturns.",
        "PA": "Pennsylvania - Manufacturing and coal industry exposure add moderate risk.",
        "GA": "Georgia - Risk due to mixed economic stability, with reliance on both agriculture and tech.",
        "AZ": "Arizona - Real estate-driven growth and drought concerns add moderate risk."
    }

    # Low-risk states: Generally stable economies with lower susceptibility to economic fluctuations
    low_risk_states = {
        "VT": "Vermont - Low risk with a small, stable economy focused on agriculture and tourism.",
        "ND": "North Dakota - Stability due to agricultural economy with limited economic volatility.",
        "SD": "South Dakota - Minimal economic risk with low reliance on volatile industries.",
        "ID": "Idaho - Stable, largely agricultural and tech-growing economy.",
        "NE": "Nebraska - Agriculture-focused and low unemployment, leading to lower economic risk."
    }

    # Check if the state is in one of the high, medium, or low-risk groups and adjust accordingly
    if state in high_risk_states:
        risk_score += 10  # High-risk states add significant risk
        logger.info(f"High-risk state: {state} - {high_risk_states[state]}")
    elif state in medium_risk_states:
        risk_score += 5  # Medium-risk states add moderate risk
        logger.info(f"Medium-risk state: {state} - {medium_risk_states[state]}")
    elif state in low_risk_states:
        risk_score -= 5  # Low-risk states reduce risk slightly
        logger.info(f"Low-risk state: {state} - {low_risk_states[state]}")
    else:
        logger.info(f"Other state: {state} - No additional risk adjustment applied.")

    # Ensure the score is clamped between 1 and 100 to avoid out-of-bounds values
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

