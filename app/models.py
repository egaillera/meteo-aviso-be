import datetime, re 
from app import db
from sqlalchemy import Index,UniqueConstraint

class Station(db.Model):
	__tablename__ = 'station'
	
	code = db.Column(db.String(25),primary_key=True)
	name = db.Column(db.String(50))
	lat = db.Column(db.Numeric(5,3))
	lon = db.Column(db.Numeric(5,3))
	
	def __repr__(self):
		return '<Station: %s>' % self.code
		
	@property
	def serialize(self):
		"""Return object data in a serializeable format"""
		return {
		    'code'    : self.code,
		    'name'    : self.name,
		    'lat'     : float(self.lat),
		    'lon'     : float(self.lon)
		}	
		
		
class Measurement(db.Model):
	__tablename__ = 'measurement'
	
	# Unique index to avoid potential duplication of mesaruments
	__table_args__ = (Index('date_station_idx','date_created','station',unique=True),) 
	
	id = db.Column(db.Integer, primary_key=True)
	date_created = db.Column(db.DateTime)
	weather_status = db.Column(db.String(20))
	current_temp = db.Column(db.Numeric(4,2))
	max_temp = db.Column(db.Numeric(4,2))
	min_temp = db.Column(db.Numeric(4,2))
	current_hum = db.Column(db.Numeric(5,2))
	max_hum = db.Column(db.Numeric(5,2))
	min_hum = db.Column(db.Numeric(5,2))
	current_pres = db.Column(db.Numeric(6,2))
	max_pres = db.Column(db.Numeric(6,2))
	min_pres = db.Column(db.Numeric(6,2))
	wind_speed = db.Column(db.Numeric(5,2))
	max_gust = db.Column(db.Numeric(5,2))
	wind_direction = db.Column(db.Integer)
	rainfall = db.Column(db.Numeric(5,2))
	station = db.Column(db.String(25),db.ForeignKey('station.code'),nullable=False)
	
	@property
	def serialize(self):
		"""Return object data in a serializeable format"""
		return {
		    'date_created'    : str(self.date_created),
		    'weather_status'  : self.weather_status,
		    'current_temp'    : float(self.current_temp),
		    'max_temp'        : float(self.max_temp),
		    'min_temp'        : float(self.min_temp),
		    'current_hum'     : float(self.current_hum),
		    'max_hum'         : float(self.max_hum),
		    'min_hum'         : float(self.min_hum),
		    'current_pres'    : float(self.current_pres),
		    'min_pres'        : float(self.min_pres),
		    'max_pres'        : float(self.max_pres),
		    'wind_speed'      : float(self.wind_speed),
		    'max_gust'        : float(self.max_gust),
		    'wind_direction'  : self.wind_direction,
		    'rainfall'        : float(self.rainfall),
		    'station'         : self.station
		}
		
	
	
