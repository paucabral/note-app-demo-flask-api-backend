from views import app
from models import db
import os

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        
    app.run(
            debug=bool(os.getenv("DEBUG")),
            port=int(os.getenv("PORT")),
            host="0.0.0.0"
            )