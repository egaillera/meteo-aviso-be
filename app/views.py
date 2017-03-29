from app import app
from models import Station,Measurement
from flask import jsonify

@app.route('/')
def homepage():
	app.logger.info('Home page visited')
	return 'Home page'

@app.route('/stations')	
def stations():
	"""Return all the stations"""
	return jsonify([i.serialize for i in Station.query.all()])
	
