#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr  2 14:09:54 2024

@author: dexter
"""
import numpy as np
import pandas as pd
import datetime

import utility as util

# Argus API 
from ArgusPossibilityCurves2 import ArgusPossibilityCurves

__all__ = ['get_apc_from_server','read_apc_data','read_portara_daily_data', 
           'read_portara_minute_data','merge_portara_data',
           'portara_data_handling', 'extract_lag_data', 
           'read_reformat_Portara_minute_data']

__author__="Dexter S.-H. Hon"


def get_apc_from_server(username, password, start_date, end_date, categories,
                        keywords=None, symbol=None):
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
def read_portara_daily_data(filename, symbol, start_date, end_date, 
                      column_select = ['Settle', 'Price Code', 
                                       'Contract Symbol', 'Date only']):
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

# tested some what
#@time_it
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

#@time_it
def merge_portara_data(table1, table2):
    """
    Merging the Portara Daily and Minute table. The merger is operated on the 
    two columns: 'Date only' and 'Price Code'.
    
    LEGACY function from Abbe.

    Parameters
    ----------
    table1 : pandas dataframe
        The pandas dataframe Daily pricing data.
    table2 : TYPE
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
def portara_data_handling(portara_dat):
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
def read_reformat_Portara_daily_data(filename):
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
    
    # include a function that let user to choose the reformat?
    
    # change the date from 20220222 (int) to '2022-02-22' (str)
    #history_data['Date'] = [str(x)[0:4] + '-' + str(x)[4:6] + '-' + str(x)[6:] 
    #                        for x in history_data['Date']]
    
    history_data['Date'] = [datetime.datetime(year = int(str(x)[0:4]), 
                                              month=int(str(x)[4:6]), 
                                              day = int(str(x)[6:])) 
                            for x in history_data['Date']]

    return history_data


#tested
def read_reformat_Portara_minute_data(filename):
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
    #history_data['Date'] = [str(x)[0:4] + '-' + str(x)[4:6] + '-' + str(x)[6:] 
    #                        for x in history_data['Date']]
    
    history_data['Date'] = [datetime.datetime(year = int(str(x)[0:4]), 
                                              month=int(str(x)[4:6]), 
                                              day = int(str(x)[6:])) 
                            for x in history_data['Date']]
    
    # convert the format 1330 (int) to 13:30 (datetime.time) obejct
    intmin = history_data['Time']
    bucket = util.convert_intmin_to_time(intmin) #, label='Time')
    
    history_data['Time'] = bucket

    return history_data


def read_reformat_APC_data(filename):
    signal_data =  pd.read_csv(filename)
    
    signal_data['Forecast Period'] = [datetime.datetime(year = int(str(x)[0:4]), 
                                              month=int(str(x)[5:7]), 
                                              day = int(str(x)[8:])) 
                            for x in signal_data['Forecast Period']]
    
    return signal_data

#tested
def extract_lag_data(signal_data, history_data, date, lag_size=5):
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
    row_index = history_data.index[history_data['Date'] == date].tolist()[0]

    # extract exactly 5 (default) lag days array
    history_data_lag = history_data.loc[row_index-lag_size:row_index-1]

    # use the relevant date from history data to get signal data to ensure matching date
    window = history_data_lag['Date'].tolist()
    # turn Timstamp into string
    window = [str(window[i])[0:10] for i in range(lag_size)]
        
    #Store the lag signal data in a list
    signal_data_lag = signal_data[signal_data['Forecast Period'] == window[0]]
    
    for i in range(lag_size-1):
        curve = signal_data[signal_data['Forecast Period'] == window[i+1]]
        signal_data_lag = pd.concat([signal_data_lag, curve])
        
    return signal_data_lag, history_data_lag

# tested
def find_closest_price(day_minute_data, target_hr='0330', direction='forward', 
                       step = 1, search_time = 1000):
    
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
            
    return target_hr_dt, target_price

#%% Construction Area
def extract_lag_data_to_list(signal_data, history_data_daily,lag_size=5):
    # make a list of lag data with a nested data structure.
    
    return None
    #extract_lag_data(signal_data, history_data_daily, "2024-01-10")




def render_PNL_xlsx(filename):
    """
    LEGACY function from Abbe.
    """
    #WIP
    
    # the function read in the backtest result to generate an xlsx file with PNL
    
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
    
    price_codes = ['CLc1', 'CLc2', 'HOc1', 'HOc2', 'RBc1', 'RBc2', 'QOc1', 'QOc2', 'QPc1', 'QPc2']
    number_barrels_per_contract = [1000, 1000, 42000, 42000, 42000, 42000, 1000, 1000, 100, 100] # https://www.cmegroup.com/trading/energy/crude-and-refined-products.html (useful info)
   
    number_contracts = 50 
    fees_per_contract = [24.0, 24.0, 25.2, 25.2, 25.2, 25.2, 24.0, 24.0, 24.0, 24.0]
    
    dat = pd.read_csv(filename)
    
    with pd.ExcelWriter(filename[:-4]+'_.xlsx') as excel_writer: 
        
        dattotal = dat
        dattotal = dattotal.sort_values(by='date')
        dattotal['number barrels/gallons'] = dattotal['Price Code'].apply(lambda x: num_per_contract[x])
        dattotal['fees'] = dattotal['Price Code'].apply(lambda x: round_turn_fees[x])
        dattotal['fees'] = np.where(np.isnan(dattotal['entry price']), 0.0, dattotal['fees'])
        dattotal['scaled returns from trades'] =  dattotal['return from trades']*dattotal['number barrels/gallons'] - dattotal['fees']

    return dattotal