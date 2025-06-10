from flask import request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Accommodation, MessService, SavedListing, Admin
from sqlalchemy import or_
from flask_jwt_extended import jwt_required
from flask_jwt_extended import create_access_token
from werkzeug.utils import secure_filename
from sqlalchemy import or_, text  # Update this line to include text

import os

UPLOAD_FOLDER = "static/uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif","avif","webp"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def init_routes(app):
    @app.route("/register", methods=["POST"])
    def register():
        data = request.get_json()
        hashed_password = generate_password_hash(data["password"])
        new_user = User(name=data["name"], email=data["email"], password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message": "User registered successfully!"}), 201

    @app.route("/login", methods=["POST", "OPTIONS"])  # ✅ Handle OPTIONS request for CORS
    def login():
        if request.method == "OPTIONS":
            return jsonify({"message": "CORS preflight successful"}), 200  

        data = request.get_json()
        email = data.get("email")
        password = data.get("password")

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):  # ✅ Hash password check
            return jsonify({"user_id": user.id})

        return jsonify({"error": "Invalid credentials"}), 401


    # @app.route("/login", methods=["POST"])
    # def login():
    #     data = request.get_json()
    #     user = User.query.filter_by(email=data["email"]).first()
    #     if user and check_password_hash(user.password, data["password"]):
    #         return jsonify({"message": "Login successful", "user_id": user.id})
    #     return jsonify({"error": "Invalid credentials"}), 401
    @app.route('/admin/login', methods=['POST'])
    def admin_login():
        data = request.get_json()
        print(f"🔍 Received Login Request: {data}")  # ✅ Debug print

        admin = Admin.query.filter_by(username=data["username"]).first()

        if admin:
            print(f"✅ Found Admin: {admin.username}")  # ✅ Debug print
            print(f"🔒 Stored Hashed Password: {admin.password}")  # ✅ Debug print

        if admin and check_password_hash(admin.password, data["password"]):
            print("✅ Password Matched!")  # ✅ Debug print
            token = create_access_token(identity={"role": "admin"})
            return jsonify({"message": "Login successful", "token": token})
        
        print("❌ Invalid Credentials!")  # ✅ Debug print
        return jsonify({"error": "Invalid credentials"}), 401


    @app.route('/admin/dashboard_stats', methods=['GET'])
    @jwt_required()
    def dashboard_stats():
        total_accommodations = Accommodation.query.count()
        total_mess = MessService.query.count()

        return jsonify({
            "total_accommodations": total_accommodations,
            "total_mess": total_mess
        })

    @app.route("/accommodation/<int:accommodation_id>", methods=["GET"])
    def get_accommodation(accommodation_id):
        print(f"🔍 Fetching accommodation with ID: {accommodation_id}")  # ✅ Debugging print
        accommodation = Accommodation.query.get(accommodation_id)
        if accommodation:
            print(f"✅ Found: {accommodation.name}") 
            return jsonify({
                "id": accommodation.id,
                "name": accommodation.name,
                "location": accommodation.location,
                "type": accommodation.type,
                "rent_price": accommodation.rent_price,
                "deposit_amount": accommodation.deposit_amount,
                "description": accommodation.description,
                "image_url": accommodation.image_url,
                "owner_name": accommodation.owner_name,
                "phone_number": accommodation.phone_number,
                "bedrooms": accommodation.bedrooms,
                "bathrooms": accommodation.bathrooms,
                "balconies": accommodation.balconies,
                "furnished_status": accommodation.furnished_status,
                "carpet_area": accommodation.carpet_area,
                "amenities": accommodation.amenities,
                "listing_date": accommodation.listing_date.strftime('%Y-%m-%d') if accommodation.listing_date else None,
                "availability_status": accommodation.availability_status,
                "property_age": accommodation.property_age,
                "parking_available": accommodation.parking_available
            })
        print("❌ Accommodation not found in the database!")  # ✅ Debugging print
        return jsonify({"error": "Accommodation not found"}), 404

    @app.route("/mess/<int:mess_id>", methods=["GET"])
    def get_mess_details(mess_id):
        mess = MessService.query.get(mess_id)
        if mess:
            return jsonify({
                "id": mess.id,
                "name": mess.name,
                "location": mess.location,
                "meal_type": mess.meal_type,
                "price": mess.price,
                "description": mess.description,
                "image_url": mess.image_url,
                "owner_name": mess.owner_name,
                "phone_number": mess.phone_number,
                "timings": mess.timings,
                "menu": mess.menu,
                "amenities": mess.amenities,
                "listing_date": mess.listing_date.strftime('%Y-%m-%d') if mess.listing_date else None
            })
        return jsonify({"error": "Mess service not found"}), 404


    # Inside init_routes(app)
    @app.route("/save", methods=["POST"])
    def save_listing():
        try:
            data = request.get_json()
            user_id = data.get("user_id")
            accommodation_id = data.get("accommodation_id")
            mess_id = data.get("mess_id")
            
            if not user_id or (not accommodation_id and not mess_id):
                return jsonify({"error": "Missing user_id or listing ID"}), 400
            
            # Check if already saved
            existing = SavedListing.query.filter_by(
                user_id=user_id,
                accommodation_id=accommodation_id if accommodation_id else None,
                mess_id=mess_id if mess_id else None
            ).first()
            if existing:
                return jsonify({"message": "Listing already saved"}), 200
            
            new_saved = SavedListing(
                user_id=user_id,
                accommodation_id=accommodation_id,
                mess_id=mess_id
            )
            db.session.add(new_saved)
            db.session.commit()
            return jsonify({"message": "Listing saved successfully!"}), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500

    @app.route("/unsave", methods=["POST"])
    def unsave_listing():
        try:
            data = request.get_json()
            user_id = data.get("user_id")
            accommodation_id = data.get("accommodation_id")
            mess_id = data.get("mess_id")
            
            if not user_id or (not accommodation_id and not mess_id):
                return jsonify({"error": "Missing user_id or listing ID"}), 400
            
            saved = SavedListing.query.filter_by(
                user_id=user_id,
                accommodation_id=accommodation_id if accommodation_id else None,
                mess_id=mess_id if mess_id else None
            ).first()
            if saved:
                db.session.delete(saved)
                db.session.commit()
                return jsonify({"message": "Listing unsaved successfully!"}), 200
            return jsonify({"error": "Listing not found in saved items"}), 404
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500

    @app.route("/saved_status", methods=["GET"])
    def check_saved_status():
        try:
            user_id = request.args.get("user_id", type=int)
            accommodation_id = request.args.get("accommodation_id", type=int)
            mess_id = request.args.get("mess_id", type=int)
            
            if not user_id or (not accommodation_id and not mess_id):
                return jsonify({"error": "Missing user_id or listing ID"}), 400
            
            saved = SavedListing.query.filter_by(
                user_id=user_id,
                accommodation_id=accommodation_id if accommodation_id else None,
                mess_id=mess_id if mess_id else None
            ).first()
            return jsonify({"isSaved": saved is not None})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/saved_listings", methods=["GET"])
    def get_saved_listings():
        try:
            user_id = request.args.get("user_id", type=int)
            if not user_id:
                return jsonify({"error": "Missing user_id"}), 400
            
            saved = SavedListing.query.filter_by(user_id=user_id).all()
            listings = []
            for item in saved:
                if item.accommodation_id:
                    acc = Accommodation.query.get(item.accommodation_id)
                    if acc:
                        listings.append({
                            "id": acc.id,
                            "type": "Accommodation",
                            "name": acc.name,
                            "location": acc.location,
                            "rent_price": acc.rent_price,
                            "image_url": acc.image_url
                        })
                elif item.mess_id:
                    mess = MessService.query.get(item.mess_id)
                    if mess:
                        listings.append({
                            "id": mess.id,
                            "type": "Mess",
                            "name": mess.name,
                            "location": mess.location,
                            "price": mess.price,
                            "image_url": mess.image_url
                        })
            return jsonify(listings)
        except Exception as e:
            return jsonify({"error": str(e)}), 500

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
            query = query.filter(Accommodation.rent_price <= max_budget)

        # ✅ Fetch results and return JSON
        results = query.all()

        return jsonify([
            {
                "id": acc.id,
                "name": acc.name,
                "location": acc.location,  # ✅ Full address will be shown
                "type": acc.type,
                "rent_price": acc.rent_price,
                "description": acc.description,
                "image_url": acc.image_url
            }
            for acc in results
        ])


    @app.route("/search_mess", methods=["GET"])
    def search_mess():
        location_keyword = request.args.get("location", "").strip().lower()
        meal_type = request.args.get("meal_type", "").strip().lower()
        max_budget = request.args.get("budget", type=int)

        query = MessService.query

        # ✅ Filter by location keyword
        if location_keyword:
            query = query.filter(MessService.location.ilike(f"%{location_keyword}%"))

        # ✅ Filter by meal type
        if meal_type == "pure veg":
            query = query.filter(MessService.meal_type.ilike("Pure Veg"))
        elif meal_type == "veg/non-veg":
            query = query.filter(MessService.meal_type.ilike("Veg/Non-Veg"))
        elif meal_type == "both":
            query = query.filter(MessService.meal_type.in_(["Pure Veg", "Veg/Non-Veg"]))

        # ✅ Filter by budget
        if max_budget:
            query = query.filter(MessService.price <= max_budget)

        # ✅ Fetch results and return JSON
        results = query.all()

        return jsonify([
            {
                "id": mess.id,
                "name": mess.name,
                "location": mess.location,
                "meal_type": mess.meal_type,
                "price": mess.price,
                "description": mess.description,
                "image_url": mess.image_url
            }
            for mess in results
        ])

    @app.route("/api/manage_listings", methods=["GET"])
    def manage_listings():
        accommodations = Accommodation.query.all()
        mess_services = MessService.query.all()

        manage_listings = []

        for acc in accommodations:
            manage_listings.append({
                "id": acc.id,
                "type": "Accommodation",
                "name": acc.name,
                "location": acc.location,
                "price": acc.rent_price,
                "status": "Available" if acc.availability_status else "Not Available",
                "phone_number": acc.phone_number
            })

        for mess in mess_services:
            manage_listings.append({
                "id": mess.id,
                "type": "Mess",
                "name": mess.name,
                "location": mess.location,
                "price": mess.price,
                "status": "Available",
                "phone_number": mess.phone_number
            })

        return jsonify(manage_listings)


    @app.route("/api/listings", methods=["GET"])
    def get_listings():
        accommodations = Accommodation.query.order_by(Accommodation.id.desc()).limit(3).all()
        mess_services = MessService.query.order_by(MessService.id.desc()).limit(3).all()

        listings = []

        for acc in accommodations:
            listings.append({
                "id": acc.id,
                "type": "Accommodation",
                "name": acc.name,
                "location": acc.location,
                "price": acc.rent_price,
                "status": "Available" if acc.availability_status else "Not Available",
                "image_url": acc.image_url if acc.image_url else "/static/uploads/default_listing.jpg",
                "listing_date": acc.listing_date.strftime('%Y-%m-%d') if acc.listing_date else None,
            })

        for mess in mess_services:
            listings.append({
                "id": mess.id,
                "type": "Mess",
                "name": mess.name,
                "location": mess.location,
                "price": mess.price,
                "status": "Available",
                "image_url": mess.image_url if mess.image_url else "/static/uploads/default_listing.jpg",
                "listing_date": mess.listing_date.strftime('%Y-%m-%d') if mess.listing_date else None,
                
            })

        # Sort combined list by id and take top 3
        sorted_listings = sorted(listings, key=lambda x: x["id"], reverse=True)[:3]
        return jsonify(sorted_listings)


    @app.route("/api/listings/<int:listing_id>", methods=["DELETE"])
    def delete_listing(listing_id):
        accommodation = Accommodation.query.get(listing_id)
        mess_service = MessService.query.get(listing_id)

        if accommodation:
            db.session.delete(accommodation)
        elif mess_service:
            db.session.delete(mess_service)
        else:
            return jsonify({"error": "Listing not found"}), 404

        db.session.commit()
        return jsonify({"message": "Listing deleted successfully"}), 200


    @app.route("/api/listings/<int:listing_id>", methods=["PUT"])
    def update_listing(listing_id):
        data = request.json
        accommodation = Accommodation.query.get(listing_id)
        mess_service = MessService.query.get(listing_id)

        if accommodation:
            for key, value in data.items():
                if key == "availability_status":  
                    value = True if value == "Available" or value is True else False  # Ensure Boolean conversion
                if hasattr(accommodation, key):
                    setattr(accommodation, key, value)
        
        elif mess_service:
            for key, value in data.items():
                if hasattr(mess_service, key):
                    setattr(mess_service, key, value)
        
        else:
            return jsonify({"error": "Listing not found"}), 404

        db.session.commit()
        return jsonify({"message": "Listing updated successfully"}), 200


    app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
    @app.route("/admin/add_accommodation", methods=["POST"])
    def add_accommodation():
        data = request.form

        # ✅ Convert "Available"/"Not Available" to Boolean
        availability_status = True if data["availability_status"] == "Available" else False

        # ✅ Handle Image Upload
        if "image" not in request.files:
            return jsonify({"error": "No image uploaded"}), 400

        image = request.files["image"]
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            image.save(image_path)
            image_url = f"/static/uploads/{filename}"
        else:
            return jsonify({"error": "Invalid image format"}), 400

        # ✅ Create New Accommodation Entry
        new_accommodation = Accommodation(
            name=data["name"],
            location=data["location"],
            type=data["type"],
            rent_price=float(data["rent_price"]),
            deposit_amount=float(data["deposit_amount"]),
            description=data["description"],
            image_url=image_url,
            owner_name=data["owner_name"],
            phone_number=data["phone_number"],
            bedrooms=int(data["bedrooms"]) if data["bedrooms"] else None,
            bathrooms=int(data["bathrooms"]) if data["bathrooms"] else None,
            balconies=int(data["balconies"]) if data["balconies"] else None,
            furnished_status=data["furnished_status"],
            carpet_area=float(data["carpet_area"]) if data["carpet_area"] else None,
            amenities=data["amenities"],
            listing_date=data["listing_date"],
            availability_status=availability_status,  # ✅ Converted to Boolean
            property_age=int(data["property_age"]) if data["property_age"] else None,
            parking_available=True if data["parking_available"] == "Yes" else False  # ✅ Converted to Boolean
        )

        db.session.add(new_accommodation)
        db.session.commit()

        return jsonify({"message": "Accommodation added successfully!"}), 201



    
    @app.route("/admin/add_mess", methods=["POST"])
    def add_mess():
        try:
            data = request.form

            # ✅ Handle Image Upload
            if "image" not in request.files:
                return jsonify({"error": "No image uploaded"}), 400

            image = request.files["image"]
            if image and allowed_file(image.filename):
                filename = secure_filename(image.filename)
                image_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                image.save(image_path)
                image_url = f"/static/uploads/{filename}"
            else:
                return jsonify({"error": "Invalid image format"}), 400

            # ✅ Insert Data into Database
            new_mess = MessService(
                name=data["name"],
                location=data["location"],
                meal_type=data["meal_type"],
                price=float(data["price"]),
                description=data["description"],
                image_url=image_url,
                owner_name=data["owner_name"],
                phone_number=data["phone_number"],
                timings=data["timings"],
                menu=data["menu"],
                amenities=data["amenities"],
                listing_date=data["listing_date"],
            )

            db.session.add(new_mess)
            db.session.commit()

            return jsonify({"message": "Mess added successfully!"}), 201

        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500

    @app.route("/admin/delete_accommodation/<int:accommodation_id>", methods=["DELETE"])
    def delete_accommodation(accommodation_id):
        accommodation = Accommodation.query.get(accommodation_id)
        if not accommodation:
            return jsonify({"error": "Accommodation not found"}), 404

        # ✅ Save to DeletedListings before deleting
        #deleted_entry = DeletedListings(name=accommodation.name, type="Accommodation")
        # db.session.add(deleted_entry)

        db.session.delete(accommodation)
        db.session.commit()
        return jsonify({"message": "Accommodation deleted successfully"})


    @app.route("/admin/delete_mess/<int:mess_id>", methods=["DELETE"])
    def delete_mess(mess_id):
        mess = MessService.query.get(mess_id)
        if not mess:
            return jsonify({"error": "Mess service not found"}), 404

        # ✅ Save to DeletedListings before deleting
        #deleted_entry = DeletedListings(name=mess.name, type="Mess")
        #db.session.add(deleted_entry)

        db.session.delete(mess)
        db.session.commit()
        return jsonify({"message": "Mess service deleted successfully"})



    @app.route("/admin/reset_id_sequence", methods=["POST"])
    def reset_id_sequence():
        db.session.execute(text("SELECT setval('accommodations_id_seq', (SELECT MAX(id) FROM accommodations));"))
        db.session.commit()
        return jsonify({"message": "ID sequence reset successfully!"})
    
    @app.route("/admin/dashboard_statistics", methods=["GET"])
    def dashboard_statistics():
        try:
            # ✅ Fetch total counts
            total_accommodations = Accommodation.query.count()
            total_mess = MessService.query.count()
            total_users = User.query.count()
            active_listings = total_accommodations + total_mess  # Simply count available entries

            # ✅ Get most popular accommodation & mess type
            accommodation_types = dict(db.session.query(Accommodation.type, db.func.count(Accommodation.id))
                                    .group_by(Accommodation.type).all())

            mess_types = dict(db.session.query(MessService.meal_type, db.func.count(MessService.id))
                            .group_by(MessService.meal_type).all())

            popular_accommodation = max(accommodation_types, key=accommodation_types.get, default="N/A")
            popular_mess = max(mess_types, key=mess_types.get, default="N/A")

            # ✅ Get latest 3 listings (Both Accommodation & Mess)
            recent_accommodations = Accommodation.query.order_by(Accommodation.id.desc()).limit(3).all()
            recent_messes = MessService.query.order_by(MessService.id.desc()).limit(3).all()

            recent_listings = [
                {"name": a.name, "location": a.location, "rent_price": a.rent_price, "status": "Available"} for a in recent_accommodations
            ] + [
                {"name": m.name, "location": m.location, "rent_price": m.price, "status": "N/A"} for m in recent_messes
            ]

            # ✅ Fetch latest 5 notifications dynamically
            notifications = []

            # Add New User Registrations
            recent_users = User.query.order_by(User.id.desc()).limit(2).all()
            notifications.extend([f"✅ New user registered: {user.name}" for user in recent_users])

            # Add New Listings
            notifications.extend([f"🏠 New accommodation added: {acc.name}" for acc in recent_accommodations])
            notifications.extend([f"🍽️ New mess added: {mess.name}" for mess in recent_messes])

            # Add Deleted Listings (Check if IDs skipped)
            all_accommodation_ids = [acc.id for acc in Accommodation.query.all()]
            all_mess_ids = [mess.id for mess in MessService.query.all()]

            # Get missing IDs from sequence (indicating deletions)
            deleted_accommodations = [id for id in range(1, max(all_accommodation_ids, default=1) + 1) if id not in all_accommodation_ids]
            deleted_messes = [id for id in range(1, max(all_mess_ids, default=1) + 1) if id not in all_mess_ids]

            # Add deleted notifications
            notifications.extend([f"📉 Accommodation deleted (ID: {id})" for id in deleted_accommodations[:2]])
            notifications.extend([f"📉 Mess service deleted (ID: {id})" for id in deleted_messes[:2]])

            # ✅ Sort notifications so newest appear first
            notifications = notifications[:5]  # Show only latest 5

            return jsonify({
                "total_accommodations": total_accommodations,
                "total_mess": total_mess,
                "total_users": total_users,
                "active_listings": active_listings,
                "popular_accommodation": popular_accommodation,
                "popular_mess": popular_mess,
                "recent_listings": recent_listings[:3],  # Show latest 3
                "notifications": notifications,  # Show latest 5
                "accommodation_types": accommodation_types,
                "mess_types": mess_types
            })

        except Exception as e:
            return jsonify({"error": str(e)}), 500

        
        # Add this to your routes.py file, inside the init_routes(app) function:

    @app.route("/api/accommodations/map", methods=["GET"])
    def get_accommodations_map():
        """
        Gets all accommodations with their full details for map integration.
        This endpoint provides the necessary data for Google Maps markers.
        """
        # Get query parameters for filtering
        location_keyword = request.args.get("location", "").strip().lower()
        property_type = request.args.get("type", "").strip().lower()
        max_budget = request.args.get("budget", type=int)

        query = Accommodation.query

        # Filter by location keyword if provided
        if location_keyword:
            query = query.filter(Accommodation.location.ilike(f"%{location_keyword}%"))

        # Filter by property type if provided and not 'all'
        if property_type and property_type != "all":
            query = query.filter(Accommodation.type.ilike(property_type))

        # Filter by budget if provided
        if max_budget:
            query = query.filter(Accommodation.rent_price <= max_budget)

        # Get all accommodations that match the filters
        accommodations = query.all()

        # Format the results for the map
        results = []
        for acc in accommodations:
            results.append({
                "id": acc.id,
                "name": acc.name,
                "location": acc.location,
                "type": acc.type,
                "rent_price": acc.rent_price,
                "deposit_amount": acc.deposit_amount,
                "description": acc.description,
                "image_url": acc.image_url,
                "bedrooms": acc.bedrooms,
                "bathrooms": acc.bathrooms,
                "furnished_status": acc.furnished_status,
                "availability_status": acc.availability_status
            })

        return jsonify(results)

    @app.route("/api/mess/map", methods=["GET"])
    def get_mess_map():
        """
        Gets all mess services with their full details for map integration.
        This endpoint provides the necessary data for Google Maps markers.
        """
        # Get query parameters for filtering
        location_keyword = request.args.get("location", "").strip().lower()
        meal_type = request.args.get("meal_type", "").strip()
        max_budget = request.args.get("budget", type=int)

        query = MessService.query

        # Filter by location keyword if provided
        if location_keyword:
            query = query.filter(MessService.location.ilike(f"%{location_keyword}%"))

        # Filter by meal type if provided
        if meal_type in ["Pure Veg", "Veg/Non-Veg"]:
            query = query.filter(MessService.meal_type.ilike(meal_type))

        # Filter by budget if provided
        if max_budget:
            query = query.filter(MessService.price <= max_budget)

        # Get all mess services that match the filters
        mess_services = query.all()

        # Format the results for the map
        results = []
        for mess in mess_services:
            results.append({
                "id": mess.id,
                "name": mess.name,
                "location": mess.location,
                "meal_type": mess.meal_type,
                "price": mess.price,
                "description": mess.description,
                "image_url": mess.image_url,
                "timings": mess.timings,
                "menu": mess.menu,
                "amenities": mess.amenities
            })

        return jsonify(results)


    from flask import render_template

