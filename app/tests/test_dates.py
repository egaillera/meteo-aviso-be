#!/usr/bin/env python
# encoding: utf-8
"""
test_dates.py

Created by egi on 2018-09-22.
Copyright (c) 2018 com.egaillera. All rights reserved.
"""

import unittest
from util.dates import *


class test_dates(unittest.TestCase):
	
	def setUp(self):
		pass
		
	def test_todate_conversion(self):
		aemet_date = '2018-05-02T23:59:59'
		mc_date = '05-03-2017 23:00'
		self.assertEqual(as_date(aemet_date).year,2018)
		self.assertEqual(as_date(aemet_date).minute,59)
		
		self.assertEqual(as_date(mc_date,'MC').minute,0)
		self.assertEqual(as_date(mc_date,'MC').month,3)
		
	def test_sp_date(self):
		
		# Summer time
		s_date = sp_date('2018-08-02 23:00:00')
		self.assertEqual(s_date,"2018-08-03 01:00:00")
		
		# Winter time
		s_date = sp_date('2018-03-02 23:00:00')
		self.assertEqual(s_date,"2018-03-03 00:00:00")
		

    
if __name__ == '__main__':
	unittest.main()