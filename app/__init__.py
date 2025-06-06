from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os
from dotenv import load_dotenv

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    load_dotenv()  # Carga variables del .env
    
    app = Flask(__name__)
    app.config.from_object('config.Config')

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    from .routes import main_bp
    from .auth import auth_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)

    with app.app_context():
        from .models import User
        from werkzeug.security import generate_password_hash

        username = os.getenv('ADMIN_USER')
        password = os.getenv('ADMIN_PASS')
        role = os.getenv('ADMIN_ROLE')

        admin = User.query.filter_by(username=username).first()
        if not admin:
            admin = User(
                username=username,
                password=generate_password_hash(password),
                role=role
            )
            db.session.add(admin)
            db.session.commit()
            print(f"✔ Usuario {username} creado")
        else:
            print(f"ℹ Usuario {username} ya existe")

    return app

from .models import User

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
