from app import app
from sqlalchemy.orm.exc import NoResultFound
from models import *
import json


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
	
	if not (('email' in config) & ('station' in config) & ('rules' in config)):
		app.logger.error("Missing email, station or rules in %s",config)
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
  - email: e-mail address of the user 
  - station: code of the station to apply the rule
  - rules: a list with the rules as dicts. Example:
    '[{"dimension":"rainfall","quantifier":">","value":0},
      {"dimension":"current_temp","quantifier":"<","value":0},
      {"dimension":"current_temp","quantifier":">","value":29},]'
'''
def insert_rules(email,station,rules):
	
	app.logger.info("---> insert_rules()")
	
	for rule in rules:
		
		# Check if there is already rules for this user, station, dimension and quantifier
		try:
			app.logger.info("Searching rules for user |%s|, station |%s|, dimension |%s|, quantifier |%s|" % 
			                (email,station,rule['dimension'],rule['quantifier']))
			config_db = Config.query.filter((Config.station == station) & 
			                                (Config.dimension == rule['dimension']) & 
			                                (Config.email == email) & 
			                                (Config.quantifier == rule['quantifier'])).one()
			# Updating rule with new value
			app.logger.info("Updating new value: %s" % rule['value'])
			config_db.value = rule['value']
			db.session.commit()
		
		# No rules for this station and user: create it	
		except NoResultFound:
			app.logger.info("Creating new rules entry")
			new_config = Config(dimension = rule['dimension'], quantifier = rule['quantifier'], 
			                    value = rule['value'],station = station, email = email,notified=False)
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
		
			
	
	