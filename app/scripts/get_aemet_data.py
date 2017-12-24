import requests
import json
import datetime

TOTAL_FIELDS = 18

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

url = "https://opendata.aemet.es/opendata/api/maestro/municipios"
url_estaciones = "https://opendata.aemet.es/opendata/api/valores/climatologicos/inventarioestaciones/todasestaciones/"
url_observaciones = "https://opendata.aemet.es/opendata/api/observacion/convencional/todas"

# To supress InsecureRequestWarning
requests.packages.urllib3.disable_warnings()


querystring = {"api_key":"eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJlZ2FpbGxlcmFAZ21haWwuY29tIiwianRpIjoiYmVhOTI4ZmEtMmM5Yy00ZDU4LWEzYjYtYWI1NDgzYWFiODRmIiwiaXNzIjoiQUVNRVQiLCJpYXQiOjE1MTI3NTAzNDMsInVzZXJJZCI6ImJlYTkyOGZhLTJjOWMtNGQ1OC1hM2I2LWFiNTQ4M2FhYjg0ZiIsInJvbGUiOiIifQ.EDSDXoL32Ng2AzIKEqUj0Eah5MHCIRc6n5WAh6lPDKE"}

headers = {
    'cache-control': "no-cache"
    }

# Fields of the AEMET stations to fill in MeteoAviso station model; order is relevant so for each field
# there is a definied postion in the array
FIELDS_TO_FILL = {'idema':STATION_CODE_IDX,'ta':CURRENT_TEMP_IDX,'lat':LAT_IDX,'lon':LON_IDX,'ubi':STATION_NAME_IDX}

def get_aemet_data():
		
	measurement_list=[]
	last_measurement_dict = {}
	
	json_response = json.loads(requests.request("GET", url_observaciones, headers=headers, params=querystring,verify=False).text)
	answer_url = json_response['datos']
	
	obs_json = json.loads(requests.request("GET", answer_url, headers=headers, verify=False).text)
	for obs in obs_json:
		
		# Initialize a measurement with TOTAL_FIELDS positions
		measurement_data = [None]*TOTAL_FIELDS
		measurement_time = datetime.datetime.strptime(obs['fint'],'%Y-%m-%dT%H:%M:%S')
		
		for field in FIELDS_TO_FILL.keys():
			if field in obs.keys():
				# To be coherent with Meteoclimatic, we put each field in fixed position 
			    # of the array given by the indexes	
				measurement_data[FIELDS_TO_FILL[field]] = obs[field]		
		
		# Because of Meteoclimatic limitations, each measurement is a tuple with two fields: 
		#  - measurement_data, with all the measurement values
		#  - measurement_time: time of the measurement
		measurement = (measurement_data,measurement_time)
		
		# Before adding the measurement, check if it's the last one. So need to keep 
		# track about the last measurement in each station
		if obs['idema'] not in last_measurement_dict.keys():
			last_measurement_dict[obs['idema']] = measurement
		else:
			if measurement_time > last_measurement_dict[obs['idema']][1]:
				last_measurement_dict[obs['idema']] = measurement
				
	for ms in last_measurement_dict.keys():
		measurement_list.append(last_measurement_dict[ms])
		
	for ms in measurement_list:
		print(ms)
		
	

def main():
	
	get_aemet_data()

if __name__ == '__main__':
	main()

