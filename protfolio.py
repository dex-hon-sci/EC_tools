#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May  6 08:55:17 2024

@author: dexter
"""
import pandas as pd

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


__all__ = ['Asset','Profolio']

__author__="Dexter S.-H. Hon"

class Asset(object):
    def __init__(self, name: str, quantity: int, unit:str, value:float, 
                 value_unit:str, asset_type:str):
        self._name = name
        self._quantity = quantity # int
        self._unit = unit
        self._value = value
        self._value_unit = value_unit
        self._asset_type = asset_type


class Profolio(object):
        
    def __init__(self, profolio=[], table=[]):
        self._profolio = profolio
        self._table = table
        
    @property
    def table(object):
        # The reason I use the table method is that some obejct stored in the 
        #profolio list may contain non standard attributes, like contract expiration 
        # date
        profolio_table = pd.dataframe([])
        return profolio_table
        
    @property
    def total_value(object, profolio, dntr='USD'):
        # dntr = denomonator
        # read in a list of dictioart value and convert the asset to currency
        return None
    
    @property
    def ls_asset_value(object):
        return None
            
    
    def sub_asset(object, asset):        
        return None
    
    def add_asset(object, profolio, new_asset):
        profolio.update(new_asset)
        return profolio
    

    
    def track_profolio_history(object):
        # make a list of dictionary indexed by time of the changing of profolio
        # add the total value of the 
        return None
    
    def trade(object, profolio, asset_1, asset_2, price_ratio, fee):
        # call in a table of exchange rate
        # check price
        
        # pay asset_1 to asset_2, 
        # make sure one of the asset is money
        
        
        # asset_1.quantity and asset_1.value
        return None
    
