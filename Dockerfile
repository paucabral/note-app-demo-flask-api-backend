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
ENV FLASK_ENV=$FLASK_ENV
ARG DEBUG
ENV DEBUG=$DEBUG
ARG PORT
ENV PORT=$PORT

# Copy the rest of your application code into the container at /app
COPY . .

# Expose the port that the app runs on
EXPOSE ${PORT}

# Command to run the application
CMD ["gunicorn", "app:app", "0.0.0.0:${PORT}"]