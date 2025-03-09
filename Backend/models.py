from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "users"  # ✅ Ensure it matches PostgreSQL table name
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)

class Accommodation(db.Model):
    __tablename__ = "accommodations"  # ✅ Matches PostgreSQL table name
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    location = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(50), nullable=False)
    rent_price = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text)
    image_url = db.Column(db.Text)

    # ✅ Fixed Column Names
    owner_name = db.Column(db.String(100), nullable=False)  # ✅ Corrected
    phone_number = db.Column(db.String(20), nullable=False)  # ✅ Corrected
    bedrooms = db.Column(db.Integer, nullable=False)
    bathrooms = db.Column(db.Integer, nullable=False)
    balconies = db.Column(db.Integer, nullable=True)
    carpet_area = db.Column(db.String(50), nullable=True)
    furnished_status = db.Column(db.String(50), nullable=True)  # ✅ Renamed for clarity
    deposit_amount = db.Column(db.Integer, nullable=True)  # ✅ Renamed for clarity
    listing_date = db.Column(db.Date, nullable=True)
    amenities = db.Column(db.Text)  # Store as comma-separated values (e.g., "Gym, Parking, Security")

class MessService(db.Model):
    __tablename__ = "mess_service" 
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    location = db.Column(db.Text, nullable=False)
    meal_type = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text)
    image_url = db.Column(db.Text)

    # ✅ Fixed Column Names
    owner_name = db.Column(db.String(100), nullable=False)  # ✅ Corrected
    phone_number = db.Column(db.String(20), nullable=False)  # ✅ Corrected
    timings = db.Column(db.String(100), nullable=True)
    menu = db.Column(db.Text, nullable=True)  # ✅ Added this missing column
    special_dishes = db.Column(db.Text, nullable=True)  # Comma-separated list
    listing_date = db.Column(db.Date, nullable=True)
    amenities = db.Column(db.Text)  # Store as "WiFi, AC, Parking"

class SavedListing(db.Model):
    __tablename__ = "saved_listing" 
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)  # ✅ Fixed Foreign Key
    accommodation_id = db.Column(db.Integer, db.ForeignKey("accommodations.id"))  # ✅ Fixed Foreign Key
    mess_id = db.Column(db.Integer, db.ForeignKey("mess_service.id"))  # ✅ Already Correct
