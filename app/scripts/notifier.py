import logging
from logging.handlers import RotatingFileHandler
import operator

from models import *
from apns3 import APNs, Frame, Payload

logger = logging.getLogger("notifier_data")
logger.setLevel(logging.INFO)
handler = RotatingFileHandler('../app/logs/notifier_data.log',maxBytes=100000, backupCount=2)
formatter = logging.Formatter('%(asctime)s - [%(filename)s:%(lineno)s - %(funcName)20s()] - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Dictionary to work with logical operators as strings
ops = {">":operator.gt,"<":operator.lt}

# Dictionary compose text for user
notif_texts_format = {"current_temp":{">":"La temperatura en %s ha superado los %s grados",
                         "<":"La temperatura en %s está por debajo de los %s grados"},
                      "rainfall":{">":"La precipitacion en %s ha superado los %s litros",
				          "<":"La precipitacion en %s está por debajo de los %s litros"}}
         
         
'''
Send notifications according to the condition matched. A understandable 
message for humans should be sent
    Args:
        user_id: e-mail address of the user to be notified
        st_code: station code
        condition: condition satisfied

    Returns:
        The return value. True for success, False otherwise.
  
'''
def send_notification(user_id,st_code,condition):
	
	logger.info("User to notify: %s" % user_id)
	
	# Get the real name of the station
	station_name = Station.query.filter(Station.code == st_code).one().name
	logger.info("Station to be notified about: %s" % station_name)
	
	# Get the notification token from the users table
	token_hex = User.query.filter(User.email == user_id).one().notif_token
	logger.info("Notification token: %s" % token_hex)
	
	# Compose the text
	notif_text = notif_texts_format[condition['dimension']][condition['quantifier']] % \
	             (station_name,condition['value'])
	logger.info("Sending notification: %s" % notif_text)
	
	apns = APNs(use_sandbox=True, cert_file='scripts/MeteoAvisoPushCert.pem')
	payload = Payload(alert=notif_text, sound="default", badge=0)
	apns.gateway_server.send_notification(token_hex, payload)
	
	logger.info("Notification sent!")
	

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
                        {"dimension":"current_temp","quantifier":"<","value":0},
                        {"dimension":"current_temp","quantifier":">","value":32},
                       ]
            },
            {
              "user_id":"eggisbert@gmail.com",
              "conditions": [
                        {"dimension":"rainfall","quantifier":">","value":5},
                        {"dimension":"current_temp","quantifier":"<","value":-5},
                        {"dimension":"current_temp","quantifier":">","value":35},
                       ]
            },
          ]
      }
'''
def get_notif_rules(station_code):
	
	logger.debug("--> get_notif_rules() for station %s",station_code)
	rules = None
	
	if station_code == '8057C':
		rules = { "st_code":'8057C',
	              "users": [
	                {
	                  "user_id":"egaillera@gmail.com",
	                  "conditions": [
	                            {"dimension":"rainfall","quantifier":">","value":0},
	                            {"dimension":"current_temp","quantifier":"<","value":0},
	                            {"dimension":"current_temp","quantifier":">","value":26},
	                           ]
	                },
	                {
	                  "user_id":"eggisbert@gmail.com",
	                  "conditions": [
	                            {"dimension":"rainfall","quantifier":">","value":5},
	                            {"dimension":"current_temp","quantifier":"<","value":-5},
	                            {"dimension":"current_temp","quantifier":">","value":26},
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
	
	logger.debug("---> station %s" % measurement.station)
	rules = get_notif_rules(measurement.station)
	if rules != None:
		for user in rules['users']:
			logger.debug("Conditions %s for user %s" % (user['conditions'],user['user_id']))
			for condition in user['conditions']:
				# Using ops dict to get the operator in the condition
				# Using getattr to get the dimension value of measurement; equvialent to measurement.dimension
				if ops[condition['quantifier']](getattr(measurement,condition['dimension']),condition['value']):
					logger.info("Match condition for %s --> sending notification to %s",
					              condition['dimension'],user['user_id'])
					send_notification(user['user_id'],measurement.station,condition)
	
