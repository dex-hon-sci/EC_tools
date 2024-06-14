#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May  6 08:55:17 2024

@author: dexter
"""
# python import
from dataclasses import dataclass, field
from typing import Protocol
from functools import cached_property
import datetime as datetime

# package import 
import pandas as pd

# EC_tools import
import EC_tools.read as read

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

SIZE_DICT = {
    'CLc1': 1000.0,
    'CLc2': 1000.0,
    'HOc1': 42000.0,
    'HOc2': 42000.0,
    'RBc1': 42000.0,
    'RBc2': 42000.0,
    'QOc1': 1000.0,
    'QOc2': 1000.0,
    'QPc1': 100.0,
    'QPc2': 100.0
    }

__all__ = ['Asset','Portfolio']

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
    
    def check_exp_date(): #WIP
        # a function to check the exp date and create an open position at the 
        # exp date for the future contract.
        return
    
    #meta: field(default_factory=dict)


class Portfolio(object):
    """
    This class manage everything related to the Portfolio.
    
    """
    def __init__(self):
        self.__pool_asset = [] # set pool to be a private attribute
        self.__pool_datetime = []
        self._pool = []
        self._pool_window = None
        self._table = None
        self._master_table = None
        self._value = None
        self._log = None
 
    @property
    def pool_asset(self):
        """
        A list that contains the the added assets.

        """
        return self.__pool_asset
    
    @property
    def pool_datetime(self):
        """
        A list that contains the corresponding datetime where asset is added

        """
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
        """
        A pool in dataframe format for easy query.
        
        """
        pool_df = pd.DataFrame(self.pool, columns=['datetime','asset'])
        return pool_df
    

    @property
    def pool_window(self): 
        """
        A pool window given by a specific time intervals. This function 
        initialised the object. Use set_pool_window to set a particular 
        time frame.


        """
        self._pool_window = self.pool
        return self._pool_window
    
    def set_pool_window(self, start_time=datetime.datetime(1900,1,1), 
                                end_time=datetime.datetime(2200,12,31)):
        """
        Setter method for the pool_window object.

        Parameters
        ----------
        start_time : datetime object, optional
            The start time . The default is datetime.datetime(1900,1,1).
        end_time : datetime object, optional
            The end time. The default is datetime.datetime(2200,12,31).

        Returns
        -------
        list
            pool_window list object.

        """
        # define a window of interest amount the pool object
        pool_df_interest = self.pool_df[(self.pool_df['datetime'] >= start_time) & 
                                (self.pool_df['datetime'] <= end_time)]
        #print(pool_df_interest)
        ind = pool_df_interest.index.to_list()
        #print(ind)
        self._pool_window = self._pool[ind[0]:ind[-1]+1]
        
        return self._pool_window
    
    @staticmethod
    def _make_table(pool_type):
        """
        A staticmethod that create a datafreame table using either pool_window
        or pool. This is an internal method to construct the table and master 
        table attributes for the portfolio class. 
        
        The reason I use the table method is that some obejct stored in the 
        profolio list may contain non standard attributes, like contract 
        expiration date.

        Parameters
        ----------
        pool_type : pool object (list)
            The pool object type. It can be either pool_window or pool, 
            corresponding to making table or master_table objects

        Returns
        -------
        table : dataframe
            The resulting table.

        """

        
        # Find the keys and values for asset within a particular time window
        # The function operate on the previously defiend poo_window
        values = [list(pool_type[i][1].__dict__.values()) 
                                  for i in range(len(pool_type))]
        keys = [list(pool_type[i][1].__dict__.keys()) 
                                  for i in range(len(pool_type))][0]
    
        # Load the inforamtion to self._table
        table = pd.DataFrame.from_records(data = values, columns = keys)
        
        # Handle repeating aseet type
        for index, (val_name, misc) in enumerate(zip(table['name'], table['misc'])):
            
            temp_df = table[(table['name'] == val_name) & (table['misc'] == misc)]
            
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
                                  'misc': [temp_df['misc'].iloc[0]]}
                
                new_entry_dict = pd.DataFrame(new_entry_dict, index=[len(table)])

                #store them in the lowest row
                table = pd.concat([table, new_entry_dict], ignore_index = False)

                #delete the old entries
                table.drop(list(temp_df.index), axis=0, inplace=True)

                # sort the table by 'name'                
                table.sort_values(by='name')
                
                # reset the indices
                table.reset_index(drop=True, inplace=True)

        return table
    
    @property
    def table(self): # tested
        """
        An attribute that show a table of all the assets in the portfolio.
        
        The table operates on pool_window, meaning it obly shows the assets 
        listed in the pool_window list. Please make sure you are setting 
        the time window correctly.
        
        """
        if self._pool_window == None:
            raise Exception("pool_window not found. Use either master_table or \
                            define a pool_window for viewing first")
    
        self._table  = self._make_table(self._pool_window)
        return self._table
    
    @property
    def master_table(self): #tested
        """
        An attribute that show a table of all the assets in the portfolio.
        
        The table operates on pool, meaning it obly shows the assets 
        listed in the pool list, i.e., it shows assets across all time.
        
        """
        self._master_table  = self._make_table(self.pool)
        return self._master_table
    
    def check_remainder(self, asset_name, quantity):
        """
        A function that check the remainder if there are enough asset of a 
        particular name in the portfolio
        
        """
        return self.master_table[self.master_table['name']==\
                                  asset_name]['quantity'].iloc[0] < quantity
         
    
    def add(self, asset,  datetime= datetime.datetime.now(), 
            quantity = 0, unit='contract', 
            asset_type='future'): #tested
        """
        A function that add a new asset to the pool.
    
        Parameters
        ----------
        asset : str, Asset Object, list
            The asset to be added.
        datetime: datetime
            The datetime that the asset is added
        quantity: float, int
            The number of the same asset added. The default is 0.
        unit: str
            The unit name of the asset. The default is 'contract'.
        asset_type: str
            The type name of the asset. The default is 'future'.
        
        """
        #asset cannot be a list
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

        print("Add action activated", asset)
    
    def sub(self, asset,  datetime= datetime.datetime.today(),  
            asset_name="", quantity = 0, unit='contract', 
            asset_type='future'): #tested
        """
        A function that subtract an existing asset from the pool.
    
        Parameters
        ----------
        asset : str, Asset object, list
            The asset to be added.
        datetime: datetime
            The datetime that the asset is added
        quantity: float, int
            The number of the same asset added. The default is 0.
        unit: str
            The unit name of the asset. The default is 'contract'.
        asset_type: str
            The type name of the asset. The default is 'future'.
        
        """
        # check if it asset is an asset format
        if type(asset) == Asset:  
            # call the quantity from table
            asset_name = asset.__dict__['name']
            #print(asset.__dict__['quantity'])
            #print(self.table[self.table['name']== asset_name]['quantity'].iloc[0])
            
            # check if the total amount is higher than the subtraction amount
            if self.check_remainder(asset_name, asset.__dict__['quantity']):
            #if asset.__dict__['quantity'] > self.master_table[self.master_table['name']==\
            #                                  asset_name]['quantity'].iloc[0]: # tested
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
        
    def value(self, date_time, price_dict = PRICE_DICT,   
              size_dict = SIZE_DICT, dntr='USD'): #WIP
        """
        A function that return a dict with the price for each assets on 
        a particular date and time.
        
        Parameters
        ----------
        datetime: datetime object
        
        price_dict: dict
            A dictionary that contains the pricing data filename for each 
            assets. The default is PRICE_DICT.
        size_dict: dict
            A dictionary that contains the size (for example, number of barrels)
            contained in each assets. The default is SIZE_DICT.
        dntr: str
            The denomanator currency for calculating the value of each asset.
            The default is USD'.
            
        Returns
        ------_
        value_dict: dict
            A dictionary for the value of each assets for that time.
        """
        # price_table is a dict containing the pricing data files
        # read the value of the portfolio of a particular date
        
        value_dict = dict()
        
        print(self.pool, date_time)
        self.set_pool_window(self.__pool_datetime[0], date_time)

        for i, asset_name in enumerate(self.table['name']):
            
            # specia handling the denomator asset (usually a currency)
            if asset_name == dntr:
                value_dict[asset_name] = float(self.table['quantity'].iloc[0])
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
                target_time = date_time.strftime("%Y-%m-%d")
                _ , value = read.find_closest_price_date(sub_price_table, target_time=target_time)
                
                #value = float(sub_price_table[sub_price_table['Date'] == date_time]['Settle'].iloc[0])
                quantity = int(self.table['quantity'].iloc[i])
                
                #new way to do things
                #print('------------')
                #print(_, asset_name, quantity, float(value.iloc[0]), size)
                
                # storage
                value_dict[asset_name] = float(value.iloc[0])*quantity*size
        
        return value_dict
        
    def asset_value(self, asset_name, datetime, price_dict = PRICE_DICT,   
              size_dict = SIZE_DICT, dntr='USD'):
        """
        A function that return a dict with of a particular asset on 
        a particular date and time.
        
        Parameters
        ----------
        asset_name : str
            The name of the asset.
        datetime : datetime object
            The date and time of interest.

        Returns
        -------
        asset_value : float
            the asset value.

        """
        asset_value = self.value(datetime, price_dict = price_dict,   
                  size_dict = size_dict, dntr=dntr)[asset_name]
        return asset_value
            
    def total_value(self, datetime):
        """
        A function that return the total value of the entire portfolio on 
        a particular date and time.

        Parameters
        ----------
        datetime : datetime object
            The date and time of interest.

        Returns
        -------
        total_value : float
            the total value.

        """
        total_value = sum(self.value(datetime).values())
        return total_value

    @property
    def log(self): # tested
        """
        The attribute that log the changes in values of each assets across 
        all time.
        
        """
        # Use the keys from the master table to construct the columns
        #columns = list(self.master_table['name'])
        log = list()
        # then loop through the pool history and 
        for i, item in enumerate(self.pool):
            value_entry = self.value(item[0])
            #print('VE', item[0], value_entry)
            #log.loc[i] = pd.Series(value_entry)
            log.append(value_entry)

        # return a log of the values of each asset by time

        self._log = pd.DataFrame(log)
        return self._log
    
    def asset_log(self, asset_name): #tested
        """
        The log of the changes in values for a particular assets across 
        all time.
        
        """
        asset_log = self.log[asset_name]
        return asset_log

    def wipe_debt():
        
        return

    
