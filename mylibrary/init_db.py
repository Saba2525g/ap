import sys
from app import create_app
from app.extensions import db
import app.models

def main():
    drop = "--drop" in sys.argv
    app = create_app("development")
    with app.app_context():
        if drop:
            print("Dropping all tables...")
            db.drop_all()
        db.create_all()
        tables = sorted(db.metadata.tables.keys())
        print(f"OK: {len(tables)} tables created")
        for t in tables:
            print(f"  - {t}")

if __name__ == "__main__":
    main()
