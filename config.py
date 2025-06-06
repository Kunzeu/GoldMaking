import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

class Config:
    SQLALCHEMY_DATABASE_URI = "SQLALCHEMY_DATABASE_URI"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "tu_clave_secreta_aqui"
