# Creating a Table in Presto with MinIO Integration

This guide explains how to create a schema and a table in Presto to interact with data stored in a MinIO bucket. The example assumes a bucket named `fraud` is already configured in MinIO, and data resides in the subfolder `streamsetsfraud`.

## Prerequisites

1. **MinIO Setup:**
   - MinIO is installed and running.
   - A bucket named `fraud` is created in MinIO.
   - The subfolder `streamsetsschema/streamsetsfraud` exists in the `fraud` bucket.

    <img width="2048" alt="image" src="https://github.com/user-attachments/assets/5e928372-28e5-424d-ae79-39bb45ce6936">

3. **StreamSets**
   https://cloud.login.streamsets.com/login
   - validate that minio is configured correctly with `fraud`bucket name
   - validate that Common Prefix is set to `streamsetsschema/streamsetsfraud` so we have a schema folder before a data folder

    <img width="1041" alt="image" src="https://github.com/user-attachments/assets/65e9a334-525f-4bec-9723-208a5697e7ab">

   

2. **Data Format:**
   - The data in the `streamsetsfraud` folder is stored in Parquet format.

## Steps to Create the Schema and Table

#### 1. Create the Schema
Run the following SQL command in Presto to create a schema that maps to the `streamsetsschema` subfolder in the `fraud` bucket:

```sql
CREATE SCHEMA miniofraud.streamsetsschema 
WITH (
    location = 's3a://fraud/streamsetsschema'
);
```

#### 2. Create the Table 
Run the following SQL command in Presto to connect a table to already existing parquet data in `streamsetsschema/streamsetsfraud` subfolder in the `fraud` bucket:
```sql
CREATE TABLE "miniofraud"."streamsetsschema"."fraud_data" (
    firstname VARCHAR,
    lastname VARCHAR,
    name VARCHAR,
    birthdate VARCHAR,
    email VARCHAR,
    city VARCHAR,
    state VARCHAR,
    address VARCHAR,
    latitude DOUBLE,
    longitude DOUBLE,
    country VARCHAR,
    customer_number INT,
    transaction_id BIGINT,
    account_number VARCHAR,
    account_type VARCHAR,
    amount DOUBLE,
    timestamp VARCHAR,
    type VARCHAR,
    risk_score INT
)
WITH (
    format = 'Parquet',
    external_location = 's3a://fraud/streamsetsschema/streamsetsfraud'
);
```
```sql
SELECT * FROM "miniofraud"."streamsetsschema"."fraud_data" LIMIT 10;
```
