import os
import getpass
from werkzeug.security import generate_password_hash
from models import db, Admin
from app import app  # Import Flask app instance

def add_admin():
    # ✅ Step 1: Retrieve Master Password from Environment Variable
    MASTER_PASSWORD = os.getenv("ADMIN_MASTER_PASSWORD")  # Load securely

    if not MASTER_PASSWORD:
        print("❌ Master password not set. Please configure the environment variable.")
        return

    # ✅ Step 2: Verify Master Password
    entered_master_password = getpass.getpass("Enter Master Password to proceed: ")
    if entered_master_password != MASTER_PASSWORD:
        print("❌ Access Denied! Incorrect Master Password.")
        return

    with app.app_context():  # Ensure database operations run inside Flask context
        username = input("Enter new admin username: ")

        # ✅ Check if username already exists
        existing_admin = Admin.query.filter_by(username=username).first()
        if existing_admin:
            print("❌ Admin with this username already exists. Try another.")
            return

        # ✅ Get Password & Confirm Password securely
        while True:
            password = getpass.getpass("Enter new admin password: ")  # Secure input
            confirm_password = getpass.getpass("Confirm password: ")  # Confirm password

            if password == confirm_password:
                break  # ✅ Passwords match, continue
            else:
                print("❌ Passwords do not match! Please try again.")

        # ✅ Hash the password before storing
        hashed_password = generate_password_hash(password)

        # ✅ Insert new admin into database
        new_admin = Admin(username=username, password=hashed_password)
        db.session.add(new_admin)
        db.session.commit()

        print(f"✅ New Admin '{username}' added successfully!")

# Run the function
if __name__ == "__main__":
    add_admin()
