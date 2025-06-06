import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

class Config:
    SQLALCHEMY_DATABASE_URI = "postgresql://root:JGWaC0WrJwJSI9gnax2V0cVD4z8ajtWp@dpg-d11lj8c9c44c73ffb9cg-a.singapore-postgres.render.com/goldmaking"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "una_clave_secreta_que_puedas_cambiar"

