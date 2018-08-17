import os,sys
import requests
import re
from datetime import *
from decimal import *
import logging
from logging.handlers import RotatingFileHandler
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import exc

sys.path.append(os.getcwd())

from models import *

from get_mc_data import get_mc_data
from get_aemet_data import get_aemet_data
from constants import *
from util.distance import *
from notifier import *

logger = logging.getLogger("collect_data")
logger.setLevel(logging.DEBUG)
handler = RotatingFileHandler('../app/logs/collect_data.log',maxBytes=100000, backupCount=2)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


def find_new_stations(all_stations,measurements):
	
	# List of station codes
	st_codes = [st.code for st in all_stations]
	
	# Check if this station is already in the DB
	for measurement in measurements:
		if measurement[0][STATION_CODE_IDX] not in st_codes:
			print("Not found '%s'" % measurement[0][STATION_CODE_IDX])
			create_station_from_measurement(measurement)
			
def create_station_from_measurement(measurement):
	
	logger.info('Station ' + measurement[0][STATION_CODE_IDX] + ' not found')
	logger.info('Creating Station ' + measurement[0][STATION_CODE_IDX])
	
	try:
		station = Station(code=measurement[0][STATION_CODE_IDX],
		                  name=measurement[0][STATION_NAME_IDX],
		                  lat=Decimal(measurement[0][LAT_IDX]),
		                  lon=Decimal(measurement[0][LON_IDX]),
		                  prov=get_province(measurement[0][STATION_NAME_IDX],
		                  measurement[0][STATION_CODE_IDX]))
		
		db.session.add(station)
		db.session.commit()
		logger.info('Created Station ' + measurement[0][STATION_CODE_IDX])
		
	except exc.IntegrityError:
		logger.info('Trying to insert a duplicated station .. ignoring it')
		db.session.rollback()
		
	
def insert_measurement(measurement):
	
	# Insert one measurement
	try:
		logger.info('Inserting measurement in station %s' % measurement[0][STATION_CODE_IDX])
		new_measurement = Measurement(date_created = measurement[1],
	         current_temp = Decimal(measurement[0][CURRENT_TEMP_IDX].replace(',','.')),
	         current_hum = Decimal(measurement[0][CURRENT_HUM_IDX].replace(',','.')),
	         current_pres = Decimal(measurement[0][CURRENT_PRES_IDX].replace(',','.')),
	         wind_speed = Decimal(measurement[0][CURRENT_WIND_SPEED_IDX].replace(',','.')),
	         max_gust = Decimal(measurement[0][MAX_WIND_SPEED_IDX].replace(',','.')),
	         wind_direction = Decimal(measurement[0][CURRENT_WIND_DIRECTION_IDX].replace(',','.')),
	         rainfall = Decimal(measurement[0][RAINFALL_IDX].replace(',','.')),
	         station = measurement[0][STATION_CODE_IDX])
		db.session.add(new_measurement)
		db.session.commit()
		check_measurement(new_measurement)
	except exc.IntegrityError:
		logger.info('Trying to insert a duplicated measurement .. ignoring it')
		db.session.rollback()
		
def insert_all(measurements):
	
	# Insert all measurements in bulk mode
	logger.info("Inserting all measurements bulk mode")
	
	# Create a list of Measurements
	measurement_list = [Measurement(date_created = measurement[1],
	                    current_temp = Decimal(measurement[0][CURRENT_TEMP_IDX].replace(',','.')),
	                    current_hum = Decimal(measurement[0][CURRENT_HUM_IDX].replace(',','.')),
	                    current_pres = Decimal(measurement[0][CURRENT_PRES_IDX].replace(',','.')),
	                    wind_speed = Decimal(measurement[0][CURRENT_WIND_SPEED_IDX].replace(',','.')),
	                    max_gust = Decimal(measurement[0][MAX_WIND_SPEED_IDX].replace(',','.')),
	                    wind_direction = Decimal(measurement[0][CURRENT_WIND_DIRECTION_IDX].replace(',','.')),
	                    rainfall = Decimal(measurement[0][RAINFALL_IDX].replace(',','.')),
	                    station = measurement[0][STATION_CODE_IDX]) for measurement in measurements]
	
	try:
		#logger.debug(measurement_list)
		db.session.bulk_save_objects(measurement_list)
		db.session.commit()
	except exc.IntegrityError:
		logger.info('Trying to insert a duplicated measurement .. ignoring it')
		
def clean_old_data():
	
	too_old = datetime.datetime.today() - datetime.timedelta(days=DAYS_TO_KEEP_MEASUREMENTS)
	Measurement.query.filter(Measurement.date_created < too_old).delete()
	db.session.commit()	

def main():
	
	# Get all stations from DB 
	all_stations = Station.query.all()
	
	# Request AEMET and Meteoclimatic data
	if "METEOCLIMATIC" in os.environ:
		mc_data = get_mc_data()
		find_new_stations(all_stations,mc_data)
		logger.info('Inserting Meteoclimatic measurements ..')
		insert_all(mc_data)
		logger.info('Finished inserting Meteoclimatic measurements')
		
	aemet_data = get_aemet_data()
	find_new_stations(all_stations,aemet_data)
	logger.info('Inserting AEMET measurements ..')
	#insert_all(aemet_data)
	for measurement in aemet_data:
		insert_measurement(measurement)
	logger.info('Finished inserting AEMET measurements')
	
	db.session.commit()
	
	# Remove old measurements
	logger.info("Removing data older than %s days" % DAYS_TO_KEEP_MEASUREMENTS)
	clean_old_data()
	

if __name__ == '__main__':
	main()
