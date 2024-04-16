#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 13 19:51:24 2024

@author: dexter

A modified script based on the Mean-Reversion Method developed by Abbe Whitford.

"""
# import libraries
import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import CubicSpline, UnivariateSpline
import getpass 
import time
import datetime
import findiff as fd 

import EC_strategy as EC_strategy
from ArgusPossibilityCurves2 import ArgusPossibilityCurves

__all__ = []

__author__="Dexter S.-H. Hon"

# def save_file():
# a master function that allows you to save a file in a "read" function

def time_it(func):
    # simple timing function
    def wrapper(*args, **kwargs):
        t1 = time.time()
        result = func(*args, **kwargs)
        t2 = time.time()-t1
        print(f"{func.__name__} ran in {t2} seconds.")
        return result
    return wrapper

def save_csv(savefilename, save_or_not = True):
    def decorator(func):
        def wrapper(*args, **kwargs):
            data = func(*args, **kwargs)
            if save_or_not:
                data.to_csv(savefilename, index=False)
                return data
            elif not save_or_not:
                return data
        return wrapper
    return decorator
         
@time_it
def date_matching(date1,date2):
    # A simple function that ensure the date from two data sources match
    if date1 == date2:
        pass
    else:
        raise Exception("Date not match. Date1:{}, Date2:{}".format(
            str(date1),str(date2)))
        
def date_matching_list(date_list1, date_list2):
    if len(date_list1) == len(date_list2):
        pass
    else:
        raise Exception("Date list missmatch dimenstion")
    for i in range(len(date_list1)):
        date_matching(date_list1[i], date_list2[i])
  
def check_format():
    return None

# Convert file from CSV to HDF5, npy? Npy might be faster
def convert_csv_to_npy(filename):
    # A function that turn big csv to npy file for faster read-time
    # This is meant to be run once only for each file
            
    #dat = pd.read_csv(filename)
    #dat['Forecast Period'] = pd.to_datetime(dat['Forecast Period']) # make columns datetime objects 
    dat = np.genfromtxt(filename, delimiter=",")
    print(dat[0:10])
    return dat


def find_quant(curve_today, price):
    """
    This is an inverse Spline interpolation treating the pdf as the x-axis.
    This is meant to find the corresponding quantile with a given price.
    
    This function assumes a range of probability distribution function in
    between 0.0025 and 0.9975 qantiles that has a 0.0025 interval

    Parameters
    ----------
    curve_today : 1D pandas dataframe
        A 1D array that contains a discrete number of pdf points.
    price : float
        The given price.

    Returns
    -------
    quant : float
        The corresponding quantile.

    """

    spline_apc = CubicSpline(curve_today.to_numpy()[1:-1], 
                            np.arange(0.0025, 0.9975, 0.0025))
    quant = spline_apc(price)
    return quant
    

# somewhat tested.
@time_it
@save_csv("APC_test.csv",save_or_not = False)
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
    return None    

# tested.
def read_portara_daily_data(filename, symbol, start_date, end_date, 
                      column_select = ['Settle', 'Price Code', 
                                       'Contract Symbol', 'Date only']):
    """
    A generic function that read the Portara Data in a suitable form. 
    The function itself only read a single csv file at a time.

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
    portara_dat: 2D pandas data frame

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
    bools = portara_dat['Date'].apply(lambda x: x > pd.to_datetime(start_date) 
                                      and x < pd.to_datetime(end_date))
        
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
    print("portara_dat",type(portara_dat))
    return portara_dat

# tested some what
#@time_it
def read_portara_minute_data(filename, symbol, start_date, end_date,
                             start_filter_hour=30, end_filter_hour=331,
                             column_select=[]):
    """
    A modified version of the generic Portara reading function specifically for 
    the 1 minute data.

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
        The start time for filtering by hours. The default is 30 because of 
        the london trading hours. 
    end_filter_hour : int, optional
        The end time for filtering by hours. The default is 331.

    Returns
    -------
    portara_dat_2 : 2D panda dataframe
        DESCRIPTION.

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
    bools = portara_dat_2['Date only'].apply(lambda x: x > pd.to_datetime(start_date) 
                                             and x < pd.to_datetime(end_date)) # filter for data after given date 
    portara_dat_2 = portara_dat_2[bools]
    
    # add c1 for front month contract
    portara_dat_2['Price Code'] = portara_dat_2['symbol'] + 'c' + str(val+1)

    return portara_dat_2

#@time_it
def merge_portara_data(table1, table2):
    """
    Merging the Portara Daily and Minute table. The merger is operated on the 
    two columns: 'Date only' and 'Price Code'.

    Parameters
    ----------
    table1 : pandas dataframe
        The Portara Daily pricing data.
    table2 : pandas dataframe
        The Portara Minute pricing data.

    Returns
    -------
    new_table : pandas dataframe
        The concantenated table containing both the daily and minute data.

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

    Parameters
    ----------
    portara_dat : TYPE
        DESCRIPTION.

    Returns
    -------
    portara_dat : TYPE
        DESCRIPTION.

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

def make_signal_bucket():
    # a function that make data bucket for a particular strategy

    signal_columns = ['APC forecast period', 'APC Contract Symbol']
    
    # usemaxofpdf_insteadof_medianpdf
    A = ["Q0.1","Q0.4","Q0.5","Q0.6","Q0.9"]
    
    B = ["Q0.1", "Qmax-0.1", "Qmax","Qmax+0.1","Q0.9"]
    
    # use_OB_OS_levels_for_lag_conditions
    C = ["Close price lag 1", "Close price lag 2", "OB level 1 lag 1", 
         "OB level 1 lag 2", "OS level 1 lag 1", "OS level 1 lag 2", 
         "OB level 3", "OS level 3", "Price 3:30 UK time"]
    
    D = ['Quant close lag 1', 'Quant close lag 2', 'mean Quant close n = 5',
         'Quant 3:30 UK time']
    
    # abs(entry_region_exit_region_range[0]) > 0
    E = ['target entry lower', 'target entry upper']
    
    F = ['target entry']
    
    # abs(entry_region_exit_region_range[1]) > 0:
    G= ['target entry lower', 'target entry upper']

    H = ['target exit']
    
    End = ['stop exit', 'direction', 'price code']
    
    # Base form of column, benchmark
    # Old + A + D + F + H + end
    
    bucket_mr_st_1_keys = signal_columns + A + D + F + H + End
    
    I1 = signal_columns + A + D + F + H + End
    
    #I1 = ['APC forecast period', 'APC Contract Symbol', "Q0.1", "Qmax-0.1", 
    #     "Qmax","Qmax+0.1","Q0.9", 'Quant close lag 1', 'Quant close lag 2', 
    #     'mean Quant close n = 5', 'Quant 3:30 UK time', 'target entry', 
    #     'target exit', 'stop exit', 'direction', 'price code']
    
    dict_futures_quant_signals = dict()
    for i in I1:
        dict_futures_quant_signals[i] = []
    
    return dict_futures_quant_signals

def argus_benchmark_strategy(price_330, history_data_lag5, apc_curve_lag5,
                                 curve_today):
        """
        The benchmark mean reversion strategy

        Parameters
        ----------
        price_330 : float
            DESCRIPTION.

        Returns
        -------
        dict
            A dictionary.

        """
        # inputs
        quant_330UKtime = price_330
        lag5_price = history_data_lag5['Settle']
        
        # Match the date just to be sure

        # define the lag 2 days settlement prices
        history_data_lag2_close = lag5_price.iloc[-2]
        history_data_lag1_close = lag5_price.iloc[-1]
        
        # The APC two days (lag2) before this date
        signal_data_lag2_median =  apc_curve_lag5.iloc[-2]['0.5'] 
        # The APC one day1 (lag1) before this date
        signal_data_lag1_median =  apc_curve_lag5.iloc[-1]['0.5']

        
        # pulling directly from a list is a factor of 3 faster than doing spline everytime
        
        # calculate the 5 days average for closing price
        rollinglagq5day = np.average(lag5_price)         
                
        # calculate the median of the apc for the last five days
        median_apc_5days = np.median([apc_curve_lag5.iloc[-5]['0.5'],
                                      apc_curve_lag5.iloc[-4]['0.5'],
                                      apc_curve_lag5.iloc[-3]['0.5'],
                                      apc_curve_lag5.iloc[-2]['0.5'],
                                      apc_curve_lag5.iloc[-1]['0.5']])

        # "BUY" condition
        # (1) Two consecutive days of closing price lower than the signal median
        cond1_buy = (history_data_lag2_close < signal_data_lag2_median)
        cond2_buy = (history_data_lag1_close < signal_data_lag1_median)
        # (2) rolling 5 days average lower than the media apc 
        cond3_buy = rollinglagq5day < median_apc_5days
        # (3) price at today's opening hour above the 0.1 quantile of today's apc
        cond4_buy = quant_330UKtime >= curve_today['0.1']
        
        # "SELL" condition
        # (1) Two consecutive days of closing price higher than the signal median
        cond1_sell = (history_data_lag2_close > signal_data_lag2_median)
        cond2_sell = (history_data_lag1_close < signal_data_lag1_median)    
        # (2) rolling 5 days average higher than the media apc 
        cond3_sell = rollinglagq5day > median_apc_5days
        # (3) price at today's opening hour below the 0.9 quantile of today's apc
        cond4_sell = quant_330UKtime <= curve_today['0.9']
        
        # Find the boolean value of strategy conditions
        Buy_cond = cond1_buy and cond2_buy and cond3_buy and cond4_buy
        Sell_cond =  cond1_sell and cond2_sell and cond3_sell and cond4_sell
        Neutral_cond = not (Buy_cond and Sell_cond)
        
        # make direction dictionary
        direction_dict = {"Buy": Buy_cond, "Sell": Sell_cond, "Neutral": Neutral_cond}
        
        for i in direction_dict:
            if direction_dict[i] == True:
                direction = i
        
        return direction
    
def set_entry_price(cond, curve_today,buy_cond=(0.4,0.1) , sell_cond =(0.6,0.9)):
        
        if cond=="Buy":
            # (A) Entry region at price < APC p=0.4 and 
            entry_price = curve_today['0.4']
            # (B) Stop loss at APC p=0.1
            stop_loss = curve_today['0.1']
        elif cond=="Sell":
            # (A) Entry region at price > APC p=0.6 and 
            entry_price = curve_today['0.6']
            # (B) Stop loss at APC p=0.9
            stop_loss = curve_today['0.9']
        elif cond == "Neutral":
            # (A) Entry region at price > APC p=0.6 and 
            entry_price = "NA"
            # (B) Stop loss at APC p=0.9
            stop_loss = "NA"
        return {entry_price, stop_loss}

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
    lag_size : TYPE, optional
        The size of the lag window. The default is 5 (days).

    Returns
    -------
    signal_data_lag : pandas data frame
        The signal data five (lag_size) days prior to the given date.
    history_data_lag : pandas data frame
        The historical data five (lag_size) days prior to the given date.

    """

    # Find the row index of the history data first
    row_index = history_data.index[history_data['Date only'] == date].tolist()[0]
    
    # extract exactly 5 (default) lag days array
    history_data_lag = history_data.loc[row_index-lag_size:row_index-1]

    # use the relevant date from history data to get signal data to ensure matching date
    window = history_data_lag['Date only'].tolist()
    
    #Store the lag signal data in a list
    signal_data_lag = signal_data[signal_data['Forecast Period'] == window[0]]
    
    for i in range(lag_size-1):
        curve = signal_data[signal_data['Forecast Period'] == window[i+1]]
        signal_data_lag = pd.concat([signal_data_lag, curve])
        
    return signal_data_lag, history_data_lag


def loop_signal(signal_data, history_data, dict_contracts_quant_signals, history_data_daily,
                loop_start_date="2024-01-10"):
    
    start_date = loop_start_date
        
    # success
    APCs_dat = signal_data[signal_data['Forecast Period'] > start_date]
    portara_dat = history_data[history_data["Date only"] > start_date]
    
    print(APCs_dat['Forecast Period'])
    # where to start
    
    for i in np.arange(len(APCs_dat)): # loop through every forecast date and contract symbol 
        
        APCs_this_date_and_contract = APCs_dat.iloc[i] # get the ith row 
        
        forecast_date = APCs_this_date_and_contract.to_numpy()[0]
        symbol = APCs_this_date_and_contract.to_numpy()[-1]
        
        ###############################
        # select for only rows in the history data with date matching the signal data
        dat_330 = portara_dat[portara_dat['Date only'] == forecast_date]
        
        # select for only rows in the history data with date matching the symbol, "CL"
        # can delete 
        dat_330 = dat_330[dat_330['Contract Symbol'].apply(lambda x: str(x)[:-3])==symbol]
        
        quant_330UKtime = np.NaN 
                        
        if dat_330.shape[0] > 0:
                
            price_330 = dat_330.iloc[0].to_numpy()[1] # 330 UK time 
                    
            if np.isnan(price_330):
                continue 
        else: 
            continue # data not available! 
            
        quantiles_forwantedprices = [0.1, 0.4, 0.5, 0.6, 0.9] 
            
        end_prices = -1 
            
        # input quantiles_forwantedprices range in the interpolation of the APC scatter plot
        # Here it get the probabilty at different x axis
        wanted_quantiles = CubicSpline(np.arange(0.0025, 0.9975, 0.0025),   # wanted quantiles for benchmark algorithm entry/exit/stop loss 
                APCs_this_date_and_contract.to_numpy()[1:end_prices])(quantiles_forwantedprices)
        
        ###############################
        
        portara_dat_filtered = portara_dat[portara_dat['Contract Symbol'].apply(lambda x: str(x)[:-3] == symbol)]
        portara_dat_filtered = portara_dat_filtered.reset_index(drop=True)
        index_thisapc = portara_dat_filtered[portara_dat_filtered['Date only'] == (forecast_date)] 
        
        #print("index_thisapc",index_thisapc)

        
        full_contract_symbol = index_thisapc.to_numpy()[0][-1]
        full_price_code = index_thisapc.to_numpy()[0][-2]
        index_thisapc = index_thisapc.index[0]
        
        ###############################   
        # calculate the quantile where the starting pice (3:30am UK) sits
        apcdat = APCs_this_date_and_contract.to_numpy()[1:end_prices]
        uapcdat = np.unique(apcdat)
        indices_wanted = np.arange(0, len(apcdat))
        indices_wanted = np.argmin(abs(apcdat[:,None] - uapcdat), axis=0)
        yvals = np.arange(0.0025, 0.9975, 0.0025)[indices_wanted]
        get_330_uk_quantile = CubicSpline(uapcdat, yvals)([price_330])          
        
        quant_330UKtime = get_330_uk_quantile[0]
        
        if quant_330UKtime > 1.0: 
            quant_330UKtime = 0.999990
        elif quant_330UKtime < 0.0:
            quant_330UKtime = 0.000001
            
        
        # input for strategy
        price_330 = quant_330UKtime
        curve_today = APCs_this_date_and_contract
        ###############################
        
        # Get the extracted 5 days Lag data 
        apc_curve_lag5, history_data_lag5 = extract_lag_data(signal_data, 
                                                             history_data_daily, 
                                                             forecast_date)
        
        print(apc_curve_lag5)
        print(history_data_lag5)
        # Run the strategy        
        direction = argus_benchmark_strategy(
             price_330, history_data_lag5, apc_curve_lag5, curve_today)
        
        print("direction done", i, direction, forecast_date)

        history_data_lag2_close = history_data_lag5["Settle"].iloc[-2]
        history_data_lag1_close = history_data_lag5["Settle"].iloc[-1]

        #print("lag1q,lag2q", lag1q,lag2q)

        # Find the quantile of the relevant price for the last two dats
        lag1q = find_quant(curve_today, history_data_lag2_close)  
        lag2q = find_quant(curve_today, history_data_lag1_close)
        
        rollinglagq5day = np.average(history_data_lag5["Settle"].to_numpy())
        
    
        ##################################################################################
        # Make a function later to do this 
        # based on the strategy chosen, the setup of the bucket should be different
        # (make_buket)-> Strategy (loop)->(store_to_bucket)
        # function: store_to_bucket
        
        # Storing the data    
        dict_contracts_quant_signals['APC forecast period'].append(forecast_date)
        dict_contracts_quant_signals['APC Contract Symbol'].append(full_contract_symbol)
    
        dict_contracts_quant_signals['Q0.1'].append(wanted_quantiles[0])
        dict_contracts_quant_signals['Q0.4'].append(wanted_quantiles[1])
        dict_contracts_quant_signals['Q0.5'].append(wanted_quantiles[2])
        dict_contracts_quant_signals['Q0.6'].append(wanted_quantiles[3])
        dict_contracts_quant_signals['Q0.9'].append(wanted_quantiles[4])
        
    
        dict_contracts_quant_signals['Quant close lag 1'].append(lag1q)
        dict_contracts_quant_signals['Quant close lag 2'].append(lag2q)
        dict_contracts_quant_signals['mean Quant close n = 5'].append(rollinglagq5day) 
        dict_contracts_quant_signals['Quant 3:30 UK time'].append(quant_330UKtime)
        
        dict_contracts_quant_signals['target entry'].append(wanted_quantiles[1])
        dict_contracts_quant_signals['target exit'].append(wanted_quantiles[3])
        dict_contracts_quant_signals['stop exit'].append(wanted_quantiles[0]) 
        
        dict_contracts_quant_signals['direction'].append(direction)
        dict_contracts_quant_signals['price code'].append(full_price_code)   


    dict_contracts_quant_signals = pd.DataFrame(dict_contracts_quant_signals)
    #sort by date
        
    #dict_contracts_quant_signals.to_csv(save_signals_name_prefix + file_save_suffices[a], index=False) 
    return dict_contracts_quant_signals




@time_it
def run_generate_MR_signals():
    # input is a dictionary or json file
    
    # run meanreversion signal generation on the basis of individual programme  
    # Loop the whole list in one go with all the contracts or Loop it one contract at a time?
    
    #inputs: Portara data (1 Minute and Daily), APC
    
    # 1) Exception case check
    # 2) File name management
    # 3) Read in CSV Argus curve
    # 4) Read Portara data
    # 5) Create pricing 
    
    # Draft
    username = "dexter@eulercapital.com.au"
    password = "76tileArg56!"
    start_date = "2024-01-10"
    start_date_2 = "2024-01-01"
    end_date = "2024-01-30"
    categories = 'Argus Nymex WTI month 1, Daily'
    keywords = "WTI"
    symbol = "CL"

    filename_daily = "../test_MS/data_zeroadjust_intradayportara_attempt1/Daily/CL.day"
    filename_minute = "../test_MS/data_zeroadjust_intradayportara_attempt1/intraday/1 Minute/CL.001"
    
    # load the table in memory and test multple strategies
    # input APC file
    signal_data = get_apc_from_server(username, password, start_date_2, 
                                      end_date, categories,
                            keywords=keywords,symbol=symbol)
    
    # input history file
    # start_date2 is a temporary solution
    history_data_daily = read_portara_daily_data(filename_daily,symbol,
                                                 start_date_2,end_date)
    history_data_minute = read_portara_minute_data(filename_minute,symbol, 
                                                   start_date_2, end_date,
                                                   start_filter_hour=30, 
                                                   end_filter_hour=331)
    history_data = merge_portara_data(history_data_daily, history_data_minute)

    # need to make sure start date of portara is at least 5days ahead of APC data
    # need to make sure the 5 days lag of the APC and history data matches

    # Deal with the date problem in Portara data
    history_data = portara_data_handling(history_data)
    
    # Checking function to make sure the input of the strategy is valid (maybe dumb them in a class)
    # check date and stuff
    
    # make an empty signal dictionary for storage
    dict_contracts_quant_signals = make_signal_bucket()
    
    # experiment with lag data extraction
    #extract_lag_data(signal_data, history_data_daily, "2024-01-10")
    
    # The strategy will be ran in loop_signal decorator
    dict_contracts_quant_signals = loop_signal(signal_data, history_data, 
                                               dict_contracts_quant_signals, history_data_daily)
    
    
    # Manual input for filename management (save)
    
    return dict_contracts_quant_signals

dict_contracts_quant_signals = run_generate_MR_signals()


