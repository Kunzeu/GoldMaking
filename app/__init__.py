from flask import Flask, url_for, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import logging
from flask_migrate import Migrate
from flask_sitemap import Sitemap

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    # En caso de que SECRET_KEY no esté en config, definirlo aquí
    if not app.config.get('SECRET_KEY'):
        app.secret_key = 'clave-secreta-por-defecto-para-dev'

    # Logging básico
    logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

    db.init_app(app)
    login_manager.init_app(app)
    migrate = Migrate(app, db)
    ext = Sitemap(app=app)

    login_manager.login_view = 'auth.login'

    from .routes import main_bp
    from .auth import auth_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)

    def register_sitemap(app):
        @app.route('/sitemap.xml')
        def sitemap():
            from app.models import Farm
            urls = [url_for('main.index', _external=True)]
            with app.app_context():
                for farm in Farm.query.all():
                    urls.append(url_for('main.farmeo_detail', farm_id=farm.id, _external=True))
            xml = render_template('sitemap.xml', urls=urls)
            return app.response_class(xml, mimetype='application/xml')
    register_sitemap(app)

    return app


from .models import User  # importa el modelo User

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
