#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 18 18:22:17 2024

@author: dexter
"""
import pandas as pd
import datetime as datetime

import EC_read as EC_read
import EC_plot as EC_plot
import utility as util

# (1) Loop through the minute price to perform action

# (2) isolate out opportunity by just finding out when the price hit the entry zone

# Spit out the document for overall PNL analysis
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

class AssetProfolio(object):
        
    def __init__(self):
        self._profolio = None
        
        return None
    
    def profolio(object):
        profolio = {"USD": 0.0,
                    "AUD": 0.0}
        return profolio
    
    def sub_asset(object):
        
        return None
    
    def add_asset(object, profolio, new_asset):
        profolio.update(new_asset)
        return profolio
    
    def cal_total_value(object, profolio, dntr='USD'):
        #dntr = denomonator
        # read in a list of dictioart value and convert the asset to currency
        return None
    
    def track_profolio_history(object):
        # make a list of dictionary indexed by time of the changing of profolio
        # add the total value of the 
        return None
    
class BackTest(object):
    def __init__(self):
        self._instruction = None
        
    def make_report(object):
        
        return None
        
    
    
def make_backtest_bucket():
    
    profits_losses_bucket = {
    'Price Code': [],
    'predicted signal': [],
    'date': [],
    'return from trades': [],
    'entry price': [],
    'entry datetime': [],
    'exit price': [],
    'exit datetime': [],
    'risk/reward value ratio': [],
    #'path': []
    }
    
def store_data_to_bucket():
    return None
    
# tested
def prepare_data(filename_buysell_signals, direction=["Buy", "Sell"], trim = False):
    """
    A function that extract data from a signal table based on some directional 
    instruction.

    Parameters
    ----------
    filename_buysell_signals : str
        The file name of the directional data. It read the table as a dataframe.
    direction : list, str, optional
        The directional instruction. The default is ["Buy", "Sell"].
    trim : bool, optional
        Choose whether the result table contain only two clomns. 
        The default is False.

    Returns
    -------
    data : pandas dataframe
        The tuncated table with only the data of interest.

    """
    # read in direction data from the signal generation
    buysell_signals_data = pd.read_csv(filename_buysell_signals)    

    # The trim function reduce the number of columns to only 'Date' and 'direction'
    # This may cut down the computing and memory cost when dealing with large 
    # table.
    if trim == True:
        buysell_signals_data = buysell_signals_data[['APC forecast period', 
                                                     'direction']]
    elif trim == False:
        pass
    
    # Select for the signals in direction list.
    signal_data = []
    for i in direction:
        temp = buysell_signals_data[buysell_signals_data['direction'] == i]
        #print('temp', temp)
        signal_data.append(temp)
    
    # concatenate the list of signals
    data = pd.concat(signal_data, ignore_index=True)

    # make a column with Timestamp as its content
    data['Date'] = pd.to_datetime(data["APC forecast period"], 
                                  format='%Y-%m-%d')
                                  
    # sort the table by Date
    data.sort_values(by='Date', inplace=True)
    
    return data

#tested
def extract_intraday_minute_data(histrot_intraday_data, date_interest, 
                                 open_hr=300, close_hr=1900):
    """
    A function that extract only the minute pricing data from a master file 
    given a single date of interest.

    Parameters
    ----------
    histrot_data_intraday : pandas dataframe
        The master file for minute data.
    date_interest : str
        In the format of '2020-02-02'.
    open_hr : int, optional
        Opening trading hour. The default is 300.
    close_hr : int, optional
        Closing trading hour. The default is 1900.

    Returns
    -------
    histroy_data_intraday : pandas dataframe
        A table isolated by the date of interest.

    """
    
    # Given a date of interest, and read-in the intraday data.
    histrot_intraday_data = histrot_intraday_data[
                                histrot_intraday_data['Date']  == date_interest]
    
    # isolate the region of interest between the opening hour and the closing hour
    histrot_intraday_data = histrot_intraday_data[
                                            histrot_intraday_data['Time'] > open_hr]
    histrot_intraday_data = histrot_intraday_data[
                                            histrot_intraday_data['Time'] < close_hr]

    return histrot_intraday_data

# WIP
def find_EES_time_price(data, entry_price, exit_price, stop_loss, direction="Buy"):
    bucket_entry, bucket_exit, bucket_stoploss = [], [], []
    # make it into a vector
    if direction == "Buy":
        if data > entry_price:
            bucket_entry.append(data)
        
    elif direction == "Sell":
        if data < entry_price:
            bucket_entry.append(data)

    return None    

def loop_date(trade_date_table, histrot_intraday_data, plot_or_not = False):
    filename_minute = "../test_MS/data_zeroadjust_intradayportara_attempt1/intraday/1 Minute/CL.001"
    signal_filename = "APC_latest_CL.csv"
    

    for date, direction in zip(trade_date_table['Date'],trade_date_table['direction']):
        
        # Define the date of interest by reading TimeStamp. 
        # We may want to remake all this and make Timestamp the universal 
        # parameter when dealing with time
        date_interest = str(date)[:10]
        
        
        day = extract_intraday_minute_data(histrot_intraday_data, date_interest, 
                                     open_hr=300, close_hr=1900)
        
        if plot_or_not == True:
            EC_plot.plot_minute(filename_minute, signal_filename, 
                date_interest = date_interest, direction= direction)
        elif plot_or_not == False:
            pass
    
    return day
    
def loop_minute_price(histroy_data_intraday):
    # loop through the prices 
    
    # Find the entry point and exit point
    
    # Spit out a list of data
    return None

def cal_crossover():
    # A function that calculate the moment of crossover to the price
    return None


def analysis_cross_percentage():
    # A function that calculate the percentage of points that crosses over to 
    # the different regions.
    return None
    

@util.time_it
def run_backtest():
    # master function that runs the backtest itself.
    
    filename_minute = "../test_MS/data_zeroadjust_intradayportara_attempt1/intraday/1 Minute/CL.001"
    filename_buysell_signals = "./benchmark_signal_test.csv"
    # read the reformatted minute history data
    history_data = EC_read.read_reformat_Portara_minute_data(filename_minute)
    
    # Find the date for trading
    trade_date_table = prepare_data(filename_buysell_signals, trim = True)
    
    # loop through the date and extract the signals
    loop_date(trade_date_table, history_data, plot_or_not = True)    

    
# =============================================================================
#     # read a signal list
#     date_interest = "2024-04-03"
#     A = extract_intraday_minute_data(history_data, date_interest, 
#                                      open_hr=300, close_hr=1900)
# =============================================================================
    
    

    return None


if __name__ == "__main__":
    run_backtest()