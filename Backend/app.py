import os
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from models import db
from routes import init_routes
from config import Config

app = Flask(__name__)
# Enable CORS with more specific configuration
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# 🔐 Load JWT secret key from environment variable
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "fallback_secret")  # Use a secure key
jwt = JWTManager(app)

# 🔧 Load configuration settings
app.config.from_object(Config)

# ✅ Initialize database
db.init_app(app)

with app.app_context():
    try:
        db.create_all()  # Ensures tables are created
        print("✅ Database tables created successfully!")
    except Exception as e:
        print(f"❌ Error initializing database: {e}")

# 🔗 Initialize all routes
init_routes(app)

# Additional route to serve frontend files
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    from flask import send_from_directory
    
    if path == '':
        return send_from_directory('../frontend', 'home.html')
    
    # Try to serve the file directly
    try:
        return send_from_directory('../frontend', path)
    except:
        # Return the home page for any non-existent route (for SPA support)
        return send_from_directory('../frontend', 'home.html')

# 🚀 Run the application
if __name__ == "__main__":
    # Binding to 0.0.0.0 makes it accessible from other devices
    app.run(host='0.0.0.0', port=5000, debug=True)
