FROM python:3.9-slim
LABEL authors="user"

WORKDIR /app

# Copy the entire back directory to /app/back
COPY . /app/back/

# Install dependencies from the requirements file
RUN pip install --no-cache-dir -r /app/back/requirements.txt

# Add the parent directory to PYTHONPATH so 'back' is recognized as a module
ENV PYTHONPATH=/app:$PYTHONPATH

# Make the startup script executable
RUN chmod +x /app/back/start.sh

# Change working directory to where your entry point is
WORKDIR /app/back
