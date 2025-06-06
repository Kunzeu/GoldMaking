from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

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
    


    return app

from .models import User  # importa el modelo User

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
