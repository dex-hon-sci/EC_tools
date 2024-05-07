#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May  6 08:55:17 2024

@author: dexter
"""

round_turn_fees = {
'CLc1': 24.0,
'CLc2': 24.0,
'HOc1': 25.2,
'HOc2': 25.2,
'RBc1': 25.2,
'RBc2': 25.2,
'QOc1': 24.0,
'QOc2': 24.0,
'QPc1': 24.0,
'QPc2': 24.0,
}

num_per_contract = {
    'CLc1': 1000.0,
    'CLc2': 1000.0,
    'HOc1': 42000.0,
    'HOc2': 42000.0,
    'RBc1': 42000.0,
    'RBc2': 42000.0,
    'QOc1': 1000.0,
    'QOc2': 1000.0,
    'QPc1': 100.0,
    'QPc2': 100.0,
}

class Asset(object):
    name = ""
    quantity = 0 # int
    unit = ""
    value_USD = 0.0 
    asset_type = ""

class Profolio(Asset):
        
    def __init__(self):
        self._profolio = None
        
        return None
    
    def profolio(object):
        # profolio only calculate the value of the asset
        profolio = {}
        #"USD": 0.0, "AUD": 0.0
        return profolio
    
    def make_profolio_table(object):
        profolio_table = None
        return profolio_table
    
    def sub_asset(object, asset):        
        return None
    
    def add_asset(object, profolio, new_asset):
        profolio.update(new_asset)
        return profolio
    
    def cal_total_value(object, profolio, dntr='USD'):
        #dntr = denomonator
        # read in a list of dictioart value and convert the asset to currency
        return None
    
    def track_profolio_history(object):
        # make a list of dictionary indexed by time of the changing of profolio
        # add the total value of the 
        return None
    
    def trade(object, profolio, asset_1, asset_2, fee):
        # call in a table of exchange rate
        # pay asset_1 to asset_2
        # make sure one of the asset is money
        
        # asset_1.quantity and asset_1.value
        return None