from app import app
from sqlalchemy.orm.exc import NoResultFound
from models import *
from util.distance import get_closest_station


def get_closest_measurement(lat,lon):
	
	app.logger.info("---> get_closest_measurement()")
	
	# Get all stations
	active_stations = Station.query.all()
	
	# Get the closest one
	closest_station = get_closest_station(active_stations,lat,lon)
	
	# Get the most recent measurement 
	data = Measurement.query.filter(Measurement.station==closest_station.code).\
	                   order_by(Measurement.date_created.desc()).first().\
	                   serialize
	
	# Add station name to the mesaurement
	data['name'] = closest_station.name
	
	return data



    
	
	