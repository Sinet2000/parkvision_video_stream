# Use the official Python image from Docker Hub
FROM python:3.12-slim

# Set environment variables to prevent writing .pyc files to disk
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Install system dependencies, including libGL
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file into the container at /app
COPY requirements.txt /app/

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container at /app
COPY . /app/

# Expose the Flask app's port (default 5000)
EXPOSE 5001

# Set the command to run the app
CMD ["python", "app.py"]


# # Use official Python image
# FROM python:3.12

# # Set the working directory
# WORKDIR /app

# # Copy only requirements first (to leverage Docker caching)
# COPY requirements.txt .

# # Install dependencies
# RUN python -m venv venv && \
#     ./venv/bin/pip install --upgrade pip && \
#     ./venv/bin/pip install -r requirements.txt

# # Copy the application code
# COPY . .

# # Expose the port Flask runs on
# EXPOSE 5000

# # Command to run the application
# CMD ["./venv/bin/python", "app.py"]