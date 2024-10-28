# Streamsets Credit Score Processing Pipeline

This project sets up a credit score processing pipeline using Docker Compose. It includes Kafka for data streaming, PostgreSQL for data storage, Streamsets for data processing, and a custom API with a dashboard to view transaction risk scores.

## Services

| Service           | Description                                                   | Username           | Password   | Port(s)                |
|-------------------|---------------------------------------------------------------|--------------------|------------|-------------------------|
| Kafka             | Data streaming service                                        | -                  | -          | 9192, 9193, 9194, 9195 |
| Kafka UI          | Web interface to monitor Kafka data                           | -                  | -          | 8194                    |
| PostgreSQL        | Database for storing transactions with risk > 50              | fraud_user         | fraud_pass | 5542                    |
| pgAdmin4          | UI to manage PostgreSQL databases                             | admin@admin.com    | IBM4ever   | 5150                    |
| MinIO             | Object storage for Streamsets and other services              | minio              | IBM4ever   | 9100, 9101             |
| Streamsets        | Main application for processing and routing data              | -                  | -          | 18630                   |
| Credit Score API  | API to calculate risk scores and serve a dashboard            | -                  | -          | 8000                    |

## Setup Instructions

1. Clone this repository and navigate to the `docker` directory.
2. Set environment variables for Streamsets in `.env`file
   ```python
   STREAMSETS_DEPLOYMENT_SCH_URL=https://na01.hub.streamsets.com
   STREAMSETS_DEPLOYMENT_ID=dba9cbf0-6d10-46d8-b4af-3de2f2a921a2:08e9a095
   STREAMSETS_DEPLOYMENT_TOKEN=your_token_here
   KAFKA_CFG_ADVERTISED_LISTENERS=EXTERNAL://`real host ip`:9192,INTERNAL://kafka:9194,LOCAL://localhost:9195
   export DEFAULT_PASSWORD=password00
   ```

3. Run the pipeline:
   \`docker-compose up -d\`

4. **Firewall Configuration**:
   Ensure all required ports are open on Fedora 41 using:
   ```bash
   sudo firewall-cmd --permanent --zone=public --add-port=8000/tcp
   sudo firewall-cmd --permanent --zone=public --add-port=8194/tcp
   sudo firewall-cmd --permanent --zone=public --add-port=18630/tcp
   sudo firewall-cmd --permanent --zone=public --add-port=5542/tcp
   sudo firewall-cmd --permanent --zone=public --add-port=5150/tcp
   sudo firewall-cmd --permanent --zone=public --add-port=9100/tcp
   sudo firewall-cmd --permanent --zone=public --add-port=9101/tcp
   sudo firewall-cmd --permanent --zone=public --add-port=9192/tcp
   sudo firewall-cmd --permanent --zone=public --add-port=9193/tcp
   sudo firewall-cmd --permanent --zone=public --add-port=9194/tcp
   sudo firewall-cmd --permanent --zone=public --add-port=9195/tcp
   sudo firewall-cmd --reload
   ```

## Explanation of Each Component

### Data Generation and Processing
- The `generateKafkaData.py` script in the `kafka` directory creates fake transaction data in JSON format and sends it to Kafka (topic: `txs`).
- Kafka streams this data to Streamsets for processing, where it calculates risk scores and routes transactions.

### Dashboard and API
- The `credit_score_api.py` provides an API endpoint to process transactions and calculate a risk score.
- A dashboard is accessible at `http://localhost:8000` for monitoring transaction risk levels.

### PostgreSQL Database
- Transactions with risk scores > 50 are stored in the PostgreSQL database (`fraud_detection`).
- Transactions with risk scores < 50 are discarded.

### Kafka UI and pgAdmin4
- **Kafka UI**: Available at `http://localhost:8194`, provides a live view of Kafka data.
- **pgAdmin4**: Available at `http://localhost:5150`, allows management of PostgreSQL databases.

## Pipeline Flow

1. **Kafka** receives streaming data from `generateKafkaData.py`.
2. **Streamsets** pulls from Kafka, processes data, calculates risk scores using `credit_score_api.py`, and saves high-risk transactions to PostgreSQL.
3. **Credit Score API Dashboard**: Displays transaction risk levels and data distribution in real time.

> **Note**: Run `python kafka/generateKafkaData.py` to generate sample transaction data for the pipeline.

## Pipeline Diagram (Text)

1. **Data Generation** (generateKafkaData.py) ➔ **Kafka** (txs topic)
2. **Streamsets Pipeline** ➔ reads from Kafka ➔ sends to **Credit Score API** for risk scoring ➔ routes data to PostgreSQL (for high-risk transactions)
