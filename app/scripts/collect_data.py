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

logger = logging.getLogger("collect_data")
logger.setLevel(logging.DEBUG)
handler = RotatingFileHandler('../app/logs/collect_data.log',maxBytes=100000, backupCount=2)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

		
def insert_measurement(measurement):
	
	# Search the station linked to the mesasuremnt in the database
	try:
		logger.info("searching station with code " + measurement[0][STATION_CODE_IDX])
		station = Station.query.filter(Station.code == measurement[0][STATION_CODE_IDX]).one()
	except NoResultFound:
		# If the station does not exist, create it
		logger.info('Station ' + measurement[0][STATION_CODE_IDX] + ' not found')
		logger.info('Creating Station ' + measurement[0][STATION_CODE_IDX])
		
		station = Station(code=measurement[0][STATION_CODE_IDX],
		                  name=measurement[0][STATION_NAME_IDX],
		                  lat=Decimal(measurement[0][LAT_IDX]),
		                  lon=Decimal(measurement[0][LON_IDX]),
		                  prov=get_province(measurement[0][STATION_NAME_IDX])
		                  )
		db.session.add(station)
		db.session.commit()
		logger.info('Created Station ' + measurement[0][STATION_CODE_IDX])
			
	
	# Insert the measurement
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
	except exc.IntegrityError:
		logger.info('Trying to insert a duplicated measaurment .. ignoring it')
		db.session.rollback()


def clean_old_data():
	
	too_old = datetime.datetime.today() - datetime.timedelta(days=DAYS_TO_KEEP_MEASUREMENTS)
	Measurement.query.filter(Measurement.date_created < too_old).delete()
	db.session.commit()	

def main():
	
	# Request AEMET and Meteoclimatic data
	if "METEOCLIMATIC" in os.environ:
		mc_data = get_mc_data()
		logger.info('Inserting Meteoclimatic measurements ..')
		for measurement in mc_data:
			station = insert_measurement(measurement)
		logger.info('Finished inserting Meteoclimatic measurements')
		
	aemet_data = get_aemet_data()
	logger.info('Inserting AEMET measurements ..')
	for measurement in aemet_data:
		station = insert_measurement(measurement)
	logger.info('Finished inserting AEMET measurements')
	
	db.session.commit()
	
	# Remove old measurements
	logger.info("Removing data older than %s days" % DAYS_TO_KEEP_MEASUREMENTS)
	clean_old_data()

if __name__ == '__main__':
	main()
