from app.models import db, User
from werkzeug.security import generate_password_hash

def create_default_user():
    if not User.query.filter_by(username="admin").first():
        admin = User(
            username="admin",
            password=generate_password_hash("admin123"),
            role="admin"
        )
        db.session.add(admin)
        db.session.commit()
        print("✔ Usuario por defecto creado")
    else:
        print("ℹ Usuario por defecto ya existe")
