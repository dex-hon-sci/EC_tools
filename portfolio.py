#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May  6 08:55:17 2024

@author: dexter
"""
import pandas as pd
from dataclasses import dataclass, field

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


__all__ = ['Asset','Portfolio', 'Positions']

__author__="Dexter S.-H. Hon"

@dataclass
class Asset:
    """
    A class that solely define the attribute of a Asset object.
    """
    name: str
    quantity: int
    unit: str
    asset_type:str 
    exp_date: None
    #meta: field(default_factory=dict)

    # note that future countract should be written in the CLM24 format
    # Set a fix amount for checking

# class price table

class Portfolio(object):
        
    def __init__(self, pool=[], table=[]):
        self._pool = pool
        self._table = table
        self._value = None


    @property
    def pool(self):
        return self._pool
        
    @property
    def table(self): # tested
        # The reason I use the table method is that some obejct stored in the 
        # profolio list may contain non standard attributes, like contract expiration 
        # date
        
        values = [list(asset.__dict__.values()) for asset in self._pool]
        keys = [list(asset.__dict__.keys()) for asset in self._pool][0]

        self._table = pd.DataFrame.from_records(data = values, columns = keys)
        print(self._table)
        #handle repeating aseet type
        
        # assume keys[0] contains the name of the asset
        for index, val_name in enumerate(self._table['name']):
            temp_df = self._table[self._table['name'] == val_name]
            if len(temp_df) == 1:
                pass
            elif len(temp_df) > 1:
                new_quantity = sum(temp_df['quantity'])
                
                print(index, list(temp_df.index), new_quantity)
                
                new_entry_dict = {'name': temp_df['name'][0], 
                                  'quantity': new_quantity,
                                  'unit': temp_df['unit'][0],
                                  'asset_type': temp_df['asset_type'][0],
                                  'exp_date': temp_df['exp_date'][0]}
                
                print(new_entry_dict)
                new_entry_dict = pd.DataFrame(new_entry_dict, index=[len(self._table)])
                
                #store them in the lowest row
                self._table = pd.concat([self._table, new_entry_dict], ignore_index = False)
                print("Added", self._table)

                #delete the old entries
                self._table.drop(list(temp_df.index), axis=0, inplace=True)
                print("Subtracted", self._table)

                #print('list of index',list(temp_df.index), type(list(temp_df.index)))
        return self._table
    
    @property
    def value(self, price_table, date = None, dntr='USD'):
        # read the value of the portfolio of a particular date
        price_table = None
        
        #WIP
        for asset_name, quantity in zip(self._table['name'], self._table['quantity']):
            sub_price_table = price_table[price_table['name'] == asset_name]
            value = sub_price_table[sub_price_table['Date']=="xx-xx-xx"]['Price']
            value_entry = asset_name, value*quantity
        # dntr = denomonator
        # read in a list of dictioart value and convert the asset to currency
        self._value = {...}
        
        return self._value
        # backtest or live
        
    def __add__(self, asset):
        #asset_info = list(asset.__dict__.values())
        # check if it exist
        
        self._pool.append(asset)
        
        #make sure that it is not repeating
        return self._pool
    
    def __sub__(self, asset):
        return self._portfolio.remove(asset)
    
    # action log, (1, datetime.datetime, action_str, asset_1, asset_2, func)


    
    def get_asset_value(self,asset_name):
        return None
            
    def add_record(self):
        return
    
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
    
    def check_expiration_date():
        return
    

@dataclass
class Positions(Portfolio):
    # Auto load position 
    # Long Cash baseline
    
    #(Position id, give_asset, get_asset, Entry ,Exit, Stoploss, close_arg=S, active = False, datetime= None)
    #(Position id, asset_obj_A, asset_obj_B, entry_datetime, entry_price (payA buyB))
    #(Position id, asset_obj_A, asset_obj_B, exit_datetime)
    pend_pos_list: list[int] = field(default_factory=list)
    open_pos_list: list[int] = field(default_factory=list)
    close_pos_list: list[int] = field(default_factory=list)
    
    def add_pos(self):
        #pos = (pos_id, give_asset, get_asset, Entry ,Exit, Stoploss, close_arg=S)
        pos = None
        return self.pend_pos_list.append(pos)
    
    def open_pos(self):
        pos_id=0
        # add new position from pending_pos_list
        pend_pos = self.pend_pos_list[0]
        self.open_pos_list.append(pend_pos)
        # add the asset to the Portfolio
        
        #remove pos in pending list
        self.pend_pos_list.remove(pend_pos)
        return self.pend_pos_list
    
    def close_pos():
        # convert the position from pending format to resolved format
        
        # check if cash
        # make a new position with void EES
        return
    
    
