from app import app
from models import Station,Measurement
from flask import jsonify,request
import db_access.users
import db_access.measurement
import db_access.rules

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
	
@app.route('/closest_measurement')
def closest_station():
	"""Return closest measurement from /closest_measurement?lat=lat&lon=lon"""
	lat = request.args.get("lat")
	lon = request.args.get("lon")
	
	return jsonify(db_access.measurement.get_closest_measurement(lat,lon))
	
@app.route('/last_measurement/<station_code>')
def last_measurement(station_code):
	""" Return last measurement of a specific station """
	
	result = db_access.measurement.get_last_measurement(station_code)
	return jsonify(result) if result != None else "[]"
	
@app.route('/token', methods=['POST'])
def save_token():
	"""Save the token to the user table in the database"""
	if db_access.users.insert_user(request.form.to_dict()):
		return jsonify(token="token",status=200)
	else:
		return jsonify(token="token",status=500)
		
@app.route('/save_rules', methods=['POST'])
def save_rules():
	content = request.json
	print(content)
	if db_access.rules.check_rules(content):
		db_access.rules.insert_rules(content['email'],content['station'],content['rules'])
		return jsonify(rules="rules",status=200)
	else:
		return jsonify(rules="rules",status=406)
	
	
	
