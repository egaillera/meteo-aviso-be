import os

class Configuration(object):
	APPLICATION_DIR = os.path.dirname(os.path.realpath(__file__))
	DEBUG=True
	#SQLALCHEMY_DATABASE_URI = 'sqlite:///%s/measures.db' % APPLICATION_DIR
	SQLALCHEMY_DATABASE_URI ='postgresql://postgres:mmm_dba1@meteo-aviso-postgres:5432/meteo' 
	SQLALCHEMY_TRACK_MODIFICATIONS = False
