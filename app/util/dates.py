import datetime,pytz
from scripts.constants import *

date_str_format={'AEMET':AEMET_DATE_FORMAT,'MC':MC_DATE_FORMAT,'db':'%Y-%m-%d %H:%M:%S'}

def sp_date(date_utc):
		
	my_date = datetime.datetime.strptime(date_utc,'%Y-%m-%d %H:%M:%S')
	my_date_utc = my_date.replace(tzinfo=pytz.timezone('UTC'))
	my_date_spain = my_date_utc.astimezone(pytz.timezone('Europe/Madrid'))
	
	return my_date_spain.strftime('%Y-%m-%d %H:%M:%S')
	
'''
Returns True if the date received is in the same day that today
'''
def is_today(date_utc,type='AEMET'):
	
	# Transform date to check to Spanish time
	date_to_check = datetime.datetime.strptime(date_utc,date_str_format[type])
	date_to_check_utc = date_to_check.replace(tzinfo=pytz.timezone('UTC'))
	date_to_check_spain = date_to_check_utc.astimezone(pytz.timezone('Europe/Madrid'))
	
	# Transform current date to Spanish time
	current_time_utc = datetime.datetime.utcnow().replace(tzinfo=pytz.timezone('UTC'))
	current_time_spain = current_time_utc.astimezone(pytz.timezone('Europe/Madrid'))
	
	return date_to_check_spain.date() == current_time_spain.date()
	
def as_date(str_date,type='AEMET'):
	
	return datetime.datetime.strptime(str_date,date_str_format[type])
	