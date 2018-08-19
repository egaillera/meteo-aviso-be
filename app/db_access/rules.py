from app import app
from sqlalchemy.orm.exc import NoResultFound
from models import *


'''
Validate the format of the config JSON. The format should be:
- An email address field
- An station name field
- A list of rules
'''
def check_rules(config):
	
	return True
	

'''
Insert or update a set of rules to trigger notifications in the database. 
Params:
  - email: e-mail address of the user 
  - station: code of the station to apply the rule
  - rules: a string in JSON format with the rules. Example:
    '{"conditions": [{"dimension":"rainfall","quantifier":">","value":0},
                     {"dimension":"current_temp","quantifier":"<","value":0},
                     {"dimension":"current_temp","quantifier":">","value":29},]}'
'''
def insert_rules(email,station,rules):
	
	app.logger.info("---> insert_rules()")
	
	# Check if there is already rules for this user and station
	try:
		app.logger.info("Searching rules for user %s and station %s" % (email,station))
		config_db = Config.query.filter((Config.station ==  station) & 
		                                (Config.email ==  email)).one()
		# Updating with new rules
		app.logger.info("Updating new conditions: %s" % rules)
		config_db.rules = rules
		
	# No rules for this station and user: create it
	except NoResultFound:
		app.logger.info("Creating new rules entry")
		new_config = Config(rules = rules, station = station, email = email)
		db.session.add(new_config)
		
	# Commit changes
	try:
		db.session.commit()
		return True
	except:
		app.logger.error("Error updating Config table in database")
		db.session.rollback()
		return False
		
			
	
	