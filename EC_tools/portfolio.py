#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May  6 08:55:17 2024

@author: dexter
"""
# python import
from dataclasses import dataclass, field
from functools import cached_property
import datetime as datetime
import time as time
# package import 
import pandas as pd

# EC_tools import
import EC_tools.utility as util
from EC_tools.bookkeep import Bookkeep
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
    # We can abnadon this and just use a dict for asset
    
    """
    name: str  # note that future countract should be written in the CLM24 format
    quantity: int or float
    unit: str
    asset_type:str 
    misc: dict[str] = field(default_factory=dict)
    

class Portfolio(object):
    """
    This class manage everything related to the Portfolio.
    
    It contains the pool list which contain every transaction operating on this
    Portfolio.
    
    
    """
    
    def __init__(self):
        self.__pool_asset: list = [] # set pool to be a private attribute
        self.__pool_datetime: list = []
        self._pool: list = []
        self._pool_window: list = []
        self._position_pool: list = []
        self._table: list = []
        self._master_table: pd.DataFrame = None
        self._zeropoint: float = 0.0 # The zero point value for the portfolio
        self._remainder_limiter: bool = False # Controls the limitation
        self._remainder_dict: dict = dict() # A dict that contains the remainder for each assets
 
    @property
    def pool_asset(self) -> list[dict]:
        """
        A list that contains the the added assets.

        """
        return self.__pool_asset
    
    @property
    def pool_datetime(self) -> list[datetime.datetime]:
        """
        A list that contains the corresponding datetime where asset is added

        """
        return self.__pool_datetime
    
    @property
    def pool(self) -> list[tuple]: 
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
        #self._pool_window = self.pool
        return self._pool_window
    
    def set_pool_window(self, 
                        start_time: datetime.datetime = datetime.datetime(1900,1,1), 
                        end_time: datetime.datetime = datetime.datetime(2200,12,31)) -> None:
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
        # make a list of start_time and end_time
        #start_time_list = [start_time for i, _ in enumerate(self.__pool_datetime)]
        #end_time_list = [end_time for i, _ in enumerate(self.__pool_datetime)]
        
        # subtract the original datetime with them
        start_time_delta_list = [abs(pool_dt - start_time) for i, pool_dt in 
                                 enumerate(self.__pool_datetime)]
        end_time_delta_list = [abs(pool_dt - end_time) for i, pool_dt in 
                               enumerate(self.__pool_datetime)]
        # Find the index of the min() time delta
        ##print(min(start_time_delta_list), min(end_time_delta_list))
        
        #print(start_time_delta_list, end_time_delta_list)
        # define a window of interest amount the pool object
        start_time_index = start_time_delta_list.index(min(start_time_delta_list))
        end_time_index = end_time_delta_list.index(min(end_time_delta_list))
        
        ##print(start_time_index, end_time_index)
        
        self._pool_window = self.pool[start_time_index:end_time_index+1]
        
        ##print(len(self._pool_window), len(self.pool[start_time_index:end_time_index+1]))
        
        return self._pool_window
    
    @property
    def position_pool(self):
        """
        The position pool is a list that contains the Position objects.
        This can be used to construct trading records using the PortfolioLog
        class and its method

        """
        return self._position_pool
    
    @staticmethod
    def _make_table(pool_type: list) -> pd.DataFrame:
        """
        A static method that create a datafreame table using either pool_window
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
        # The function operate on the previously defined pool_window      
        values = [list(pool_type[i][1].values()) 
                                  for i in range(len(pool_type))]
        keys = [list(pool_type[i][1].keys()) 
                                  for i in range(len(pool_type))][0]
                
        # Load the inforamtion to self._table
        table = pd.DataFrame.from_records(data = values, columns = keys)
        
        # Handle repeating aseet type
        for index, (val_name, misc) in enumerate(zip(table['name'], table['misc'])):
            # add more conditions with unit and type
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
    def table(self) -> pd.DataFrame: # tested
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
    def master_table(self) -> pd.DataFrame: #tested
        """
        An attribute that show a table of all the assets in the portfolio.
        
        The table operates on pool, meaning it obly shows the assets 
        listed in the pool list, i.e., it shows assets across all time.
        
        """
        self._master_table  = self._make_table(self.pool)
        return self._master_table
    
    def _add_to_remainder_dict(self, 
                               asset_name: str, 
                               asset_quantity: int | float) -> None:
        """
        An internal method to add to the reaminder_dict every time there is 
        a 'add' or 'sub' action operating on the pool attributes.

        Parameters
        ----------
        asset_name : str
            The name of the asset.
        asset_quantity : int or float
            The quantity of the asset.

        Returns
        -------
        None.

        """
        # Add a new entry in the remainder_dict if the asset does not exist in
        # the Portfolio
        if asset_name not in self._remainder_dict:
            self._remainder_dict[asset_name] = asset_quantity
        # If it is already there, add the quantity.
        else: 
            new_quantity = asset_quantity 
            self._remainder_dict[asset_name] = self._remainder_dict[asset_name] +\
                                                new_quantity
         
            
    def check_remainder(self, 
                        asset_name: str, 
                        quantity: int | float) -> bool:
        """
        A function that check the remainder if there are enough asset of a 
        particular name in the portfolio.
        
        Parameters
        ----------
        asset_name : str
            The name of the asset.
        asset_quantity : int or float
            The quantity of the asset.
            
        Returns
        -------
        bool: whether
        
        """
        baseline = self._remainder_dict[asset_name] - self._zeropoint
            
        return baseline < quantity
         
    
    def add(self, 
            asset: Asset | str | dict,  
            datetime: datetime.datetime = datetime.datetime.now(), 
            quantity: int | float = 0, 
            unit: str ='contract', 
            asset_type: str ='future') -> None: #tested
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
            
        Returns
        -------
        None.
        
        """
        #asset cannot be a list
        # check if it asset is an asset format
        if type(asset) == Asset:
            asset_name = asset.name
        elif type(asset) == str: 
            # # search the dictionary to see what kind of asset is this 
            # (potential improvement)
            # make a new asset
            #asset = Asset(asset, quantity, unit, asset_type)
            asset = {'name': asset, 'quantity': quantity, 
                         'unit': unit, 'asset_type':asset_type, 'misc':{}}
            asset_name = asset['name']
            asset_quantity = asset['quantity']
            
        elif type(asset) == dict:
            asset_name = asset['name']
            asset_quantity = asset['quantity']

        # Add the asset into the pool
        self.__pool_asset.append(asset)   # save new asset
        self.__pool_datetime.append(datetime) #record datetime
        
        # Add the latest quantity to the remainder_dict for remainder check
        self._add_to_remainder_dict(asset_name, asset_quantity)
    
    def sub(self, 
            asset: Asset | str | dict,  
            datetime: datetime.datetime = datetime.datetime.today(),  
            asset_name: str = "", 
            quantity: int | float = 0, 
            unit: str = 'contract', 
            asset_type: str = 'future') -> None: #tested
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
        
        Returns
        -------
        None.

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
            asset_quantity = new_asset['quantity']

        if type(asset) == str: 
            # # search the dictionary to see what kind of asset is this
            # make a new asset
            asset_name = asset
            
            # make a new asset with a minus value for quantity
            new_asset = {'name': asset_name, 'quantity': quantity*-1, 
                         'unit': unit, 'asset_type':asset_type, 'misc':{}}
            asset_quantity = new_asset['quantity']
        
        self.__pool_asset.append(new_asset)   # save new asset
        self.__pool_datetime.append(datetime) # record datetime
        
        # Add the latest quantity to the remainder_dict for remainder check
        self._add_to_remainder_dict(asset_name, asset_quantity)

    def value(self, 
              date_time: datetime.datetime, 
              price_dict: dict = PRICE_DICT,   
              size_dict: dict = SIZE_DICT, 
              dntr: str ='USD', 
              price_proxy: str = "Settle",
              time_proxy: str = 'Date'): #WIP
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
        # Set a pool window for intrest
        self.set_pool_window(self.__pool_datetime[0], date_time)
        
        # Initialise dict, find unique asset_name
        unique_name_list = list(set([asset['name'] for asset in self.__pool_asset]))  
        quantity_dict = {unique_name: 0 for unique_name in unique_name_list}
        
        # loop and get the quantity of each assets
        for i, (_, asset)in enumerate(self.pool_window): 
            quantity_dict[asset['name']] =  quantity_dict[asset['name']] + \
                                                                asset['quantity'] 

        value_dict = dict() 
        for i, (dt, asset)in enumerate(self.pool_window): 
            if asset['name'] == dntr:
                value_dict[dntr] = quantity_dict[dntr]
            else:
                if size_dict == None: # manage the size of the asset
                    size = 1
                else:                     # Get the size of each asset
                    size = size_dict[asset['name']]
                    
                sub_price_table = price_dict[asset['name']]
                target_time = date_time.strftime("%Y-%m-%d")

                # query search for the price of an asset of the date of interest
                price = sub_price_table[price_proxy][sub_price_table[time_proxy] == \
                                                      target_time].item()
                quantity = quantity_dict[asset['name']]
                value_dict[asset['name']] = float(price)*quantity*size

        return value_dict

    def asset_value(self, 
                    asset_name: str, 
                    datetime: datetime.datetime, 
                    price_dict: dict = PRICE_DICT,   
                    size_dict: dict = SIZE_DICT, dntr: str = 'USD') -> float:
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
            
    def total_value(self, datetime: datetime.datetime) -> float:
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


    def wipe_debt(self):
        
        return self.master_table
    
@dataclass
class PortfolioLog(Portfolio):
    """
    A class that produce A full transaction Log for the Portfolio.
    Note that this method generates a log that contains the changes in Portfolio
    values, not the trade records.
    
    """
    portfolio: Portfolio = None
    _log: pd.DataFrame = None

    @util.time_it
    def _make_log(self, simple_log = False): #Decrepated time complexity too large
        """
        An internal method to construct logs for the portfolio.
        """
        log = list()
        print("Generating Portfolio Log...")
        
        if simple_log:
        # simple_log make a log with only the inforamtion at the start of the day
            temp = [datetime.datetime.combine(dt.date(), datetime.time(0,0)) 
                                            for dt in self.portfolio.pool_datetime]
            # reorganised the time_list because set() function scramble the order
            # Use the set function to output a unique datetime list
            time_list = sorted(list(set(temp)))
            # Add an extra day to see what is the earning for the last day
            #time_list = time_list + \
            #                [time_list[-1]+datetime.timedelta(days=1)]

        else:
            time_list = self.portfolio.pool_datetime
        print(time_list)
        # Add an entry at the end of the day to see what is the earning for the last day
        last_dt = datetime.datetime.combine(time_list[-1].date(), datetime.time(23,59))
        time_list = time_list + [last_dt]
        
            
        #then loop through the pool history and store them in log list 
        for item in time_list:
            print(item)
            value_entry = self.portfolio.value(item)
            value_entry["Total"] = sum(list(value_entry.values()))
            value_entry['Datetime'] = item

            #print('VE', item, value_entry)
            log.append(value_entry)
            
        # return a log of the values of each asset by time
        self._log = pd.DataFrame(log)
        
        #reorganise columns order
        asset_name_list = list(self.portfolio.value(\
                                    self.portfolio.pool_datetime[-1]).keys())
        
        
        self._log = self._log[['Datetime', 'Total']+asset_name_list]
        
        print("Log is avalibale.")     
        
        self._log.sort_values(by="Datetime", inplace = True, ignore_index= True)
        return self._log
    
    @cached_property
    def log(self) -> pd.DataFrame:
        """
        A simple log that only shows the Portfolio's value at 00:00:00 of the 
        day.

        Returns
        -------
        DataFrame
            Simple Log.

        """
        return self._make_log(simple_log=True)
    
    @cached_property
    def full_log(self) -> pd.DataFrame:
        """
        A full log that only shows every entry in the changes in the 
        Portfolio's value.

        Returns
        -------
        DataFrame
            Full Log.

        """
        return self._make_log(simple_log=False)
    

    def asset_log(self, asset_name) -> pd.DataFrame: #tested
        """
        The log of the changes in values for a particular assets across 
        all time.
        
        """
        asset_log = self.log[asset_name]
        return asset_log
    
    def asset_full_log(self, asset_name) -> pd.DataFrame: #tested
        """
        The log of the changes in values for a particular assets across 
        all time.
        
        """
        asset_log = self.full_log[asset_name]
        return asset_log
    
    def add_column(self):
        pass
    
    def render_tradebook(self):
        position_pool = self.portfolio.position_pool
        book = Bookkeep(bucket_type='backtest')
        custom_list0 = ['Trade_Id', 'Direction', 'Commodity', 'Price_Code', 
                        'Contract_Month',
                        'Entry_Date',	'Entry_Datetime', 'Entry_Price',
                        'Exit_Date','Exit_Datetime','Exit_Price',
                        'Return_Trades', 'Risk_Reward_Ratio', 'strategy_name']
        trade_PNL = book.make_bucket(custom_keywords_list=custom_list0)
        
        data = None
        trade_PNL = book.store_to_bucket_single(data)

        pass

    def render_xlsx(self):
        pass
    
class PortfolioMetrics(PortfolioLog):
    
    def __init__():
        return
    
    def avg_daily_return():
        return
    
    def total_trade():
        return
    
    def sharpe_ratio(self):
        return
    
    def calmar_ratio(self):
        return
    
    def omega_ratio(self):
        return
    
    def sortino_ratio(self):
        return
    
    def make_full_report(self):
        return 
    
    # Period (Days)
    # Start_cash
    # End_cash
    # Total Return [%]
    # Max Gross Exposure
    
# =============================================================================
# Benchmark Return [%]                        92987.961948
# Max Gross Exposure [%]                             100.0
# Total Fees Paid                             10991.676981
# Max Drawdown [%]                               70.734951
# Max Drawdown Duration                  760 days 00:00:00
# Total Trades                                          54
# Total Closed Trades                                   53
# Total Open Trades                                      1
# Open Trade PnL                              67287.940601
# Win Rate [%]                                   52.830189
# Best Trade [%]                               1075.803607
# Worst Trade [%]                               -29.593414
# Avg Winning Trade [%]                          95.695343
# Avg Losing Trade [%]                          -11.890246
# Avg Winning Trade Duration    35 days 23:08:34.285714286
# Avg Losing Trade Duration                8 days 00:00:00
# Profit Factor                                   2.651143
# Expectancy                                   10434.24247
# Sharpe Ratio                                    2.041211
# Calmar Ratio                                      4.6747
# Omega Ratio                                     1.547013
# Sortino Ratio                                   3.519894
# =============================================================================
