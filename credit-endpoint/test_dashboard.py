from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import random
from datetime import datetime, timedelta

app = FastAPI()

# Set up static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Generate sample transaction data
def generate_sample_transactions(count=5):
    account_types = ["LOAN", "CHECKING", "SAVINGS"]
    states = ["CA", "NY", "TX", "FL", "NV", "IL", "OH", "MI", "PA", "GA", "AZ", "VT", "ND", "SD", "ID", "NE"]
    transaction_types = ["DEBIT", "CREDIT"]
    genders = ["M", "F"]

    transactions = []
    for _ in range(count):
        transaction = {
            "account_type": random.choice(account_types),
            "amount": round(random.uniform(100, 10000), 2),
            "state": random.choice(states),
            "type": random.choice(transaction_types),
            "bias": random.choice(["YES", ""]),
            "age": random.randint(25, 65),
            "gender": random.choice(genders),
            "risk_score": random.randint(1, 100),
            "timestamp": (datetime.now() - timedelta(minutes=random.randint(0, 60))).strftime("%Y-%m-%d %H:%M:%S")
        }
        transactions.append(transaction)
    return transactions

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/api/dashboard-data")
async def get_dashboard_data():
    """Simulate dashboard data endpoint"""
    transactions = generate_sample_transactions(10)
    risk_below_50 = sum(1 for t in transactions if t["risk_score"] < 50)
    risk_above_50 = len(transactions) - risk_below_50

    return {
        "risk_below_50": risk_below_50,
        "risk_above_50": risk_above_50,
        "last_records": transactions
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)