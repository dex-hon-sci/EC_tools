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
import time as time
# package import 
import pandas as pd

# EC_tools import
import EC_tools.utility as util
import EC_tools.read as read
from crudeoil_future_const import SIZE_DICT, HISTORY_DAILY_FILE_LOC

#PRICE_DICT = HISTORY_DAILY_FILE_LOC 
    
HISTORY_DAILY_PKL = util.load_pkl("/home/dexter/Euler_Capital_codes/EC_tools/data/pkl_vault/crudeoil_future_daily_full.pkl")
PRICE_DICT = HISTORY_DAILY_PKL 

#now we preload the price dict

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
        self._zeropoint = 0.0
        self._remainder_limiter = False
 
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
        #pool_df_interest = self.pool_df[(self.pool_df['datetime'] >= start_time) & 
        #                        (self.pool_df['datetime'] <= end_time)]
        pool_df_interest = self.pool_df.loc[(self.pool_df['datetime'] >= start_time) & 
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
# =============================================================================
#         values = [list(pool_type[i][1].__dict__.values()) 
#                                   for i in range(len(pool_type))]
#         keys = [list(pool_type[i][1].__dict__.keys()) 
#                                   for i in range(len(pool_type))][0]
# =============================================================================
        
        values = [list(pool_type[i][1].values()) 
                                  for i in range(len(pool_type))]
        keys = [list(pool_type[i][1].keys()) 
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
        baseline = self.master_table[self.master_table['name']==\
                                  asset_name]['quantity'].iloc[0] - self._zeropoint
            
        return baseline < quantity
         
    
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
            #asset = Asset(asset, quantity, unit, asset_type)
            asset = {'name': asset, 'quantity': quantity, 
                         'unit': unit, 'asset_type':asset_type, 'misc':{}}
        elif type(asset) == dict:
            pass
        
        self.__pool_asset.append(asset)   # save new asset
        self.__pool_datetime.append(datetime) #record datetime

        #print("Add action activated", asset)
    
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
        if type(asset) == dict:
            # call the quantity from table
            asset_name = asset['name']
            
            # check if the total amount is higher than the subtraction amount
            if self._remainder_limiter:
                if self.check_remainder(asset_name, asset['quantity']):
                    raise Exception('There is not enough {} to be subtracted \
                                    from the portfolio.'.format(asset_name))
            else:
                quantity = asset['quantity']
                unit = asset['unit']
                asset_type = asset['asset_type']
                pass
            new_asset = {'name': asset_name, 'quantity': quantity*-1, 
                         'unit': unit, 'asset_type':asset_type, 'misc':{}}

        if type(asset) == str: 
            # # search the dictionary to see what kind of asset is this
            # make a new asset
            asset_name = asset
            
            # make a new asset with a minus value for quantity
            new_asset = {'name': asset_name, 'quantity': quantity*-1, 
                         'unit': unit, 'asset_type':asset_type, 'misc':{}}
        
        self.__pool_asset.append(new_asset)   # save new asset
        self.__pool_datetime.append(datetime) #record datetime
        
    @util.time_it
    def value(self, date_time, price_dict = PRICE_DICT,   
              size_dict = SIZE_DICT, dntr='USD'): #WIP
        """
        A function that return a dict with the price for each assets on 
        a particular date and time.
        
        Parameters
        ----------
        datetime: datetime object
            The datetime for query.
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
        
        #print(self.pool, date_time)
        self.set_pool_window(self.__pool_datetime[0], date_time)

        for i, asset_name in enumerate(self.table['name']):
            # specia handling the denomator asset (usually a currency)
            if asset_name == dntr:
                dntr_value = float(self.table['quantity'].iloc[0])
                value_dict[asset_name] = float(self.table['quantity'].iloc[0])
                #print('Cashhh')
            else:
            
                # manage the size of the asset
                if size_dict == None:
                    size = 1
                else:
                    # Get the size of each asset
                    size = size_dict[asset_name]
                   
                #asset_price_filename = price_dict[asset_name]
                sub_price_table = price_dict[asset_name]
                #sub_price_table = read.read_reformat_Portara_daily_data(
                #                                        asset_price_filename)

                # The current version of this method only gets the price data iff 
                # it exist in the table, i.e. it does not get anything outside of the trading days
                target_time = date_time.strftime("%Y-%m-%d")
                value = sub_price_table['Open'][sub_price_table['Date'] == target_time].item()
                #value = sub_price_table.loc[target_time]['Open']
               # _ , value = read.find_closest_price_date(sub_price_table, 
               #                                          target_time=target_time)
                #print('value',value)
                #value = float(sub_price_table[sub_price_table['Date'] == date_time]['Settle'].iloc[0])
                quantity = int(self.table['quantity'].iloc[i])
                
                #new way to do things  
                #print('------------')
                #print(_, asset_name, quantity, float(value.iloc[0]), size)
                #print(asset_name, float(value.iloc[0])*quantity*size)
                # storage
                value_dict[asset_name] = float(value)*quantity*size

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

    def _make_log(self, simple_log = False):
        """
        An internal method to construct logs for the portfolio.
        """
        log = list()
        print("Generating Portfolio Log...")
        
        if simple_log:
        # simple_log make a log with only the inforamtion at the start of the day
            temp = [datetime.datetime.combine(dt.date(), datetime.time(0,0)) 
                                            for dt in self.pool_datetime]
            # reorganised the time_list because set() function scramble the order
            time_list = sorted(list(set(temp)))
            # Add an extra day to see what is the earning for the last day
            time_list = time_list + \
                            [time_list[-1]+datetime.timedelta(days=1)]

        else:
            time_list = self.pool_datetime
            time_list = time_list + [time_list[-1]+datetime.timedelta(days=1)]
            
        #then loop through the pool history and store them in log list 
        for i, item in enumerate(time_list):
            value_entry = self.value(item)
            value_entry["Total"] = sum(list(value_entry.values()))
            value_entry['Datetime'] = item

            #print('VE', item, value_entry)
            log.append(value_entry)
            
        # return a log of the values of each asset by time
        self._log = pd.DataFrame(log)
        
        #reorganise columns order
        asset_name_list = list(self.value(self.pool_datetime[-1]).keys())
        self._log = self._log[['Datetime', 'Total']+asset_name_list]
        
        print("Log is avalibale.")     
        
        self._log.sort_values(by="Datetime", inplace = True, ignore_index= True)
        return self._log
    
    @cached_property
    def log(self):
        """
        A simple log that only shows the Portfolio's value at 00:00:00 of the 
        day.

        Returns
        -------
        TYPE
            DESCRIPTION.

        """
        return self._make_log(simple_log=True)
    
    @cached_property
    def full_log(self):
        """
        A full log that only shows every entry in the changes in the 
        Portfolio's value.

        Returns
        -------
        TYPE
            DESCRIPTION.

        """
        return self._make_log(simple_log=False)
    

    def asset_log(self, asset_name): #tested
        """
        The log of the changes in values for a particular assets across 
        all time.
        
        """
        asset_log = self.full_log[asset_name]
        return asset_log

    def wipe_debt(self):
        
        return self.master_table


    
class PortfolioMetrics(Portfolio):
    def __init__():
        return
    def sharpe_ratio(self):
        return