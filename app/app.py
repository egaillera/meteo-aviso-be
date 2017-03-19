from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from config import Configuration #import configuration data

app = Flask(__name__)
app.config.from_object(Configuration) # use values from the Configuration object
db = SQLAlchemy(app)