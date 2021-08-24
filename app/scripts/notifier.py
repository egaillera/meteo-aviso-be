import logging
import random
from logging.handlers import RotatingFileHandler
import operator

from models import *
from constants import *
from sqlalchemy.orm.exc import NoResultFound
from apns2.client import APNsClient
from apns2.payload import Payload
from apns2.credentials import TokenCredentials



logger = logging.getLogger("notifier_data")
logger.setLevel(logging.DEBUG)
handler = RotatingFileHandler('../app/logs/notifier_data.log',maxBytes=1000000, backupCount=3)
formatter = logging.Formatter('%(asctime)s - [%(filename)s:%(lineno)s - %(funcName)20s()] - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Dictionary to work with logical operators as strings
ops = {">":operator.gt,"<":operator.lt}

# Dictionary compose text for user
notif_texts_format = {"current_temp":{">":"La temperatura en %s ha superado los %s grados: %.1f",
                         "<":"La temperatura en %s está por debajo de los %s grados: %.1f"},
                      "rainfall":{">":"La precipitacion en %s ha superado los %s litros: %.1f",
				          "<":"La precipitacion en %s está por debajo de los %s litros: %.1f"}}
         

'''
Change notified flag in the database to avoid notify more than once per day
'''
def mark_as_notified(user_id,st_code,condition):
	
	logger.info("Searching condition %s for station %s and user %s" % (condition,st_code,user_id))
	rule = RulesConfig.query.filter((RulesConfig.station == st_code) & 
	                           (RulesConfig.dimension == condition['dimension']) & 
	                           (RulesConfig.device_id == user_id) & 
	                           (RulesConfig.quantifier == condition['quantifier'])).one()
	
	logger.info("Marking condition %s for station %s and device_id %s as notified" % (condition,st_code,user_id))
	
	rule.notified = True
	db.session.commit()
	

'''
Send notifications according to the condition matched. A understandable 
message for humans should be sent
    Args:
        user_id: device_id of the user to be notified
        st_code: station code
        condition: condition satisfied

    Returns:
        The return value. True for success, False otherwise.
  
'''
def send_notification(user_id,st_code,condition,curr_value):
	
	logger.info("User to notify: %s" % user_id)
	notif_flag = False
	
	# Get the real name of the station
	station_name = Station.query.filter(Station.code == st_code).one().name
	logger.info("Station to be notified about: %s" % station_name)
	
	# Get the notification token from the users table
	token_hex = User.query.filter(User.device_id == user_id).one().notif_token
	logger.info("Notification token: %s" % token_hex)

	# Get the key, key path and team_id from the constants file and build 
	# token credentials object
	token_credentials = TokenCredentials(auth_key_path=NOTIF_AUTH_KEY_PATH, auth_key_id=NOTIF_AUTH_KEY_ID, team_id=NOTIF_TEAM_ID)
	
	# Compose the text
	notif_text = notif_texts_format[condition['dimension']][condition['quantifier']] % \
	             (station_name,condition['value'],float(curr_value))
	logger.info("Sending notification: %s" % notif_text)

	# Compose the dict with the station code and station name
	custom_data = {'station_code' : st_code, 'station_name' : station_name}
	
	topic = NOTIF_TOPIC
	payload = Payload(alert=notif_text, sound="default", badge=0, custom = custom_data)
	client = APNsClient(credentials=token_credentials,use_sandbox=True)
	try:
		#apns.gateway_server.send_notification(token_hex, payload,identifier=identifier)
		client.send_notification(token_hex, payload,topic)
		mark_as_notified(user_id,st_code,condition)
		logger.info("Notification sent!")
		notif_flag = True
	except:
		logger.error("Error sending notification!!")
		print("ERROR ENVIANDO NOTIFICACION")


	return notif_flag
	

'''
Check if there are notifications rules for an station. For the moment only 
"rainfall" and "curr_temp" are supported

TODO: Is it better to keep the table in memory?

Returns a dictionary with the information:

{
'538BDF5F-EC8C-4F64-9DB7-55024C67E66D': 
     [{'dimension': 'current_temp', 'value': -3, 'quantifier': '<'}, 
      {'dimension': 'current_temp', 'value': 35, 'quantifier': '>'}, 
      {'dimension': 'rainfall', 'value': 0, 'quantifier': '>'}], 
 '15D50E4B-4B97-4B19-84A6-FD1F567A0D7E': 
     [{'dimension': 'current_temp', 'value': -3, 'quantifier': '<'}, 
      {'dimension': 'rainfall', 'value': 0, 'quantifier': '>'}]
}


'''
def get_notif_rules(station_code):
	
	logger.debug("--> get_notif_rules() for station %s",station_code)
	rules = None
		
	# Get rules for this station from the database
	try:
		dbrules = RulesConfig.query.filter(RulesConfig.station == station_code).all()	
	except NoResultFound:
		dbrules = None
	except:
		logger.error("Error querying database")
		dbrules = None
		
	# Initialize the structures to compose dict/JSON, including users
	rules = {}
	condition = {}
		
	# There will be one row for condition and user	
	if dbrules != None:
		for dbrule in dbrules:
			condition = {}
			if dbrule.notified == False:
				condition['dimension'] = dbrule.dimension
				condition['quantifier'] = dbrule.quantifier
				condition['value'] = dbrule.value
				if dbrule.device_id not in rules.keys():
					rules[dbrule.device_id] = []
				rules[dbrule.device_id].append(condition)
	
	if rules == {}: rules = None		
	logger.info("Rules returned: %s",str(rules))
	return rules
	

'''
Check if a measurement should trigger a notification to an end user
'''
def check_measurement(measurement):
	
	logger.info("---> station %s" % measurement.station)

	ntf_flag = False

	rules = get_notif_rules(measurement.station)
	if rules != None:
		for user in rules.keys():
			logger.info("Conditions %s for user %s" % (rules[user],user))
			for condition in rules[user]:
				logger.info("Checking condition %s",condition)
				# Using ops dict to get the operator in the condition
				# Using getattr to get the dimension value of measurement; equivalent to measurement.dimension
				if ops[condition['quantifier']](getattr(measurement,condition['dimension']),condition['value']):
					logger.info("Match condition for %s --> sending notification to %s",
					              condition['dimension'],user)
					ntf_flag = send_notification(user,measurement.station,condition,getattr(measurement,condition['dimension']))
	else:
		logger.info('Not rules found!')

	return ntf_flag
		

	
