from app import app
from sqlalchemy.orm.exc import NoResultFound
from models import *

'''
Insert user information in the database. User information come
as a dict:
  - emailaddress: e-mail address of the user (not used)
  - deviceid: strint to uniquely identify the device for this app  
  - token: to be used to send notifications to this device
'''
def insert_user(user):
	app.logger.info("To insert user %s" % str(user))
	
	# See if this user is already signed up
	try:
		app.logger.info("searching for user %s" % user['deviceid'])
		user_db = User.query.filter(User.device_id ==  user['deviceid']).one()
		
		# Updating user with new token
		app.logger.info("Updating device %s with token %s" %(user['deviceid'],
		                                                     user['token']))
		user_db.notif_token = user['token']
	
	# User does not exist: create it
	except NoResultFound:
		app.logger.info("Creating user %s" % user['deviceid'])
		new_user = User(email=user['emailaddress'],
		                device_id = user['deviceid'],
		                notif_token = user['token'])
		db.session.add(new_user)
	
	try:	
		db.session.commit()
		return True
	except:
		app.logger.error("Error inserting in database")
		db.session.rollback()
		return False
		
