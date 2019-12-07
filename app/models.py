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
		
	# To compare Stations
	def __eq__(self, other):
		return self.code == other.code
		
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
		
		
class RulesConfig(db.Model):
	__tablename__ = 'rulesconfig'

	# Unique index to have only one row by user, station and dimension 
	# and quantifier to avoid same condition over two values
	__table_args__ = (Index('rulecfg_idx','station', 'device_id', 'dimension', 
	                        'quantifier', unique=True),)

	id = db.Column(db.Integer, primary_key=True)
	station = db.Column(db.String(25),db.ForeignKey('station.code'),
	                    nullable=False)
	device_id = db.Column(db.String(100), nullable=False)
	dimension = db.Column(db.String(25),nullable=False)
	quantifier = db.Column(db.String(3),nullable=False)
	value = db.Column(db.Integer,nullable=False)
	offset = db.Column(db.Integer,nullable=False)
	current_value = db.Column(db.Integer,nullable=True)
	notified = db.Column(db.Boolean,nullable=False)


	@property
	def serialize(self):
		"""Return object data in a serializeable format"""
		return {
			'station'	: self.station,
			'device_id'		: self.device_id,
			'dimension'	: self.dimension,
			'quantifier': self.quantifier,
			'value'		: int(self.value),
			'offset'	: int(self.offset),
			'current_value'	: int(self.current_value)
		}

	
		
	
