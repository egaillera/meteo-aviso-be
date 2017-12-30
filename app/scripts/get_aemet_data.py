import requests
import json
import datetime

from decimal import *
from constants import *


# To supress InsecureRequestWarning
requests.packages.urllib3.disable_warnings()

querystring = {"api_key": aemet_api_key}

headers = {
    'cache-control': "no-cache"
    }
		
def get_aemet_data():
		
	measurement_list=[]
	last_measurement_dict = {}
	
	json_response = json.loads(requests.request("GET", aemet_url, headers=headers, params=querystring,verify=False).text)
	answer_url = json_response['datos']
	
	obs_json = json.loads(requests.request("GET", answer_url, headers=headers, verify=False).text)
	for obs in obs_json:
		
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
	print(aemet_data)
	

if __name__ == '__main__':
	main()

