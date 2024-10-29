-- init.sql
CREATE TABLE IF NOT EXISTS financial_transactions (
    firstname VARCHAR(50),
    lastname VARCHAR(50),
    name VARCHAR(100),
    birthdate DATE,
    email VARCHAR(100),
    city VARCHAR(100),
    state CHAR(2),  -- US state abbreviation
    address TEXT,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    country VARCHAR(50),
    customer_number INT,
    transaction_id BIGINT,
    account_number VARCHAR(20),
    account_type VARCHAR(20),
    amount DECIMAL(10, 2),
    timestamp TIMESTAMP,
    type VARCHAR(10),
    risk_score INT
);
