#!/usr/bin/env python
# encoding: utf-8
"""
test_notifications.py

Created by egi on 2019-12-08.
Copyright (c) 2018 com.egaillera. All rights reserved.
"""

import unittest
from util.dates import *
import sqlite3
from scripts.notifier import *


class test_notifications(unittest.TestCase):

	station_code = 'XXXX'
	station_name = 'ALICANTE'
	station_prov = 3
	station_lat = 40
	station_lon = 1
	device_code = 'device2'
	user_email = 'kk@kk.com'
	user_id = 123456
	device_notif_token = '766845fddd59049fa1f99ab3626be2860f2bf0f07fa60042208ba1ea6a2080f8'
	rule_id = 100000
	
	def setUp(self):
		con = sqlite3.connect("measures.db")
		cr = con.cursor()

		user_insert_sentence = 'INSERT INTO USER VALUES (?,?,?,?)'
		user_entities = (self.user_id,self.user_email,self.device_code,self.device_notif_token)
		cr.execute(user_insert_sentence,user_entities)

		st_insert_sentence = 'INSERT INTO station(code,name,lat,lon,prov) VALUES (?,?,?,?,?)'
		st_entities = (self.station_code,self.station_name,self.station_lat,self.station_lon,self.station_prov)
		cr.execute(st_insert_sentence,st_entities)

		rule_insert_sentence = 'INSERT INTO rulesconfig(id,station,device_id,dimension,quantifier,value,offset,notified) \
			            VALUES (?,?,?,?,?,?,?,?)'
		rule_entities = (self.rule_id,self.station_code,self.device_code,'rainfall','>',5,0,0)
		cr.execute(rule_insert_sentence,rule_entities)

		con.commit()

	def tearDown(self):
		con = sqlite3.connect("measures.db")
		cr = con.cursor()
		cr.execute('DELETE FROM rulesconfig WHERE id = %d' % self.rule_id)
		cr.execute("DELETE FROM station WHERE code = '%s'" % self.station_code)
		cr.execute('DELETE FROM user WHERE id = %d' % self.user_id)
		con.commit()

		
	def test_measurement_not_notified(self):
		measurement = Measurement(date_created = datetime.datetime(2019, 12, 8, 15, 0),
	         current_temp = 20,
	         current_hum = 90,
	         current_pres = 1020,
	         wind_speed = 10,
	         max_gust = 25,
	         wind_direction = 45,
	         rainfall = 0,
	         station = self.station_code)
		self.assertFalse(check_measurement(measurement))

	def test_measurement_notified(self):
		measurement = Measurement(date_created = datetime.datetime(2019, 12, 8, 15, 0),
	         current_temp = 20,
	         current_hum = 90,
	         current_pres = 1020,
	         wind_speed = 10,
	         max_gust = 25,
	         wind_direction = 45,
	         rainfall = 10,
	         station = self.station_code)
		self.assertTrue(check_measurement(measurement))

		
		
if __name__ == '__main__':
	unittest.main()