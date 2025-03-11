import os
from dotenv import load_dotenv

DATABASE_URL = "postgresql://postgres:sharvari3083@localhost/accommodation_db"

class Config:
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False



# Load environment variables from .env file
load_dotenv()

# Get the API key from environment variables
GEOAPIFY_API_KEY = os.getenv("GEOAPIFY_API_KEY")
