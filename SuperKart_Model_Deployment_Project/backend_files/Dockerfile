# Use a minimal base image with Python 3.9 installed
FROM python:3.9-slim

# Set the working directory inside the container to /app
WORKDIR /app

# Copy all files from the current directory on the host to the container's /app directory
COPY . .

# Install Python dependencies listed in requirements.txt
RUN pip3 install -r requirements.txt

# Expose the port the Flask app listens on
EXPOSE 5000

# Define the command to run the Flask app, bound to all interfaces so it can be
# reached through a forwarded Codespaces port
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
