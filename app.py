import os
from views import app
from models import db

if __name__ == "__main__":
    with app.app_context():
        db.create_all() # Create the DB if not exists
    app.run(
            debug=bool(os.getenv("DEBUG")) if os.getenv("DEBUG") else False,
            port=int(os.getenv("PORT")) if os.getenv("PORT") else 5000,
            host="0.0.0.0"
            )