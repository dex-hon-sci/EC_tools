#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May  6 08:55:17 2024

@author: dexter
"""
import pandas as pd
from dataclasses import dataclass, field
from functools import cached_property
import datetime as datetime

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

price_table = {
    'CLc1': 70.0,
    'CLc2': 74.0,
    'HOc1': 5.0,
    'HOc2': 3.0,
    'RBc1': 3.0,
    'RBc2': 2.0,
    'QOc1': 2.45,
    'QOc2': 2.67,
    'QPc1': 90.0,
    'QPc2': 92.0,
    }

__all__ = ['Asset','Portfolio', 'Positions']

__author__="Dexter S.-H. Hon"

@dataclass
class Asset:
    """
    A class that solely define the attribute of a Asset object.
    """
    name: str  # note that future countract should be written in the CLM24 format
    quantity: int or float
    unit: str
    asset_type:str 
    misc: dict[str] = field(default_factory=dict)
    
    def check_exp_date():
        return
    #meta: field(default_factory=dict)



class Portfolio(object):
    """
    This class manage everything related to Portfolio.
    """
    def __init__(self):
        self.__pool_asset = [] # set pool to be a private attribute
        self.__pool_datetime = []
        self._pool = []
        self._pool_window = []
        self._table = None
        self._value = None
        self._log = None
 
    @property
    def pool_asset(self):
        """
        A pool that contains all the Asset objects. This is the unstructured 
        data containers. Refined method should be operating on the attribute 
        'table'.
        
        This is to also avoid mixing fungible and non-fungible assets.
        
        It contains a sequential record of the adding and subtracting assets 
        from the portfolio. It can be used to generate a log of asset movement
        and a table for viewing its overall values.
        
        Note that Asset can have a negative quantity. It means an exit of
        some asset from the portfolio.  
        
        To add or subtract asset from the pool, you need to use the add and 
        sub function.

        """
        return self.__pool_asset
    
    @property
    def pool_datetime(self):
        # A list that contains the corresponding datetime where asset is added
        return self.__pool_datetime
    
    @property
    def pool(self): 
    
        self._pool = list(zip(self.__pool_datetime, self.__pool_asset))

        return self._pool
    
    @property
    def pool_df(self):
        pool_df = pd.DataFrame(self.pool, columns=['datetime','asset'])
        return pool_df
    
    @property
    def pool_window(self, start_time, end_time): #WIP
    
        temp = self.pool_df[self.pool_df['datetime'] > start_time]
        pool_df_interest = temp[temp['datetime'] < end_time]
        ind = pool_df_interest.index.to_list()
        self._pool_window = self._pool[ind[0]:ind[-1]]
        return self._pool_window
    
    @property # cached ths for fast access # tested
    def table(self, datetime=None): 
        """
        The atteribute that show a table of all the assets in the portfolio.

        """
        # The reason I use the table method is that some obejct stored in the 
        # profolio list may contain non standard attributes, like contract expiration 
        # date
        
        # Extract the values and keys from the Asset class objects
        values = [list(asset.__dict__.values()) for asset in self.__pool_asset]
        keys = [list(asset.__dict__.keys()) for asset in self.__pool_asset][0]

        # Load the inforamtion to
        self._table = pd.DataFrame.from_records(data = values, columns = keys)
        
        # Handle repeating aseet type
        for index, val_name in enumerate(self._table['name']):
            
            temp_df = self._table[self._table['name'] == val_name]
            
            # If the asset is unique in the pool, pass.
            if len(temp_df) == 1:
                pass
            # If the asset is not unique, perform the condesation action
            elif len(temp_df) > 1:
                #print(list(temp_df['quantity']), sum(list(temp_df['quantity'])))
                # the summed quantity
                new_quantity = sum(list(temp_df['quantity']))
                
                # make new entry_dictionary                
                new_entry_dict = {'name': temp_df['name'].iloc[0], 
                                  'quantity': new_quantity,
                                  'unit': temp_df['unit'].iloc[0],
                                  'asset_type': temp_df['asset_type'].iloc[0],
                                  'misc': dict()}
                
                new_entry_dict = pd.DataFrame(new_entry_dict, index=[len(self._table)])
                
                #store them in the lowest row
                self._table = pd.concat([self._table, new_entry_dict], ignore_index = False)

                #delete the old entries
                self._table.drop(list(temp_df.index), axis=0, inplace=True)

                # sort the table by 'name'                
                self._table.sort_values(by='name')
                
                # reset the indices
                self._table.reset_index(drop=True, inplace=True)

        return self._table

# =============================================================================
#     @property # cached ths for fast access # tested
#     def table(self, datetime=None): 
#         """
#         The atteribute that show a table of all the assets in the portfolio.
# 
#         """
#         # The reason I use the table method is that some obejct stored in the 
#         # profolio list may contain non standard attributes, like contract expiration 
#         # date
#         
#         # Extract the values and keys from the Asset class objects
#         values = [list(asset.__dict__.values()) for asset in self.__pool_asset]
#         keys = [list(asset.__dict__.keys()) for asset in self.__pool_asset][0]
# 
#         # Load the inforamtion to
#         self._table = pd.DataFrame.from_records(data = values, columns = keys)
#         
#         # Handle repeating aseet type
#         for index, val_name in enumerate(self._table['name']):
#             
#             temp_df = self._table[self._table['name'] == val_name]
#             
#             # If the asset is unique in the pool, pass.
#             if len(temp_df) == 1:
#                 pass
#             # If the asset is not unique, perform the condesation action
#             elif len(temp_df) > 1:
#                 #print(list(temp_df['quantity']), sum(list(temp_df['quantity'])))
#                 # the summed quantity
#                 new_quantity = sum(list(temp_df['quantity']))
#                 
#                 # make new entry_dictionary                
#                 new_entry_dict = {'name': temp_df['name'].iloc[0], 
#                                   'quantity': new_quantity,
#                                   'unit': temp_df['unit'].iloc[0],
#                                   'asset_type': temp_df['asset_type'].iloc[0],
#                                   'misc': dict()}
#                 
#                 new_entry_dict = pd.DataFrame(new_entry_dict, index=[len(self._table)])
#                 
#                 #store them in the lowest row
#                 self._table = pd.concat([self._table, new_entry_dict], ignore_index = False)
# 
#                 #delete the old entries
#                 self._table.drop(list(temp_df.index), axis=0, inplace=True)
# 
#                 # sort the table by 'name'                
#                 self._table.sort_values(by='name')
#                 
#                 # reset the indices
#                 self._table.reset_index(drop=True, inplace=True)
# 
#         return self._table
# =============================================================================
    
    def add(self, asset,  datetime= datetime.datetime.now(), 
            quantity = 0, unit='contract', 
            asset_type='future'): #tested
        """
        A function that .
    
        Parameters
        ----------
        asset : str, Asset Object, list
            
        datetime: datetime
        
        quantity: float, int
            
        ...
        
        """
        #asset can be a list
        # check if it asset is an asset format
        if type(asset) == Asset:
            pass
        elif type(asset) == str: 
            # # search the dictionary to see what kind of asset is this 
            # (potential improvement)
            # make a new asset
            asset = Asset(asset, quantity, unit, asset_type)
        
        self.__pool_asset.append(asset)   # save new asset
        self.__pool_datetime.append(datetime) #record datetime

    
    def sub(self, asset,  datetime= datetime.datetime.today(),  
            asset_name="", quantity = 0, unit='contract', 
            asset_type='future'): #tested
        """
        A function that p.
    
        Parameters
        ----------
        asset : str, Asset Object, list
            
        datetime: datetime
        
        quantity: float, int
            
        ...
        
        """
        # check if it asset is an asset format
        if type(asset) == Asset:  
            # call the quantity from table
            asset_name = asset.__dict__['name']
            #print(asset.__dict__['quantity'])
            #print(self.table[self.table['name']== asset_name]['quantity'].iloc[0])
            
            # check if the total amount is higher than the subtraction amount
            if asset.__dict__['quantity'] > self.table[self.table['name']==\
                                              asset_name]['quantity'].iloc[0]: # tested
                
                raise Exception('There is not enough {} to be subtracted \
                                from the portfolio.'.format(asset_name))
            else:
                quantity = asset.__dict__['quantity']
                unit = asset.__dict__['unit']
                asset_type = asset.__dict__['asset_type']
                pass
            
        if type(asset) == str: 
            # # search the dictionary to see what kind of asset is this
            # make a new asset
            asset_name = asset
            
        # make a new asset with a minus value for quantity
        new_asset = Asset(asset_name, quantity*-1, unit, asset_type)
        
        self.__pool_asset.append(new_asset)   # save new asset
        self.__pool_datetime.append(datetime) #record datetime
        
        
    @property
    def value(self, price_table, datetime = None, dntr='USD'): #WIP
        # price_table is a dictionary containing the price of a set of assets of a particular date
        
        # from date extract a price_table
        
        # read the value of the portfolio of a particular date
        
        for asset_name, quantity in zip(self._table['name'], self._table['quantity']):
            sub_price_table = price_table[price_table['name'] == asset_name]
            value = sub_price_table[sub_price_table['Date']=="xx-xx-xx"]['Price']
            value_entry = asset_name, value*quantity
        # dntr = denomonator
        # read in a list of dictioart value and convert the asset to currency
        self._value = {...}
        
        
        # give a dict of value
        return self._value
        # backtest or live
        
    
    def total_value(self, datetime):
        return 
        
    def asset_value(self, asset_name, datetime):
        return None
    
    @cached_property
    def log(self):
        
        # set index to datetime time
        return self._log
    
    def asset_log(self, asset_name):
        return

    # action log, (1, datetime.datetime, action_str, asset_1, asset_2, func)

    
    
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
        
        # add the relevant asset to the Portfolio
        return
    
    
