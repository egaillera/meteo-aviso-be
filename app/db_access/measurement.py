from app import app
from sqlalchemy.orm.exc import NoResultFound
from models import *
from util.distance import get_closest_station

# TODO: check errors in query
def get_closest_measurement(lat,lon):
	
	app.logger.info("---> get_closest_measurement()")
	
	# Get all stations
	active_stations = Station.query.all()
	
	# Get the closest one
	closest_station = get_closest_station(active_stations,lat,lon)
	
	return get_last_measurement(closest_station.code)
	
	'''
	# Get the most recent measurement 
	data = Measurement.query.filter(Measurement.station==closest_station.code).\
	                   order_by(Measurement.date_created.desc()).first().\
	                   serialize
	
	# Add station name to the mesaurement
	data['name'] = closest_station.name
	
	return data
	'''	

def get_last_measurement(station_code):
	
	app.logger.info("---> get_last_measurement()")
	
	data = None
	
	# Get the most recent measurement
	try:
		m = Measurement.query.filter(Measurement.station==station_code).\
		                                order_by(Measurement.date_created.desc()).first()                         
		if m != None:
			data = m.serialize 
		
		# Add station name
		data['name'] = Station.query.filter(Station.code == station_code).one().name
		
	
	except NoResultFound:
		data = None
	
	return data
	
	
	
	



    
	
	