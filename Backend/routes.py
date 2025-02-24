from flask import request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Accommodation, MessService, SavedListing
from sqlalchemy import or_

def init_routes(app):
    @app.route("/register", methods=["POST"])
    def register():
        data = request.get_json()
        hashed_password = generate_password_hash(data["password"])
        new_user = User(name=data["name"], email=data["email"], password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message": "User registered successfully!"}), 201

    # @app.route("/login", methods=["POST"])
    # def login():
    #     data = request.get_json()
    #     user = User.query.filter_by(email=data["email"]).first()
    #     if user and check_password_hash(user.password, data["password"]):
    #         return jsonify({"message": "Login successful", "user_id": user.id})
    #     return jsonify({"error": "Invalid credentials"}), 401
    @app.route("/login", methods=["POST"])
    def login():
        if request.is_json:
            data = request.get_json()
        else:
            return jsonify({"error": "Invalid request format. Please send JSON data."}), 400

        user = User.query.filter_by(email=data.get("email")).first()
        if user and check_password_hash(user.password, data.get("password")):
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
    
    @app.route("/get_user/<int:user_id>", methods=["GET"])
    def get_user(user_id):
        user = User.query.get(user_id)
        if user:
            return jsonify({"name": user.name, "email": user.email})
        return jsonify({"error": "User not found"}), 404
    

    @app.route("/search_accommodations", methods=["GET"])
    def search_accommodations():
        location_keyword = request.args.get("location", "").strip().lower()
        property_type = request.args.get("type", "").strip().lower()
        max_budget = request.args.get("budget", type=int)

        query = Accommodation.query

        # ✅ Filter by location keyword (Matches any part of the address)
        if location_keyword:
            query = query.filter(Accommodation.location.ilike(f"%{location_keyword}%"))

        # ✅ Handle "Any Type" search (Return all types if "all" is selected)
        if property_type and property_type != "all":
            query = query.filter(Accommodation.type.ilike(property_type))

        # ✅ Filter by budget
        if max_budget:
            query = query.filter(Accommodation.price <= max_budget)

        # ✅ Fetch results and return JSON
        results = query.all()

        return jsonify([
            {
                "id": acc.id,
                "name": acc.name,
                "location": acc.location,  # ✅ Full address will be shown
                "type": acc.type,
                "price": acc.price,
                "description": acc.description,
                "image_url": acc.image_url
            }
            for acc in results
        ])


    @app.route("/search_mess", methods=["GET"])
    def search_mess():
        location_keyword = request.args.get("location", "").strip().lower()
        meal_type = request.args.get("meal_type", "").strip()
        max_budget = request.args.get("budget", type=int)

        query = MessService.query

        # ✅ Filter by location keyword (Matches any part of the address)
        if location_keyword:
            query = query.filter(MessService.location.ilike(f"%{location_keyword}%"))

        # ✅ Filter by meal type
        if meal_type in ["Pure Veg", "Veg/Non-Veg"]:
            query = query.filter(MessService.meal_type.ilike(meal_type))

        # ✅ Filter by budget
        if max_budget:
            query = query.filter(MessService.price <= max_budget)

        # ✅ Fetch results and return JSON
        results = query.all()

        return jsonify([
            {
                "id": mess.id,
                "name": mess.name,
                "location": mess.location,  # ✅ Shows full address now
                "meal_type": mess.meal_type,
                "price": mess.price,
                "description": mess.description,
                "image_url": mess.image_url
            }
            for mess in results
        ])
