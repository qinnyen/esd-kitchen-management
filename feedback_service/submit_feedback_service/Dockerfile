FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the application code
COPY ./submit_feedback_service/submit_feedback.py /app/submit_feedback.py

# Copy the shared configuration and requirements files from the root directory
COPY ../requirements.txt /app/requirements.txt
COPY ../config.py /app/config.py

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the Flask port (if necessary)
EXPOSE 5005

# Command to run the service
CMD ["python", "submit_feedback.py"]
