from kafka import KafkaConsumer
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def show_last_n_records(topic_name="txs", n=10):
    """
    Show the last n records from a Kafka topic
    """
    # Configuration variables for Kafka connection
    bootstrap_server = os.getenv("HOST_IP")
    bootstrap_server_port = 9192
    bootstrap_servers = f"{bootstrap_server}:{bootstrap_server_port}"

    print(f"Connecting to Kafka at {bootstrap_servers}")

    # Create consumer that starts reading from the end
    consumer = KafkaConsumer(
        topic_name,
        bootstrap_servers=bootstrap_servers,
        value_deserializer=lambda x: json.loads(x.decode('utf-8')),
        auto_offset_reset='latest',  # Start reading from the end
        enable_auto_commit=False,    # Don't commit offsets
        consumer_timeout_ms=5000     # Timeout after 5 seconds of no messages
    )

    # Get the end offsets for each partition
    partitions = consumer.partitions_for_topic(topic_name)
    if not partitions:
        print(f"Topic '{topic_name}' not found")
        return

    # Create a list to store the last n records
    last_records = []

    try:
        # Assign to all partitions
        consumer.assign([tp for tp in consumer.assignment()])

        # Seek to end and then back by n messages
        for partition in consumer.assignment():
            # Get the end offset
            end_offset = consumer.end_offsets([partition])[partition]
            # Calculate start offset (end - n)
            start_offset = max(0, end_offset - n)
            # Seek to start offset
            consumer.seek(partition, start_offset)

        # Read messages
        for message in consumer:
            last_records.append(message.value)
            if len(last_records) >= n:
                break

    finally:
        consumer.close()

    # Print the records
    print(f"\nLast {len(last_records)} records from topic '{topic_name}':")
    for i, record in enumerate(last_records, 1):
        print(f"\n{i}. Transaction:")
        print(f"   Name: {record['name']}")
        print(f"   Location: {record['city']}, {record['state']}")
        print(f"   Coordinates: ({record['latitude']}, {record['longitude']})")
        print(f"   Amount: ${record['amount']} ({record['type']})")
        print(f"   Account: {record['account_type']}")
        print(f"   Timestamp: {record['timestamp']}")

if __name__ == "__main__":
    show_last_n_records()