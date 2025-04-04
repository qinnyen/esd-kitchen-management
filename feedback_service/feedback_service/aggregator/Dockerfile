FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the application code
COPY ./aggregator/aggregator.py /app/aggregator.py
COPY ../feedback_service/feedback.py /app/feedback.py

# Copy the shared configuration and requirements files from the root directory
COPY ../requirements.txt /app/requirements.txt
COPY ../config.py /app/config.py


# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Command to run the script
CMD ["python", "aggregator.py"]
