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
import EC_read as EC_read

from ArgusPossibilityCurves2 import ArgusPossibilityCurves

__all__ = []

__author__="Dexter S.-H. Hon"

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
        ValueError("Date list missmatch dimenstion")
    for i in range(len(date_list1)):
        date_matching(date_list1[i], date_list2[i])
        
def list_match(list1,list2):
    if list1 == list2:
        pass
    else:
        # Find the exception
        bool_list = list( map(lambda x, y: x==y, list1, list2)) 
        
        mismatch_index = []
        for i in range(len(bool_list)):
            if bool_list[i] == False:         
                mismatch_index.append(i)
        
        raise ValueError(
            "Mismatch at the following positions:{}".format(mismatch_index))
  
def check_format():
    return None
#%%

def cal_APC_pdf(apc_prices):
    #cdf
    even_spaced_prices = np.arange(np.min(apc_prices), np.max(apc_prices), 0.005)
    spline_apc_rev = UnivariateSpline(apc_prices, np.arange(0.0025, 0.9975, 0.0025), s = 0)
    quantiles_even_prices = spline_apc_rev(even_spaced_prices)

    dq = even_spaced_prices[1]-even_spaced_prices[0]
    deriv = fd.FinDiff(0, dq, 1)
    pdf = deriv(quantiles_even_prices)
    spline_pdf = UnivariateSpline(even_spaced_prices, pdf,  s = 0.0015)
    pdf = spline_pdf(even_spaced_prices)
    
    return pdf
    
# Convert file from CSV to HDF5, npy? Npy might be faster
def convert_csv_to_npy(filename):
    # A function that turn big csv to npy file for faster read-time
    # This is meant to be run once only for each file
            
    #dat = pd.read_csv(filename)
    #dat['Forecast Period'] = pd.to_datetime(dat['Forecast Period']) # make columns datetime objects 
    dat = np.genfromtxt(filename, delimiter=",")
    print(dat[0:10])
    return dat


def find_quant_APC(curve_today, price):
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
    
#%%
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
    portara_dat: 2D pandas dataframe
        The table from Portara
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
        The minute table form Portara.

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

        price_330 = np.where(np.isnan(portara_dat['Close 330'].to_numpy()), 
                             portara_dat['Close ' + str(i)].to_numpy(),
                             portara_dat['Close 330'].to_numpy())
        portara_dat['Close 330'] = price_330
            
    for i in np.flip(minutes_2): # if there are no trades Portara doesn't create a bar so we have to go backwards to the last bar where a trade
    # happened to get the price iff there is no bar for 330 (getting 230 prices for when daylight savings moving UK to BST (1 hour forward) from UTC/GMT

        price_230 = np.where(np.isnan(portara_dat['Close 230'].to_numpy()), 
                             portara_dat['Close ' + str(i)].to_numpy(), 
                             portara_dat['Close 230'].to_numpy())
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

def make_signal_bucket(strategy_name="benchmark"):
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
    
        
    # a dictionary for column combination
    strategy_dict = {
        "benchmark": signal_columns + A + D + F + H + End, 
        "mode": signal_columns + B + D + F + H + End 
                   }
   
    # Define the empty bucket keys
    bucket_keys = strategy_dict[strategy_name]
    
    dict_futures_quant_signals = dict()
    for i in bucket_keys:
        dict_futures_quant_signals[i] = []
    
    return dict_futures_quant_signals

def store_to_bucket_single(bucket, data):
    # THis function should be used in adjacent to make_signal_bucket
    
    # Check the if the columns mathces? and the input list dimension
    
    # Storing the data    
    for i, key in enumerate(bucket):
        bucket[key].append(data[i])   

    return bucket

def argus_benchmark_strategy(price_330, history_data_lag5, apc_curve_lag5,
                                 curve_today):
    """
    This function takes in one single day worth of data and 
    produce a string of "Buy/Sell" signal.
    
    The benchmark mean reversion strategy from Argus media. This is our 
    baseline MR strategy. It generate a "Buy/Sell" signal base on the followiing:
        
        IF (1) Two consecutive days of closing price lower than the signal median
           (2) rolling 5 days average lower than the median apc 
           (3) price at today's opening hour above the 0.1 quantile of today's apc
        Then,
            produce "Buy" signal.
            
        IF (1) Two consecutive days of closing price higher than the signal median
           (2) rolling 5 days average higher than the median apc 
           (3) price at today's opening hour below the 0.9 quantile of today's apc
         Then,
             produce "Sell" signal.
    
    Note that the neutral signal is given by a xnor gate. It means that if 
    both Buy_cond and Sell_cond are the same, Neutral_cond return True.

    Parameters
    ----------
    price_330 : float
        The starting price of the day.
    history_data_lag5 : pandas dataframe table
        The last 5 days of historical data.
    apc_curve_lag5 : pandas dataframe table
        The last 5 days of APC data.
    curve_today : 1D pandas dataframe
        The APC curve of today.

    Returns
    -------
    direction : str
        "Buy/Sell" signal.

    """
    # inputs
    quant_330UKtime = price_330
    lag5_price = history_data_lag5['Settle']
        
    # Match the date just to be sure
    # To be added
    
    # define the lag 2 days settlement prices
    history_data_lag2_close = lag5_price.iloc[-2]
    history_data_lag1_close = lag5_price.iloc[-1]
        
    # The APC two days (lag2) before this date
    signal_data_lag2_median =  apc_curve_lag5.iloc[-2]['0.5'] 
    # The APC one day1 (lag1) before this date
    signal_data_lag1_median =  apc_curve_lag5.iloc[-1]['0.5']

    # Reminder: pulling directly from a list is a factor of 3 faster than doing 
    # spline everytime
        
    # calculate the 5 days average for closing price
    rollinglagq5day = np.average(lag5_price)         
                
    # calculate the median of the apc for the last five days
    median_apc_5days = np.median([apc_curve_lag5.iloc[-5]['0.5'],
                                      apc_curve_lag5.iloc[-4]['0.5'],
                                      apc_curve_lag5.iloc[-3]['0.5'],
                                      apc_curve_lag5.iloc[-2]['0.5'],
                                      apc_curve_lag5.iloc[-1]['0.5']])
    
    lag1q = find_quant_APC( apc_curve_lag5.iloc[-1], lag5_price.iloc[-1])
    lag2q = find_quant_APC( apc_curve_lag5.iloc[-2], lag5_price.iloc[-2])
    lag3q = find_quant_APC( apc_curve_lag5.iloc[-3], lag5_price.iloc[-3])
    lag4q = find_quant_APC( apc_curve_lag5.iloc[-4], lag5_price.iloc[-4])
    lag5q = find_quant_APC( apc_curve_lag5.iloc[-5], lag5_price.iloc[-5])
    
    rol5q = (lag1q+lag2q+lag3q+lag4q+lag5q)/5.0

    # "BUY" condition
    # (1) Two consecutive days of closing price lower than the signal median
    cond1_buy = (history_data_lag2_close < signal_data_lag2_median)
    cond2_buy = (history_data_lag1_close < signal_data_lag1_median)
    # (2) rolling 5 days average lower than the median apc 
    #cond3_buy = rollinglagq5day < median_apc_5days
    cond3_buy = rol5q < 0.5
    # (3) price at today's opening hour above the 0.1 quantile of today's apc
    cond4_buy = quant_330UKtime >= curve_today['0.1']
    
    # "SELL" condition
    # (1) Two consecutive days of closing price higher than the signal median
    cond1_sell = (history_data_lag2_close > signal_data_lag2_median)
    cond2_sell = (history_data_lag1_close > signal_data_lag1_median)    
    # (2) rolling 5 days average higher than the median apc 
    # cond3_sell = rollinglagq5day > median_apc_5days
    cond3_sell = rol5q > 0.5

    # (3) price at today's opening hour below the 0.9 quantile of today's apc
    cond4_sell = quant_330UKtime <= curve_today['0.9']
        
    print("======================")  
    print("cond1_buy", cond1_buy, history_data_lag2_close, signal_data_lag2_median)
    print("cond2_buy", cond2_buy, history_data_lag1_close, signal_data_lag1_median)
    print("cond3_buy", cond3_buy, rollinglagq5day,  median_apc_5days)
    print("cond4_buy", cond4_buy, quant_330UKtime, curve_today['0.1'])
    print("====================")
    print("cond1_sell", cond1_sell, history_data_lag2_close, signal_data_lag2_median)
    print("cond2_sell", cond2_sell, history_data_lag1_close, signal_data_lag1_median)
    print("cond3_sell", cond3_sell, rollinglagq5day,  median_apc_5days)
    print("cond4_sell", cond4_sell, quant_330UKtime, curve_today['0.1'])
    print("======================")
    print("lag1q,lag2q, inside",lag1q,lag2q,rol5q)
    print("======================")

    # Find the boolean value of strategy conditions
    Buy_cond = cond1_buy and cond2_buy and cond3_buy and cond4_buy
    Sell_cond =  cond1_sell and cond2_sell and cond3_sell and cond4_sell
        
    Neutral_cond = not (Buy_cond ^ Sell_cond) #xnor gate
    
    # make direction dictionary
    direction_dict = {"Buy": Buy_cond, "Sell": Sell_cond, "Neutral": Neutral_cond}
        
    for i in direction_dict:
        if direction_dict[i] == True:
            direction = i
        
    return direction

def MR_mode_strategy(price_330, history_data_lag5, apc_curve_lag5, curve_today):
    
    # inputs
    quant_330UKtime = price_330
    lag5_price = history_data_lag5['Settle']
   
    # define the lag 2 days settlement prices
    history_data_lag2_close = lag5_price.iloc[-2]
    history_data_lag1_close = lag5_price.iloc[-1]
        
    #Find the mode of the curve and find the quantile
    pdf_lag1, even_spaced_prices_lag1, spline_apc_lag1 = get_APC_spline_for_APC_pdf(lag_apc_data[0].to_numpy()[0][1:end_prices])

    price_max_prob_lag1 = even_spaced_prices_lag1[np.argmin(abs(pdf_lag1-np.max(pdf_lag1)))]
    q_price_max_prob_lag1 = spline_apc_lag1(price_max_prob_lag1) 
    
    
    # The APC two days (lag2) before this date
    signal_data_lag2_mode =  max(apc_curve_lag5.iloc[-2][1:-1])
    # The APC one day1 (lag1) before this date
    signal_data_lag1_mode =  max(apc_curve_lag5.iloc[-1][1:-1])
    
    lag1q = find_quant_APC(apc_curve_lag5.iloc[-2], signal_data_lag2_mode)
    lag2q = find_quant_APC(apc_curve_lag5.iloc[-1], signal_data_lag1_mode)

    print("lag1q, lag2q", lag1q, lag2q)
    # Reminder: pulling directly from a list is a factor of 3 faster than doing 
    # spline everytime
        
    # calculate the 5 days average for closing price
    rollinglagq5day = np.average(lag5_price)         
                
    # calculate the median of the apc for the last five days
    mode_apc_5days = np.median([max(apc_curve_lag5.iloc[-5][1:-1]),
                                      max(apc_curve_lag5.iloc[-4][1:-1]),
                                      max(apc_curve_lag5.iloc[-3][1:-1]),
                                      max(apc_curve_lag5.iloc[-2][1:-1]),
                                      max(apc_curve_lag5.iloc[-1][1:-1])])
    
    # "BUY" condition
    # (1) Two consecutive days of closing price lower than the signal median
    cond1_buy = (history_data_lag2_close < signal_data_lag2_mode)
    cond2_buy = (history_data_lag1_close < signal_data_lag1_mode)
    # (2) rolling 5 days average lower than the median apc 
    cond3_buy = rollinglagq5day < mode_apc_5days
    # (3) price at today's opening hour above the 0.1 quantile of today's apc
    cond4_buy = quant_330UKtime >= curve_today['0.1']
    argus_benchmark_strategy
    # "SELL" condition
    # (1) Two consecutive days of closing price higher than the signal median
    cond1_sell = (history_data_lag2_close > signal_data_lag2_mode)
    cond2_sell = (history_data_lag1_close > signal_data_lag1_mode)    
    # (2) rolling 5 days average higher than the median apc 
    cond3_sell = rollinglagq5day > mode_apc_5days
    # (3) price at today's opening hour below the 0.9 quantile of today's apc
    cond4_sell = quant_330UKtime <= curve_today['0.9']

    # Find the boolean value of strategy conditions
    Buy_cond = cond1_buy and cond2_buy and cond3_buy and cond4_buy
    Sell_cond =  cond1_sell and cond2_sell and cond3_sell and cond4_sell
        
    Neutral_cond = not (Buy_cond ^ Sell_cond) #xnor gate
    
    # make direction dictionary
    direction_dict = {"Buy": Buy_cond, "Sell": Sell_cond, "Neutral": Neutral_cond}
        
    for i in direction_dict:
        if direction_dict[i] == True:
            direction = i
    
    return direction

def generic_MR_strategy(price_330, history_data_lag5, apc_curve_lag5, curve_today):
    # Under construction
    # Strategy dictionary
    
    # inputs
    quant_330UKtime = price_330
    lag5_price = history_data_lag5['Settle']
   
    # define the lag 2 days settlement prices
    history_data_lag2_close = lag5_price.iloc[-2]
    history_data_lag1_close = lag5_price.iloc[-1]
        
    #Find the mode of the curve and find the quantile
    
    # The APC two days (lag2) before this date
    signal_data_lag2_mode =  max(apc_curve_lag5.iloc[-2])
    # The APC one day1 (lag1) before this date
    signal_data_lag1_mode =  max(apc_curve_lag5.iloc[-1])

    # Reminder: pulling directly from a list is a factor of 3 faster than doing 
    # spline everytime
        
    # calculate the 5 days average for closing price
    rollinglagq5day = np.average(lag5_price)         
                
    # calculate the median of the apc for the last five days
    mode_apc_5days = np.median([apc_curve_lag5.iloc[-5]['0.5'],
                                      apc_curve_lag5.iloc[-4]['0.5'],
                                      apc_curve_lag5.iloc[-3]['0.5'],
                                      apc_curve_lag5.iloc[-2]['0.5'],
                                      apc_curve_lag5.iloc[-1]['0.5']])
    
    # "BUY" condition
    # (1) Two consecutive days of closing price lower than the signal median
    cond1_buy = (history_data_lag2_close < signal_data_lag2_mode)
    cond2_buy = (history_data_lag1_close < signal_data_lag1_mode)
    # (2) rolling 5 days average lower than the median apc 
    cond3_buy = rollinglagq5day < mode_apc_5days
    # (3) price at today's opening hour above the 0.1 quantile of today's apc
    cond4_buy = quant_330UKtime >= curve_today['0.1']
    
    # "SELL" condition
    # (1) Two consecutive days of closing price higher than the signal median
    cond1_sell = (history_data_lag2_close > signal_data_lag2_mode)
    cond2_sell = (history_data_lag1_close > signal_data_lag1_mode)    
    # (2) rolling 5 days average higher than the median apc 
    cond3_sell = rollinglagq5day > mode_apc_5days
    # (3) price at today's opening hour below the 0.9 quantile of today's apc
    cond4_sell = quant_330UKtime <= curve_today['0.9']

    # Find the boolean value of strategy conditions
    Buy_cond = cond1_buy and cond2_buy and cond3_buy and cond4_buy
    Sell_cond =  cond1_sell and cond2_sell and cond3_sell and cond4_sell
        
    Neutral_cond = not (Buy_cond ^ Sell_cond) #xnor gate
    
    # make direction dictionary
    direction_dict = {"Buy": Buy_cond, "Sell": Sell_cond, "Neutral": Neutral_cond}
        
    for i in direction_dict:
        if direction_dict[i] == True:
            direction = i
    
    return direction
    
def set_entry_price_APC(cond, curve_today, buy_cond=(0.4,0.6,0.1), 
                    sell_cond =(0.6,0.4,0.9)):
    """
    A generic method to set the entry, exit, and stop loss price base on an
    APC. 

    Parameters
    ----------
    cond : str
        Only accept "Buy", "Sell", or "Neutral".
    curve_today : 1D pandas dataframe
        The APC for one single day.
    buy_cond : 3 elements tuple, optional
        The quantile for extracting the price of the APC for a "Buy" signal. 
        This has to be a 3-element tuple: 
            (entry quant, exit quant, stop loss quant)
        The default is (0.4,0.6,0.1).
    sell_cond : 3 elements tuple, optional
        The quantile for extracting the price of the APC for a "Buy" signal. 
        This has to be a 3-element tuple: 
            (entry quant, exit quant, stop loss quant)
        The default is (0.6,0.4,0.9).

    Returns
    -------
    entry_price : float
        entry_price.
    exit_price : float
        exit_price.
    stop_loss : float
        stop_loss.

    """
    # actually, I can make a spline first and call it later
    
    if cond == "Buy":
        # (A) Entry region at price < APC p=0.4 and 
        entry_price = curve_today[str(buy_cond[0])]
        # (B) Exit price
        exit_price = curve_today[str(buy_cond[1])]
        # (C) Stop loss at APC p=0.1
        stop_loss = curve_today[str(buy_cond[2])]

            
    elif cond == "Sell":
        # (A) Entry region at price > APC p=0.6 and 
        entry_price = curve_today[str(sell_cond[0])]
        # (B) Exit price
        exit_price = curve_today[str(sell_cond[1])]
        # (C) Stop loss at APC p=0.9
        stop_loss = curve_today[str(sell_cond[2])]
            
    elif cond == "Neutral":
        # (A) Entry region at price > APC p=0.6 and 
        entry_price = "NA"
        # (B) Exit price
        exit_price = "NA"
        # (C) Stop loss at APC p=0.9
        stop_loss = "NA"
    else:
        raise Exception(
            'Unaccepted input, condition needs to be either Buy, Sell, or Neutral.')
            
    return entry_price, exit_price, stop_loss

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

def extract_lag_data_to_list(signal_data, history_data_daily):
    
    return None
    #extract_lag_data(signal_data, history_data_daily, "2024-01-10")


def loop_signal(signal_data, history_data, dict_contracts_quant_signals, history_data_daily,
                loop_start_date="2024-01-10"):
    """
    A method taken from Abbe's original method. It is not necessary to loop 
    through each date and run evaluation one by one. But this is a rudamentary 
    method.

    Parameters
    ----------
    signal_data : pandas dataframe table
        The signal data (assuming the signal is from APC).
    history_data : pandas dataframe table
        The historical data (assuming the data is from Portara).
    dict_contracts_quant_signals : dict
        An empty bucket for final data storage.
    history_data_daily : pandas dataframe table
        The historical data (assuming the data is from Portara).
    loop_start_date : TYPE, optional
        DESCRIPTION. The default is "2024-01-10".

    Returns
    -------
    dict_contracts_quant_signals : TYPE
        DESCRIPTION.

    """
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
        
        full_contract_symbol = portara_dat['Contract Symbol'].iloc[i]
        full_price_code = portara_dat['Price Code'].iloc[i]
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
        
        # Should I match the price code and contract data?
        
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
        #price_330 = quant_330UKtime
        curve_today = APCs_this_date_and_contract
        ############################### 
        # Make data for later storage in signal bucket.
        
        # Get the extracted 5 days Lag data 
        apc_curve_lag5, history_data_lag5 = EC_read.extract_lag_data(signal_data, 
                                                             history_data_daily, 
                                                             forecast_date)
        
        print(apc_curve_lag5[['Forecast Period','0.5']])
        print(history_data_lag5)
        
        # Run the strategy        
        #direction = argus_benchmark_strategy(
        #     price_330, history_data_lag5, apc_curve_lag5, curve_today)
        direction = EC_strategy.MeanReversionStrategy.argus_benchmark_strategy(
             price_330, history_data_lag5, apc_curve_lag5, curve_today)
       # direction = MR_mode_strategy(
       #      price_330, history_data_lag5, apc_curve_lag5, curve_today)
        
        
        print("direction done", i, direction, forecast_date)
        print("curve_today", curve_today["Forecast Period"])
        history_data_lag2_close = history_data_lag5["Settle"].iloc[-2]
        history_data_lag1_close = history_data_lag5["Settle"].iloc[-1]


        # Find the quantile of the relevant price for the last two dates
        lag2q = find_quant_APC(curve_today, history_data_lag2_close)  
        lag1q = find_quant_APC(curve_today, history_data_lag1_close)
        
        rollinglagq5day = np.average(history_data_lag5["Settle"].to_numpy())
        
        roll5q = find_quant_APC(curve_today, rollinglagq5day) 
        print("lag1q,lag2q",lag1q,lag2q,roll5q)

        # set resposne price.
        entry_price, exit_price, stop_loss = EC_strategy.MeanReversionStrategy.set_entry_price_APC(direction, curve_today)
        
        ##################################################################################

        # Storing the data    
        bucket = dict_contracts_quant_signals
        data = [forecast_date, 
                full_contract_symbol,
                wanted_quantiles[0],
                wanted_quantiles[1],
                wanted_quantiles[2],
                wanted_quantiles[3],
                wanted_quantiles[4],
                lag1q, lag2q, roll5q, quant_330UKtime,
                entry_price, exit_price, stop_loss, 
                direction, full_price_code
                ]
        
        dict_contracts_quant_signals = EC_strategy.MeanReversionStrategy.store_to_bucket_single(bucket, data)

    dict_contracts_quant_signals = pd.DataFrame(dict_contracts_quant_signals)
    
    #sort by date
    #XXXX
    return dict_contracts_quant_signals

def signal_gen_vector(signal_data, history_data, loop_start_date = ""):
    # a method to generate signal assuming the input are vectors
    
    start_date = loop_start_date
    
    APCs_dat = signal_data[signal_data['Forecast Period'] > start_date]
    portara_dat = history_data[history_data["Date only"] > start_date]
    
    # generate a list of 5 days lag data
    
    # make a list of lag1q
    # make a list of lag2q
    # make a list of median APC
    
    #make a list of rolling5days
    #make a list of median APC for 5 days
    
    # make a list of 0.1, 0.9 quantiles
    
    # Turn the list into numpy array, then run condition 1-4 through it, get a list of true or false.
    
    dict_contracts_quant_signals = []
    
    return dict_contracts_quant_signals
# make a vectoralised way to perform signal generation


@time_it
@save_csv("benchmark_signal_test.csv")
def run_generate_MR_signals():
    # input is a dictionary or json file
    
    # run meanreversion signal generation on the basis of individual programme  
    # Loop the whole list in one go with all the contracts or Loop it one contract at a time?
    
    #inputs: Portara data (1 Minute and Daily), APC
    
    username = "dexter@eulercapital.com.au"
    password = "76tileArg56!"
    
    filename_daily = "../test_MS/data_zeroadjust_intradayportara_attempt1/Daily/CL.day"
    filename_minute = "../test_MS/data_zeroadjust_intradayportara_attempt1/intraday/1 Minute/CL.001"

    start_date = "2024-01-10"
    start_date_2 = "2024-01-01"
    end_date = "2024-03-13"
    categories = 'Argus Nymex WTI month 1, Daily'
    keywords = "WTI"
    symbol = "CL"
    
    # load the table in memory and test multple strategies
    # input APC file
    # download the relevant APC data from the server
    signal_data = EC_read.get_apc_from_server(username, password, start_date_2, 
                                      end_date, categories,
                            keywords=keywords,symbol=symbol)
    
    # input history file
    # start_date2 is a temporary solution
    history_data_daily = EC_read.read_portara_daily_data(filename_daily,symbol,
                                                 start_date_2,end_date)
    history_data_minute = EC_read.read_portara_minute_data(filename_minute,symbol, 
                                                   start_date_2, end_date,
                                                   start_filter_hour=30, 
                                                   end_filter_hour=331)
    history_data = EC_read.merge_portara_data(history_data_daily, history_data_minute)

    # need to make sure start date of portara is at least 5days ahead of APC data
    # need to make sure the 5 days lag of the APC and history data matches

    # Deal with the date problem in Portara data
    history_data = EC_read.portara_data_handling(history_data)
    
    # Checking function to make sure the input of the strategy is valid (maybe dumb them in a class)
    # check date and stuff
    
    # make an empty signal dictionary for storage
    dict_contracts_quant_signals = EC_strategy.MeanReversionStrategy.make_signal_bucket()
    
    # experiment with lag data extraction
    #extract_lag_data(signal_data, history_data_daily, "2024-01-10")
    
    # The strategy will be ran in loop_signal decorator
    dict_contracts_quant_signals = loop_signal(signal_data, history_data, 
                                               dict_contracts_quant_signals, 
                                               history_data_daily)
    
    # there are better ways than looping. here is a vectoralised method
    
    # Manual input for filename management (save)
    
    return dict_contracts_quant_signals

dict_contracts_quant_signals = run_generate_MR_signals()


