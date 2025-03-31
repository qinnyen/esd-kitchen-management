# Use a lightweight Python image
FROM python:3.10-slim

# Set working directory in the container
WORKDIR /app

# Install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the app source code
COPY ./submit_feedback.py .

# Expose the port used by the Flask app
EXPOSE 5005

# Start the Submit Feedback Service
CMD ["python", "submit_feedback.py"]
