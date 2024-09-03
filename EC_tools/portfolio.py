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
import re
import inspect
# package import
import pandas as pd
import numpy as np
from prettytable import PrettyTable

# EC_tools import
import EC_tools.utility as util
from EC_tools.asset import Asset
from EC_tools.bookkeep import Bookkeep
import EC_tools.read as read
from crudeoil_future_const import SIZE_DICT, HISTORY_DAILY_FILE_LOC, \
                                  SYMBOL_KEYWORDS_DICT, DAILY_DATA_PKL

# PRICE_DICT = HISTORY_DAILY_FILE_LOC
# now we preload the price dict
HISTORY_DAILY_PKL = util.load_pkl(DAILY_DATA_PKL)
PRICE_DICT = HISTORY_DAILY_PKL

__all__ = ['Portfolio', 'PortfolioLog', 'PortfolioMetrics']

__author__ = "Dexter S.-H. Hon"


class Portfolio(object):
    """
    This class manage everything related to the Portfolio.

    It contains the pool list which contain every transaction operating on this
    Portfolio.


    """

    def __init__(self):
        self.__pool_asset: list = []  # set pool to be a private attribute
        self.__pool_datetime: list = []
        self._pool: list = []
        self._pool_window: list = []
        self._position_pool: list = []
        self._position_pool_window: list = []
        self._table: pd.DataFrame = None
        self._master_table: pd.DataFrame = None
        self._zeropoint: float = 0.0  # The zero point value for the portfolio
        self._remainder_limiter: bool = True  # Controls the limitation
        # A dict that contains the remainder for each assets
        self._remainder_dict: dict = dict()
        
        self.wipe_debt_or_not: bool = False

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
        pool_df = pd.DataFrame(self.pool, columns=['datetime', 'asset'])
        return pool_df

    @property
    def pool_window(self):
        """
        A pool window given by a specific time intervals. This function 
        initialised the object. Use set_pool_window to set a particular 
        time frame.


        """
        # self._pool_window = self.pool
        return self._pool_window

    def set_pool_window(self,
                        start_time: datetime.datetime = datetime.datetime(1900, 1, 1),
                        end_time: datetime.datetime = datetime.datetime(2200, 12, 31)) -> None:
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
        # subtract the original datetime with them
        start_time_delta_array = np.array([abs(pool_dt - start_time) for i, pool_dt in
                                 enumerate(self.__pool_datetime)])
        end_time_delta_array = np.array([abs(pool_dt - end_time) for i, pool_dt in
                               enumerate(self.__pool_datetime)])
        # Find the index of the min() time delta
        # print(min(start_time_delta_list), min(end_time_delta_list))

        # print(start_time_delta_list, end_time_delta_list)
        # define a window of interest amount the pool object
        start_time_index = np.where(start_time_delta_array == min(start_time_delta_array))[0][0] 
        end_time_index = np.where(end_time_delta_array == min(end_time_delta_array))[0][-1] 

        self._pool_window = self.pool[start_time_index:end_time_index+1]

        # print(len(self._pool_window), len(self.pool[start_time_index:end_time_index+1]))

        return self._pool_window


    def set_position_pool_window(self,
                                 start_time: datetime.datetime = \
                                             datetime.datetime(1900, 1, 1),
                                 end_time: datetime.datetime = \
                                           datetime.datetime(2200, 12, 31)):
        
        position_time_list = [pos.open_time for pos in self.position_pool]
        
        start_time_delta_list = [abs(pool_dt - start_time) for pool_dt in
                                 position_time_list]
        end_time_delta_list = [abs(pool_dt - end_time) for pool_dt in
                               position_time_list]
        
        # define a window of interest amount the pool object
        start_time_index = start_time_delta_list.index(min(start_time_delta_list))
        end_time_index = end_time_delta_list.index(min(end_time_delta_list))


        self._position_pool_window = self.position_pool[start_time_index:\
                                                        end_time_index+1]
        
        return self._position_pool_window
    
    def position_pool_window(self):
        """
        A subset of position pool that is made by the set_position_pool_window
        method. 

        """
        return self._position_pool_window
    
    @property
    def position_pool(self):
        """
        The master position pool is a list that contains all the Position objects.
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
        values = [list(pool_type[i][1].values()) for i in range(len(pool_type))]
        keys = [list(pool_type[i][1].keys()) for i in range(len(pool_type))][0]

        # Load the inforamtion to self._table
        table = pd.DataFrame.from_records(data=values, columns=keys)
        #print('tabletable', table)
        
        for index, (val_name, misc) in enumerate(zip(table['name'], table['misc'])):
            # add more conditions with unit and type
            temp_df = table[(table['name'] == val_name) & (table['misc'] == misc)]

            # If the asset is unique in the pool, pass.
            if len(temp_df) == 1:
                pass
            # If the asset is not unique, perform the condesation action
            elif len(temp_df) > 1:
                # print(list(temp_df['quantity']), sum(list(temp_df['quantity'])))
                # the summed quantity
                new_quantity = sum(list(temp_df['quantity']))

                # make new entry_dictionary
                new_entry_dict = {'name': temp_df['name'].iloc[0],
                                  'quantity': new_quantity,
                                  'unit': temp_df['unit'].iloc[0],
                                  'asset_type': temp_df['asset_type'].iloc[0],
                                  'misc': [temp_df['misc'].iloc[0]]}

                new_entry_dict = pd.DataFrame(
                    new_entry_dict, index=[len(table)])

                # store them in the lowest row
                table = pd.concat([table, new_entry_dict], ignore_index=False)

                # delete the old entries
                table.drop(list(temp_df.index), axis=0, inplace=True)

                # sort the table by 'name'
                table.sort_values(by='name')

                # reset the indices
                table.reset_index(drop=True, inplace=True)

        return table
    
    @staticmethod
    def _wipe_debt(table_type) -> None:
        """
        An internal function to wipe the debt in tables if the debt asset has
        a quantity of 0.

        Parameters
        ----------
        table_type : TYPE
            The type of tables, it can be either self.table or 
            self.master_table.

        Returns
        -------
        DataFrame
            new_table.

        """
        index_list = []
        # This assume misc contains a set. We may need to change this into dict later
        for i in range(len(table_type)):
            if table_type['quantity'].iloc[i] == 0 and \
               'debt' in table_type['misc'].iloc[i]:
                index_list.append(i)
                
        new_table = table_type.drop(index_list)
        new_table.reset_index(drop=True)
        
        return new_table

    @property
    def table(self) -> pd.DataFrame:  # tested
        """
        An attribute that show a table of all the assets in the portfolio.

        The table operates on pool_window, meaning it obly shows the assets 
        listed in the pool_window list. Please make sure you are setting 
        the time window correctly.

        """
        if self._pool_window == None:
            raise Exception("pool_window not found. Use either master_table or \
                            define a pool_window for viewing first")

        self._table = self._make_table(self.pool_window)
        
        if self.wipe_debt_or_not == True:
            self._table = self._wipe_debt(self._table)
            
        self._table.reset_index(drop=True)
        
        return self._table

    @property
    def master_table(self) -> pd.DataFrame:  # tested
        """
        An attribute that show a table of all the assets in the portfolio.

        The table operates on pool, meaning it obly shows the assets 
        listed in the pool list, i.e., it shows assets across all time.

        """
        self._master_table = self._make_table(self.pool)
        
        if self.wipe_debt_or_not == True:
            self._master_table = self._wipe_debt(self._master_table)
            
        self._master_table.reset_index(drop=True)

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
        bool: whether it has more cash or asset than the zeropoint

        """
        baseline = self._remainder_dict[asset_name] - self._zeropoint

        return baseline < quantity
    
    @property
    def remainder_dict(self) -> dict:
        """
        It contains a dictionary of how much remainder of each asset is remained
        in the portfolio, essentially a counter for the ease of calculation.
        
        Returns
        -------
        dict
            remainder_dict.

        """
        
        return self._remainder_dict
    
    def add(self,
            asset: Asset | str | dict,
            datetime: datetime.datetime = datetime.datetime.now(),
            quantity: int | float = 0,
            unit: str = 'contract',
            asset_type: str = 'future') -> None:  # tested
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
        # asset cannot be a list
        # check if it asset is an asset format
        if type(asset) == Asset:
            asset_name = asset.name
        elif type(asset) == str:
            # # search the dictionary to see what kind of asset is this
            # (potential improvement)
            # make a new asset
            # asset = Asset(asset, quantity, unit, asset_type)
            asset = {'name': asset, 'quantity': quantity,
                     'unit': unit, 'asset_type': asset_type, 'misc': {}}
            asset_name = asset['name']
            asset_quantity = asset['quantity']

        elif type(asset) == dict:
            asset_name = asset['name']
            asset_quantity = asset['quantity']

        # Add the asset into the pool
        self.__pool_asset.append(asset)   # save new asset
        self.__pool_datetime.append(datetime)  # record datetime

        # Add the latest quantity to the remainder_dict for remainder check
        self._add_to_remainder_dict(asset_name, asset_quantity)

    def sub(self,
            asset: Asset | str | dict,
            datetime: datetime.datetime = datetime.datetime.today(),
            asset_name: str = "",
            quantity: int | float = 0,
            unit: str = 'contract',
            asset_type: str = 'future') -> None:  # tested
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
            
            quantity = asset['quantity']
            unit = asset['unit']
            asset_type = asset['asset_type']
                

        if type(asset) == str:
            # # search the dictionary to see what kind of asset is this
            # make a new asset
            asset_name = asset

        # make a new asset with a minus value for quantity
        new_asset = {'name': asset_name, 'quantity': quantity*-1,
                     'unit': unit, 'asset_type': asset_type, 'misc': {}}
        asset_quantity = new_asset['quantity']

        #print('sub','new_asset', new_asset)

        self.__pool_asset.append(new_asset)   # save new asset
        self.__pool_datetime.append(datetime)  # record datetime

        # Add the latest quantity to the remainder_dict for remainder check
        self._add_to_remainder_dict(asset_name, asset_quantity)

    def value(self,
              date_time: datetime.datetime,
              price_dict: dict = PRICE_DICT,
              size_dict: dict = SIZE_DICT,
              dntr: str = 'USD',
              price_proxy: str = "Settle",
              time_proxy: str = 'Date'):  # WIP
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
        unique_name_list = list(set([asset['name']
                                for asset in self.__pool_asset]))
        quantity_dict = {unique_name: 0 for unique_name in unique_name_list}

        # loop and get the quantity of each assets
        for i, (_, asset) in enumerate(self.pool_window):
            quantity_dict[asset['name']] = quantity_dict[asset['name']] + \
                asset['quantity']

        value_dict = dict()
        for i, (dt, asset) in enumerate(self.pool_window):
            if asset['name'] == dntr:
                value_dict[dntr] = quantity_dict[dntr]
            else:
                if size_dict == None:  # manage the size of the asset
                    size = 1
                else: # Get the size of each asset
                    size = size_dict[asset['name']]

                sub_price_table = price_dict[asset['name']]
                target_time = date_time.strftime("%Y-%m-%d")
                # print('price:', sub_price_table[price_proxy][sub_price_table[time_proxy] == \
                #                                      target_time])

                # query search for the price of an asset of the date of interest
                price = sub_price_table[price_proxy][sub_price_table[time_proxy] ==
                                                     target_time].item()
                quantity = quantity_dict[asset['name']]
                value_dict[asset['name']] = float(price)*quantity*size

        return value_dict

    def asset_value(self,
                    asset_name: str,
                    datetime: datetime.datetime,
                    price_dict: dict = PRICE_DICT,
                    size_dict: dict = SIZE_DICT,
                    dntr: str = 'USD') -> float:
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
        asset_value = self.value(datetime, price_dict=price_dict,
                                 size_dict=size_dict, dntr=dntr)[asset_name]
        return asset_value

    def total_value(self,
                    datetime: datetime.datetime,
                    dntr: str = 'USD') -> float:
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
        total_value = sum(self.value(datetime, dntr=dntr).values())
        return total_value


@dataclass
class PortfolioLog(Portfolio):
    """
    A class that produce A full transaction Log for the Portfolio.
    Note that this method generates a log that contains the changes in Portfolio
    values.
    
    The key differences between PortfolioLog and Portfolio is that the former 
    handles the prices for assets at a given time and the trading records of 
    the Porfolio while later only handles what is contained in the Portfolio.


    """
    portfolio: Portfolio = None
    _log: pd.DataFrame = None
    tradebook_filename = str = ""

    @util.time_it
    def _make_log(self, simple_log=False):  # Decrepated time complexity too large
        """
        An internal method to construct logs for the portfolio.
        """
        log = list()
        print("Generating Portfolio Log...")

        if simple_log:
            # simple_log make a log with only the inforamtion at the start of the day
            temp = [datetime.datetime.combine(dt.date(), datetime.time(0, 0))
                    for dt in self.portfolio.pool_datetime]
            # reorganised the time_list because set() function scramble the order
            # Use the set function to output a unique datetime list
            time_list = sorted(list(set(temp)))
            # Add an extra day to see what is the earning for the last day
            # time_list = time_list + \
            #                [time_list[-1]+datetime.timedelta(days=1)]

        else:
            time_list = self.portfolio.pool_datetime
        # print(time_list)
        # Add an entry at the end of the day to see what is the earning for the last day
        last_dt = datetime.datetime.combine(
            time_list[-1].date(), datetime.time(23, 59))
        time_list = time_list + [last_dt]

        # then loop through the pool history and store them in log list
        for item in time_list:
            #print('time', item)

            value_entry = self.portfolio.value(item)
            value_entry["Total"] = sum(list(value_entry.values()))
            value_entry['Datetime'] = item

            print('VE', item, value_entry)
            log.append(value_entry)

        # return a log of the values of each asset by time
        self._log = pd.DataFrame(log)

        # reorganise columns order
        asset_name_list = list(self.portfolio.value(
            self.portfolio.pool_datetime[-1]).keys())

        self._log = self._log[['Datetime', 'Total']+asset_name_list]

        print("Log is avalibale.")

        self._log.sort_values(by="Datetime", inplace=True, ignore_index=True)
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

    def asset_log(self, asset_name) -> pd.DataFrame:  # tested
        """
        The log of the changes in values for a particular assets across 
        all time.

        """
        asset_log = self.log[asset_name]
        return asset_log

    def asset_full_log(self, asset_name) -> pd.DataFrame:  # tested
        """
        The log of the changes in values for a particular assets across 
        all time.

        """
        asset_log = self.full_log[asset_name]
        return asset_log

    def render_tradebook(self,
                          save_or_not: bool = True):

        position_pool = self.portfolio.position_pool
        book = Bookkeep(bucket_type='backtest')

        custom_list0 = ['Trade_ID', 'Direction', 'Commodity', 'Price_Code',
                        'Entry_Date', 'Entry_Datetime', 'Entry_Price',
                        'Exit_Date', 'Exit_Datetime', 'Exit_Price',
                        'Trade_Return', 'Trade_Return_Fraction', 'value']
        #, 'Scaled_Return']  # , 'Risk_Reward_Ratio', 'strategy_name']

        trade_PNL = book.make_bucket(custom_keywords_list=custom_list0)

        def select_func_fill(x): return position_pool[x].status.value == 'Filled'
        
        PP = read.group_trade(position_pool,
                              select_func=select_func_fill)
        for i, ele in enumerate(PP):
            trade_id = ele[0].pos_id
            direction = re.sub(r'\-(.*)', '', ele[0].pos_type)
            symbol = ele[0].get_obj['name']
            commodity_name = SYMBOL_KEYWORDS_DICT[symbol]
            entry_date = ele[0].fill_time.date()
            entry_datetime = ele[0].fill_time
            entry_price = ele[0].price
            exit_date = ele[1].fill_time.date()
            exit_datetime = ele[1].fill_time
            exit_price = ele[1].price
            
            if direction == "Long":
                trade_return = exit_price - entry_price
                trade_return_fraction = (exit_price - entry_price) / entry_price
                #scaled_return = 000

                
            elif direction == "Short":
                trade_return = entry_price - exit_price
                trade_return_fraction = (entry_price - exit_price) / exit_price
                
            
            
            data = [trade_id, direction, commodity_name, symbol,
                    entry_date, entry_datetime, entry_price,
                    exit_date, exit_datetime, exit_price,
                    trade_return, trade_return_fraction, value]

            trade_PNL = book.store_to_bucket_single(data)

        trade_PNL = pd.DataFrame(trade_PNL)
        trade_PNL = trade_PNL.sort_values(by='Trade_ID')  # sort by ID

        if save_or_not:
            trade_PNL.to_csv(self.tradebook_filename, index=False)

        return trade_PNL
    
    
    def render_tradebook_xlsx(self):
        tradebook_xlsx = read.render_PNL_xlsx([self.tradebook_filename],
                                              return_proxy='Trade_Return')
        return tradebook_xlsx

    @property
    def tradebook(self) -> pd.DataFrame:
        """
        The tradebook made using the position pool.

        Returns
        -------
        DataFrame
            Tradebook.

        """
        return self.render_tradebook(save_or_not=False)
    
    def full_tradebook(self) -> pd.DataFrame:
        
        return self.render_tradebook(save_or_not=False)

    def add_column(self):
        pass



@dataclass
class PortfolioMetrics(Portfolio):
    """
    A class that generate all Portfolio metrics.
    Generally, the Portfolio Metrics method returns a tuple of 
    (value, unit, metric_name).
    
    """
    _portfolio: Portfolio

    def __post_init__(self):
        self.portfolio_log = PortfolioLog(self._portfolio)
        self.tradebook = self.portfolio_log.tradebook
        
# =============================================================================
#         
#     @property
#     def portfolio(self):
#         return self._portfolio
#     
# =============================================================================
    def _load_filled_position_pool(self) -> list:
        """
        A function to load only the filled position to a list
        
        Returns
        -------
        list
            Filled position list
        """
        position_pool = self._portfolio.position_pool

        def select_func_fill(x): 
            return position_pool[x].status.value == 'Filled'
        
        PP = read.group_trade(position_pool,
                              select_func=select_func_fill)
        return PP
    
    def start_capital(self, 
                      dntr: str = 'USD', 
                      cash_only: bool = False) -> tuple[float, str, str]:
        
        first_date = self._portfolio.pool_datetime[0]

        if not cash_only:
            first_entry_total_value = self._portfolio.total_value(
                first_date, dntr=dntr)
            
        return first_entry_total_value, dntr, 'Starting Capital'
    
    def end_capital(self, 
                    dntr: str = 'USD', 
                    cash_only: bool = False) -> tuple[float, str, str]:
        
        last_date = self._portfolio.pool_datetime[-1]

        if not cash_only:
            last_entry_total_value = self._portfolio.total_value(
                last_date, dntr=dntr)
        return last_entry_total_value, dntr,  "Final Capital"
    
    def period(self, 
               time_proxy: str = 'Exit_Date', 
               unit: str = "Days") -> tuple[int, str, str]:
        """
        Total Days of trading

        Parameters
        ----------
        time_proxy : str, optional
            Column name for the time. The default is 'Exit_Date'.
        unit : str, optional
            Unit. The default is "Days".

        """
        
        period = self.tradebook[time_proxy].iloc[-1] - self.tradebook[time_proxy].iloc[0]
        return period, unit, "Period"

    def total_trades(self) -> tuple[int, str, str]:
        """
        The total number of trades in the tradebook.

        """
        return len(self.tradebook), '#', "Total Trades"

    def total_fee_paid(self) -> float: # WIP
        position_pool = self._portfolio.position_pool

        def select_func_fill(x): 
            return position_pool[x].status.value == 'Filled'
        
        PP = read.group_trade(position_pool,
                              select_func=select_func_fill)

        total_fee_dict = dict()
        total_fee = 0
        for ele in PP:
            # Assuming the second item in each element contains the fee
            total_fee = total_fee + ele[1].fee['quantity']

        return total_fee, '', 'Total Fee Paid'

    def total_returns(self, dntr='USD') -> tuple[float,str]:
        """
        The total returns given a currency denomanator 

        Parameters
        ----------
        dntr : str, optional
            Currency denomanator. The default is 'USD'.

        Returns
        -------
        tuple[float,str,str]
            total returns, unit, metric name.

        """
        first_date = self._portfolio.pool_datetime[0]
        last_date = self._portfolio.pool_datetime[-1]

        first_entry_total_value = self._portfolio.total_value(
            first_date, dntr=dntr)
        last_entry_total_value = self._portfolio.total_value(
            last_date, dntr=dntr)

        return (last_entry_total_value - first_entry_total_value), dntr, \
               "Total Returns"

    def total_returns_fraction(self, unit: str = '%') -> tuple[float,str, str]:
        """
        The total returns by fraction (percentage).

        Parameters
        ----------
        unit : str, optional
            Percentage. The default is '%'.

        Returns
        -------
        tuple[float,str]
            total return

        """
        first_date = self._portfolio.pool_datetime[0]
        last_date = self._portfolio.pool_datetime[-1]

        first_entry_total_value = self._portfolio.total_value(first_date)
        last_entry_total_value = self._portfolio.total_value(last_date)
        
        #print(first_entry_total_value, last_entry_total_value)

        return 100*(last_entry_total_value - first_entry_total_value) / \
               first_entry_total_value, unit, "Total Returns"

    def win_rate(self, return_proxy: str = "Trade_Return", unit: str = "%") -> \
                 tuple[float, str, str]:
        """
        The win rate by percentage.

        Parameters
        ----------
        return_proxy : str, optional
            The column name to query in the tradebook. 
            The default is "Trade_Return".
        unit : str, optional
            The Unit percentage. The default is "%".

        Returns
        -------
        tuple[float,str]
            Win Rate.

        """
        win_trades = sum(
            1 for i in self.tradebook[return_proxy].to_list() if i >= 0)
        lose_trades = sum(
            1 for i in self.tradebook[return_proxy].to_list() if i < 0)

        return (win_trades/(win_trades+lose_trades))*100, unit, "Win Rate"

    def profit_factor(self, return_proxy: str = "Trade_Return") -> \
        tuple[float, str, str]:
        """
        The Profit factor (Money Won /Money Lose)

        Parameters
        ----------
        return_proxy : str, optional
            The column name to query in the tradebook. 
            The default is "Trade_Return".

        Returns
        -------
        float
            The profit factor.

        """

        win_trades_val = sum(i for i in self.tradebook[return_proxy].to_list()
                             if i >= 0)
        lose_trades_val = sum(i for i in self.tradebook[return_proxy].to_list()
                              if i < 0)
        # print(win_trades_val, lose_trades_val)
        return abs(win_trades_val)/abs(lose_trades_val), '', 'Profit Factor'

    def total_open_positions(self) -> tuple[int, str, str]: #WIP
        position_pool = self._portfolio.position_pool
        
        trade_pool = read.group_trade(position_pool)
        
        total_open_pos = sum(1 for pos in trade_pool 
                             if pos[0].status.value == 'Filled' and 
                                pos[1].status.value == 'Pending' and
                                pos[2].status.value == 'Pending' and
                                pos[3].status.value == 'Pending')
        
        return total_open_pos, '#', 'Total Open Positions'
    
    def total_close_positions(self): 
        position_pool = self._portfolio.position_pool
        
        # Group the trades by ID and Filled status
        trade_pool = read.group_trade(position_pool, select_func= 
                                      lambda x : position_pool[x].status.value 
                                      == 'Filled')
        
        total_open_pos = sum(1 for pos in trade_pool if len(pos) == 2)
        
        return total_open_pos, '#', 'Total Close Positions'

    def avg_trade_return(self, 
                         return_proxy: str = "Trade_Return", 
                         unit: str = 'USD') -> tuple[str,str]:
        """
        A method that calculate average trade return

        Parameters
        ----------
        return_proxy : str, optional
            DESCRIPTION. The default is "Trade_Return".
        unit : str, optional
            The unit relies on user-input. 
            The default is 'USD'.

        Returns
        -------
        tuple[str,str]
            The average trade return and the currency unit.

        """
        
        filled_pos_list = self._load_filled_position_pool()
    
        trade_return = np.array([trade for trade 
                                 in self.tradebook[return_proxy].to_list()])
        trade_size = np.array([trade[1].size for trade in filled_pos_list])
        trade_quantity =  np.array([trade[1].get_obj['quantity'] 
                                    for trade in filled_pos_list])
        
        daily_return_amount = trade_return*trade_size*trade_quantity
        return np.average(daily_return_amount), unit, 'Average Trade Return'
    
    #def _daily_exposure(self):
    #    return

    def sharpe_ratio(self,
                     return_proxy: str = "Trade_Return",
                     riskfree_rate: float | list = 0.05) -> float:
        """
        The Sharpe Ratio (S).
        
            S = E(R_p - R_f)/std(S_p)

        Parameters
        ----------
        return_proxy : str, optional
            The column name to query in the tradebook. 
            The default is "Trade_Return".
        riskfree_rate : float | list, optional
            The proxy for risk-free rate. 
            The default is 0.05. Assuming 5 % yield in 5-years treasurey bond.

        Returns
        -------
        float
            The Sharpe Ratio.

        """
        #trade_return = self.tradebook[return_proxy].to_numpy()
        filled_pos_list = self._load_filled_position_pool()
        
        
        direction = np.array([trade for trade 
                                 in self.tradebook["Direction"].to_list()])
        
        entry_price = np.array([trade for trade 
                                 in self.tradebook["Entry_Price"].to_list()])

        exit_price = np.array([trade for trade 
                                         in self.tradebook["Exit_Price"].to_list()])

        #print("filled_pos_list", filled_pos_list[0:2])
        trade_return = np.array([trade for trade 
                                 in self.tradebook["Trade_Return"].to_list()])

        trade_return_fraction = np.array([trade for trade 
                                 in self.tradebook["Trade_Return_Fraction"].to_list()])
        
       # trade_open = np.array([trade[0].give_obj['quantity'] for trade in filled_pos_list])
       # trade_close = np.array([trade[1].give_obj['quantity'] for trade in filled_pos_list])
        
      #  print('trade_open', trade_open, 'trade_close', trade_close)
         
        trade_size = np.array([trade[1].size for trade in filled_pos_list])
        trade_quantity =  np.array([trade[1].get_obj['quantity'] 
                                    for trade in filled_pos_list])
        
        daily_return_amount = trade_return*trade_size*trade_quantity
        cumsum = np.cumsum(daily_return_amount)
        cumsum_growth = (cumsum[1:-1] - cumsum[0:-2])/cumsum[0:-2]
        
        print('entry_price', entry_price)
        print('exit_price', exit_price)
        print('trade_return', trade_return)
        print("trade_return_fraction", trade_return_fraction)
        print('max, min', max(trade_return_fraction), min(trade_return_fraction))
        print('daily_return_amount', daily_return_amount)
        print('cumsum', cumsum, len(cumsum))
        print('cumsum_growth', cumsum_growth, len(cumsum_growth))
        print("self.total_returns_fraction()[0]*0.01", self.total_returns_fraction()[0]*0.01)
        print('std(cumsum_growth)', np.std(cumsum_growth))
        
       # trade_return_fraction = (trade_close-trade_open)/trade_open
        
        #print('daily_return_amount', daily_return_amount, trade_close-trade_open)
        #print('trade_return_fraction', trade_return_fraction)
        
        #riskfree_rate = np.repeat(riskfree_rate, len(daily_return_amount))
        #sharpe_ratio = (self.total_returns_fraction()[0]*0.01 - riskfree_rate) / \
        #               np.std(daily_return_amount)
        sharpe_ratio = (self.total_returns_fraction()[0]*0.01-riskfree_rate)/\
                       np.std(cumsum_growth)**0.5
        return sharpe_ratio, '', 'Sharpe Ratio' 
    # so far it is the wrong number because the growth of cumsum is corss-asset, 
    # the return should be calculated using per day basis not per trade/

    def calmar_ratio(self):
        return

    def omega_ratio(self):
        return

    def sortino_ratio(self):
        return

    @classmethod
    def make_full_data(cls):
        # Calculate all metrics related to thid portfolio
        full_data = dict()

        attr_name = [value for value in dir(cls) if value not 
                     in dir(Portfolio) and value[0] != '_' 
                     and value[0:4] != 'make']
        
        attrs = (getattr(cls, name) for name in attr_name)

        #methods = filter(inspect.ismethod, attrs)
        
        for attr, name in zip(attrs, attr_name):
            print(attr, name)
            #df = method(cls)
            #full_data[name] = df
            
        print(attr_name, attrs)
        #full_data = {name: getattr(cls, name)() for name in attr_name}
        print(full_data)
        return full_data

    def make_full_report(self):
        print('Period [{}]'.format(self.period()[1]), self.period()[0])
        print("Initial Capital [{}]".format(self.start_capital()[1]), 
              self.start_capital()[0])
        print("Final Capital [{}]".format(self.end_capital()[1]), 
              self.end_capital()[0])  
        print('Total Trades [{}]'.format(self.total_trades()[1]), self.total_trades()[0])
        print('Total Fee []', self.total_fee_paid())
        print('Total Returns [{}]'.format(self.total_returns()[1]),
              self.total_returns()[0])
        print('Total_returns [{}]'.format(self.total_returns_fraction()[1]),
              self.total_returns_fraction()[0])
        print('win_rate [{}]'.format(self.win_rate()[1]), self.win_rate()[0])
        print('Profit Factor', self.profit_factor())
        print('Total Open Positions [{}]'.format(self.total_open_positions()[1]), 
              self.total_open_positions()[0])
        print('total Close Positions [{}]'.format(self.total_close_positions()[1]), 
              self.total_close_positions()[0])
        print('Average Trade Return [{}]'.format(self.avg_trade_return()[1]), 
              self.avg_trade_return()[0])
        print('Sharpe Ratio (#sigma not stable)', 
              self.sharpe_ratio()[0])

        x = PrettyTable()
        
        #print(x)
    
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
