# demo_client.py
import requests
import random
from faker import Faker
import time

fake = Faker()

# URL of the FastAPI service
url = "http://127.0.0.1:8000/calculate-risk-score"

# List of US states, DC, and territories
STATES = [
    'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
    'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
    'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
    'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
    'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY',
    'DC', 'PR', 'VI', 'GU', 'MP', 'AS'  # Added DC and territories
]

def generate_random_transaction():
    account_type = random.choice(["LOAN", "CHECKING", "SAVINGS"])
    amount = round(random.uniform(10.0, 2000.0), 2)
    state = random.choice(STATES + [None])  # Include None for some transactions without state
    tx_type = random.choice(["DEBIT", "CREDIT"])
    bias = random.choice(["YES", ""])
    age = random.randint(25, 65)
    gender = random.choice(["M", "F"])

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
    print("Starting transaction generation...")
    while True:
        try:
            # Generate and send 10 random transactions
            for _ in range(10):
                transaction = generate_random_transaction()
                get_risk_score(transaction)

            # Wait for 5 seconds before generating more transactions
            time.sleep(5)
        except KeyboardInterrupt:
            print("\nStopping transaction generation...")
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)  # Wait before retrying

