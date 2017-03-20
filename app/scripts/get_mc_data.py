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

logger = logging.getLogger("get_mc_data")
logger.setLevel(logging.DEBUG)
handler = RotatingFileHandler('../app/logs/get_mc_data.log',maxBytes=10000, backupCount=1)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Constants
REGEX_METEO_DATA = u'\[\[<BEGIN:[0-9A-Z]+:DATA>\]\]\n\[\[<([0-9A-Z]+);\(([\-,0-9]+);([\-,0-9]+);([\-,0-9]+);([a-z]+)\);\(([\-,0-9]+);([\-,0-9]+);([\-,0-9]+)\);\(([\-,0-9]+);([\-,0-9]+);([\-,0-9]+)\);\(([\-,0-9]+);([\-,0-9]+);([\-0-9]+)\);\(([-,0-9]+)\);([\/\-\(\)\.;\'&\#\sA-Za-z0-9]+)>\]\]\n\[\[<END:ES[0-9A-Z]+:DATA>\]\]\n-->\n   </description>\n   <georss:point>([\-0-9\.]+) ([\-0-9\.]+)</georss:point>'
REGEX_UPDATE_TIME_DATA = u'Actualizado: ([\-0-9\w\s:]+) UTC</li>'

METEOCLIMATIC_URL = 'http://meteoclimatic.com/feed/rss/ES' 

MC_DATE_FORMAT = u'%d-%m-%Y %H:%M'

MAX_MEASUREMENTS = 100

STATION_CODE_IDX = 0
CURRENT_TEMP_IDX = 1
MAX_TEMP_IDX = 2
MIN_TEMP_IDX = 3 
CURRENT_WEATHER_IDX = 4
CURRENT_HUM_IDX = 5
MAX_HUM_IDX = 6
MIN_HUM_IDX = 7 
CURRENT_PRES_IDX = 8
MAX_PRES_IDX = 9
MIN_PRES_IDX = 10
CURRENT_WIND_SPEED_IDX = 11
MAX_WIND_SPEED_IDX = 12
CURRENT_WIND_DIRECTION_IDX = 13
RAINFALL_IDX = 14
STATION_NAME_IDX = 15
LAT_IDX = 16
LON_IDX = 17

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

        # Merge measurements with time and date
        all_data = zip(meteo_data,time_data)

    else:
        logger.error('Error downloading data from meteoclimatic.com')
        all_data = None

    return all_data
	
def insert_measurement(measurement):
	
	# Search the station linked to the mesasuremnt in the database
	try:
		print("searching station with code " + measurement[0][STATION_CODE_IDX])
		station = Station.query.filter(Station.code == measurement[0][STATION_CODE_IDX]).one()
	except NoResultFound:
		# If the station does not exist, create it
		logger.info('get_mc_data: station ' + measurement[0][STATION_CODE_IDX] + ' not found')
		logger.info('get_mc_data: creating Station ' + measurement[0][STATION_CODE_IDX])
		station = Station(code=measurement[0][STATION_CODE_IDX],
		                  name=measurement[0][STATION_NAME_IDX],
		                  lat=Decimal(measurement[0][LAT_IDX]),
		                  lon=Decimal(measurement[0][LON_IDX]))
		db.session.add(station)
		db.session.commit()
		
	# Insert the measurement
	new_measurement = Measurement(date_created = datetime.datetime.strptime(measurement[1], MC_DATE_FORMAT),
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

	

def main():

    # Request Meteoclimatic data
    mc_data = get_mc_data()
    #print_stations(mc_data)

    logger.info('Inserting measurements ..')
    for measurement in mc_data:
        station = insert_measurement(measurement)
        #clean_station(station)
    db.session.commit()

if __name__ == '__main__':
    main()
