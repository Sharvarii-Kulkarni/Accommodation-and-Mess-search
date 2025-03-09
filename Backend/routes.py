from flask import request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Accommodation, MessService, SavedListing
from flask_cors import cross_origin

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
            "rent_price": a.rent_price,
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
    @cross_origin()
    def search_accommodations():
        location_keyword = request.args.get("location", "").strip().lower()
        property_type = request.args.get("type", "").strip().lower()
        max_budget = request.args.get("budget", type=int)

        query = Accommodation.query

        if location_keyword:
            query = query.filter(Accommodation.location.ilike(f"%{location_keyword}%"))
        
        if property_type and property_type != "all":
            query = query.filter(Accommodation.type.ilike(property_type))
        
        if max_budget:
            query = query.filter(Accommodation.rent_price <= max_budget)

        print(query)  # Debugging

        results = query.all()

        return jsonify([
            {
                "id": acc.id,
                "name": acc.name,
                "location": acc.location,
                "type": acc.type,
                "rent_price": acc.rent_price,
                "description": acc.description,
                "image_url": acc.image_url,
                "owner_name": acc.owner_name,
                "phone_number": acc.phone_number
            }
            for acc in results
        ])

    @app.route("/search_mess", methods=["GET"])
    @cross_origin()
    def search_mess():
        location_keyword = request.args.get("location", "").strip().lower()
        meal_type = request.args.get("meal_type", "").strip()
        max_budget = request.args.get("budget", type=int)

        query = MessService.query

        if location_keyword:
            query = query.filter(MessService.location.ilike(f"%{location_keyword}%"))

        # Normalize meal_type input
        if meal_type:
            if meal_type.lower() == "pure veg":
                meal_type = "Vegetarian"
            elif meal_type.lower() == "veg/non-veg":
                meal_type = "Veg/Non-Veg"
            elif meal_type.lower() == "both":
                meal_type = "all"  # Ensure "both" gets treated as "all"

        if meal_type and meal_type != "all":
            query = query.filter(MessService.meal_type.ilike(meal_type))

        if max_budget:
            query = query.filter(MessService.price <= max_budget)

        print(query)  # Debugging

        results = query.all()

        return jsonify([
            {
                "id": mess.id,
                "name": mess.name,
                "location": mess.location,
                "meal_type": mess.meal_type,
                "price": mess.price,
                "description": mess.description,
                "image_url": mess.image_url,
                "owner_name": mess.owner_name,
                "phone_number": mess.phone_number,
                "menu": mess.menu  # ✅ Fixed column name
            }
            for mess in results
        ])

    @app.route("/get_property/<int:property_id>", methods=["GET"])
    def get_property(property_id):
        property_data = Accommodation.query.get(property_id)

        if property_data:
            return jsonify({
                "id": property_data.id,
                "name": property_data.name,
                "location": property_data.location,
                "type": property_data.type,
                "rent_price": property_data.rent_price,
                "description": property_data.description,
                "image_url": property_data.image_url if property_data.image_url else "images/default.jpg",
                "owner_name": property_data.owner_name,
                "phone_number": property_data.phone_number,
                "bedrooms": property_data.bedrooms,
                "bathrooms": property_data.bathrooms,
                "balconies": property_data.balconies,
                "carpet_area": property_data.carpet_area,
                "furnished_status": property_data.furnished_status,
                "deposit_amount": property_data.deposit_amount,
                "listing_date": property_data.listing_date.strftime("%Y-%m-%d") if property_data.listing_date else None,
                "amenities": property_data.amenities.split(", ") if property_data.amenities else []
            })

        return jsonify({"error": "Property not found"}), 404

    @app.route("/mess/<int:mess_id>", methods=["GET"])
    def get_mess_by_id(mess_id):
        mess_data = MessService.query.get(mess_id)

        if mess_data:
            return jsonify({
                "id": mess_data.id,
                "name": mess_data.name,
                "location": mess_data.location,
                "meal_type": mess_data.meal_type,
                "price": mess_data.price,
                "description": mess_data.description,
                "image_url": mess_data.image_url if mess_data.image_url else "images/default.jpg",
                "owner_name": mess_data.owner_name,
                "phone_number": mess_data.phone_number,
                "timings": mess_data.timings,
                "menu": mess_data.menu,  # ✅ Fixed column name
                "special_dishes": mess_data.special_dishes.split(", ") if mess_data.special_dishes else [],
                "listing_date": mess_data.listing_date.strftime("%Y-%m-%d") if mess_data.listing_date else None,
                "amenities": mess_data.amenities.split(", ") if mess_data.amenities else []
            })

        return jsonify({"error": "Mess not found"}), 404
