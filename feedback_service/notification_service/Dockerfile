FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the application code
COPY ./notification_service/notification.py /app/notification.py

# Copy the shared configuration and requirements files from the root directory
COPY ../requirements.txt /app/requirements.txt
COPY ../config.py /app/config.py

# Install dependencies
RUN pip install --no-cache-dir -r /app/requirements.txt

# Set environment variables
ENV SMTP_SERVER=${SMTP_SERVER}
ENV SMTP_PORT=${SMTP_PORT}
ENV SMTP_USERNAME=${SMTP_USERNAME}
ENV SMTP_PASSWORD=${SMTP_PASSWORD}
ENV SENDER_EMAIL=${SENDER_EMAIL}
ENV RECIPIENT_EMAIL=${RECIPIENT_EMAIL}

# Expose the necessary port
EXPOSE 5006

# Command to run the script
CMD ["python", "notification.py"]
