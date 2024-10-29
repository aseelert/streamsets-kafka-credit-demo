from kafka import KafkaProducer, KafkaAdminClient
from kafka.admin import NewTopic
import json
import time
from faker import Faker
import random
from datetime import datetime

# Configuration variables for Kafka connection
bootstrap_server = "9.153.103.108"
bootstrap_server_port = 9192
bootstrap_servers = f"{bootstrap_server}:{bootstrap_server_port}"
topic_name = "txs"

# Initialize Faker with only the 'en_US' locale
fake = Faker('en_US')

def generate_us_transaction():
    """
    Generate a sample financial transaction with age-based account type and amount adjustments.

    The function simulates realistic financial behavior by varying transaction types and amounts
    based on the age of the individual:

    Age Group Influence:
    --------------------
    - Younger People (<25 years):
      - More likely to have smaller savings and checking accounts.
      - Transaction amounts are smaller, as younger people typically have lower balances and spend
        on day-to-day expenses.
      - Higher probability of DEBIT transactions.

    - Middle Age (25-40 years):
      - Likely to have a mix of checking, savings, and loan accounts.
      - Larger loan sizes for significant purchases (e.g., homes, vehicles).
      - More frequent CREDIT transactions for consumer goods, balanced with larger checking amounts.

    - Older Adults (40+ years):
      - More stable financial status, often with higher savings and possibly larger loan amounts
        (e.g., mortgages).
      - Moderate CREDIT activity for expenses but more likely larger savings deposits.

    This structure aims to provide a realistic financial dataset for testing and analysis.
    """

    firstname = fake.first_name()
    lastname = fake.last_name()
    country = "United States"

    # Generate email using firstname and lastname
    email_domain = random.choice(["gmail.com", "yahoo.com", "outlook.com", "mail.com"])
    email = f"{firstname.lower()}.{lastname.lower()}@{email_domain}"
    birthdate = fake.date_of_birth(minimum_age=18, maximum_age=85)
    age = (datetime.now().year - birthdate.year)

    # Determine likely account type and amount range based on age group
    if age < 25:
        # Younger individuals (<25): Focus on smaller transactions in checking and savings
        account_type = random.choices(["CHECKING", "SAVINGS"], weights=[0.7, 0.3], k=1)[0]
        amount = random.uniform(10, 500) if account_type == "SAVINGS" else random.uniform(10, 1000)
    elif 25 <= age < 40:
        # Middle-aged (25-40): Higher chance of loan activity, larger amounts
        account_type = random.choices(["CHECKING", "SAVINGS", "LOAN"], weights=[0.5, 0.2, 0.3], k=1)[0]
        amount = (random.uniform(100, 10000) if account_type == "LOAN" else
                  random.uniform(100, 3000) if account_type == "CHECKING" else
                  random.uniform(50, 1500))
    else:
        # Older adults (40+): Larger loans, stable savings, moderate credit
        account_type = random.choices(["CHECKING", "SAVINGS", "LOAN"], weights=[0.4, 0.3, 0.3], k=1)[0]
        amount = (random.uniform(5000, 20000) if account_type == "LOAN" else
                  random.uniform(200, 5000) if account_type == "CHECKING" else
                  random.uniform(100, 3000))

    # DEBIT/CREDIT probability with higher DEBIT likelihood across groups
    tx_type = random.choices(["DEBIT", "CREDIT"], weights=[0.7, 0.3], k=1)[0]
    amount = round(amount, 2)

    # Construct transaction data
    transaction = {
        "firstname": firstname,
        "lastname": lastname,
        "name": f"{firstname} {lastname}",
        "birthdate": birthdate.strftime("%Y-%m-%d"),
        "email": email,
        "city": fake.city(),
        "state": fake.state_abbr(),
        "address": fake.address(),
        "latitude": float(fake.latitude()),
        "longitude": float(fake.longitude()),
        "country": country,
        "customer_number": random.randint(100000, 999999),
        "transaction_id": random.randint(1000000000000000000, 9223372036854775807),
        "account_number": f"{random.randint(100000, 999999)}-{random.randint(1000000, 9999999)}",
        "account_type": account_type,
        "amount": amount,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "type": tx_type,
    }
    return transaction


# Function to create Kafka topic if it does not exist
def create_kafka_topic():
    try:
        admin_client = KafkaAdminClient(bootstrap_servers=bootstrap_servers)
        topics = admin_client.list_topics()
        if topic_name not in topics:
            new_topic = NewTopic(name=topic_name, num_partitions=1, replication_factor=1)
            admin_client.create_topics([new_topic])
            print(f"Topic '{topic_name}' created successfully.")
        else:
            print(f"Topic '{topic_name}' already exists.")
    except Exception as e:
        print(f"Error creating topic '{topic_name}': {e}")

# Function to send data to Kafka in random-sized batches
def send_data_to_kafka(retries=5):
    for attempt in range(retries):
        try:
            producer = KafkaProducer(
                bootstrap_servers=bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
            print("Successfully connected to Kafka broker.")
            create_kafka_topic()

            while True:
                # Generate a random number of transactions (between 500 and 1000)
                batch_size = random.randint(500, 1000)
                transactions = [generate_us_transaction() for _ in range(batch_size)]
                print(f"Generated batch of {batch_size} US-based transactions")

                # Send each transaction in the batch to Kafka
                for transaction in transactions:
                    producer.send(topic_name, transaction)

                # Flush the batch to ensure all records are sent
                producer.flush()
                print(f"Batch of {batch_size} transactions sent to Kafka topic '{topic_name}'.")

                # Wait 10 seconds before the next batch
                time.sleep(10)

            break  # Exit loop if connection is successful

        except Exception as e:
            print(f"Attempt {attempt + 1}: Unable to connect to Kafka or send message: {e}")
            if attempt < retries - 1:
                time.sleep(5)  # Wait before retrying
            else:
                print("Max retries reached. Exiting.")
                break

# Run the data generation and sending function
if __name__ == "__main__":
    send_data_to_kafka()

