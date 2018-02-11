from app import app
from models import Station,Measurement
from flask import jsonify,request
from util.distance import get_closest_station
import db_access

@app.route('/')
def homepage():
	app.logger.info('Home page visited')
	return 'Home page' + '\n'

@app.route('/stations')	
def stations():
	"""Return all the stations"""
	return jsonify([i.serialize for i in Station.query.all()])
	
@app.route('/measurements/<station_code>')
def measurements(station_code):
	"""Return all the measurements for a station"""
	return jsonify([i.serialize for i in Measurement.query.filter(Measurement.station == station_code).all()])	
	
@app.route('/closest_station')
def closest_station():
	"""Return closest station from /closest_station?lat=lat&lon=lon"""
	lat = request.args.get("lat")
	lon = request.args.get("lon")
	
	return get_closest_station(lat,lon) + '\n'
	
@app.route('/token', methods=['POST'])
def save_token():
	"""Save the token to the user table in the database"""
	if db_access.insert_user(request.form.to_dict()):
		return jsonify(token="token",status=200)
	else:
		return jsonify(token="token",status=500)
	
	
