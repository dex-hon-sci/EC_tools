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
import read as read

PRICE_DICT = {"CLc1": "../test_MS/data_zeroadjust_intradayportara_attempt1/Daily/CL.day",
               "CLc2": "../test_MS/data_zeroadjust_intradayportara_attempt1/Daily/CL_d01.day",
               "HOc1": "../test_MS/data_zeroadjust_intradayportara_attempt1/Daily/HO.day",
               "HOc2": "../test_MS/data_zeroadjust_intradayportara_attempt1/Daily/HO_d01.day",
               "RBc1": "../test_MS/data_zeroadjust_intradayportara_attempt1/Daily/RB.day",
               "RBc2": "../test_MS/data_zeroadjust_intradayportara_attempt1/Daily/RB_d01.day",
               "QOc1": "../test_MS/data_zeroadjust_intradayportara_attempt1/Daily/QO.day",
               "QOc2": "../test_MS/data_zeroadjust_intradayportara_attempt1/Daily/QO_d01.day",
               "QPc1": "../test_MS/data_zeroadjust_intradayportara_attempt1/Daily/QP.day",
               "QPc2": "../test_MS/data_zeroadjust_intradayportara_attempt1/Daily/QP_d01.day"
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
        # a function to check the exp date and create an open position at the 
        # exp date for the future contract.
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
        self._pool_window = self._pool
        self._table = None
        self._master_table = None
        self._value = None
        self._log = None
 
    @property
    def pool_asset(self):

        return self.__pool_asset
    
    @property
    def pool_datetime(self):
        # A list that contains the corresponding datetime where asset is added
        return self.__pool_datetime
    
    @property
    def pool(self): 
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
        self._pool = list(zip(self.__pool_datetime, self.__pool_asset))

        return self._pool
    
    @property
    def pool_df(self):
        pool_df = pd.DataFrame(self.pool, columns=['datetime','asset'])
        return pool_df
    

    @property
    def pool_window(self): 
        # define a window of interest amount the pool object
        self._pool_window = self.pool

        return self._pool_window
    
    def set_pool_window(self, start_time=datetime.datetime(1900,1,1), 
                                end_time=datetime.datetime(2200,12,31)): #WIP
        # define a window of interest amount the pool object
        pool_df_interest = self.pool_df[(self.pool_df['datetime'] > start_time) & 
                                (self.pool_df['datetime'] < end_time)]
        ind = pool_df_interest.index.to_list()
        self._pool_window = self._pool[ind[0]:ind[-1]]
        
        return self._pool_window
    
    
    @property # cached ths for fast access # tested
    def table(self): 
        """
        The atteribute that show a table of all the assets in the portfolio.
        
        The table operate on pool_window

        """
        # The reason I use the table method is that some obejct stored in the 
        # profolio list may contain non standard attributes, like contract 
        # expiration date.
# =============================================================================
#         # Extract the values and keys from the Asset class objects
#         values = [list(asset.__dict__.values()) for asset in self.__pool_asset]
#         keys = [list(asset.__dict__.keys()) for asset in self.__pool_asset][0]
# =============================================================================
        
        # Find the keys and values for asset within a particular time window
        # The function operate on the previously defiend poo_window
        values = [list(self._pool_window[i][1].__dict__.values()) 
                                  for i in range(len(self._pool_window))]
        keys = [list(self._pool_window[i][1].__dict__.keys()) 
                                  for i in range(len(self._pool_window))][0]
    
        # Load the inforamtion to self._table
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
    @classmethod
    def _make_table(cls, pool_type):
        """
        The atteribute that show a table of all the assets in the portfolio.
        
        The table operate on pool_window

        """
        # The reason I use the table method is that some obejct stored in the 
        # profolio list may contain non standard attributes, like contract 
        # expiration date.
# =============================================================================
#         # Extract the values and keys from the Asset class objects
#         values = [list(asset.__dict__.values()) for asset in self.__pool_asset]
#         keys = [list(asset.__dict__.keys()) for asset in self.__pool_asset][0]
# =============================================================================
        
        # Find the keys and values for asset within a particular time window
        # The function operate on the previously defiend poo_window
        values = [list(cls.pool_type[i][1].__dict__.values()) 
                                  for i in range(len(pool_type))]
        keys = [list(cls.pool_type[i][1].__dict__.keys()) 
                                  for i in range(len(pool_type))][0]
    
        # Load the inforamtion to self._table
        cls._table = pd.DataFrame.from_records(data = values, columns = keys)
        
        # Handle repeating aseet type
        for index, val_name in enumerate(cls._table['name']):
            
            temp_df = cls._table[cls._table['name'] == val_name]
            
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
                
                new_entry_dict = pd.DataFrame(new_entry_dict, index=[len(cls._table)])
                
                #store them in the lowest row
                cls._table = pd.concat([cls._table, new_entry_dict], ignore_index = False)

                #delete the old entries
                cls._table.drop(list(temp_df.index), axis=0, inplace=True)

                # sort the table by 'name'                
                cls._table.sort_values(by='name')
                
                # reset the indices
                cls._table.reset_index(drop=True, inplace=True)

        return cls._table
    
    @property
    def master_table(self):
        self._master_table  = self._make_table(self.__pool)
        return self._master_table
    
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
        
    def value(self, datetime, price_dict = PRICE_DICT,   
              size_dict = None, dntr='USD'): #WIP
        """
        A function that return a dict with the price for each assets on 
        a particular date and time.
        
        Parameters
        ----------
        datetime: datetime object
    
        """
        # price_table is a dict containing the pricing data files
        # read the value of the portfolio of a particular date
        
        value_dict = dict()

        for i, asset_name in enumerate(self._table['name']):
            
            # specia handling the denomator asset (usually a currency)
            if asset_name == dntr:
                value_dict[asset_name] = float(self._table['quantity'].iloc[0])
            else:
            
                # manage the size of the asset
                if size_dict == None:
                    size = 1
                else:
                    # Get the size of each asset
                    size = size_dict[asset_name]
                    
                asset_price_filename = price_dict[asset_name]
                sub_price_table = read.read_reformat_Portara_daily_data(
                                                        asset_price_filename)
                
                # The current version of this method only gets the price data iff 
                # it exist in the table, i.e. it does not get anything outside of the trading days
                value = float(sub_price_table[sub_price_table['Date'] == datetime]['Settle'].iloc[0])
                quantity = int(self._table['quantity'].iloc[i])
                                
                #print(asset_name, quantity, value, size, value*quantity*size)
                
                # storage
                value_dict[asset_name] = value*quantity*size
        
        return value_dict
        
    def asset_value(self, asset_name, datetime):
        asset_value = self.value(datetime)[asset_name]
        return asset_value
            
    def total_value(self, datetime):
        total_value = sum(self.value(datetime).values())
        return total_value

    @cached_property
    def log(self):
        # Run the calculation for all asset values for each time unit and 
        # return a log of the values of each asset by time
        
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
    
    
