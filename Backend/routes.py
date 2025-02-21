from flask import request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Accommodation, MessService, SavedListing

def init_routes(app):
    @app.route("/register", methods=["POST"])
    def register():
        data = request.get_json()
        hashed_password = generate_password_hash(data["password"])
        new_user = User(name=data["name"], email=data["email"], password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message": "User registered successfully!"}), 201

    @app.route("/login", methods=["POST"])
    def login():
        data = request.get_json()
        user = User.query.filter_by(email=data["email"]).first()
        if user and check_password_hash(user.password, data["password"]):
            return jsonify({"message": "Login successful", "user_id": user.id})
        return jsonify({"error": "Invalid credentials"}), 401

    @app.route("/accommodations", methods=["GET"])
    def get_accommodations():
        accommodations = Accommodation.query.all()
        return jsonify([{
            "id": a.id,
            "name": a.name,
            "location": a.location,
            "type": a.type,
            "price": a.price,
            "description": a.description,
            "image_url": a.image_url
        } for a in accommodations])

    @app.route("/mess", methods=["GET"])
    def get_mess():
        mess = MessService.query.all()
        return jsonify([{
            "id": m.id,
            "name": m.name,
            "location": m.location,
            "meal_type": m.meal_type,
            "price": m.price,
            "description": m.description,
            "image_url": m.image_url
        } for m in mess])

    @app.route("/save", methods=["POST"])
    def save_listing():
        data = request.get_json()
        new_saved = SavedListing(user_id=data["user_id"], accommodation_id=data.get("accommodation_id"), mess_id=data.get("mess_id"))
        db.session.add(new_saved)
        db.session.commit()
        return jsonify({"message": "Listing saved!"})
