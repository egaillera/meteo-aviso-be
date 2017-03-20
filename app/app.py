import logging
from logging.handlers import RotatingFileHandler
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from config import Configuration #import configuration data

app = Flask(__name__)
app.config.from_object(Configuration) # use values from the Configuration object
db = SQLAlchemy(app)
handler = RotatingFileHandler('logs/meteo-aviso-be.log', maxBytes=10000, backupCount=1)
handler.setLevel(logging.INFO)
app.logger.addHandler(handler)
