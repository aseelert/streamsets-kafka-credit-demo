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

# Function to generate sample transaction data specific to the United States
def generate_us_transaction():
    firstname = fake.first_name()
    lastname = fake.last_name()
    country = "United States"  # Fixed country to United States

    # Generate email using firstname and lastname
    email_domain = random.choice(["gmail.com", "yahoo.com", "outlook.com", "mail.com"])
    email = f"{firstname.lower()}.{lastname.lower()}@{email_domain}"

    transaction = {
        "firstname": firstname,
        "lastname": lastname,
        "name": f"{firstname} {lastname}",  # Construct name from firstname and lastname
        "birthdate": fake.date_of_birth().strftime("%m-%d-%Y"),
        "email": email,  # Email based on firstname and lastname
        "city": fake.city(),
        "state": fake.state_abbr(),  # US state abbreviation
        "address": fake.address(),
        "latitude": float(fake.latitude()),  # Latitude for US
        "longitude": float(fake.longitude()),  # Longitude for US
        "country": country,
        "customer_number": random.randint(100000, 999999),
        "transaction_id": random.randint(1000000000000000000, 9223372036854775807),
        "account_number": f"{random.randint(100000, 999999)}-{random.randint(1000000, 9999999)}",
        "account_type": random.choices(["CHECKING", "SAVINGS", "LOAN"], weights=[0.5, 0.2, 0.3], k=1)[0],
        "amount": float(round(random.uniform(10.0, 1000.0), 2)),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "type": random.choices(["DEBIT", "CREDIT"], weights=[0.65, 0.35], k=1)[0],
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

