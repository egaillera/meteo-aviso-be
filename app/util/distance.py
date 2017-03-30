from models import Station,Measurement
import numpy
import scipy.spatial
import datetime


def get_closest_station(lat,lon):

    # Get all stations that took a measurement today 
    active_stations = Station.query.all()

    coord = []
    for station in active_stations:
        coord.append((station.lat,station.lon))
    np_coord = numpy.array(coord)
    mytree = scipy.spatial.cKDTree(np_coord)

    point = numpy.array([[float(lat),float(lon)]])
    dist,index = mytree.query(point)

    return active_stations[index[0]].name

