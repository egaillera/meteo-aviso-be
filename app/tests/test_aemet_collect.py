#!/usr/bin/env python
# encoding: utf-8
"""
test_aemet_collect.py

Created by egi on 2018-09-22.
Copyright (c) 2018 com.egaillera. All rights reserved.
"""
from pprint import pprint
import unittest
import json
import datetime
from scripts.get_aemet_data import *

class test_aemet_collect(unittest.TestCase):
	
	def setUp(self):
		
		# Open example data 
		with open('tests/datos_aemet.json') as f:
			self.data = json.load(f)
			self.data_to_order = [{'idema':'8025','fint':'2018-09-23T07:00:00'},\
			                      {'idema':'8057C','fint':'2018-09-23T08:00:00'},\
			                      {'idema':'8025','fint':'2018-09-23T06:00:00'},\
			                      {'idema':'8025','fint':'2018-09-24T13:00:00','prec':0.1},\
			                      {'idema':'8057C','fint':'2018-09-23T07:00:00'},\
			                      {'idema':'8057C','fint':'2018-09-23T05:00:00'}]
			
		
		# Calculate today and yesterday dates
		today_date = datetime.datetime.utcnow().strftime('%Y-%m-%d')
		yesterday_date = (datetime.datetime.utcnow() - datetime.timedelta(1)).strftime('%Y-%m-%d')
		
		# Substitute 'Yesterday' and 'Today' for yesterday and today dates	
		for i in range(0,len(self.data)):
			self.data[i]['fint'] = self.data[i]['fint'].replace('Today',today_date)
			self.data[i]['fint'] = self.data[i]['fint'].replace('Yesterday',yesterday_date)
			
	def test_aemet_data(self):
		self.assertTrue('8025' in self.data[0].values())
			
	def test_order_data(self):
		o_list = order_aemet_data(self.data_to_order)
		self.assertEqual(o_list['8057C'][-2]['fint'],'2018-09-23T07:00:00')
		self.assertEqual(o_list['8025'][-2]['fint'],'2018-09-23T07:00:00')
		
	# 8205: 1.0 + 2.0 + 1.0 + 2.0 + 8.0 = 14
	def test_rainfall(self):
		o_dict = order_aemet_data(self.data)
		self.assertEqual(o_dict['8025'][-1]['prec'],14.0)
		self.assertEqual(o_dict['8025'][-2]['prec'],6.0)
		
	def test_rainfall_no_data(self):
		o_dict = order_aemet_data(self.data_to_order)
		self.assertEqual(o_dict['8025'][-1]['prec'],0.1)
		
	def test_process_aemet_data(self):
		o_list = process_aemet_data(self.data_to_order)
		for o in o_list:
			if o['fint'] == '2018-09-24T13:00:00' and o['idema'] == '8025':
				self.assertEqual(o['prec'],0.1)
					    
if __name__ == '__main__':
	unittest.main()