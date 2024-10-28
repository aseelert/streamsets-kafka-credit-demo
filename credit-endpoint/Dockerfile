# Use a base Python image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy only the specified files and folders
COPY templates /app/templates
COPY static /app/static
COPY demo_client.py /app/demo_client.py
COPY credit_score_api.py /app/credit_score_api.py

# Expose port 8000
EXPOSE 8000

# Run the FastAPI application with uvicorn
CMD ["uvicorn", "credit_score_api:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

