from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from werkzeug.security import generate_password_hash

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')  # tu configuración

    db.init_app(app)
    login_manager.init_app(app)

    login_manager.login_view = 'auth.login'  # nombre de la ruta login

    from .routes import main_bp
    from .auth import auth_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)

    with app.app_context():
        from .models import User  # importa dentro del contexto para evitar ciclos
        db.create_all()  # crea tablas si no existen
        create_default_user()

    return app

@login_manager.user_loader
def load_user(user_id):
    from .models import User
    return User.query.get(int(user_id))


def create_default_user():
    from .models import User
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            password=generate_password_hash('admin123'),
            role='admin'
        )
        db.session.add(admin)
        db.session.commit()
        print("✔ Usuario admin creado")
    else:
        print("ℹ Usuario admin ya existe")
