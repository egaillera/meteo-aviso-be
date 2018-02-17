import datetime, re 
from app import db
from sqlalchemy import Index,UniqueConstraint

class Station(db.Model):
	__tablename__ = 'station'
	
	code = db.Column(db.String(25),primary_key=True)
	name = db.Column(db.String(50))
	lat = db.Column(db.Numeric(5,3))
	lon = db.Column(db.Numeric(5,3))
	prov = db.Column(db.Integer)
	
	def __repr__(self):
		return '<Station: %s>' % self.code
		
	@property
	def serialize(self):
		"""Return object data in a serializeable format"""
		return {
		    'code'    : self.code,
		    'name'    : self.name,
		    'lat'     : float(self.lat),
		    'lon'     : float(self.lon),
		    'prov'	  : self.prov
		}	
		
		
class Measurement(db.Model):
	__tablename__ = 'measurement'
	
	# Unique index to avoid potential duplication of measurements
	__table_args__ = (Index('date_station_idx','date_created','station',unique=True),) 
	
	id = db.Column(db.Integer, primary_key=True)
	date_created = db.Column(db.DateTime)
	current_temp = db.Column(db.Numeric(5,2))
	current_hum = db.Column(db.Numeric(5,2))
	current_pres = db.Column(db.Numeric(6,2))
	wind_speed = db.Column(db.Numeric(5,2))
	max_gust = db.Column(db.Numeric(5,2))
	wind_direction = db.Column(db.Numeric(5,2))
	rainfall = db.Column(db.Numeric(5,2))
	station = db.Column(db.String(25),db.ForeignKey('station.code'),nullable=False)
	
	@property
	def serialize(self):
		"""Return object data in a serializeable format"""
		return {
		    'date_created'    : str(self.date_created),
		    'current_temp'    : float(self.current_temp),
		    'current_hum'     : float(self.current_hum),
		    'current_pres'    : float(self.current_pres),
		    'wind_speed'      : float(self.wind_speed),
		    'max_gust'        : float(self.max_gust),
		    'wind_direction'  : float(self.wind_direction),
		    'rainfall'        : float(self.rainfall),
		    'station'         : self.station
		}
		
class User(db.Model):
	__tablename__ = 'user'
	
	# Unique index to avoid potential duplication of measurements
	__table_args__ = (Index('device_id_idx','device_id',unique=True),)
	
	id = db.Column(db.Integer, primary_key=True)
	email = db.Column(db.String(255), nullable=False)
	device_id = db.Column(db.String(100), nullable=False)
	notif_token = db.Column(db.String(100), nullable=False)
	
	@property
	def serialize(self):
		"""Return object data in a serializeable format"""
		return {
			'e-mail'	: self.email,
			'Device Id'	: self.device_id,
			'Token'		: self.notif_token
		}
		
class Config(db.Model):
	__tablename__ = 'config'
	
	id = db.Column(db.Integer, primary_key=True)
	rules = db.Column(db.String(4096)) # Rules to apply in serialized JSON format
	station = db.Column(db.String(25),db.ForeignKey('station.code'),nullable=False)
	device_id = db.Column(db.String(100),db.ForeignKey('user.device_id'),nullable=False)
	
	@property
	def serialize(self):
		"""Return object data in a serializeable format"""
		return {
			'rules'		: self.rules,
			'station'	: self.station,
			'device_id'	: self.device_id
		}
	
		
	
