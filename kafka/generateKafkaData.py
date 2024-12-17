import os
from kafka import KafkaProducer, KafkaAdminClient, KafkaConsumer
from kafka.admin import NewTopic
import json
import time
from faker import Faker
import random
from datetime import datetime
import argparse
from tqdm import tqdm  # for progress bar
from dotenv import load_dotenv
from geonamescache import GeonamesCache
import pandas as pd  # Add this to imports at the top

# Load environment variables from .env file
load_dotenv()

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

# Population-weighted state selection (all 50 states, population in millions)
states_population = [
    ("CA", 39.24), ("TX", 30.17), ("FL", 22.24), ("NY", 19.85), ("PA", 13.02),
    ("IL", 12.58), ("OH", 11.78), ("GA", 11.00), ("NC", 10.67), ("MI", 10.05),
    ("NJ", 9.26), ("VA", 8.68), ("WA", 7.88), ("AZ", 7.28), ("MA", 7.07),
    ("TN", 7.05), ("IN", 6.83), ("MO", 6.17), ("MD", 6.17), ("WI", 5.93),
    ("CO", 5.81), ("MN", 5.64), ("SC", 5.19), ("AL", 5.04), ("LA", 4.62),
    ("KY", 4.52), ("OR", 4.24), ("OK", 4.00), ("CT", 3.61), ("UT", 3.34),
    ("IA", 3.21), ("NV", 3.11), ("AR", 3.04), ("MS", 2.94), ("KS", 2.94),
    ("NM", 2.12), ("NE", 1.97), ("WV", 1.79), ("ID", 1.90), ("HI", 1.46),
    ("NH", 1.39), ("ME", 1.36), ("MT", 1.12), ("RI", 1.09), ("DE", 1.02),
    ("SD", 0.91), ("ND", 0.77), ("AK", 0.74), ("VT", 0.64), ("WY", 0.58)
]

# Unpack states and weights for random selection
states, weights = zip(*states_population)

# Initialize GeonamesCache once
gc = GeonamesCache()
us_cities = gc.get_cities()

def generate_us_coordinates():
    """
    Generate random coordinates within the continental US bounds.
    Returns a tuple of (latitude, longitude)
    """
    # Continental US bounds (approximately)
    min_lat, max_lat = 24.396308, 49.384358  # Southernmost to Northernmost points
    min_lon, max_lon = -125.000000, -66.934570  # Westernmost to Easternmost points

    return (
        random.uniform(min_lat, max_lat),
        random.uniform(min_lon, max_lon)
    )

def get_city_for_state(state_code):
    """
    Get a random real city and its coordinates for a given state.
    """
    # Filter cities for the given state
    state_cities = [
        city for city in us_cities.values()
        if city['countrycode'] == 'US' and
        city['admin1code'] == state_code
    ]

    if not state_cities:
        # Fallback if no cities found
        return fake.city(), generate_us_coordinates()

    # Select a random city from the filtered list
    city_data = random.choice(state_cities)
    return (
        city_data['name'],
        float(city_data['latitude']),
        float(city_data['longitude'])
    )

def generate_us_transaction():
    """
    Generate a sample financial transaction with realistic age distribution.
    """
    # Age distribution weights based on US demographic data
    age_ranges = [
        (18, 24, 0.12),  # 12% young adults
        (25, 34, 0.23),  # 23% millennials
        (35, 44, 0.22),  # 22% younger Gen X
        (45, 54, 0.20),  # 20% older Gen X
        (55, 64, 0.15),  # 15% younger boomers
        (65, 85, 0.08),  # 8% older population
    ]

    # Select age range based on weights
    min_age, max_age, _ = random.choices(age_ranges, weights=[r[2] for r in age_ranges], k=1)[0]
    birthdate = fake.date_of_birth(minimum_age=min_age, maximum_age=max_age)
    age = (datetime.now().year - birthdate.year)

    # Generate gender first
    gender = random.choice(['M', 'F'])

    # Generate gender-specific names
    if gender == 'M':
        firstname = fake.first_name_male()
        lastname = fake.last_name()
    else:
        firstname = fake.first_name_female()
        lastname = fake.last_name()

    country = "United States"

    # Add bias logic for females between 42 and 47
    bias = "YES" if gender == 'F' and 42 <= age <= 47 else ""

    # Generate email using firstname and lastname
    email = f"{firstname.lower()}.{lastname.lower()}@{random.choice(email_providers)}"

    # Adjust account types and amounts based on more realistic age groups
    if age < 25:
        account_type = random.choices(["CHECKING", "SAVINGS"], weights=[0.8, 0.2], k=1)[0]
        amount = random.uniform(20, 800) if account_type == "SAVINGS" else random.uniform(50, 1500)
    elif 25 <= age < 35:
        account_type = random.choices(["CHECKING", "SAVINGS", "LOAN"], weights=[0.5, 0.3, 0.2], k=1)[0]
        amount = random.uniform(1000, 15000) if account_type == "LOAN" else \
                random.uniform(100, 4000) if account_type == "CHECKING" else \
                random.uniform(500, 5000)
    elif 35 <= age < 50:
        account_type = random.choices(["CHECKING", "SAVINGS", "LOAN"], weights=[0.4, 0.3, 0.3], k=1)[0]
        amount = random.uniform(5000, 30000) if account_type == "LOAN" else \
                random.uniform(500, 8000) if account_type == "CHECKING" else \
                random.uniform(1000, 15000)
    else:
        account_type = random.choices(["CHECKING", "SAVINGS", "LOAN"], weights=[0.35, 0.45, 0.2], k=1)[0]
        amount = random.uniform(10000, 50000) if account_type == "LOAN" else \
                random.uniform(1000, 10000) if account_type == "CHECKING" else \
                random.uniform(5000, 50000)

    # DEBIT/CREDIT probability with higher DEBIT likelihood
    tx_type = random.choices(["DEBIT", "CREDIT"], weights=[0.7, 0.3], k=1)[0]
    amount = round(amount, 2)

    # Select a state with population-weighted probability
    state = random.choices(states, weights=weights, k=1)[0]

    # Get a real city and its coordinates for the selected state
    city, latitude, longitude = get_city_for_state(state)



    # Construct transaction data
    transaction = {
        "firstname": firstname,
        "lastname": lastname,
        "gender": gender,
        "bias": bias,
        "name": f"{firstname} {lastname}",
        "birthdate": birthdate.strftime("%Y-%m-%d"),
        "age": age,
        "email": email,
        "city": city,
        "state": state,
        "address": fake.street_address(),
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

def send_data_to_kafka(records=10000, batch=1000, interval=10, topic_name="txs", retries=5):
    for attempt in range(retries):
        try:
            producer = KafkaProducer(
                bootstrap_servers=bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
            print("Successfully connected to Kafka broker.")
            create_kafka_topic(topic_name)

            with tqdm(total=records, desc="Sending transactions to Kafka") as pbar:
                records_sent = 0

                while records_sent < records:
                    batch_size = min(batch, records - records_sent)
                    transactions = [generate_us_transaction() for _ in range(batch_size)]
                    print(f"Generated batch of {batch_size} transactions.")

                    for transaction in transactions:
                        producer.send(topic_name, transaction)

                    producer.flush()
                    records_sent += batch_size
                    pbar.update(batch_size)

                    time.sleep(interval)

                print(f"Total of {records} transactions sent to Kafka topic '{topic_name}'.")
                break

        except Exception as e:
            print(f"Attempt {attempt + 1}: Unable to connect to Kafka or send message: {e}")
            if attempt < retries - 1:
                time.sleep(5)
            else:
                print("Max retries reached. Exiting.")
                break

def show_last_n_records(topic_name):
    """
    Show the last 10 records from a Kafka topic using pandas DataFrame
    """
    # Configuration variables for Kafka connection
    bootstrap_server = os.getenv("HOST_IP")
    bootstrap_server_port = 9192
    bootstrap_servers = f"{bootstrap_server}:{bootstrap_server_port}"

    print(f"Connecting to Kafka at {bootstrap_servers}")

    # Create consumer that starts reading from the end
    consumer = KafkaConsumer(
        bootstrap_servers=bootstrap_servers,
        value_deserializer=lambda x: json.loads(x.decode('utf-8')),
        auto_offset_reset='latest',  # Start reading from the end
        enable_auto_commit=False,    # Don't commit offsets
        consumer_timeout_ms=5000     # Timeout after 5 seconds of no messages
    )

    # Subscribe to the topic
    consumer.subscribe([topic_name])

    # Wait for partition assignment
    while not consumer.assignment():
        consumer.poll(timeout_ms=1000)

    # Get the end offsets for each partition
    partitions = consumer.partitions_for_topic(topic_name)
    if not partitions:
        print(f"Topic '{topic_name}' not found")
        return

    # Create a list to store the last n records
    last_records = []

    try:
        # Seek to end and then back by n messages for each partition
        for partition in consumer.assignment():
            # Get the end offset
            end_offset = consumer.end_offsets([partition])[partition]
            # Calculate start offset (end - n)
            start_offset = max(0, end_offset - 10)
            # Seek to start offset
            consumer.seek(partition, start_offset)

        # Read messages
        while len(last_records) < 10:
            messages = consumer.poll(timeout_ms=1000)
            if not messages:
                break
            for partition_messages in messages.values():
                for message in partition_messages:
                    last_records.append(message.value)
                    if len(last_records) >= 10:
                        break
                if len(last_records) >= 10:
                    break

    finally:
        consumer.close()

    # Convert records to pandas DataFrame
    if last_records:
        df = pd.DataFrame(last_records)

        # Format the DataFrame
        pd.set_option('display.max_columns', None)  # Show all columns
        pd.set_option('display.width', None)        # Don't wrap to multiple lines
        pd.set_option('display.max_colwidth', None) # Show full content of each cell
        pd.set_option('display.max_rows', None)     # Show all rows

        print(f"\nLast {len(last_records)} records from topic '{topic_name}':")
        print(df.to_string(index=False))
    else:
        print(f"\nNo records found in topic '{topic_name}'")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Send generated transaction data to Kafka.")
    parser.add_argument("-r", "--records", type=int, default=10000, help="Total number of records to send.")
    parser.add_argument("-b", "--batch", type=int, default=1000, help="Batch size for each Kafka send.")
    parser.add_argument("-i", "--interval", type=int, default=10, help="Interval (seconds) between batches.")
    parser.add_argument("--topic_name", type=str, default="txs", help="Kafka topic name to send data to.")
    args = parser.parse_args()

    send_data_to_kafka(records=args.records, batch=args.batch, interval=args.interval, topic_name=args.topic_name)

    # Show last records from the same topic
    show_last_n_records(topic_name=args.topic_name)
