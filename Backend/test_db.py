from app import db, app
from models import Accommodation

with app.app_context():  # ✅ Creates an application context
    acc = Accommodation.query.get(10)
    print(acc)

