import logging
from logging.handlers import RotatingFileHandler

logger = logging.getLogger("notifier_data")
logger.setLevel(logging.DEBUG)
handler = RotatingFileHandler('../app/logs/notifier_data.log',maxBytes=100000, backupCount=2)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


'''
Check if there are notifications rules for an station. For the moment only 
"rainfall" and "curr_temp" are supported

TODO: for the moment the behaviour is simulated, but the database should be consulted. 
      Is it better to keep the table in memory?

Returns a dictionary with the information:

{ "st_code":'8059C',
          "rules": [
            {
              "user_id":"egaillera@gmail.com",
              "conditions": [
                        {"dimension":"rainfall","quantifier":">","value":0},
                        {"dimension":"curr_temp","quantifier":"<","value":0},
                        {"dimension":"curr_temp","quantifier":">","value":32},
                       ]
            },
            {
              "user_id":"eggisbert@gmail.com",
              "conditions": [
                        {"dimension":"rainfall","quantifier":">","value":5},
                        {"dimension":"curr_temp","quantifier":"<","value":-5},
                        {"dimension":"curr_temp","quantifier":">","value":35},
                       ]
            },
          ]
      }
'''
def get_notif_rules(station_code):
	
	logger.debug("--> get_notif_rules() for station %s",station_code)
	rules = None
	
	if station_code == '8059C':
		rules = { "st_code":'8059C',
	              "users": [
	                {
	                  "user_id":"egaillera@gmail.com",
	                  "conditions": [
	                            {"dimension":"rainfall","quantifier":">","value":0},
	                            {"dimension":"curr_temp","quantifier":"<","value":0},
	                            {"dimension":"curr_temp","quantifier":">","value":32},
	                           ]
	                },
	                {
	                  "user_id":"eggisbert@gmail.com",
	                  "conditions": [
	                            {"dimension":"rainfall","quantifier":">","value":5},
	                            {"dimension":"curr_temp","quantifier":"<","value":-5},
	                            {"dimension":"curr_temp","quantifier":">","value":35},
	                           ]
	                },
	              ]
	          }
	
	logger.debug("Rules returned: %s",str(rules))
	return rules
	

'''
Check if a measurement should trigger a notification to an end user
'''
def check_measurement(measurement):
	
	logger.debug("---> check_measurement() for station %s" % measurement.station)
	rules = get_notif_rules(measurement.station)
	if rules != None:
		for user in rules['users']:
			logger.debug("Conditions %s for user %s" % (user['conditions'],user['user_id']))
	
