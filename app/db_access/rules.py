from app import app
from sqlalchemy.orm.exc import NoResultFound
from models import *
import json
from pprint import pprint


'''
Validate the format of the config JSON. The format should be
something like:

{"email":"egaillera@gmail.com",
 "station":"1234",
 "rules": [{"dimension":"rainfall","quantifier":">","value":0},
      {"dimension":"current_temp","quantifier":"<","value":0},
      {"dimension":"current_temp","quantifier":">","value":29}]}

- the fields email, station and rules are present
- for each rule, fields dimension, quantifier and value are present:
'''
def check_rules(config):
	
	app.logger.info("---> check_rules()")
	
	if config == None:
		app.logger.error("Config is None")
		return False
	
	if not (('device_id' in config) & ('station' in config) & ('rules' in config)):
		app.logger.error("Missing device_id, station or rules in %s",config)
		return False
	else:
		for rule in config['rules']:
			if not (('dimension' in rule) & ('quantifier' in rule) & ('value' in rule)):
				app.logger.error("Missing dimension, quantifier or value in rule %s",rule)
				return False
			
	return True

'''
Insert or update a set of rules to trigger notifications in the database. 
Params:
  - device_id: identifier of the user mobile
  - station: code of the station to apply the rule
  - rules: a list with the rules as dicts. Example:
    '[{"dimension":"rainfall","quantifier":">","value":0},
      {"dimension":"current_temp","quantifier":"<","value":0},
      {"dimension":"current_temp","quantifier":">","value":29},]'
'''
def insert_rules(device_id,station,rules):

	app.logger.info("---> insert_rules()")

	for rule in rules:

		# Check if there is already rules for this user, station, dimension and quantifier
		try:
			app.logger.info("Searching rules for device_id |%s|, station |%s|, dimension |%s|, quantifier |%s|" % 
			                (device_id,station,rule['dimension'],rule['quantifier']))
			config_db = RulesConfig.query.filter((RulesConfig.station == station) & 
			                                     (RulesConfig.dimension == rule['dimension']) & 
			                                     (RulesConfig.device_id == device_id) & 
			                                     (RulesConfig.quantifier == rule['quantifier'])).one()
			# Updating rule with new value
			app.logger.info("Updating new value: %s" % rule['value'])
			config_db.value = rule['value']
			config_db.notified = False
			db.session.commit()

		# No rules for this station and user: create it	
		except NoResultFound:
			app.logger.info("Creating new rules entry")
			new_config = RulesConfig(dimension = rule['dimension'], quantifier = rule['quantifier'], 
			                         value = rule['value'],station = station, device_id = device_id,notified=False)
			db.session.add(new_config)
			db.session.commit()

	# Commit changes
	try:
		db.session.commit()
		return True
	except:
		app.logger.error("Error updating Config table in database")
		db.session.rollback()
		return False

''' 
Return set of rules for a user. Format shoud be a dict of dicts, where the key
will be the station and the value another dict with the list of rules and
the name of the station. Example follows:

{'2966D': {'rules': [{'dimension': 'rainfall', 'quantifier': '>', 'value': 0},
                     {'dimension': 'current_temp',
                      'quantifier': '<',
                      'value': 0},
                     {'dimension': 'current_temp',
                      'quantifier': '>',
                      'value': 29}],
           'station_name': 'ALCAÑICES-VIVINERA'},
 '8057C': {'rules': [{'dimension': 'current_temp',
                      'quantifier': '>',
                      'value': 20},
                     {'dimension': 'current_temp',
                      'quantifier': '<',
                      'value': -3},
                     {'dimension': 'rainfall', 'quantifier': '>', 'value': 0}],
           'station_name': 'PEGO'},
 'ESCAT0800000008005A': {'rules': [{'dimension': 'current_temp',
                                    'quantifier': '<',
                                    'value': 15},
                                   {'dimension': 'rainfall',
                                    'quantifier': '>',
                                    'value': 2}],
                         'station_name': 'Barcelona - Poblenou'}}

'''
def get_rules(device_id):

	app.logger.info("---> get_rules('%s')" % device_id)
	rules = {}

	try:
		db_rules = RulesConfig.query.filter(RulesConfig.device_id == device_id).all()
		for r in db_rules:
			if r.station not in rules.keys():
				rules[r.station] = {}
				rules[r.station]['rules'] = []
				# Get name of the station
				station = Station.query.filter(Station.code == r.station).one()
				rules[r.station]['station_name'] = station.name
			rules[r.station]['rules'].append({"dimension":r.dimension,
			                                  "quantifier":r.quantifier,
			                                  "value":r.value})
	except:
		app.logger.error("Error querying database")
		rules = None

	return rules
	
''' 
Return a list of notification rules for a station and a user. Format should be an
array of dicts with the rules. Example follows:
[
{'dimension': 'current_temp','quantifier': '<','value': 15},
{'dimension': 'rainfall','quantifier': '>','value': 2}
]
'''	
def get_rules_for_station(device_id,station_code):
	app.logger.info("---> get_rule('%s,%s')" % (device_id,station_code))
	rules = []

	try:
		db_rules = RulesConfig.query.filter((RulesConfig.device_id == device_id) &
		                               (RulesConfig.station == station_code)).all()
		for r in db_rules:
			rules.append({"dimension":r.dimension,
			              "quantifier":r.quantifier,
			               "value":r.value})
	except:
		app.logger.error("Error querying database")
		rules = None

	return rules
	
''' 
Delete all rules about an station for a user
'''	
def delete_rules(device_id,station_code):
	app.logger.info("---> delete_rules('%s,%s')" % (device_id,station_code))

	try:
		RulesConfig.query.filter((RulesConfig.device_id == device_id) & (RulesConfig.station == station_code)).delete()
	except:
		app.logger.error("Error deleting rules")
		return False

	# Commit changes
	try:
		db.session.commit()
		return True
	except:
		app.logger.error("Error deleting rules in database")
		db.session.rollback()
		return False


def main():

	#pprint(get_rules('egaillera@gmail.com'))
	#pprint(get_rules('eggisbert@gmail.com'))
	
	r1 = [{"dimension":"rainfall","quantifier":">","value":0}, {"dimension":"current_temp","quantifier":"<","value":0},{"dimension":"current_temp","quantifier":">","value":29},]
	r2 = [{"dimension":"rainfall","quantifier":">","value":3}, {"dimension":"current_temp","quantifier":"<","value":2},{"dimension":"current_temp","quantifier":">","value":25},]
	c1 = {"device_id":"aksfhksjhfkjdsfjsdk",
	 "station":"1234",
	 "rules": [{"dimension":"rainfall","quantifier":">","value":0},
	      {"dimension":"current_temp","quantifier":"<","value":0},
	      {"dimension":"current_temp","quantifier":">","value":29}]}
	
	#check_rules(c)
	insert_rules('movil_de_quique','8025',r1)
	insert_rules('movil_de_quique','8057C',r2)
	insert_rules('movil_de_papa','8025',r1)
	insert_rules('movil_de_papa','8057C',r2)

	
	#pprint(get_rules("sdhifskjfsdkjfhsdkhdsk"))
	#pprint(get_rules("jfdhfhdufsdfisdfdkfshsdkhdsf"))
	
	#pprint(get_rules_for_station('movil_de_quique','8025'))
	#pprint(get_rules_for_station('movil_de_quique','8057C'))
	
if __name__ == '__main__':
	main()

		
			
	
	