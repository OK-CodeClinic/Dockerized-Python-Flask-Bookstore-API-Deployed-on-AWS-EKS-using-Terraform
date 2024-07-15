# Use an official Python runtime as a parent image
FROM python:3.9-alpine

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN apk update \
    && apk add --no-cache mariadb-connector-c-dev build-base \
    && pip install --no-cache-dir -r requirements.txt \
    && pip install flask-mysqldb

# Make port 80 available to the world outside this container
EXPOSE 80

# Run book-api.py when the container launches
CMD ["python", "./book-api.py"]
