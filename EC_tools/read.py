"""
Created on Tue Apr  2 14:09:54 2024

@author: dexter

The read module contains handy functions related reading and reformating raw 
data. It also contains some relevant function in mainpulating data or deriving 
new information from the raw data. 


"""
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
import datetime
import pickle

from typing import Union, Callable

import EC_tools.utility as util
from crudeoil_future_const import round_turn_fees, SIZE_DICT

# Argus API 
from ext_codes.ArgusPossibilityCurves2 import ArgusPossibilityCurves




__all__ = ['get_apc_from_server','read_apc_data','read_portara_daily_data', 
           'read_portara_minute_data','merge_portara_data',
           'portara_data_handling', 'extract_lag_data', 
           'read_reformat_Portara_minute_data', 'find_closest_price', 
           'find_crossover', 'find_minute_EES','open_portfolio',
           'render_PNL_xlsx', 'group_trade']

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
        apc_data = apc.getPossibilityCurves(start_date=start_date, 
                                            end_date=end_date, 
                                            categories=[categories])
        
        # Delete irrelavant columns
        #apc_data = apc_data.drop(columns=['PUBLICATION_DATE', 
        #                                  'CONTINUOUS_FORWARD', 
        #                                  'PRICE_UNIT', 'TIMESTAMP'])
        #apc_data.columns = ['Forecast_Period'] + [i for i in apc_data.columns[1:]] # Add the term "APC" in each column

        # If no specific symbol input, use the name of the categories
        if symbol == None:
            symbol = categories
        else:
            pass
        
        # make a new column with nothing in it. Then write the short symbol
        apc_data['symbol'] = None  
        apc_data['symbol'] = np.where(apc_data['CATEGORY'].apply(lambda x: keywords in x), symbol, apc_data['symbol'])

        
    elif type(categories) is list: # if the asset name input is a list, pull a list of APC
        
        apc_data = apc.getPossibilityCurves(start_date=start_date, 
                                            end_date=end_date, 
                                            categories=categories)
            
        #apc_data = apc_data.drop(columns=['PUBLICATION_DATE', 
        #                                  'CONTINUOUS_FORWARD', 
        #                                  'PRICE_UNIT', 'TIMESTAMP'])
        #apc_data.columns = ['Forecast_Period'] + [i for i in apc_data.columns[1:]]
        apc_data['symbol'] = None 
        
        # add new column with symbols corresponding to the keywords.
        for i, c in zip(keywords,symbol):
            
            apc_data['symbol'] = np.where(apc_data['CATEGORY'].apply(lambda x: i in x), c, apc_data['symbol'])
    
    # Drop the Category column
    #apc_data = apc_data.drop(columns=['CATEGORY'])

    return apc_data

def read_apc_data(filename: str)->pd.DataFrame:
    """
    Nothing Special. Just a shorthand function to read the apc

    Parameters
    ----------
    filename : str
        APC CSVfilename.

    Returns
    -------
    data : Data Frame
        APC in dataframe.

    """
    # This function should be used in conjuction with get_apc_from_server(). 
    # The data should be pulled from the server using that function
    data = pd.read_csv(filename)

    return data    

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
    Use the function 'read_reformat_Portara_daily_data' instead.
    
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
    Use the function 'read_reformat_Portara_minute_data' instead.

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
    
    LEGACY function from Abbe. Not in use at the moment.

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
    
    LEGACY function from Abbe. Not in Use at the moment.

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
                                      add_col_data: dict = {},
                                      time_to_datetime = False) -> \
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
    
# =============================================================================
#     if time_to_datetime:
#         history_data['Time'] = [datetime.datetime.strptime(t, '%H%M') 
#                                 for t in history_data['Time']]
#     
# =============================================================================
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
    """
    A function that read and reformat the openprice data.

    Parameters
    ----------
    filename : str
        CSV filename.

    Returns
    -------
    DataFrame

    """
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

def read_reformat_dateNtime(filename: str, 
                            time_proxies: list[str] =['Date', 'Time'], 
                            str_formats: list[str]=['%Y-%m-%d', '%H:%M:%S']) \
                            -> pd.DataFrame:
    """
    Utility function that read and reformat data with multiple columns of 
    time elements, e.g. 'Date' and 'Time'.

    Parameters
    ----------
    filename : str
        CSV filename.
    time_proxies : list[str], optional
        A list. The default is ['Date', 'Time'].
    str_formats : list[str], optional
        A list of str arg passing to datetime.strptime function. 
        The default is ['%Y-%m-%d', '%H:%M:%S'].

    Returns
    -------
    data : Data Frame

    """
    data = pd.read_csv(filename)
    bucket_1 = [datetime.datetime.strptime(x, str_formats[0])
                               for x in data[time_proxies[0]]]
    bucket_2 = [datetime.datetime.strptime(x, str_formats[1]).time()
                               for x in data[time_proxies[1]]]
    data[time_proxies[0]] = bucket_1
    data[time_proxies[1]] = bucket_2
    
    print(data[time_proxies[0]], data[time_proxies[1]])
    return data

def read_reformat_APC_data(filename: str, 
                           time_proxies: list[str] = 
                           ['PUBLICATION_DATE', 'PERIOD']) -> pd.DataFrame:
    """
    Read and reformat APC data

    Parameters
    ----------
    filename : str
        APC filename.
    time_proxies : list[str], optional
        A list of time (or Date) proxy. These are the column name in the
        DataFrame.
        The default is ['PUBLICATION_DATE', 'PERIOD'].

    Returns
    -------
    DataFrame

    """
    signal_data =  pd.read_csv(filename)
        
    if type(time_proxies) == str:
        time_proxies = [time_proxies]
    
    for time_proxy in time_proxies:
        signal_data[time_proxy] = [datetime.datetime.strptime(x, '%Y-%m-%d')
                                   for x in signal_data[time_proxy]]
        
    #signal_data[time_proxy_2] = [datetime.datetime.strptime(x, '%Y-%m-%d')
    #                            for x in signal_data[time_proxy_2]]
    
    #signal_data_reindex = signal_data.set_index('Forecast Period',drop=False)
    
    signal_data_reindex = signal_data
    return signal_data #signal_data_reindex

#tested
def extract_lag_data(signal_data: pd.DataFrame, 
                     history_data: pd.DataFrame, 
                     date:str, 
                     lag_size:int = 5,
                     time_proxy = "PERIOD") -> \
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
    #lag_days = datetime.timedelta(days=lag_size)
    
    #lag5days = row_index-lag_days
    #lag1day = row_index - datetime.timedelta(days=1)

    # extract exactly 5 (default) lag days array
    history_data_lag = history_data.loc[row_index-lag_size:row_index-1]
    # history_data_lag = history_data.loc[lag5days:lag1day]
    
    # use the relevant date from history data to get signal data to ensure matching date
    window = history_data_lag['Date'].tolist()

    # turn Timstamp into string
    #window = [str(window[i])[0:10] for i in range(lag_size)]
        
    #Store the lag signal data in a list
    #signal_data_lag = signal_data[signal_data['Forecast Period'] == window[0]]
    signal_data_lag = signal_data[signal_data[time_proxy] == window[0]]
    
    for i in range(lag_size-1):
        curve = signal_data[signal_data[time_proxy] == window[i+1]]
        signal_data_lag = pd.concat([signal_data_lag, curve])

    return signal_data_lag, history_data_lag

# tested
def find_closest_price(day_minute_data: pd.DataFrame, 
                       target_hr: str ='0330', 
                       direction: str ='forward', 
                       price_proxy: str = 'Open',
                       time_proxy: str = 'Time',
                       step: int = 1, 
                       search_time: int = 1000) -> \
                       tuple[datetime.datetime, float]:    
    """
    A method to find the closest price next to a traget hour

    Parameters
    ----------
    day_minute_data : DataFrame
        The minute pricing data.
    target_hr : str, optional
        The target hour for the search. The default is '0330'.
    direction : dtr, optional
        To search the list either 'backward' or 'forward'. 
        The default is 'forward'.
    step : int, optional
        The step size of the search. The default is 1.
    search_time : int, optional
        The total minutes (steps) of the search. The default is 1000.

    Returns
    -------
    target_hr_dt : datetime.datetime
        The datetime of the closest hour to the target.
    float
        The target price.

    """
    # If the input is forward, the loop search forward a unit of minute (step)
    if direction == 'forward':
        step = 1.* step
    # If the input is backward, the loop search back a unit of minute (step)
    elif direction == 'backward':
        step = -1* step
        
    target_hr_dt= datetime.time(hour=int(target_hr[0:2]),minute=int(target_hr[2:4]))
    
    #initial estimation of the target price
    target_price = day_minute_data[day_minute_data[time_proxy] == target_hr_dt][price_proxy]
    #loop through the next 30 minutes to find the opening price    
    for i in range(search_time):    
        if len(target_price) == 0:
            delta = datetime.timedelta(minutes = step)
            
            # Note that the datetime.datetime.today() is a place holder, it does  
            # not affect the target_hr_dt vatriables.
            target_hr_dt = (datetime.datetime.combine(datetime.datetime.today(), 
                            target_hr_dt) + delta).time()
            #print(i, target_hr_dt)

            target_price = day_minute_data[day_minute_data[time_proxy] == target_hr_dt][price_proxy]
            
    target_price = [float(target_price.iloc[0])] # make sure that this is float
            
    return target_hr_dt, target_price[0]

@util.time_it
def find_closest_price_datetime(day_minute_data: pd.DataFrame, 
                                target_date: datetime.datetime,
                                target_hr: str ='0330', 
                                direction: str ='forward', 
                                price_proxy: str = 'Open',
                                time_proxy: str = 'Time',
                                date_proxy: str = 'Date',
                                step: int = 1, 
                                search_time: int = 1000) -> \
                                tuple[datetime.datetime, float]:    
    """
    A method to find the closest price next to a traget date and hour

    Parameters
    ----------
    day_minute_data : DataFrame
        The minute pricing data.
    target_hr : str, optional
        The target hour for the search. The default is '0330'.
    direction : dtr, optional
        To search the list either 'backward' or 'forward'. 
        The default is 'forward'.
    step : int, optional
        The step size of the search. The default is 1.
    search_time : int, optional
        The total minutes (steps) of the search. The default is 1000.

    Returns
    -------
    target_hr_dt : datetime.datetime
        The datetime of the closest hour to the target.
    float
        The target price.

    """
    # If the input is forward, the loop search forward a unit of minute (step)
    if direction == 'forward':
        step = 1.* step
    # If the input is backward, the loop search back a unit of minute (step)
    elif direction == 'backward':
        step = -1* step
        
    target_hr_dt= datetime.time(hour=int(target_hr[0:2]),minute=int(target_hr[2:4]))
    
    day_minute_data = day_minute_data[day_minute_data[date_proxy] == target_date]
    print(target_date, day_minute_data)
    #initial estimation of the target price
    target_price = day_minute_data[day_minute_data[time_proxy] == target_hr_dt][price_proxy]
    #loop through the next 30 minutes to find the opening price    
    for i in range(search_time):    
        if len(target_price) == 0:
            delta = datetime.timedelta(minutes = step)
            
            # Note that the datetime.datetime.today() is a place holder, it does  
            # not affect the target_hr_dt vatriables.
            target_hr_dt = (datetime.datetime.combine(datetime.datetime.today(), 
                            target_hr_dt) + delta).time()
            #print(i, target_hr_dt)

            target_price = day_minute_data[day_minute_data[time_proxy] == target_hr_dt][price_proxy]
            
    print(target_price)
    target_price = [float(target_price.iloc[0])] # make sure that this is float
            
    return target_hr_dt, target_price[0]


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
    if not target_range[1] > target_range[0]:
        raise Exception("Second element is not larger than the first.\
                        Target Range input must in the form of [lower_bound, \
                                                                upper_bound].")
        
    lower_bound = np.repeat(target_range[0], len(input_array))
    upper_bound = np.repeat(target_range[1], len(input_array))
    
    delta_lower = input_array - lower_bound
    delta_upper = upper_bound - input_array
    
    delta = np.sign(delta_upper) * np.sign(delta_lower)
    
    #print(np.sign(delta_lower), np.sign(delta_upper), delta)
    #print(delta_lower, delta_upper, delta)
    
    range_indices = np.where(delta>0)
    bound_indices = np.where(delta ==0)
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
                    price_proxy: str = 'Open', 
                    time_proxy: str= 'Time',
                    date_proxy: str ='Date',
                    direction: str = 'Neutral',
                    close_trade_hr: str = '1925', 
                    dt_scale: str = 'datetime') -> dict:
    """
    Find the points of crossover given a set of EES value in a time-series of 
    minute intraday data.
    This function is the key for crossover loops in the backtest

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
    price_proxy : str, optional
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
        It has the following format:
            {'entry': [(entry_times,entry_pts), ...],
            'exit': [(exit_times,exit_pts), ...],
            'stop': [(stop_times,stop_pts), ...],
            'open': (open_datetime, open_pt),
            'close': (close_datetime, close_pt)}

    """
    # (This function can be made in one more layer of abstraction. Work on this later)
    
    # define subsample. turn the pandas series into a numpy array
    price_list = histroy_data_intraday[price_proxy].to_numpy()
    time_list = histroy_data_intraday[time_proxy].to_numpy()
    
    #print("time_list", time_list[0], type(time_list[0]))
    # read in date list
    date_list = histroy_data_intraday[date_proxy].to_numpy() 
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
    
    # Define the opening/closing time and closing price. 
    # Here we choose 19:25 for final trade
    open_hr_str = open_hr.strftime("%H%M")
    close_hr_str = close_hr.strftime("%H%M")

    ## Find the closest price and datettime instead of having it at exactly the open time
    open_date_new, open_pt = find_closest_price(histroy_data_intraday, 
                                                  target_hr = open_hr_str, 
                                                  direction = 'forward',
                                                  price_proxy = price_proxy,
                                                  time_proxy = time_proxy)
    
    open_date = date_list[np.where(time_list==open_date_new)[0]][0]
    open_datetime = datetime.datetime.combine(pd.to_datetime(open_date).date(), 
                                               open_date_new)

    # Find the closest price and datettime instead of having it at exactly the close time
    close_date_new, close_pt = find_closest_price(histroy_data_intraday, 
                                                  target_hr = close_hr_str, 
                                                  direction = 'backward',   
                                                  price_proxy = price_proxy,
                                                  time_proxy = time_proxy)

    
    close_date = date_list[np.where(time_list==close_date_new)[0]][0]
    close_datetime = datetime.datetime.combine(pd.to_datetime(close_date).date(), 
                                               close_date_new)

    # storage
    EES_dict = {'entry': list(zip(entry_times,entry_pts)),
                'exit': list(zip(exit_times,exit_pts)),
                'stop': list(zip(stop_times,stop_pts)),
                'open': tuple((open_datetime, open_pt)),
                'close': tuple((close_datetime, close_pt))}

    #print('EES_dict', EES_dict['close'])
    return EES_dict


def find_minute_EES_range(histroy_data_intraday: pd.DataFrame,
                          target_entry_range: list[float|int] | tuple[float|int], 
                          target_exit_range: list[float|int] | tuple[float|int], 
                          stop_exit: float | int,
                          open_hr: str = "0330", close_hr: str = "1930", 
                          price_proxy: str = 'Open',
                          date_proxy: str = 'Date',
                          time_proxy: str= 'Time',
                          direction: str = 'Neutral',
                          dt_scale: str = 'datetime') -> dict[str,list|tuple]:
    """
    Find the points within a range of EES value in a time-series of minute 
    intrday data.
    This function is the key for range loop in backtesting.


    Parameters
    ----------
    histroy_data_intraday : pd.DataFrame
        The historical data.
    target_entry_range : list[float|int] | tuple[float|int]
        A range of entry price in the format of 
        [lower_bound_price, upper_bound_price].
    target_exit_range : list[float|int] | tuple[float|int]
        A range of exit price in the format of 
        [lower_bound_price, upper_bound_price].
    stop_exit : float | int
        The stop loss value.
    open_hr : str, optional
        The opening hour. The default is "0330".
    close_hr : str, optional
        The closing hour. The default is "1930".
    price_proxy : str, optional
        The column name for the price. The default is 'Open'.
    time_proxy : str, optional
        The column name for the time. The default is 'Time'.
    direction : str, optional
        The direction of the trade. The default is 'Neutral'.
    dt_scale : str, optional
        datetime scale. It could be either 'time', 'date', or 'datetime'.
        It choose from either the time or date columns, or 
        combine the two into datetime.
        The default is 'datetime'.

    Returns
    -------
    range_dict : TYPE
        A dictionary contianing the points in a day that falls within the 
        entry and exit range, as well as points that crossover to the stoploss,
        along with the open and close points of the day.
        It has the following format:
            {'entry': [(entry_times,entry_pts), ...],
            'exit': [(exit_times,exit_pts), ...],
            'stop': [(stop_times,stop_pts), ...],
            'open': (open_datetime, open_pt),
            'close': (close_datetime, close_pt)}
    """
    
    # define subsample. turn the pandas series into a numpy array
    price_array = histroy_data_intraday[price_proxy].to_numpy()
    time_array = histroy_data_intraday[time_proxy].to_numpy()
    
    # read in date list
    date_array = histroy_data_intraday[date_proxy].to_numpy() 
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
    open_hr_str = open_hr.strftime("%H%M")
    close_hr_str = close_hr.strftime("%H%M")
    ## Find the closest price and datettime instead of having it at exactly the open time
    open_date_new, open_pt = find_closest_price(histroy_data_intraday, 
                                                  target_hr = open_hr_str, 
                                                  direction = 'forward')
    open_date = date_array[np.where(time_array==open_date_new)[0]][0]
    open_datetime = datetime.datetime.combine(pd.to_datetime(open_date).date(), 
                                               open_date_new)
    ## Find the closest price and datettime instead of having it at exactly the close time
    close_date_new, close_pt = find_closest_price(histroy_data_intraday, 
                                                  target_hr=close_hr_str, 
                                                  direction='backward')
    close_date = date_array[np.where(time_array==close_date_new)[0]][0]

    close_datetime = datetime.datetime.combine(pd.to_datetime(close_date).date(), 
                                               close_date_new)

    range_dict = {'entry': list(zip(entry_times,entry_pts)),
                  'exit': list(zip(exit_times,exit_pts)),
                  'stop': list(zip(stop_times,stop_pts)),
                  'open': tuple((open_datetime, open_pt)),
                  'close': tuple((close_datetime, close_pt))}
    #print(range_dict)

    return range_dict


def open_portfolio(filename: str):
    """
    A handy function to open a portfolio. Nothing special but easy to remember.

    Parameters
    ----------
    filename : str
        The filename of the Portfolio object in pickle format  .

    Returns
    -------
    portfo : Portfolio

    """
    file = open(filename, 'rb')
    
    portfo = pickle.load(file)
    
    file.close()
    return portfo

def concat_CSVtable(filename_list: list[str], 
                    sort_by: str = 'Date') -> pd.DataFrame:
    """
    Concatenate CSV tables.

    Parameters
    ----------
    filename_list : list
        A list of CSV filename.
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

def merge_raw_data(filename_list: list[str], 
                   save_filename: str, 
                   sort_by: str = "PERIOD") -> pd.DataFrame:
    """
    A function that merges a list of CSV files into one CSV file.

    Parameters
    ----------
    filename_list : list
        A list of filename if CSV to be Concatenated.
    save_filename : str
        The filename for saving.
    sort_by : str, optional
        The column name used in the sorting. The default is "PERIOD".

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
                    suffix: str = '_.xlsx',
                    symbol_proxy: str = 'Price_Code', 
                    entry_price_proxy: str = 'Entry_Price', 
                    entry_date_proxy: str = 'Entry_Date', 
                    exit_price_proxy: str = 'Exit_Price',
                    return_proxy: str = 'Return_Trades') -> pd.DataFrame:
    """
    A function that read in the back-test result to generate an xlsx PNL file 

    Parameters
    ----------
    listfiles : list
        A list of filenames that to be included in the PNL report
    number_contracts_list : list
        A list of numbers of contracts to be calculated in the return and 
        cumulative return
    suffix : str
        The suffix for the output filename. The Default is '_.xlsx'.
    symbol_proxy: str
        The name for the symbol column. The Default is 'Price_Code'.
    entry_price_proxy: str
        The name of the entry price column. The Default is 'Entry_Price'.
    entry_date_proxy: str
        The name of the entry date column. The Default is 'Entry_Date'.
    exit_price_proxy: str
        The name of the exit price column. The Default is 'Exit_Price'.
    return_proxy: str
        The name of the return column. The Default is 'Return_Trades'.
    Returns
    -------
    datpc : DataFrame
        The output PNL file.
    """
    for fn in listfiles: 
        
        # regular output
        price_codes = list(SIZE_DICT.keys())
        dat = pd.read_csv(fn)
        print(fn,dat)
        with pd.ExcelWriter(fn[:-4]+suffix) as excel_writer: 
            
            dattotal = dat
            dattotal = dattotal.sort_values(by = entry_date_proxy)
            dattotal['number barrels/gallons'] = dattotal[symbol_proxy].apply(
                                                        lambda x: SIZE_DICT[x])
            dattotal['fees'] = dattotal[symbol_proxy].apply(
                                                    lambda x: round_turn_fees[x])
            dattotal['fees'] = np.where(np.isnan(dattotal['Entry_Price']), 
                                                    0.0, dattotal['fees'])
            
            # Make columns for scaled returns
            dattotal['scaled returns from trades'] = dattotal[return_proxy]*\
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
                datpc = dattotal[dattotal[symbol_proxy] == pc].drop(columns=cum_col_name_list)
                       
                ##################################
                datpc['cumulative P&L from trades'] = np.cumsum(datpc['scaled returns from trades']) 
                
                for num_contracts in number_contracts_list:
                    cum_col_name = 'cumulative P&L from trades for contracts (x {})'.format(num_contracts)
                    PNL_col_name = 'scaled returns from trades (x {})'.format(num_contracts)
                    
                    datpc[cum_col_name] = np.cumsum(datpc[PNL_col_name])     
                                
                if len(datpc) > 0:
                    
                    datpc.to_excel(excel_writer=excel_writer, sheet_name=pc)         
    return datpc 
           

def group_trade(position_pool: list, 
                select_func: Callable[[int], bool] = lambda x: True) -> list: #
    """
    A function to group positions by trade id along with some given conditions.

    Parameters
    ----------
    position_pool : list
        The position_pool list inside a portfolio object.
    select_func : Callable function, optional
        Additional functions for unique condition for grouping trade.
        The default is a lambda function that return True 
        (It will return true no matter what).
        
    Returns
    -------
    list
        A new list with each traded grouped as a list element in a bucket

    """
    # A function that matches the trade_id and group them in a list
    # First sort the pool by trade_id.
    pos_pool = position_pool.copy()
    pos_pool.sort(key=lambda x : x.pos_id)
    
    bucket, temp = [], []
    trade_id_now = pos_pool[0].pos_id
    
    
    i=0
    while i < len(pos_pool):
        # loop through each position, if the pos_id == trade_id_now, save in 
        # a temp list
        if  pos_pool[i].pos_id == trade_id_now:
            if select_func(i):
                temp.append(pos_pool[i])
            i = i + 1
                
        elif pos_pool[i].pos_id != trade_id_now: 
            # Otherwise, put the temp list into the overall bucket, restart 
            # the counter and make a new temp list to repeat the process
            #print('switch')
            #print(i, pos_pool[i].pos_id)
            bucket.append(temp)
            trade_id_now = pos_pool[i].pos_id
            temp = []
            temp.append(pos_pool[i])
            
            i = i + 1

    return bucket

# =============================================================================
# #%% Construction Area
# =============================================================================
# input a month settlement data, output the cumulative average of each month
def cal_cumavg(history_daily_data: pd.DataFrame,
               time_proxy='Date',
               price_proxy="Settle"):
    # Calculate the cumulative average by months
    
    # Inputs
    times = history_daily_data[time_proxy].to_list()
    prices = history_daily_data[price_proxy].to_list()
    
    # Initialise container
    #val_bucket, time_bucket, N_bucket = [],[], []
    cumavg_price_data = []
    # Check what month does this belong to
    # Start the loop
    cumavg_price_data.append((times[0], np.nan , np.nan))

    month_tracker = times[0].month #use the first element as the starting month
    cum_avg_tracker, N = 0, 0
    for time, price in zip(times[1:],prices[1:]):
        
        if time.month == month_tracker:
            cum_avg_tracker = cum_avg_tracker*(N/(N+1)) + price/(N+1)
            
            cumavg_price_data.append((time, cum_avg_tracker , N))
            
            N = N + 1
        # During the switch of month, change the total days to 1 and the cumavg 
        # to the current price.
        elif time.month != month_tracker: 
            cumavg_price_data.append((time, cum_avg_tracker , N))

            cum_avg_tracker = price
            N = 0
            month_tracker = time.month

        ##time_bucket.append(time)
        #val_bucket.append(cum_avg_tracker)
        #N_bucket.append(N)
        
        #cumavg_price_data.append((time, cum_avg_tracker , N))
        
    cumavg_price_data = pd.DataFrame(cumavg_price_data, columns=[time_proxy, 
                                                                 'cumavg_price', 
                                                                 'prev_cum_n'])
    return cumavg_price_data

def cal_cumavg_minute(history_minute_data: pd.DataFrame,
                      cumavg_price_data: pd.DataFrame, 
                      price_proxy: str = 'Settle'):
    # A method that calculate the cumulative average
    #print("Len", len(history_minute_data['Date']))
    dates = history_minute_data['Date']#[0:5000]
    times = history_minute_data['Time']#[0:5000]
    prices = history_minute_data[price_proxy]#[0:5000]
    #print("dtp", dates[dates==datetime.datetime(2016,1,7)].iloc[0])
    today_cum_avg_data = []
    count = 0
    for date, time, price in zip(dates, times, prices):
       # str, pandas timestamp
       date_str = date.strftime("%Y-%m-%d")
       
       #print(type(cumavg_price_data['Date'].iloc[0]), type(date_str))
       cumavg_data_today  = cumavg_price_data[cumavg_price_data['Date'] == date_str]
       #print("cumavg_data_today", cumavg_data_today)
       prev_cum_n = cumavg_data_today['prev_cum_n']
       prev_cum_avg = cumavg_data_today['cumavg_price']
       #print('prev_cum_n, prev_cum_avg', date, prev_cum_n, prev_cum_avg)
       if len(prev_cum_n) == 0 and len(prev_cum_avg) ==0:
           #print("Null", count)
           prev_cum_n, prev_cum_avg = np.nan, np.nan
           today_cum_avg = np.nan
       elif len(prev_cum_n) == 1 and len(prev_cum_avg) ==1:
           prev_cum_n, prev_cum_avg = prev_cum_n.item(), prev_cum_avg.item()
           today_cum_avg = (prev_cum_avg*prev_cum_n + price) / (prev_cum_n + 1)
           #print("item", prev_cum_n, prev_cum_avg, today_cum_avg, count)

       else:
           raise Exception("There is a misalignment! A mismatch between \
                           prev_cum_n and prev_cum_avg.")
                           
       #print("today_cum_avg", today_cum_avg)

       today_cum_avg_data.append((date, time, price, today_cum_avg))
       count = count + 1
        
    today_cum_avg_data = pd.DataFrame(today_cum_avg_data, columns=['Date', 
                                                                   'Time', 
                                                                   price_proxy,
                                                                   'today_cum_avg'])
    return today_cum_avg_data
    

def cal_cumavg_minute_2(history_minute_data: pd.DataFrame,
                        cumavg_price_data: pd.DataFrame, 
                        price_proxy: str = 'Settle'): #WIP
    # A method that calculate the cumulative average
    # change this to the daily cumaverage using the whole day instead of just the point
    #print("Len", len(history_minute_data['Date']))
    dates = history_minute_data['Date']#[0:5000]
    times = history_minute_data['Time']#[0:5000]
    prices = history_minute_data[price_proxy]#[0:5000]
    #print("dtp", dates[dates==datetime.datetime(2016,1,7)].iloc[0])
    today_cum_avg_data = []
    count = 0
    for date, time, price in zip(dates, times, prices):
       # str, pandas timestamp
       date_str = date.strftime("%Y-%m-%d")
       
       #print(type(cumavg_price_data['Date'].iloc[0]), type(date_str))
       cumavg_data_today  = cumavg_price_data[cumavg_price_data['Date'] == date_str]
       #print("cumavg_data_today", cumavg_data_today)
       prev_cum_n = cumavg_data_today['prev_cum_n']
       prev_cum_avg = cumavg_data_today['cumavg_price']
       #print('prev_cum_n, prev_cum_avg', date, prev_cum_n, prev_cum_avg)
       if len(prev_cum_n) == 0 and len(prev_cum_avg) ==0:
           #print("Null", count)
           prev_cum_n, prev_cum_avg = np.nan, np.nan
           today_cum_avg = np.nan
       elif len(prev_cum_n) == 1 and len(prev_cum_avg) ==1:
           prev_cum_n, prev_cum_avg = prev_cum_n.item(), prev_cum_avg.item()
           today_cum_avg = (prev_cum_avg*prev_cum_n + price) / (prev_cum_n + 1)
           print("item", prev_cum_n, prev_cum_avg, today_cum_avg, count)

       else:
           raise Exception("There is a misalignment! A mismatch between \
                           prev_cum_n and prev_cum_avg.")
                           
       #print("today_cum_avg", today_cum_avg)

       today_cum_avg_data.append((date, time, price, today_cum_avg))
       count = count + 1
        
    today_cum_avg_data = pd.DataFrame(today_cum_avg_data, columns=['Date', 
                                                                   'Time', 
                                                                   price_proxy,
                                                                   'today_cum_avg'])
    return today_cum_avg_data


def find_minute_EES_long(histroy_data: pd.DataFrame, 
                         target_entry: float, target_exit: float, stop_exit: float,
                         open_hr: str = "0330", close_hr: str = "1930", 
                         price_proxy: str = 'Open', 
                         time_proxy: str= 'Time',
                         date_proxy: str = 'Date',
                         direction: str = 'Neutral',
                         close_trade_hr: str = '1925', 
                         dt_scale: str = 'datetime',
                         first_date = None, last_date = None) -> dict:
    """
    Set the EES value given a time-series of minute intraday data.
    This function is the key for crossover loops in the backtest

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
    # (This function can be made in one more layer of abstraction. Work on this later)
    if first_date == None:
        first_date = histroy_data[date_proxy].iloc[0]
    if last_date == None:
        last_date = histroy_data[date_proxy].iloc[-1]
        
    print('first_date, last_date', first_date, last_date)
    # define subsample. turn the pandas series into a numpy array
    price_list = histroy_data[price_proxy].to_numpy()
    time_list = histroy_data[time_proxy].to_numpy()
    
    # read in date list
    date_list = histroy_data[date_proxy].to_numpy() 
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
    
    # Define the opening/closing time and closing price. 
    first_date_str = first_date.strftime("%y-%m-%d")
    last_date_str = last_date.strftime("%y-%m-%d")
    # Here we choose 19:25 for final trade
    open_hr_str = open_hr.strftime("%H%M")
    close_hr_str = close_hr.strftime("%H%M")

    ## Find the closest price and datettime instead of having it at exactly the open time
    open_date_new, open_pt = find_closest_price_datetime(histroy_data, 
                                                  target_date = first_date, 
                                                  target_hr = open_hr_str,
                                                  price_proxy=price_proxy,
                                                  direction = 'forward')
    
    #open_date = date_list[np.where(time_list==open_date_new)[0]][0]
    open_date = datetime_list[0]
    open_datetime = datetime.datetime.combine(open_date.date(), 
                                               open_date_new)

    # Find the closest price and datettime instead of having it at exactly the close time
    close_date_new, close_pt = find_closest_price_datetime(histroy_data, 
                                                  target_date = last_date,
                                                  target_hr = close_hr_str,
                                                  price_proxy=price_proxy,
                                                  direction = 'backward')
    #close_date = date_list[np.where(time_list==close_date_new)[0]][0]
    close_date = datetime_list[-1]
    close_datetime = datetime.datetime.combine(close_date.date(), 
                                               close_date_new)

    # storage
    EES_dict = {'entry': list(zip(entry_times,entry_pts)),
                'exit': list(zip(exit_times,exit_pts)),
                'stop': list(zip(stop_times,stop_pts)),
                'open': tuple((open_datetime, open_pt)),
                'close': tuple((close_datetime, close_pt))}

    print('EES_dict', EES_dict)
    return EES_dict

def find_minute_EES_range_long():
    ...


# I: prev_cum_avg, prev_cum_n, minute_data; O:
# today_cum_avg
# Make a list of today_cum_avg base on minute by minute


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