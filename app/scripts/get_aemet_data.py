import requests
import json
import datetime
from util.dates import *

from decimal import *
from pprint import pprint


# To supress InsecureRequestWarning
requests.packages.urllib3.disable_warnings()

querystring = {"api_key": aemet_api_key}

headers = {
    'cache-control': "no-cache"
    }

'''
Receives an sorted list of measurements by date, and returns the 
same list with the accumulated rainfall for the current day
'''
def calculate_rainfall(obs_list):
	
	acc_rainfall = 0
	
	for ob in obs_list:
		if 'prec' not in ob.keys():
			ob['prec'] = 0.0
			
		if is_today(ob['fint']):
			acc_rainfall += ob['prec']
			ob['prec'] = acc_rainfall
	
	return obs_list

'''
Get all observations as a list, and a return a dictionary:

- Keys: station codes
- Values: list of dicts, sorted by date. Each element is a measurement.
          Note that the station code is replicated in each measurement

{'8025': [{'fint': '2018-09-23T06:00:00', 'idema': '8025' , ....},
          {'fint': '2018-09-23T07:00:00', 'idema': '8025' , ....},
          {'fint': '2018-09-24T13:00:00', 'idema': '8025' , ....}],
 '8057C': [{'fint': '2018-08-23T07:00:00', 'idema': '8057C' , ....},
           {'fint': '2018-09-23T05:00:00', 'idema': '8057C' , ....},
           {'fint': '2018-09-23T08:00:00', 'idema': '8057C' , ....}]}
	
'''
def order_aemet_data(obs):
	
	ordered_data = {}
	
	# Create a dict item per station to store all measurements
	for ob in obs:
		if ob['idema'] not in ordered_data.keys():
			ordered_data[ob['idema']] = []
		ordered_data[ob['idema']].append(ob)
	
	# Order by date the measurements per each station
	for station in ordered_data.keys():
		ordered_data[station].sort(key=lambda k: as_date(k['fint']).timestamp())
		ordered_data[station] = calculate_rainfall(ordered_data[station])	
					
	return ordered_data

'''
Get all observations and returns the last one per station. Change
the rainfall field to sum the precipitation along the day
'''
def process_aemet_data(obs):
	
	obs_processed = {}
	
	for ob in obs:
		# If an observation for this station already exists but this observation is more recent, 
		# substitute it and increase the rainfall field if it belongs to present day
		# to calculate total rainfall for the current day
		if ob['idema'] in obs_processed.keys() \
		               and (as_date(ob['fint']) > as_date(obs_processed[ob['idema']]['fint'])):
			if 'prec' in ob.keys():
				daily_rainfall = obs_processed[ob['idema']]['prec']
				if is_today(obs_processed[ob['idema']]['fint']):
					daily_rainfall += ob['prec']
			obs_processed[ob['idema']] = ob
			obs_processed[ob['idema']]['prec'] = daily_rainfall
		else:
			obs_processed[ob['idema']] = ob
			# Make sure the field 'prec' exists when creating the
			# first entry for each station
			if 'prec' not in ob.keys():
				obs_processed[ob['idema']]['prec'] = 0.0
	
	# Return values as a list
	obs_list = []
	for o in obs_processed.values():
		obs_list.append(o)
		
	return obs_list
	
	

def get_aemet_data():
		
	measurement_list=[]
	last_measurement_dict = {}
	
	json_response = json.loads(requests.request("GET", aemet_url, headers=headers, params=querystring,verify=False).text)
	answer_url = json_response['datos']
	
	obs_json = json.loads(requests.request("GET", answer_url, headers=headers, verify=False).text)
	o_list = process_aemet_data(obs_json)
	for obs in o_list:
		
		# Initialize a measurement with TOTAL_FIELDS positions with -999 default value
		measurement_data = ["-999"]*TOTAL_FIELDS
		measurement_time = datetime.datetime.strptime(obs['fint'],'%Y-%m-%dT%H:%M:%S')
		
		for field in FIELDS_TO_FILL.keys():
			if field in obs.keys():
				# To be coherent with Meteoclimatic, we put each field in fixed position 
			    # of the array given by the indexes	and as a string
				measurement_data[FIELDS_TO_FILL[field]] = str(obs[field])		
		
		# Because of Meteoclimatic limitations, each measurement is a tuple with two fields: 
		#  - measurement_data, with all the measurement values
		#  - measurement_time: time of the measurement
		measurement = (measurement_data,measurement_time)
		
		# Before adding the measurement, check if it's the last one. So we need to keep 
		# track about the last measurement in each station
		if obs['idema'] not in last_measurement_dict.keys():
			last_measurement_dict[obs['idema']] = measurement
		else:
			if measurement_time > last_measurement_dict[obs['idema']][1]:
				last_measurement_dict[obs['idema']] = measurement
				
	for ms in last_measurement_dict.keys():
		measurement_list.append(last_measurement_dict[ms])
		
	#for ms in measurement_list:
	#	print(ms)
		
	return measurement_list
			
def main():
	
	aemet_data = get_aemet_data()
	pprint(aemet_data)
	

if __name__ == '__main__':
	main()

