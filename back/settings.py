# Configure logging
import logging

from passlib.context import CryptContext

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SECRET_KEY = "mysecret"  # Should be moved to environment variables in production
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")