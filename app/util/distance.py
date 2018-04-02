from models import Station
import numpy
import scipy.spatial
import datetime
from geopy.geocoders import Nominatim
import csv
import editdistance



def get_closest_station(active_stations,lat,lon):

    coord = []
    for station in active_stations:
        coord.append((station.lat,station.lon))
    np_coord = numpy.array(coord)
    mytree = scipy.spatial.cKDTree(np_coord)

    point = numpy.array([[float(lat),float(lon)]])
    dist,index = mytree.query(point)

    return active_stations[index[0]]


def load_cities():
	
	cities_dict = {}
	reader = csv.reader(open('util/cities.csv','r'),delimiter=';')
	for row in reader:
		cities_dict[row[0].lower()] = row[1]
		
	return cities_dict
	
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
		cit_dict = load_cities()
		return int(cit_dict[min(cit_dict.keys(), key=lambda v: editdistance.eval(city.lower(),v))])
	

	
	


		
		
	

