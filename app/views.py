from app import app
from models import Station,Measurement
from flask import jsonify,request
import json
import db_access.users
import db_access.measurement
import db_access.rules
import db_access.new_rules

@app.route('/')
def homepage():
	app.logger.info('Requested home page')
	return 'MeteoAviso Home Page' + '\n'

@app.route('/stations')	
def stations():
	"""Return all the stations"""
	app.logger.info("Requested /stations")
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
	
@app.route('/last_measurements')
def last_measurements():
	""" Return last measurements of all stations """
	app.logger.info("Requested /last_measurements")

	result = db_access.measurement.get_last_measurements()
	app.logger.debug("Returned %d measurements" % len(result))
	return jsonify(result) if result != None else "[]"
	
	
@app.route('/token', methods=['POST'])
def save_token():
	"""Save the token to the user table in the database"""
	if db_access.users.insert_user(request.form.to_dict()):
		return jsonify(token="token",status=200)
	else:
		return jsonify(error="Database error",status=500),500
		
@app.route('/save_rules', methods=['POST'])
def save_rules():
	content = request.json
	print(content)
	if db_access.new_rules.check_rules1(content):
		db_access.new_rules.insert_rules1(content['device_id'],content['station'],content['rules'])
		return jsonify(rules="rules",status=200)
	else:
		return jsonify(rules="rules",status=406),406

# TODO: TO BE DEPRECATED		
@app.route('/get_rules')
def get_rules():
	"""Return rules from a user from /get_rules?email=kk@kk.com"""
	
	email = request.args.get("email")
	rules = db_access.rules.get_rules(email)
	if rules == None:
		return jsonify(error="Database access error",status=500),500
	else:
		return jsonify(rules)
# /TO BE DEPRECATED
		
@app.route('/get_rules1/<device_id>')
def get_rules1(device_id):
	"""Return rules from a user from /get_rules/<device_id>"""
	app.logger.info("Requested /get_rules/%s" % device_id)

	rules = db_access.new_rules.get_rules1(device_id)
	if rules == None:
		return jsonify(error="Database access error",status=500),500
	else:
		return jsonify(rules)

# TODO: TO BE DEPRECATED	
@app.route('/get_rules/<station_code>')
def get_rules_from_station(station_code):
	"""Return rules from /get_rules/<station_name>?email=kk@kk.com"""
	
	email = request.args.get("email")
	rules = db_access.rules.get_rules_for_station(email,station_code)
	if rules == None:
		return jsonify(error="Database access error",status=500),500
	else:
		return jsonify(rules)
# /TO BE DEPRECATED
		
@app.route('/get_rules1/<device_id>/<station_code>')
def get_rules_from_station1(device_id,station_code):
	"""Return rules from /get_rules/<device_id>/<station_name>"""
	
	app.logger.info("Requested /get_rules/%s/%s" % (device_id,station_code))

	rules = db_access.new_rules.get_rules_for_station1(device_id,station_code)
	if rules == None:
		return jsonify(error="Database access error",status=500),500
	else:
		return jsonify(rules)

# TODO: TO BE DEPRECATED
@app.route('/delete_rules/<station_code>',methods=['POST'])
def delete_rules(station_code):
	"""Return rules from /delete_rules/<station_name>?email=kk@kk.com"""

	email = request.args.get("email")
	if db_access.rules.delete_rules(email,station_code):
		return jsonify(error="None",status=200),200
	else:
		return jsonify(error="Database access error",status=500),500
# /TO BE DEPRECATED

@app.route('/delete_rules1/<device_id>/<station_code>',methods=['POST'])
def delete_rules1(device_id,station_code):
	"""Return rules from /delete_rules/<device_id>/<station_name>"""

	if db_access.new_rules.delete_rules1(device_id,station_code):
		return jsonify(error="None",status=200),200
	else:
		return jsonify(error="Database access error",status=500),500

	
	
	
