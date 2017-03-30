from app import app
from models import Station,Measurement
from flask import jsonify,request
from util.distance import get_closest_station

@app.route('/')
def homepage():
	app.logger.info('Home page visited')
	return 'Home page' + '\n'

@app.route('/stations')	
def stations():
	"""Return all the stations"""
	return jsonify([i.serialize for i in Station.query.all()])
	
@app.route('/closest_station')
def closest_station():
	"""Return closest station from /closest_station?lat=lat&lon=lon"""
	lat = request.args.get("lat")
	lon = request.args.get("lon")
	
	return get_closest_station(lat,lon) + '\n'
	
	
