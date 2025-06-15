from . import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class Farm(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    veces_realizadas = db.Column(db.Integer, nullable=False)
    ganancia = db.Column(db.Float, nullable=False)
    waypoint = db.Column(db.String(100))
    duracion = db.Column(db.String(20))
    requerimientos = db.Column(db.String(200))
    profit_hr = db.Column(db.Float)
    limitation = db.Column(db.String(200))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='admin')  # 'admin', 'editor', 'user'

class DailyRoutine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    farm_id = db.Column(db.Integer, db.ForeignKey('farm.id'), nullable=False)
    orden = db.Column(db.Integer, default=0)

    # Propiedad para password: se evita acceso directo y se usa para setear hash
    @property
    def password(self):
        raise AttributeError('No se puede leer el atributo password directamente')

    @password.setter
    def password(self, password_plain):
        self.password_hash = generate_password_hash(password_plain)

    def check_password(self, password_plain):
        return check_password_hash(self.password_hash, password_plain)
