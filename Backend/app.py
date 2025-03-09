from flask import Flask
from flask_cors import CORS
from models import db
from routes import init_routes
from config import Config


app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Allow all origins

app.config.from_object(Config)

db.init_app(app)

with app.app_context():
    db.create_all()


init_routes(app)

if __name__ == "__main__":
    app.run(debug=True)
