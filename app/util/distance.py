from app import app
from models import Station
import numpy
import scipy.spatial
import datetime
from geopy.geocoders import Nominatim
import csv
import editdistance
import unidecode
from util.cities import *

def get_closest_station(active_stations,lat,lon):
	
	app.logger.debug("---> get_closest_station() to lat=%s, lon=%s" % (lat,lon))
	
	coord = []
	
	for station in active_stations:
		coord.append((station.lat,station.lon))
		
	np_coord = numpy.array(coord)
	mytree = scipy.spatial.cKDTree(np_coord)
	point = numpy.array([[float(lat),float(lon)]])
	dist,index = mytree.query(point)
	
	app.logger.debug("Closest station: %s" % active_stations[index[0]])
	return active_stations[index[0]]


'''
Usually, real name of city is at the beginning, before '(', '-' or '/'.

Examples:

  LA OLIVA (CARRETERA DEL COTILLO)
  MAZARRÓN/LAS TORRES
  SAN BARTOLOME TIRAJANA-LOMO PEDRO ALFONSO

'''
def clean_name(city):

	real_name = city.replace('  ','-').replace('(','-').replace('/','-').rstrip().lower().split('-')

	return unidecode.unidecode(real_name[0])


'''
Returns the digits that identify Spanish province (8 for Barcelona, 28 for Madrid, ...)
as a integer
'''
def get_province(city,code):
	
	# If code is like ESPVA0300000003802E (Meteoclimatic), province is in position 5
	if len(code) == 19 and code[0:2] == 'ES':
		return int(code[5:7])
	else:
		# If it's AEMET station, try to find the most similar name in the dict
		return cit_dict[min(cit_dict.keys(), key=lambda v: editdistance.eval(clean_name(city),v))]
	

	
	


		
		
	

