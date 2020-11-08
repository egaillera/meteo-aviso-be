import os
import json
import re

from app import app
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import func
from models import *
from util.distance import get_closest_station
from util.dates import sp_date,sp_date_str
import datetime,pytz
from pprint import pprint


	
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
		
		# Add station name and coordinates
		st = Station.query.filter(Station.code == station_code).one()
		data['name'] = st.name
		data['code'] = st.code
		data['lat'] = float(st.lat)
		data['lon'] = float(st.lon)
		
		# Convert to Spanish time
		data['date_created'] = sp_date(data['date_created'])
		
	
	except NoResultFound:
		data = None
	
	app.logger.debug(data)
	return data
	

'''
Returns the last measurement for each station. A join with Sation is also needed 
to add station coordinates.

The SQL query to get the last measurement, using window functions:
select * from (
   select *,rank() over (partition by station order by date_created desc) rank 
   from measurement order by station) subquery 
where rank = 1;
'''	
def get_last_measurements(use_cache=True):
	
	app.logger.info("---> get_last_measurements()")
	
	measurements_array = []

	# Check if a cache file exists to avoid querying the database
	# TODO: put cache file path in ONE place
	if os.path.isfile("/shared_data/last_measurements.json") and use_cache:
		with open("/shared_data/last_measurements.json") as measurements_file:
			app.logger.debug("Returning cache data")
			return json.load(measurements_file)
		
	app.logger.debug("Executing subquery")
	# Subquery to get all measurements ranked by station based on date. Rank 1 is the most recent	
	subquery = db.session.query(
	    Measurement,
	    func.rank().over(
	        order_by=Measurement.date_created.desc(),
	        partition_by=Measurement.station
	    ).label('rnk')
	).subquery()
	app.logger.debug("End of subquery execution")
	
	# Query to get the first ranked measurment (most recent), and then joined with Station
	# to extract readable name and coordinates
	app.logger.debug("Executing JOIN")
	query = db.session.query(subquery,Station).filter(subquery.c.rnk==1).filter(Station.code==subquery.c.station)
	app.logger.debug("End of JOIN execution")
	
	# Result is a tuple with a Station object in the 11th position. Create a full 
	# measurement object with the station name and coordinates
	for ms in query:
		full_ms = {}
		
		full_ms['name']= ms[11].name
		full_ms['lat'] = float(ms[11].lat)
		full_ms['lon'] = float(ms[11].lon)
		
		# Convert date to Spanish Time
		full_ms['date_created'] = sp_date_str(ms.date_created)
		full_ms['current_temp'] = float(ms.current_temp)
		full_ms['current_hum'] = float(ms.current_hum)
		full_ms['current_pres'] = float(ms.current_pres)
		full_ms['wind_speed'] = float(ms.current_pres)
		full_ms['max_gust'] = float(ms.max_gust)
		full_ms['wind_direction'] = float(ms.wind_direction)
		full_ms['rainfall'] = float(ms.rainfall)
		full_ms['code'] = ms.station
		
		measurements_array.append(full_ms)
	
	app.logger.info("Returning %d measurements" % len(measurements_array))	
	return measurements_array
	
	
'''
Returns the last measurement for a city. Look for this city 
in all the stations, and return the first measurement found.
'''	
def get_last_measurement_by_city(city):
	
	app.logger.info("---> get_last_measurement_by_city(%s)" % city)
	
	ms_list = get_last_measurements()
	
	pattern = '^' + city.lower() + '[ /-]|^' + city.lower() + '$'
	app.logger.info("Appliying pattern %s over %s" %(pattern,city.lower()))
	
	for ms in ms_list:
		if re.match(pattern,ms['name'].lower()):
			return ms
			
	return None

	