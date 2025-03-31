# Use official slim Python base image
FROM python:3.10-slim

# Set the working directory inside the container
# all commands will run the /app directory
WORKDIR /app

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app source files into the container
COPY feedback.py .
COPY ../config.py .

# Expose the Flask port (5003 as used in feedback.py)
EXPOSE 5003

# Run the Feedback Service
CMD ["python", "feedback.py"]
