#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr  2 14:09:54 2024

@author: dexter
"""
import numpy as np
import pandas as pd
import datetime
import pickle

from typing import Union


import EC_tools.utility as util
from crudeoil_future_const import round_turn_fees, SIZE_DICT

# Argus API 
from EC_tools.ArgusPossibilityCurves2 import ArgusPossibilityCurves

__all__ = ['get_apc_from_server','read_apc_data','read_portara_daily_data', 
           'read_portara_minute_data','merge_portara_data',
           'portara_data_handling', 'extract_lag_data', 
           'read_reformat_Portara_minute_data', 'find_closest_price', 
           'find_crossover', 'find_minute_EES','open_portfolio',
           'render_PNL_xlsx']

__author__="Dexter S.-H. Hon"


def get_apc_from_server(username: str, password: str, 
                        start_date: str, end_date: str, 
                        categories: Union[str, list],
                        keywords: Union[str, list] = None, 
                        symbol: Union[str, list] = None) -> pd.DataFrame:
    """
    Use the ArgusPossibilityCurve.py script to extract the APCin the wide format from the server.
    Note that the latest version is 1.1.0 (21 March 2024).

    Parameters
    ----------
    username : str
        The username of your argus account.
    password : srt
        The password of your argus account.
    start_date : str
        The desired start date of the apc, it should be in tcategorieshe format of this:
            "2020-01-20"
    end_date : str
        The end date of the apc. Similar to the above.
    categories : str or list
        The asset name. It could be either 
        1) A string such as "Argus Nymex WTI month 1, Daily", or 
        2) A list that contain the list of asset names, like this:
            ['Argus Nymex WTI month 1, Daily', 
             'Argus Nymex Heating oil month 1, Daily', ...]
    keywords: str or list
        Keywords in the categories to look for. Same dimension as the categories input.
    symbol: str or list
        Symbols to write in the new column. Same dimension as the categories input.
        
    Returns
    -------
    apc_data : list
        A list that contain the spread of APC with the following collumns:
            Index(['Forecast Period', 'CATEGORY', '0.0025', '0.005', '0.0075', 
                   '0.01', '0.0125', '0.015', '0.0175', '0.02',
                   ...
                   '0.9775', '0.98', '0.9825', '0.985', '0.9875', '0.99', 
                   '0.9925', '0.995', '0.9975', 'symbol'], dtype='object', 
                  length=402)
    """
    print('symbol',symbol)
    
    # Check if categories and keywords varaible matches in dimension
    # Login and Authentication
    apc = ArgusPossibilityCurves(username=username, password=password)
    apc.authenticate()
    apc.getMetadataCSV(filepath="argus_latest_meta.csv")
    
    # Make the start and end date in the datetime.date format
    start_date = datetime.date(int(start_date[:4]), int(start_date[5:7]), int(start_date[8:10]))
    end_date = datetime.date(int(end_date[:4]), int(end_date[5:7]), int(end_date[8:10]))

    if type(categories) is str: # if the asset name input is a string, pull only one 

        # This retrieve the apc from the server
        apc_data = apc.getPossibilityCurves(start_date=start_date, end_date=end_date, categories=[categories])
        
        # Delete irrelavant columns
        apc_data = apc_data.drop(columns=['PUBLICATION_DATE', 'CONTINUOUS_FORWARD', 'PRICE_UNIT', 'TIMESTAMP'])
        apc_data.columns = ['Forecast Period'] + [i for i in apc_data.columns[1:]] # Add the term "APC" in each column

        # If no specific symbol input, use the name of the categories
        if symbol == None:
            symbol = categories
        else:
            pass
        
        # make a new column with nothing in it. Then write the short symbol
        apc_data['symbol'] = None  
        apc_data['symbol'] = np.where(apc_data['CATEGORY'].apply(lambda x: keywords in x), symbol, apc_data['symbol'])

        
    elif type(categories) is list: # if the asset name input is a list, pull a list of APC
        
        apc_data = apc.getPossibilityCurves(start_date=start_date, end_date=end_date, categories=categories)
            
        apc_data = apc_data.drop(columns=['PUBLICATION_DATE', 'CONTINUOUS_FORWARD', 'PRICE_UNIT', 'TIMESTAMP'])
        apc_data.columns = ['Forecast Period'] + [i for i in apc_data.columns[1:]]
        apc_data['symbol'] = None 
        
        # add new column with symbols corresponding to the keywords.
        for i, c in zip(keywords,symbol):
            
            apc_data['symbol'] = np.where(apc_data['CATEGORY'].apply(lambda x: i in x), c, apc_data['symbol'])
    
    # Drop the Category column
    apc_data = apc_data.drop(columns=['CATEGORY'])

    return apc_data

def read_apc_data(filename):
    # This function should be used in conjuction with get_apc_from_server(). 
    # The data should be pulled from the server using that function
    data = pd.read_csv(filename)

    return data    

# tested.
def read_portara_daily_data(filename:str, symbol:str, 
                            start_date:str, end_date:str, 
                            column_select: list[str] = 
                                        ['Settle', 'Price Code', 
                                         'Contract Symbol', 'Date only']) -> \
                            pd.DataFrame:
    """
    A generic function that read the Portara Data in a suitable form. 
    The function itself only read a single csv file at a time.

    LEGACY function from Abbe.
    
    Parameters
    ----------
    filename : str
        The filename in the correct address.
    symbol : str
        A short symbol for the asset.
    start_date: str
        The start date of the query. e.g, "2024-01-13".
    end_date: str
        The end date of the query. e.g, "2024-01-18".
    column_select: 1D list
        A list of columns name to select for in the master file. The default is 
        ['Settle', 'Price Code', 'Contract Symbol', 'Date only']
        
    Returns
    -------
    portara_dat: 2D pandas dataframe
        The Portara daily data
    """
    # Read downloaded data using panda
    portara_dat = pd.read_csv(filename)
    
    # A list of symbol
    portara_dat['symbol'] = symbol
    
    # Transform the date format from 20160104 to 2016-01-04 00:00:00 (panda timestamp)
    portara_dat['Date'] = portara_dat['Date'].apply(lambda x: str(x)[0:4] + '-' + str(x)[4:6] + '-' + str(x)[6:])
    portara_dat['Date'] = pd.to_datetime(portara_dat['Date'])
    portara_dat['Date only'] = portara_dat['Date'] #2016-01-04 00:00:00 format
    
    # Datetime beyond 2020-12-14 is accepted beyond 2020-12-14
    # Select datetime between start_date and end_date
    bools = portara_dat['Date'].apply(lambda x: x >= pd.to_datetime(start_date) 
                                      and x <= pd.to_datetime(end_date))
        
    # Select for the data that fits the bool condition (date after 2020-12-14)
    portara_dat = portara_dat[bools]
    
    val = 0
    # add c1 to the back of CL
    portara_dat['Price Code'] = portara_dat['symbol'] + 'c' + str(val+1)
    
    contract_year = portara_dat['Contract'].apply(lambda x: str(x)[-3:-1]) # Get contract year 2021->21
    contract_month = portara_dat['Contract'].apply(lambda x: str(x)[-1]) # Get contract month

    # make a new column with CL21F from CLA2021F
    portara_dat['Contract Symbol'] = portara_dat['symbol'] + contract_year + contract_month

    # Select for only the following 4 columns because the others are not relevant to us
    portara_dat = portara_dat[column_select]

    return portara_dat

def read_portara_minute_data(filename, symbol, start_date, end_date,
                             start_filter_hour=30, end_filter_hour=331,
                             column_select=[]):
    """
    A modified version of the generic Portara reading function specifically for 
    the 1 minute data.
    
    LEGACY function from Abbe.

    Parameters
    ----------
    filename : str
        The filename in the correct address.
    symbol : str
        A short symbol for the asset.
    start_date: str
        The start date of the query. e.g, "2024-01-13".
    end_date: str
        The end date of the query. e.g, "2024-01-18".
    start_filter_hour : int, optional
        The start time for filtering by hours. The default is 30 because of the london trading hours
    end_filter_hour : int, optional
        The end time for filtering by hours. The default is 331.

    Returns
    -------
    portara_dat_2 : 2D panda dataframe
        The Portara minute data.

    """
    # Maybe first select for date then select for time?
    
    val = 0
    
    # Reading only these column
    portara_dat_2 = pd.read_csv(filename,
        names=['Date', 'Time', 'Low', 'High', 'Open', 'Close', 'Trade Volume', 'Contract'])
    
    # Add a column of symbol
    portara_dat_2['symbol'] = symbol
    
    #print(portara_dat_2,'9')
    
    # Transform the date format from 20160104 to 2016-01-04 00:00:00 (panda timestamp)
    portara_dat_2['Date'] = portara_dat_2['Date'].apply(lambda x: str(x)[0:4] + '-' + str(x)[4:6] + '-' + str(x)[6:])
    portara_dat_2['Date'] = pd.to_datetime(portara_dat_2['Date'])
    portara_dat_2['Date only'] = portara_dat_2['Date']
    
    # only select time within the range of starting price and ending price
    bools = portara_dat_2['Time'].apply(lambda x: x in np.arange(start_filter_hour, end_filter_hour)) # for the moment need only price at 330 so filtering for prices at 330 and few hours before 
    portara_dat_2 = portara_dat_2[bools]
    
    # Select for only these five columns
    portara_dat_2 = portara_dat_2[['Date only', 'Time', 'Close', 'Contract', 'symbol']]
    #print(portara_dat_2,'5')

    # Pivot: Return reshaped DataFrame organized by given index / column values.
    # Make the main columns time basedm and indexed
    portara_dat_2 = portara_dat_2.pivot(index=['Date only', 'Contract', 'symbol'], 
                                        columns='Time', values='Close')
    
    # make new column order by  ['Date only', 'Contract', 'symbol'] and reset index to numbers
    portara_dat_2.reset_index(inplace=True) 
    #print(portara_dat_2,'pivot')
  
    # add multiple columns 
    list_names = ['Close ' + str(i) for i in portara_dat_2.columns[3:].to_list()] # rename the columns with times 
    portara_dat_2.columns = ['Date only', 'Contract', 'symbol'] + list_names
    
    # Select for data after first date and end date
    bools = portara_dat_2['Date only'].apply(lambda x: x >= pd.to_datetime(start_date) 
                                             and x <= pd.to_datetime(end_date)) # filter for data after given date 
    portara_dat_2 = portara_dat_2[bools]
    
    # add c1 for front month contract
    portara_dat_2['Price Code'] = portara_dat_2['symbol'] + 'c' + str(val+1)

    return portara_dat_2


def merge_portara_data(table1: pd.DataFrame, 
                       table2: pd.DataFrame)-> pd.DataFrame:
    """
    Merging the Portara Daily and Minute table. The merger is operated on the 
    two columns: 'Date only' and 'Price Code'.
    
    LEGACY function from Abbe.

    Parameters
    ----------
    table1 : dataframe
        The pandas dataframe Daily pricing data.
    table2 : dataframe
        The Portara Minute pricing data.

    Returns
    -------
    new_table : pandas dataframe
        The new merged table.

    """
    # A function that merges 
    # construct a master table of price across all minutes
    
    # merge the minute and daily data based on Date only and Price code
    new_table = table1.merge(table2, on=['Date only', 'Price Code'], how='right')
   
    # add c1 to the price code
    val = 0
    table2['Price Code'] = table2['symbol'] + 'c' + str(val+1)
    
    new_table = table1.merge(table2, on=['Date only', 'Price Code'], how='right')
    
    del table1, table2
    
    # drop contract columns
    new_table = new_table.drop(columns='Contract')
        
    return new_table

#@time_it
def portara_data_handling(portara_dat: pd.DataFrame) -> pd.DataFrame:
    """
    A function that handle Portara's data.
    
    LEGACY function from Abbe.

    Parameters
    ----------
    portara_dat : pandas dataframe 
        Input Portara data.

    Returns
    -------
    portara_dat : pandas dataframe
        Output post-processed Portara data.

    """
    
    # now tidy up the data 
    minutes = np.concatenate((
            np.arange(30, 60), 
            np.arange(100, 160), 
            np.arange(200, 260),
            np.arange(300, 331)))
        
    minutes_2 = np.concatenate((
            np.arange(30, 60),  # half past to 1 
            np.arange(100, 160),  # 1 to 2 
            np.arange(200, 231))) # 2 to 3 
        
    for i in np.flip(minutes): # if there are no trades Portara doesn't create a bar so we have to go backwards to the last bar where a trade
    # happened to get the price iff there is no bar for 330 - otherwise the price is 'nan'

        price_330 = np.where(np.isnan(portara_dat['Close 330'].to_numpy()), portara_dat['Close ' + str(i)].to_numpy(), portara_dat['Close 330'].to_numpy())
        portara_dat['Close 330'] = price_330
            
    for i in np.flip(minutes_2): # if there are no trades Portara doesn't create a bar so we have to go backwards to the last bar where a trade
    # happened to get the price iff there is no bar for 330 (getting 230 prices for when daylight savings moving UK to BST (1 hour forward) from UTC/GMT

        price_230 = np.where(np.isnan(portara_dat['Close 230'].to_numpy()), portara_dat['Close ' + str(i)].to_numpy(), portara_dat['Close 230'].to_numpy())
        portara_dat['Close 230'] = price_230
            
    portara_dat = portara_dat[['Date only', 'Close 330', 'Settle', 'Price Code', 'Contract Symbol', 'Close 230']]
    portara_dat['daylight saving forward date'] = portara_dat['Date only'].apply(lambda x: pd.to_datetime(str(x.year) +'-03-31')) # date for daylight savings start 
    portara_dat['daylight saving back date'] = portara_dat['Date only'].apply(lambda x: pd.to_datetime(str(x.year)+'-10-27')) # date for daylight savings end 
        
    portara_dat['Close 330'] = np.where(
            np.logical_and(portara_dat['Date only'] > portara_dat['daylight saving forward date'],
                        portara_dat['Date only'] < portara_dat['daylight saving back date']),  
            portara_dat['Close 230'], 
            portara_dat['Close 330']
        )
    portara_dat = portara_dat[['Date only', 'Close 330', 'Settle', 'Price Code', 'Contract Symbol']]
    portara_dat = portara_dat.sort_values(by='Date only') # dates in ascending order 
        
    return portara_dat

#tested
def read_reformat_Portara_daily_data(filename: str, 
                                     add_col_data: dict = {}) -> \
                                     pd.DataFrame:
    """
    Reformat the Portara minute data in a format readable by the scripts.

    Parameters
    ----------
    filename : str
        The filename of the Portara minute data.

    Returns
    -------
    history_data : pandas dataframe
        The reformatted table.

    """
    history_data =  pd.read_csv(filename)
    
    history_data.columns = ['Date', 'Open', 'High', 'Low', 
                            'Settle', 'Volume', 'OpenInterest', 'Contract Code']
        
    # change the date from 20220222 (int) to '2022-02-22' (str)
    history_data['Date'] = [datetime.datetime.strptime(str(x)[0:4]+str(x)[4:6]+str(x)[6:], '%Y%m%d')
                            for x in history_data['Date']]
    #history_data_reindex = history_data.set_index('Date',drop=False)
    history_data_reindex = history_data
    
    match add_col_data:
        case {} | [] | None:
            pass
        case _:
            for key in add_col_data:
                history_data_reindex[key] = add_col_data[key] 
            
    return history_data


#tested
def read_reformat_Portara_minute_data(filename: str,  
                                      add_col_data: dict = {}) -> \
                                      pd.DataFrame:
    """
    Reformat the Portara minute data in a format readable by the scripts.

    Parameters
    ----------
    filename : str
        The filename of the Portara minute data.

    Returns
    -------
    history_data : pandas dataframe
        The reformatted table.

    """
    history_data =  pd.read_csv(filename)
    history_data.columns = ['Date', 'Time', 'Open', 'High', 'Low', 
                            'Settle', 'Volume', 'Contract Code']
    
    # include a function that let user to choose the reformat?
    
    # change the date from 20220222 (int) to '2022-02-22' (str)
    history_data['Date'] = [datetime.datetime.strptime(str(x)[0:4]+str(x)[4:6]\
                                                       +str(x)[6:], '%Y%m%d')
                                                for x in history_data['Date']]
    
    # convert the format 1330 (int) to 13:30 (datetime.time) obejct
    intmin = history_data['Time']
    bucket = util.convert_intmin_to_time(intmin) #, label='Time')
    
    history_data['Time'] = bucket
    
    #history_data_reindex = history_data.set_index('Date',drop=False)
    history_data_reindex = history_data

    match add_col_data:
        case {} | [] | None:
            pass
        case _:
            for key in add_col_data:
                history_data_reindex[key] = add_col_data[key] 
                
    return history_data#history_data_reindex

def read_reformat_openprice_data(filename: str) ->  pd.DataFrame:
    openprice_data = pd.read_csv(filename)
    
    openprice_data["Date"] = [datetime.datetime(year = int(str(x)[0:4]), 
                                              month=int(str(x)[5:7]), 
                                              day = int(str(x)[8:])) 
                            for x in openprice_data['Date']]
    
    # convert the format 1330 (int) to 13:30 (datetime.time) obejct
    intmin = openprice_data['Time']
    bucket = [datetime.datetime.strptime(intmin.iloc[i], "%H:%M:%S").time() 
              for i in range(len(intmin))]
    openprice_data['Time'] = bucket

    #openprice_data_reindex = openprice_data.set_index('Date',drop=False)
    openprice_data_reindex = openprice_data
    #print(openprice_data_reindex)
    return openprice_data #openprice_data_reindex


def read_reformat_APC_data(filename:str) -> pd.DataFrame:
    signal_data =  pd.read_csv(filename)
    signal_data['Forecast Period'] = [datetime.datetime.strptime(x, '%Y-%m-%d')
                            for x in signal_data['Forecast Period']]
    #signal_data_reindex = signal_data.set_index('Forecast Period',drop=False)
    signal_data_reindex = signal_data
    return signal_data #signal_data_reindex

#tested
def extract_lag_data(signal_data: pd.DataFrame, 
                     history_data: pd.DataFrame, 
                     date:str, lag_size:int = 5) -> \
                     tuple[pd.DataFrame, pd.DataFrame]:
    """
    Extract the Lag data based on a given date.

    Parameters
    ----------
    signal_data : pandas dataframe
        The signal data.
    history_data : pandas dataframe
        The historical data.
    date : str
        The date of interest, format like this "2024-01-10".
    lag_size : int, optional
        The size of the lag window. The default is 5 (days).

    Returns
    -------
    signal_data_lag : pandas data frame
        The signal data five (lag_size) days prior to the given date.
    history_data_lag : pandas data frame
        The historical data five (lag_size) days prior to the given date.

    """
    # Find the row index of the history data first
    #row_index = history_data.index[history_data['Date'] == date].tolist()[0]
    row_index = history_data.index[history_data['Date'] == date].item()
    #print('row_index',row_index)
    #lag_days = datetime.timedelta(days=lag_size)
    
    #lag5days = row_index-lag_days
    #lag1day = row_index - datetime.timedelta(days=1)
    #print('row_index', row_index, row_index-lag_size, row_index-1)
    #print('lag_size', lag_size, row_index-lag_size, row_index - datetime.timedelta(days=1))
    # extract exactly 5 (default) lag days array
    history_data_lag = history_data.loc[row_index-lag_size:row_index-1]
   #history_data_lag = history_data.loc[lag5days:lag1day]
    
    #print('history_data_lag', history_data_lag)
    # use the relevant date from history data to get signal data to ensure matching date
    window = history_data_lag['Date'].tolist()
    #print('window',history_data_lag['Date'].tolist())

    # turn Timstamp into string
    #print(window)
    #window = [str(window[i])[0:10] for i in range(lag_size)]
        
    #Store the lag signal data in a list
    #signal_data_lag = signal_data[signal_data['Forecast Period'] == window[0]]
    signal_data_lag = signal_data[signal_data['Forecast Period'] == window[0]]
    
    for i in range(lag_size-1):
        curve = signal_data[signal_data['Forecast Period'] == window[i+1]]
        signal_data_lag = pd.concat([signal_data_lag, curve])

    return signal_data_lag, history_data_lag

# tested
def find_closest_price(day_minute_data: pd.DataFrame, 
                       target_hr: str ='0330', 
                       direction: str ='forward', 
                       step: int = 1, 
                       search_time: int = 1000) -> \
                       tuple[datetime.datetime, float]:    
    """
    A method to find the closest price next to a traget hour

    Parameters
    ----------
    day_minute_data : TYPE
        DESCRIPTION.
    target_hr : TYPE, optional
        DESCRIPTION. The default is '0330'.
    direction : TYPE, optional
        DESCRIPTION. The default is 'forward'.
    step : TYPE, optional
        DESCRIPTION. The default is 1.
    search_time : TYPE, optional
        DESCRIPTION. The default is 1000.

    Returns
    -------
    target_hr_dt : TYPE
        DESCRIPTION.
    TYPE
        DESCRIPTION.

    """
    # If the input is forward, the loop search forward a unit of minute (step)
    if direction == 'forward':
        step = 1.* step
    # If the input is backward, the loop search back a unit of minute (step)
    elif direction == 'backward':
        step = -1* step
        
    target_hr_dt= datetime.time(hour=int(target_hr[0:2]),minute=int(target_hr[2:4]))
    
    #initial estimation of the target price
    target_price = day_minute_data[day_minute_data['Time'] == target_hr_dt]['Open']
    #loop through the next 30 minutes to find the opening price    
    for i in range(search_time):    
        if len(target_price) == 0:
            delta = datetime.timedelta(minutes = step)
            target_hr_dt = (datetime.datetime.combine(datetime.datetime.today(), 
                            target_hr_dt) + delta).time()
            target_price = day_minute_data[day_minute_data['Time'] == target_hr_dt]['Open']
            
    target_price = [float(target_price.iloc[0])] # make sure that this is float
            
    return target_hr_dt, target_price[0]

def find_closest_price_date(data: pd.DataFrame, 
                            target_time: str ='2024-01-03', 
                            time_proxy: str = 'Date', 
                            price_proxy: str ='Open',
                            direction: str = 'forward', 
                            step: int = 1, 
                            search_time: int = 30) -> \
    tuple[datetime.datetime, float]: # WIP
    
    # If the input is forward, the loop search forward a unit of minute (step)
    if direction == 'forward':
        step = 1* step
    # If the input is backward, the loop search back a unit of minute (step)
    elif direction == 'backward':
        step = -1* step
        
    # determine whether it is in the time frame of minutes,    
    #target_time_dt= datetime.time(hour=int(target_time[0:2]),minute=int(target_time[2:4]))
    target_time_dt = datetime.datetime.strptime(target_time, "%Y-%m-%d")
    
    #initial estimation of the target price
    target_price = data[data[time_proxy] == target_time_dt][price_proxy]
    #loop through the next 30 days to find the opening price    
    for i in range(search_time): 
        if len(target_price) == 0:
            
            delta = datetime.timedelta(days = step)
            
            target_time_dt = target_time_dt + delta
          #  print(target_time_dt)
            target_price = data[data[time_proxy] == target_time_dt][price_proxy]
            
    return target_time_dt, target_price


def find_closest_price_generic(data: pd.DataFrame, 
                               target_time: str ='0330', 
                               time_proxy: str = 'Time', 
                               price_proxy: str ='Open',
                               direction: str ='forward', 
                               step: int = 1, 
                               search_time: int = 1000) -> \
                               tuple[datetime.datetime, float]: # WIP
    
    # If the input is forward, the loop search forward a unit of minute (step)
    if direction == 'forward':
        step = 1* step
    # If the input is backward, the loop search back a unit of minute (step)
    elif direction == 'backward':
        step = -1* step
        
    # determine whether it is in the time frame of minutes,
    target_time_dt = datetime.datetime.strftime(target_time, "%H%M")
    
    #initial estimation of the target price
    target_price = data[data[time_proxy] == target_time_dt][price_proxy]
    #loop through the next 30 minutes to find the opening price    
    for i in range(search_time):    
        if len(target_price) == 0:
            
            delta = datetime.timedelta(minutes = step)
            
            target_time_dt = (datetime.datetime.combine(datetime.datetime.today(), 
                            target_time_dt) + delta).time()
            
            target_price = data[data[time_proxy] == target_time_dt][price_proxy]
            
    return target_time_dt, target_price

def find_price_by_time(history_data_daily: pd.DataFrame, 
                    history_data_minute: pd.DataFrame, 
                    open_hr: str ='0330') -> pd.DataFrame: #tested
    """
    A function to search for the opening price of the day.
    If at the opening hour, there are no bid or price information, the script 
    loop through the next 30 minutes to find the opening price.

    Parameters
    ----------
    history_data_daily : dataframe
        The historical daily data.
    history_data_minute : dataframe
        The historical minute data.
    open_hr : str, optional
        Defining the opening hour. The default is '0330'.

    Returns
    -------
    open_price_data: dataframe
        A table consist of three columns: 'Date', 'Time', and 'Open Price'.

    """
    date_list = history_data_daily['Date'].to_list()
    open_price_data = []
    
    #loop through daily data to get the date
    for date in date_list:
        day_data = history_data_minute[history_data_minute['Date'] == date]
        
        # Find the closest hour and price
        open_hr_dt, open_price = find_closest_price(day_data,
                                                            target_hr='0330')
        #print('open_price',open_price)
        if type(open_price) ==  float:
            pass
        elif len(open_price)!=1:
            print(open_price)
        #storage
        #open_price_data.append((date.to_pydatetime(), open_hr_dt , 
        #                        open_price.item()))
        open_price_data.append((date.to_pydatetime(), open_hr_dt , 
                                open_price))
        
    open_price_data = pd.DataFrame(open_price_data, columns=['Date', 'Time', 'Open Price'])

    return open_price_data

def find_range(input_array: np.ndarray, 
               target_range: tuple[float|int] | list[float|int] | np.ndarray)\
                -> dict:
    """
    A function that find the points' indicies given a target range. 
    It finds the points within that range .


    Parameters
    ----------
    input_array : np.ndarray
        A 1D numpy array with only numbers.
    target_range : tuple[float|int] | list[float|int] | np.ndarray
        A tuple, list, or array of target range. e.g. [0,1], (0,1),...
        The first element is the lower bound and the second the upper bound.

    Raises
    ------
    Exception
        When the target_range input does not contain exactly two values.

    Returns
    -------
    dict
        range_dict contains the indices of the element of the input_array that
        is within the target_range, outside the target_range, and the boundaries
        of the range.

    """
                    
    if len(target_range) != 2:
        raise Exception("Target Range input must contains exactly two values.")
        
    lower_bound = np.repeat(target_range[0], len(input_array))
    upper_bound = np.repeat(target_range[1], len(input_array))
    
    delta_lower = input_array - lower_bound
    delta_upper = upper_bound - input_array
    
    delta = np.sign(delta_upper) + np.sign(delta_lower)
    
    range_indices = np.where(delta>0)
    bound_indices = np.where(delta ==1)
    outbound_indices = np.where(delta<0)
    
    return {'range_indices': range_indices,
            'outbound_indices': outbound_indices,
            'bound_indices': bound_indices}

def find_crossover(input_array: np.ndarray, 
                   threshold: float | list[float|int] | np.ndarray) -> dict:
    """
    A function that find the crossover points' indicies. It finds the points right
    after either rise above, or drop below the threshold value.
    
    Parameters
    ----------
    input_array : numpy array
        A 1D numpy array with only numbers.
    threshold : float, list, numpy array
        the threshold value.

    Returns
    -------
    dict
        The 'rise' value contains a numpy array containing the indicies of 
        points that rise above the the threshold.
        The 'drop' value contains a numpy array containing the indicies of 
        points that drop below the the threshold.

    """
    if type(threshold) == float:
        # make a numpy array of the threshold value    
        threshold = np.repeat(threshold, len(input_array)) 
    elif (type(threshold) == list or type(threshold) == np.ndarray) and \
                                        len(threshold) != len(input_array):
        raise Exception("Mismatch input and threshold arraty length.")
    elif type(threshold) == list and len(threshold) == len(input_array):
        # make a numpy array of the threshold value    
        threshold = np.array(threshold)
    elif type(threshold) == np.ndarray and len(threshold) == len(input_array):
        pass
    
    # The difference between the input value and the threshold number
    # Positive values mean the input is higher than threshold
    # Negative values mean the input is lower than threshold
    delta = input_array - threshold
    # This is an array 1 unit in the past
    #delta_lag = np.concatenate([delta, np.array([np.nan])])[1:]
    delta_lag = np.concatenate([np.array([np.nan]), delta])[:-1]

    # IF delta[i] > delta_lag[i], then the price rise above threshold
    # Because all elements are either +1, -1 or 0, the larger value has to be +1.
    # np.sign(delta) = +1, while np.sign(delta_lag) = -1 means yesterday the value 
    # is lower than threshold and today's value is higher than the threshold-> rise above
    indices_rise_above  = np.where(np.sign(delta) > np.sign(delta_lag))

    # IF delta[i] < delta_lag[i], then the price drop below threshold
    indices_drop_below = np.where(np.sign(delta) < np.sign(delta_lag))

    # Produce a dic of indicies for below and above
    return {'rise': indices_rise_above, 
            'drop': indices_drop_below}
#tested
def find_minute_EES(histroy_data_intraday: pd.DataFrame, 
                    target_entry: float, target_exit: float, stop_exit: float,
                    open_hr: str = "0330", close_hr: str = "1930", 
                    price_approx: str = 'Open', 
                    time_proxy: str= 'Time',
                    direction: str = 'Neutral',
                    close_trade_hr: str = '1925', 
                    dt_scale: str = 'datetime') -> dict:
    """
    Set the EES value given a time-series of minute intraday data.

    Parameters
    ----------
    histroy_data_intraday : dataframe
        The histort intraday minute data. This assume the file contains the 
        ohlc value of the day
    target_entry : float 
        target entry price.
    target_exit : float
        target exit price.
    stop_exit : float
        target stop loss price.
    open_hr : str, optional
        The opening hour of trade in military time format. 
        The default is "0330".
    close_hr : str, optional
        The closing hour of trade in military time format. 
        The default is "1930".
    price_approx : str, optional
        The price approximator. The default uses the opening price of each 
        minute as the price indicator. It calls in the 'Open' column in the 
        history intradday minute dataframe
        The default is 'Open'.
    time_prox: 
        The time proxy. This function assume the input time data come fomr the 
        'Time' column of the dataframe. 
        The default is 'Time'.
    direction : str, optional
        Trade direction. Either "Buy", "Sell", or "Neutral".
        The default is 'Neutral'.
    close_trade_hr : str, optional
        The final minute to finish off the trade in military time format. 
        The default is '1925'.
    dt_scale :

    Raises
    ------
    ValueError
        Direction data can only be either "Buy", "Sell", or "Neutral".

    Returns
    -------
    EES_dict : dict
        A dictionary that cantains the possible EES points and time.

    """
    # This function can be made in one more layer of abstraction. Work on this later
    
    # define subsample. turn the pandas series into a numpy array
    price_list = histroy_data_intraday[price_approx].to_numpy()
    time_list = histroy_data_intraday[time_proxy].to_numpy()
    
    # read in date list
    date_list = histroy_data_intraday['Date'].to_numpy() 
    # Temporary solution. Can be made using two to three time layer

    # make datetime list
    datetime_list = np.array([datetime.datetime.combine(pd.to_datetime(d).date(), t) \
                              for d, t in zip(date_list,time_list)])
    
    if dt_scale == "time":
        time_proxy_list = time_list
    elif dt_scale == 'date':
        time_proxy_list = date_list
    elif dt_scale == 'datetime':
        time_proxy_list = datetime_list

    # Find the crossover indices
    entry_pt_dict = find_crossover(price_list, target_entry)
    exit_pt_dict = find_crossover(price_list, target_exit)
    stop_pt_dict = find_crossover(price_list, stop_exit)
    
    if direction == "Neitral":
        #print("Neutral day")
        # for 'Neutral' action, all info are empty
        entry_pts, entry_times = [], []
        exit_pts, exit_times = [], []
        stop_pts, stop_times = [], []
    
    elif direction == "Buy":
        #print("Finding Buy points.")
        # for 'Buy' action EES sequence is drop,rise,drop
        entry_pts = price_list[entry_pt_dict['drop'][0]]
        entry_times = time_proxy_list[entry_pt_dict['drop'][0]]
            
        exit_pts = price_list[exit_pt_dict['rise'][0]]
        exit_times = time_proxy_list[exit_pt_dict['rise'][0]]
        
        stop_pts = price_list[stop_pt_dict['drop'][0]]
        stop_times = time_proxy_list[stop_pt_dict['drop'][0]]
            
    elif direction == "Sell":
        #print("Finding Sell points.")
        # for 'Sell' action EES sequence is rise,drop,rise
        entry_pts = price_list[entry_pt_dict['rise'][0]]
        entry_times = time_proxy_list[entry_pt_dict['rise'][0]]
            
        exit_pts = price_list[exit_pt_dict['drop'][0]]
        exit_times = time_proxy_list[exit_pt_dict['drop'][0]]
        
        stop_pts = price_list[stop_pt_dict['rise'][0]]
        stop_times = time_proxy_list[stop_pt_dict['rise'][0]]
    else:
        raise ValueError('Direction has to be either Buy, Sell, or Neutral.')
    
    # Define the closing time and closing price. Here we choose 19:25 for final trade
    close_hr_str = close_hr.strftime("%H%M")

    ## Find the closest price and datettime instead of having it at exactly the close time
    close_date_new, close_pt = find_closest_price(histroy_data_intraday, 
                                                  target_hr=close_hr_str, 
                                                  direction='backward')
    close_date = date_list[np.where(time_list==close_date_new)[0]][0]

    close_datetime = datetime.datetime.combine(pd.to_datetime(close_date).date(), 
                                               close_date_new)

    # storage
    EES_dict = {'entry': list(zip(entry_times,entry_pts)),
                'exit': list(zip(exit_times,exit_pts)),
                'stop': list(zip(stop_times,stop_pts)),
                'close': tuple((close_datetime, close_pt))}

    #print('EES_dict', EES_dict['close'])
    return EES_dict


def find_minute_range(histroy_data_intraday: pd.DataFrame,
                      target_entry_range: list[float|int] | tuple[float|int], 
                      target_exit_range: list[float|int] | tuple[float|int], 
                      stop_exit: float | int,
                      open_hr: str = "0330", close_hr: str = "1930", 
                      price_approx: str = 'Open', 
                      time_proxy: str= 'Time',
                      direction: str = 'Neutral',
                      dt_scale: str = 'datetime'):
    
    # define subsample. turn the pandas series into a numpy array
    price_array = histroy_data_intraday[price_approx].to_numpy()
    time_array = histroy_data_intraday[time_proxy].to_numpy()
    
    # read in date list
    date_array = histroy_data_intraday['Date'].to_numpy() 
    # Temporary solution. Can be made using two to three time layer

    # make datetime list
    datetime_array = np.array([datetime.datetime.combine(pd.to_datetime(d).date(), t) \
                              for d, t in zip(date_array,time_array)])
        
    if dt_scale == "time":
        time_proxy_array = time_array
    elif dt_scale == 'date':
        time_proxy_array = date_array
    elif dt_scale == 'datetime':
        time_proxy_array = datetime_array
        
    # Find the crossover indices
    entry_region_dict = find_range(price_array, target_entry_range)
    exit_region_dict = find_range(price_array, target_exit_range)
    # Stop loss find crossover
    stop_pt_dict = find_crossover(price_array, stop_exit)
    
    if direction == "Neitral":
        # for 'Neutral' action, all info are empty
        entry_pts, entry_times = [], []
        exit_pts, exit_times = [], []
        stop_pts, stop_times = [], []
        
    elif direction == "Buy":
        #print("Finding Buy points.")
        # for 'Buy' action EES sequence is drop,rise,drop
        entry_pts = price_array[entry_region_dict['range_indices'][0]]
        entry_times = time_proxy_array[entry_region_dict['range_indices'][0]]
            
        exit_pts = price_array[exit_region_dict['range_indices'][0]]
        exit_times = time_proxy_array[exit_region_dict['range_indices'][0]]
        
        stop_pts = price_array[stop_pt_dict['drop'][0]]
        stop_times = time_proxy_array[stop_pt_dict['drop'][0]]
        
    elif direction == "Sell":
        #print("Finding Sell points.")
        # for 'Sell' action EES sequence is rise,drop,rise
        entry_pts = price_array[entry_region_dict['range_indices'][0]]
        entry_times = time_proxy_array[entry_region_dict['range_indices'][0]]
            
        exit_pts = price_array[exit_region_dict['range_indices'][0]]
        exit_times = time_proxy_array[exit_region_dict['range_indices'][0]]
        
        stop_pts = price_array[stop_pt_dict['rise'][0]]
        stop_times = time_proxy_array[stop_pt_dict['rise'][0]]
    
    
    # Define the closing time and closing price. Here we choose 19:25 for final trade
    close_hr_str = close_hr.strftime("%H%M")

    ## Find the closest price and datettime instead of having it at exactly the close time
    close_date_new, close_pt = find_closest_price(histroy_data_intraday, 
                                                  target_hr=close_hr_str, 
                                                  direction='backward')
    close_date = date_array[np.where(time_array==close_date_new)[0]][0]

    close_datetime = datetime.datetime.combine(pd.to_datetime(close_date).date(), 
                                               close_date_new)

    range_dict = {'entry_region': list(zip(entry_times,entry_pts)),
                  'exit_region': list(zip(exit_times,exit_pts)),
                  'stop': list(zip(stop_times,stop_pts)),
                  'close': tuple((close_datetime, close_pt))}

    return range_dict


def open_portfolio(filename: str):
    """
    A handy function to open a portfolio. Nothing special but easy to remember.

    Parameters
    ----------
    filename : TYPE
        DESCRIPTION.

    Returns
    -------
    portfo : TYPE
        DESCRIPTION.

    """
    file = open(filename, 'rb')
    
    portfo = pickle.load(file)
    
    file.close()
    return portfo

def concat_CSVtable(filename_list: list[str], 
                    sort_by: str = 'Date') -> pd.DataFrame:
    """
    

    Parameters
    ----------
    filename_list : list
        A list of filename.
    sort_by : str, optional
        The column name in which the dataframe is sorted. 
        The default is 'Date'.

    Returns
    -------
    master_table : dataframe
        The resulting table.

    """
    
    master_table = pd.DataFrame()
    
    for filename in filename_list:
        temp = pd.read_csv(filename)
        master_table = pd.concat([master_table,temp])
        
    master_table.sort_values(by=sort_by, inplace=True)
    return master_table

@util.time_it
def merge_raw_data(filename_list: list[str], 
                   save_filename: str, 
                   sort_by: str = "Forecast Period") -> pd.DataFrame:
    """
    A functiob that merge a list of CSV files into one CSV file.

    Parameters
    ----------
    filename_list : list
        A list of filename if CSV to be Concatenated.
    save_filename : str
        The filename for saving.
    sort_by : str, optional
        The column name used in the sorting. The default is "Forecast Period".

    Returns
    -------
    merged_data : dataframe
         The merged data.

    """
    merged_data = concat_CSVtable(filename_list, sort_by= sort_by)
    merged_data.to_csv(save_filename,index=False)
    return merged_data
        

def render_PNL_xlsx(listfiles: list[str], 
                    number_contracts_list: list[int | float] = [5,10,15,20,25,50], 
                    suffix: str = '_.xlsx') -> pd.DataFrame:
    """
    LEGACY function from Abbe.
    A function that read in the back-test result to generate an xlsx PNL file 

    
    """
    for fn in listfiles: 
        
        # regular output
        price_codes = list(SIZE_DICT.keys())
        dat = pd.read_csv(fn)
        
        with pd.ExcelWriter(fn[:-4]+suffix) as excel_writer: 
            
            dattotal = dat
            dattotal = dattotal.sort_values(by='Entry_Date')
            dattotal['number barrels/gallons'] = dattotal['Price_Code'].apply(
                                                        lambda x: SIZE_DICT[x])
            dattotal['fees'] = dattotal['Price_Code'].apply(
                                                    lambda x: round_turn_fees[x])
            dattotal['fees'] = np.where(np.isnan(dattotal['Entry_Price']), 
                                                    0.0, dattotal['fees'])
            
            # Make columns for scaled returns
            dattotal['scaled returns from trades'] =  dattotal['Return_Trades']*\
                                                        dattotal['number barrels/gallons']\
                                                            - dattotal['fees']
            
            for num_contracts in number_contracts_list:
                col_name = 'scaled returns from trades (x {})'.format(num_contracts)
                dattotal[col_name] = dattotal['scaled returns from trades'] * num_contracts
                
            # Make columns for cumulative returns
            dattotal['cumulative P&L from trades'] = np.cumsum(dattotal['scaled returns from trades']) 

            cum_col_name_list = ['cumulative P&L from trades']
            for num_contracts in number_contracts_list:
                cum_col_name = 'cumulative P&L from trades for contracts (x {})'.format(num_contracts)
                PNL_col_name = 'scaled returns from trades (x {})'.format(num_contracts)
                
                dattotal[cum_col_name] = np.cumsum(dattotal[PNL_col_name]) 
                cum_col_name_list.append(cum_col_name)

            
            dattotal.to_excel(excel_writer=excel_writer, sheet_name='Total')
        
            # make sub-spread sheet for output sorted by individual asset 
            for _, pc in enumerate(price_codes): 
                # recalculate the cumulative returns for each assets
                # First drop the columns previously calculated
                datpc = dattotal[dattotal['Price_Code'] == pc].drop(columns=cum_col_name_list)
                       
                
                ##################################
                datpc['cumulative P&L from trades'] = np.cumsum(datpc['scaled returns from trades']) 
                
                for num_contracts in number_contracts_list:
                    cum_col_name = 'cumulative P&L from trades for contracts (x {})'.format(num_contracts)
                    PNL_col_name = 'scaled returns from trades (x {})'.format(num_contracts)
                    
                    datpc[cum_col_name] = np.cumsum(datpc[PNL_col_name])     
                                
                if len(datpc) > 0:
                    
                    datpc.to_excel(excel_writer=excel_writer, sheet_name=pc)
                    
    return datpc            

# =============================================================================
# #%% Construction Area
# def extract_lag_data_to_list(signal_data, history_data_daily,lag_size=5):
#     # make a list of lag data with a nested data structure.
#     
#     return None
#     #extract_lag_data(signal_data, history_data_daily, "2024-01-10")
# 
# =============================================================================
