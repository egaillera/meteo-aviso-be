from app import app
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import func
from models import *
from util.distance import get_closest_station
from util.dates import sp_date
import datetime,pytz
from pprint import pprint

'''
def sp_date(date_utc):
	
	my_date = datetime.datetime.strptime(date_utc,'%Y-%m-%d %H:%M:%S')
	my_date_utc = my_date_utc = my_date.replace(tzinfo=pytz.timezone('UTC'))
	my_date_spain = my_date_spain = my_date_utc.astimezone(pytz.timezone('Europe/Madrid'))
	
	return my_date_spain.strftime('%Y-%m-%d %H:%M:%S')
'''
	
# TODO: check errors in query
def get_closest_measurement(lat,lon):
	
	app.logger.info("---> get_closest_measurement to lat=%s, lon=%s" % (lat,lon))
	
	# Get all stations with a Measurement in the last day
	recent = datetime.datetime.today() - datetime.timedelta(days=1)
	m = Measurement.query.filter(Measurement.date_created > recent).subquery('m')
	active_stations = Station.query.filter(Station.code == m.c.station)
	
	# Transform to list before using it
	# TODO Why is this needed?
	# TODO Why if there is no active station? Now we crash!!
	as_list = []
	for station in active_stations:
		as_list.append(station)
	
	#active_stations = Station.query.all()
	
	# Get the closest one
	#closest_station = get_closest_station(active_stations,lat,lon)
	
	if as_list == []:
		app.logger.error("No active station in the last 24 hours!!")
		return None
	else:
		closest_station = get_closest_station(as_list,lat,lon)
		return get_last_measurement(closest_station.code)
	
	

def get_last_measurement(station_code):
	
	app.logger.info("---> get_last_measurement() from " + station_code)
	
	data = None
	
	# Get the most recent measurement
	try:
		m = Measurement.query.filter(Measurement.station==station_code).\
		                                order_by(Measurement.date_created.desc()).first()                         
		if m != None:
			data = m.serialize 
		
		# Add station name
		data['name'] = Station.query.filter(Station.code == station_code).one().name
		
		# Convert to Spanish time
		data['date_created'] = sp_date(data['date_created'])
	
	except NoResultFound:
		data = None
	
	app.logger.debug(data)
	return data
	
	
def get_last_measurements():
	
	measurements_array = []
	
	# Get all stations with a Measurement in the last day
	recent = datetime.datetime.today() - datetime.timedelta(days=1)
	m = Measurement.query.filter(Measurement.date_created > recent).subquery('m')
	active_stations = Station.query.filter(Station.code == m.c.station)
	
	for station in active_stations:
		lm = get_last_measurement(station.code)
		lm['lat'] = float(station.lat)
		lm['lon'] = float(station.lon)
		measurements_array.append(lm)
		
	return measurements_array
	
def prueba():
	
	join_query = db.session.query(Measurement,Station).join(Station)
	
	subquery = db.session.query(
	    join_query,
	    func.rank().over(
	        order_by=join_query.c.date_created.desc(),
	        partition_by=join_query.c.code
	    ).label('rnk')
	).subquery()
	
	for i in join_query:
		print(i[0].station,i[0].date_created,i[1].name)
	
	
	