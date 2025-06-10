from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "users"  # 🔥 Ensure it matches PostgreSQL table name
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)  # Store hashed password
    
class Accommodation(db.Model):
    __tablename__ = "accommodations"  # ✅ Make sure this matches your table name

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    location = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(50), nullable=False)
    rent_price = db.Column(db.Integer, nullable=False)
    deposit_amount = db.Column(db.Integer, nullable=True)
    description = db.Column(db.Text)
    image_url = db.Column(db.Text)
    owner_name = db.Column(db.String(100), nullable=True)
    phone_number = db.Column(db.String(20), nullable=True)
    bedrooms = db.Column(db.Integer, nullable=True)
    bathrooms = db.Column(db.Integer, nullable=True)
    balconies = db.Column(db.Integer, nullable=True)
    furnished_status = db.Column(db.String(50), nullable=True)
    carpet_area = db.Column(db.Integer, nullable=True)
    amenities = db.Column(db.Text, nullable=True)
    listing_date = db.Column(db.Date, nullable=True)
    availability_status = db.Column(db.Boolean, nullable=True)
    property_age = db.Column(db.Integer, nullable=True)
    parking_available = db.Column(db.Boolean, nullable=True)



class MessService(db.Model):
    __tablename__ = "mess_service" 
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    location = db.Column(db.Text, nullable=False)
    meal_type = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text)
    image_url = db.Column(db.Text)
    owner_name = db.Column(db.String(100), nullable=True)  # ✅ Added owner name
    phone_number = db.Column(db.String(20), nullable=True)  # ✅ Added phone number
    timings = db.Column(db.String(100), nullable=True)
    menu = db.Column(db.Text, nullable=True)
    amenities = db.Column(db.Text, nullable=True)
    listing_date = db.Column(db.Date, nullable=True)


class SavedListing(db.Model):
    __tablename__ = "saved_listing" 
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    accommodation_id = db.Column(db.Integer, db.ForeignKey("accommodations.id"))
    mess_id = db.Column(db.Integer, db.ForeignKey("mess_service.id"))
