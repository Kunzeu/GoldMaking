from app import create_app
from app.models import db
from app.seed import create_default_user
import os

app = create_app()

with app.app_context():
    db.create_all()
    create_default_user()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
