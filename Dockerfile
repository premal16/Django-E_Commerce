# FROM python:3.8-alpine

# RUN apk add --no-cache build-base gcc python3-dev

# WORKDIR /app

# COPY requirements.txt .
# RUN pip install -r requirements.txt

# COPY backend /app/backend
# COPY docker /app/docker

# RUN chmod +x ./docker/entrypoint.sh

# CMD ["/app/docker/entrypoint.sh"]


# FROM python:3.8-alpine

# COPY requirements.txt .
# RUN pip install -r requirements.txt

# COPY . /app

# COPY docker /docker

# RUN chmod +x ./docker/entrypoint.sh

# RUN cp -r /docker /app

# CMD ["/app/entrypoint.sh"]

# FROM python:3.8-alpine

# RUN apt-get update && apt-get install -y libsqlite3-dev


# WORKDIR /app

# COPY requirements.txt .
# RUN pip install -r requirements.txt

# COPY . /app

# # COPY docker /app/docker

# RUN chmod +x ./docker/entrypoint.sh

# CMD ["/app/docker/entrypoint.sh"]

# FROM python:3.8-alpine

# COPY requirements.txt .
# RUN pip install -r requirements.txt

# COPY . /app

# WORKDIR /app

# CMD ["python", "app.py"]
# Use an appropriate base image for your application
# FROM python:3.8-alpine

# # Install system dependencies and build tools
# RUN apk add --no-cache gcc musl-dev libffi-dev openssl-dev

# COPY requirements.txt .
# RUN pip install -r requirements.txt

# COPY . /app

# WORKDIR /app

# CMD ["python", "app.py"]

# Use an official Python runtime as a parent image
# Use the official Python image as the base image
# Use an official Python runtime as a parent image
FROM python:3.9

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install system dependencies (including GCC)
RUN apt-get update && apt-get install -y gcc

# Install Python dependencies from the requirements file
RUN pip install --no-cache-dir -r requirements.txt

# Collect Django's static files (if needed)
# RUN python manage.py collectstatic

# Make port 80 available to the world outside this container
EXPOSE 8000

# # Define environment variable
# ENV NAME World

# Run app.py when the container launches
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

