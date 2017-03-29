import logging
import os
from logging.handlers import RotatingFileHandler
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from config import Configuration,Configuration_dev #import configuration data

# Create app
app = Flask(__name__)

# Setting configuration
if  "VIRTUAL_ENV" in os.environ:
	app.config.from_object(Configuration_dev) # virtualenv is always used in dev
else:
	app.config.from_object(Configuration) 

# Initiate db connection
db = SQLAlchemy(app)

# Setting the logs
handler = RotatingFileHandler('logs/meteo-aviso-be.log', maxBytes=10000, backupCount=1)
handler.setLevel(logging.INFO)
app.logger.addHandler(handler)
