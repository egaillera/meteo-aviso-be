import os,sys
import requests
import re
from datetime import *
from decimal import *
import logging
from logging.handlers import RotatingFileHandler
from sqlalchemy.orm.exc import NoResultFound

sys.path.append(os.getcwd())

from models import *
from constants import *

logger = logging.getLogger("get_mc_data")
logger.setLevel(logging.DEBUG)
handler = RotatingFileHandler('../app/logs/get_mc_data.log',maxBytes=100000, backupCount=2)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


def print_stations(stations):

     for station in stations:
         print("Estacion codigo: " + station[0][STATION_CODE_IDX])
         print("  Fecha de la medicion: " + station[1])
         print("  Temperatura actual: " + station[0][CURRENT_TEMP_IDX])
         print("  Temperatura maxima: " + station[0][MAX_TEMP_IDX]) 
         print("  Temperatura minima: " + station[0][MIN_TEMP_IDX])
         print("  Estado: " + station[0][CURRENT_WEATHER_IDX])
         print("  Humedad actual: " + station[0][CURRENT_HUM_IDX])
         print("  Humedad maxima: " + station[0][MAX_HUM_IDX]) 
         print("  Humedad minima: " + station[0][MIN_HUM_IDX])
         print("  Presion actual: " + station[0][CURRENT_PRES_IDX])
         print("  Presion maxima: " + station[0][MAX_PRES_IDX]) 
         print("  Presion minima: " + station[0][MIN_PRES_IDX])
         print("  Velocidad del viento: " + station[0][CURRENT_WIND_SPEED_IDX])
         print("  Racha maxima: " + station[0][MAX_WIND_SPEED_IDX]) 
         print("  Direccion del viento: " + station[0][CURRENT_WIND_DIRECTION_IDX])
         print("  Precipitacion: " + station[0][RAINFALL_IDX])
         print("  Nombre de la estacion: " + station[0][STATION_NAME_IDX])
         print("  Localizacion: (" + station[0][LAT_IDX] + ", " + station[0][LON_IDX] + ")")


def get_mc_data():
    
    # Request Meteoclimatic data
    rsp = requests.get(METEOCLIMATIC_URL)
    resp = rsp.content.decode('utf8')
    
    #print(resp)

    logger.info("Loading Meteoclimatic stations from %s",METEOCLIMATIC_URL)
    if rsp.status_code == 200:

        meteo_data = re.findall(REGEX_METEO_DATA,resp)
        time_data = re.findall(REGEX_UPDATE_TIME_DATA,resp)
        time_data_conv = [datetime.datetime.strptime(x, MC_DATE_FORMAT) for x in time_data]

        # Merge measurements with time and date
        all_data = list(zip(meteo_data,time_data_conv))

    else:
        logger.error('Error downloading data from meteoclimatic.com')
        all_data = None

    return all_data
	
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
		                  lon=Decimal(measurement[0][LON_IDX]))
		db.session.add(station)
		db.session.commit()
		
	# Insert the measurement
	logger.info('Inserting measurement in station %s' % measurement[0][STATION_CODE_IDX])
	new_measurement = Measurement(date_created = measurement[1],
	         weather_status = measurement[0][CURRENT_WEATHER_IDX],
	         current_temp = Decimal(measurement[0][CURRENT_TEMP_IDX].replace(',','.')),
	         max_temp = Decimal(measurement[0][MAX_TEMP_IDX].replace(',','.')),
	         min_temp = Decimal(measurement[0][MIN_TEMP_IDX].replace(',','.')),
	         current_hum = Decimal(measurement[0][CURRENT_HUM_IDX].replace(',','.')),
	         max_hum = Decimal(measurement[0][MAX_HUM_IDX].replace(',','.')),
	         min_hum = Decimal(measurement[0][MIN_HUM_IDX].replace(',','.')),
	         current_pres = Decimal(measurement[0][CURRENT_PRES_IDX].replace(',','.')),
	         max_pres = Decimal(measurement[0][MAX_PRES_IDX].replace(',','.')),
	         min_pres = Decimal(measurement[0][MIN_PRES_IDX].replace(',','.')),
	         wind_speed = Decimal(measurement[0][CURRENT_WIND_SPEED_IDX].replace(',','.')),
	         max_gust = Decimal(measurement[0][MAX_WIND_SPEED_IDX].replace(',','.')),
	         wind_direction = int(measurement[0][CURRENT_WIND_DIRECTION_IDX]),
	         rainfall = Decimal(measurement[0][RAINFALL_IDX].replace(',','.')),
	         station = measurement[0][STATION_CODE_IDX])
	db.session.add(new_measurement)
	db.session.commit()


def clean_old_data():
	
	too_old = datetime.datetime.today() - datetime.timedelta(days=DAYS_TO_KEEP_MEASUREMENTS)
	Measurement.query.filter(Measurement.date_created < too_old).delete()
	db.session.commit()	

def main():

    # Request Meteoclimatic data
    mc_data = get_mc_data()
    #print_stations(mc_data)


    '''logger.info('Inserting measurements ..')
    for measurement in mc_data:
        station = insert_measurement(measurement)
        #clean_station(station)
    db.session.commit()
    logger.info('Finished inserting measurements')

    # Remove old measurements
    logger.info("Removing data older than %s days" % DAYS_TO_KEEP_MEASUREMENTS)
    clean_old_data()'''

if __name__ == '__main__':
    main()
