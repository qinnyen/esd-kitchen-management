# Base Python image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy and install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install RabbitMQ client library
RUN pip install pika

# Copy the aggregator script and config
COPY weekly_feedback_aggregator.py .
COPY ../config.py .
COPY feedback.py .

# Expose nothing (not a web service)

# Run the script (useful for testing or manual run)
CMD ["python", "weekly_feedback_aggregator.py"]
