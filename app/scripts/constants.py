# Number of days to keep the measurements
DAYS_TO_KEEP_MEASUREMENTS = 3


# Constants for Meteoclimatic connection
REGEX_METEO_DATA = u'\[\[<BEGIN:[0-9A-Z]+:DATA>\]\]\n\[\[<([0-9A-Z]+);\(([\-,0-9]+);([\-,0-9]+);([\-,0-9]+);([a-z]+)\);\(([\-,0-9]+);([\-,0-9]+);([\-,0-9]+)\);\(([\-,0-9]+);([\-,0-9]+);([\-,0-9]+)\);\(([\-,0-9]+);([\-,0-9]+);([\-0-9]+)\);\(([-,0-9]+)\);([\/\-\(\)\.;\'&\#\sA-Za-z0-9]+)>\]\]\n\[\[<END:ES[0-9A-Z]+:DATA>\]\]\n-->\n   </description>\n   <georss:point>([\-0-9\.]+) ([\-0-9\.]+)</georss:point>'
REGEX_UPDATE_TIME_DATA = u'Actualizado: ([\-0-9\w\s:]+) UTC</li>'

METEOCLIMATIC_URL = 'http://meteoclimatic.com/feed/rss/ES' 

MC_DATE_FORMAT = u'%d-%m-%Y %H:%M'

# Fields in Meteoclimatic structure (used as well for AEMET)
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

# Fields of the AEMET stations to fill in MeteoAviso station model; order is relevant becasue for 
# each field there is a defined postion in the array
FIELDS_TO_FILL = {'idema': STATION_CODE_IDX,'ta': CURRENT_TEMP_IDX,'lat': LAT_IDX,'lon': LON_IDX,\
                  'ubi': STATION_NAME_IDX,'prec': RAINFALL_IDX, 'vv': CURRENT_WIND_SPEED_IDX, 
                  'vmax': MAX_WIND_SPEED_IDX, 'dv': CURRENT_WIND_DIRECTION_IDX, 'hr': CURRENT_HUM_IDX,
                  'pres': CURRENT_PRES_IDX}

# Constants for AEMET connection
aemet_url = "https://opendata.aemet.es/opendata/api/observacion/convencional/todas"
aemet_api_key = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJlZ2FpbGxlcmFAZ21haWwuY29tIiwianRpIjoiYmVhOTI4ZmEtMmM5Yy00ZDU4LWEzYjYtYWI1NDgzYWFiODRmIiwiaXNzIjoiQUVNRVQiLCJpYXQiOjE1MTI3NTAzNDMsInVzZXJJZCI6ImJlYTkyOGZhLTJjOWMtNGQ1OC1hM2I2LWFiNTQ4M2FhYjg0ZiIsInJvbGUiOiIifQ.EDSDXoL32Ng2AzIKEqUj0Eah5MHCIRc6n5WAh6lPDKE"

