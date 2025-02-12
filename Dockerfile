# Use a Python base image (slim version for smaller size)
FROM python:3.9-slim-buster

# Set the working directory inside the container
WORKDIR /app

# Copy requirements file first to leverage Docker's caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code
COPY ./src /app/

# Specify the command to run when the container starts
ENTRYPOINT ["python", "grocery_ocr.py"]