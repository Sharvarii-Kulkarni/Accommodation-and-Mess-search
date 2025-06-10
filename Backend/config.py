import os

DATABASE_URL = "postgresql://postgres:sharvari3083@localhost/accommodation_db"

class Config:
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False

