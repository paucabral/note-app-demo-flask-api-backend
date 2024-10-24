# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt ./

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variables.
ARG FLASK_ENV
ENV FLASK_ENV $FLASK_ENV
ARG DEBUG
ENV DEBUG $DEBUG
ARG PORT
ENV PORT $PORT

ARG DEV_SECRET_KEY
ENV DEV_SECRET_KEY $DEV_SECRET_KEY
ARG TEST_SECRET_KEY
ENV TEST_SECRET_KEY $TEST_SECRET_KEY
ARG STG_SECRET_KEY
ENV STG_SECRET_KEY $STG_SECRET_KEY
ARG PROD_SECRET_KEY
ENV PROD_SECRET_KEY $PROD_SECRET_KEY

ARG DEV_DB_URI
ENV DEV_DB_URI $DEV_DB_URI
ARG TEST_DB_URI
ENV TEST_DB_URI $TEST_DB_URI
ARG STG_DB_URI
ENV STG_DB_URI $STG_DB_URI
ARG STG_DB_URI
ENV PROD_DB_URI $STG_DB_URI

ARG TEST_USER
ENV TEST_USER $TEST_USER
ARG TEST_PASSWORD
ENV TEST_PASSWORD $TEST_PASSWORD

# Copy the rest of your application code into the container at /app
COPY . .

# Expose the port that the app runs on
EXPOSE 5000

# Command to run the application
CMD ["gunicorn", "app:app", "0.0.0.0:5000"]