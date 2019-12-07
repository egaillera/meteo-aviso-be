#!/usr/bin/env python
# encoding: utf-8
"""
test_dates.py

Created by egi on 2019-12-05.
Copyright (c) 2019 com.egaillera. All rights reserved.
"""

import unittest
from pprint import pprint
import json
from db_access.rules import *
from models import *


class test_rules(unittest.TestCase):

    def setUp(self):

        # Read example data
        with open('tests/rules/alicante.json') as f:
            self.rule_alc = json.load(f) 
        with open('tests/rules/barcelona.json') as f:
            self.rule_bcn = json.load(f) 
        with open('tests/rules/onil.json') as f:
            self.rule_onil = json.load(f) 

        # Insert in DB the stations to be used during tests
        station1 = Station(code='ESCAT0800000008005A',
		                  name='Barcelona',
		                  lat=41,
		                  lon=1)          
        db.session.add(station1)
        station2 = Station(code='ESPVA0300000003430A',
		                  name='Onil',
		                  lat=41,
		                  lon=1)          
        db.session.add(station2)
        db.session.commit()


        # Remove test records from database
        delete_rules(self.rule_bcn['device_id'],self.rule_bcn['station'])
        delete_rules(self.rule_onil['device_id'],self.rule_onil['station'])

    def tearDown(self):

        Station.query.filter(Station.code == 'ESCAT0800000008005A').delete()
        Station.query.filter(Station.code == 'ESPVA0300000003430A').delete()
        db.session.commit()


    def test_check_rules(self):
        self.assertFalse(check_rules(self.rule_alc))
        self.assertTrue(check_rules(self.rule_bcn))

    
    def test_insert_rules(self):
        # Check the insertion doesn't produce errors
        self.assertTrue(insert_rules(self.rule_bcn['device_id'],self.rule_bcn['station'],self.rule_bcn['rules']))
        self.assertTrue(insert_rules(self.rule_onil['device_id'],self.rule_onil['station'],self.rule_onil['rules']))

        # Check the inserted rules for one user and one station are read correctly
        db_rules = get_rules_for_station(self.rule_bcn['device_id'],self.rule_bcn['station'])
        self.assertEqual(db_rules,self.rule_bcn['rules'])

        # Check the inserted rules for one user are read correctly
        db_rules = get_rules('device1')
        pprint(db_rules)
        self.assertEqual(db_rules['ESCAT0800000008005A']['rules'],self.rule_bcn['rules'])


    def test_update_rule(self):
        temp_rule = self.rule_bcn
        temp_rule['rules'][0]['offset'] = 10
        self.assertTrue(insert_rules(temp_rule['device_id'],temp_rule['station'],temp_rule['rules']))
