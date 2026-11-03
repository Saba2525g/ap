import getpass
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app
from app.extensions import db
from app.models.user import User, ROLE_ADMIN


def main():
    app = create_app("development")
    with app.app_context():
        existing = db.session.query(User).filter(User.role == ROLE_ADMIN).first()
        if existing:
            print(f"Admin already exists: {existing.email}")
            return

        email = input("Admin email: ").strip().lower()
        if not email:
            print("ERROR: email required")
            return
        if db.session.query(User).filter(User.email == email).first():
            print("ERROR: email already used")
            return

        name = input("Admin full name: ").strip()
        if not name:
            print("ERROR: name required")
            return

        password = getpass.getpass("Password (min 8 chars): ")
        if len(password) < 8:
            print("ERROR: password too short")
            return

        u = User(email=email, full_name=name, role=ROLE_ADMIN, is_active=True)
        u.set_password(password)
        db.session.add(u)
        db.session.commit()
        print(f"OK: admin created (id={u.id}, email={u.email})")


if __name__ == "__main__":
    main()
