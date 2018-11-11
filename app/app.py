import logging
import os
from logging.handlers import RotatingFileHandler
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address


from config import Configuration,Configuration_dev #import configuration data

# Create app
app = Flask(__name__)

# Setting configuration
if  "VIRTUAL_ENV" in os.environ:
	app.config.from_object(Configuration_dev) # virtualenv is always used in dev
else:
	app.config.from_object(Configuration) 

# Setting the logs
handler = RotatingFileHandler('logs/meteo-aviso-be.log', maxBytes=1000000, backupCount=1)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
handler.setLevel(logging.DEBUG)
app.logger.addHandler(handler)
	
# Limit number of requests
if "LIMIT" in os.environ:
	limit = os.environ['LIMIT']
else:
	limit = "50"
app.logger.info("Setting limit as " + limit + " requests per day")	
limiter = Limiter(
                  app,
                  key_func=get_remote_address,
                  default_limits=[limit + " per day"]
)

# Initiate db connection
db = SQLAlchemy(app)


