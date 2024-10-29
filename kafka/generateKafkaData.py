from kafka import KafkaProducer, KafkaAdminClient
from kafka.admin import NewTopic
import json
import time
from faker import Faker
import random
from datetime import datetime
import argparse
from tqdm import tqdm  # for progress bar
from dotenv import load_dotenv

# Configuration variables for Kafka connection
bootstrap_server = os.getenv("HOST_IP")
bootstrap_server_port = 9192
bootstrap_servers = f"{bootstrap_server}:{bootstrap_server_port}"
print(f"Connecting to Kafka at {bootstrap_server}")
# Initialize Faker with only the 'en_US' locale
fake = Faker('en_US')

# Known email providers
email_providers = ["gmail.com", "yahoo.com", "outlook.com", "mail.com",
                   "aol.com", "icloud.com", "comcast.net", "msn.com",
                   "live.com", "protonmail.com"]

def generate_us_transaction():
    """
    Generate a sample financial transaction with age-based account type and amount adjustments.

    The function simulates realistic financial behavior by varying transaction types and amounts
    based on the age of the individual:

    Age Group Influence:
    --------------------
    - Younger People (<25 years): Focus on smaller checking and savings transactions.
    - Middle Age (25-40 years): Higher chance of loans and larger amounts.
    - Older Adults (40+ years): Larger loans, stable savings, moderate credit.

    This structure provides a realistic financial dataset for testing and analysis.
    """

    firstname = fake.first_name()
    lastname = fake.last_name()
    country = "United States"

    # Generate email using firstname and lastname
    email = f"{firstname.lower()}.{lastname.lower()}@{random.choice(email_providers)}"
    birthdate = fake.date_of_birth(minimum_age=18, maximum_age=85)
    age = (datetime.now().year - birthdate.year)

    # Determine account type and amount based on age group
    if age < 25:
        account_type = random.choices(["CHECKING", "SAVINGS"], weights=[0.7, 0.3], k=1)[0]
        amount = random.uniform(10, 500) if account_type == "SAVINGS" else random.uniform(10, 1000)
    elif 25 <= age < 40:
        account_type = random.choices(["CHECKING", "SAVINGS", "LOAN"], weights=[0.5, 0.2, 0.3], k=1)[0]
        amount = random.uniform(100, 10000) if account_type == "LOAN" else random.uniform(100, 3000) if account_type == "CHECKING" else random.uniform(50, 1500)
    else:
        account_type = random.choices(["CHECKING", "SAVINGS", "LOAN"], weights=[0.4, 0.3, 0.3], k=1)[0]
        amount = random.uniform(5000, 20000) if account_type == "LOAN" else random.uniform(200, 5000) if account_type == "CHECKING" else random.uniform(100, 3000)

    # DEBIT/CREDIT probability with higher DEBIT likelihood
    tx_type = random.choices(["DEBIT", "CREDIT"], weights=[0.7, 0.3], k=1)[0]
    amount = round(amount, 2)

    # Ensure realistic latitude and longitude within the U.S.
    latitude, longitude = generate_us_coordinates()

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
        "latitude": latitude,
        "longitude": longitude,
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

def generate_us_coordinates():
    """
    Generate realistic latitude and longitude within U.S. bounds.
    Returns approximate values for landmarks within the U.S.
    """
    latitude = round(random.uniform(24.396308, 49.384358), 6)   # U.S. latitude range
    longitude = round(random.uniform(-125.0, -66.93457), 6)     # U.S. longitude range
    return latitude, longitude

# Function to create Kafka topic if it does not exist
def create_kafka_topic(topic_name):
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

# Function to send data to Kafka in random-sized batches with progress tracking
def send_data_to_kafka(total_records=10000, topic_name="txs", retries=5):
    for attempt in range(retries):
        try:
            producer = KafkaProducer(
                bootstrap_servers=bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
            print("Successfully connected to Kafka broker.")
            create_kafka_topic(topic_name)

            # Initialize progress bar
            with tqdm(total=total_records, desc="Sending transactions to Kafka") as pbar:
                records_sent = 0

                while records_sent < total_records:
                    # Generate a random batch size, constrained by remaining records
                    batch_size = min(random.randint(500, 1000), total_records - records_sent)
                    transactions = [generate_us_transaction() for _ in range(batch_size)]
                    print(f"Generated batch of {batch_size} US-based transactions")

                    # Send each transaction in the batch to Kafka
                    for transaction in transactions:
                        producer.send(topic_name, transaction)

                    # Flush the batch to ensure all records are sent
                    producer.flush()
                    records_sent += batch_size
                    pbar.update(batch_size)

                    # Wait 10 seconds before the next batch
                    time.sleep(10)

                print(f"Total of {total_records} transactions sent to Kafka topic '{topic_name}'.")
                break  # Exit loop if connection is successful

        except Exception as e:
            print(f"Attempt {attempt + 1}: Unable to connect to Kafka or send message: {e}")
            if attempt < retries - 1:
                time.sleep(5)  # Wait before retrying
            else:
                print("Max retries reached. Exiting.")
                break

# Parse command-line arguments
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Send generated transaction data to Kafka.")
    parser.add_argument("--total_records", type=int, default=10000, help="Total number of records to send.")
    parser.add_argument("--topic_name", type=str, default="txs", help="Kafka topic name to send data to.")
    args = parser.parse_args()

    send_data_to_kafka(total_records=args.total_records, topic_name=args.topic_name)
