# demo_client.py
import requests
import random
from faker import Faker

fake = Faker()

# URL of the FastAPI service
url = "http://127.0.0.1:8000/calculate-risk-score"

def generate_random_transaction():
    account_type = random.choice(["LOAN", "CHECKING", "SAVINGS"])
    amount = round(random.uniform(10.0, 2000.0), 2)
    state = random.choice(["CA", "NY", "TX", None])  # Include some higher-risk states
    tx_type = random.choice(["DEBIT", "CREDIT"])

    transaction = {
        "account_type": account_type,
        "amount": amount,
        "state": state,
        "type": tx_type,
        "bias": bias,
        "age": age,
        "gender": gender
    }
    return transaction

def get_risk_score(transaction):
    response = requests.post(url, json=transaction)
    if response.status_code == 200:
        print(f"Transaction: {transaction}")
        print(f"Risk Score: {response.json()['risk_score']}\n")
    else:
        print(f"Error: {response.status_code} - {response.text}")

if __name__ == "__main__":
    for _ in range(5):  # Generate and send 5 random transactions
        transaction = generate_random_transaction()
        get_risk_score(transaction)

