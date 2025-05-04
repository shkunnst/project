import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Get bootstrap servers from environment variable or use default
boostrap_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')