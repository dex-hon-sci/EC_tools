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
from scipy.interpolate import CubicSpline, UnivariateSpline


import EC_strategy as EC_strategy
import EC_read as EC_read
import update_db as update_db
import utility as util
import math_func as mfunc


__all__ = ['loop_signal','gen_signal_vector','run_gen_MR_signals']

__author__="Dexter S.-H. Hon"

#%%
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

def extract_lag_data_to_list(signal_data, history_data_daily,lag_size=5):
    # make a list of lag data with a nested data structure.
    
    return None
    #extract_lag_data(signal_data, history_data_daily, "2024-01-10")

#%%
def loop_signal(signal_data, history_data, dict_contracts_quant_signals, 
                history_data_daily, start_date, end_date):
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
    start_date : str
        The start date for looping.
    end_date: str
        The end date for looping.

    Returns
    -------
    dict_contracts_quant_signals : dict
        A dictionary for storing the signals and wanted quantiles.

    """
    # Define a small window of interest
    APCs_dat = signal_data[signal_data['Forecast Period'] > start_date]
    # APCs_dat = signal_data[signal_data['Forecast Period'] < end_date] 

    # leave the end date open because on some date there are no APC published, 
    # leading to a mismatch of history and signal data. Now this method use the 
    # history data as anchor to search for relevant APC date.
    
    portara_dat = history_data[history_data["Date only"] > start_date]
    #portara_dat = history_data[history_data["Date only"] < end_date]
    
    print("length", len(portara_dat), len(APCs_dat))
    
    # loop through every forecast date and contract symbol 
    for i in np.arange(len(portara_dat)): 
        
        # get some basic info for the final storage
        APCs_this_date_and_contract = APCs_dat.iloc[i] # get the ith row 
        
        forecast_date = APCs_this_date_and_contract.to_numpy()[0]
        symbol = APCs_this_date_and_contract.to_numpy()[-1]
        
        full_contract_symbol = portara_dat['Contract Symbol'].iloc[i]
        full_price_code = portara_dat['Price Code'].iloc[i]
        
        ##############################################################
        ##############################################################
        # The following part is purely Abbe's code. I may need to modify it later
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
        #-------------------------------#
        portara_dat_filtered = portara_dat[portara_dat['Contract Symbol'].apply(lambda x: str(x)[:-3] == symbol)]
        portara_dat_filtered = portara_dat_filtered.reset_index(drop=True)
        index_thisapc = portara_dat_filtered[portara_dat_filtered['Date only'] == (forecast_date)] 
                
        # Should I match the price code and contract data?
        full_contract_symbol = index_thisapc.to_numpy()[0][-1]
        full_price_code = index_thisapc.to_numpy()[0][-2]
        index_thisapc = index_thisapc.index[0]
        
        #-------------------------------#   
        # calculate the quantile where the starting pice (3:30am UK) sits
        apcdat = APCs_this_date_and_contract.to_numpy()[1:-1]
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
        ##############################################################    
        ##############################################################
        
        # input for strategy
        #price_330 = quant_330UKtime
        curve_today = APCs_this_date_and_contract
                
        # Get the extracted 5 days Lag data 
        apc_curve_lag5, history_data_lag5 = EC_read.extract_lag_data(signal_data, 
                                                             history_data_daily, 
                                                             forecast_date)
                
        # Run the strategy        
        direction = EC_strategy.MRStrategy.argus_benchmark_strategy(
             price_330, history_data_lag5, apc_curve_lag5, curve_today)
        
        #direction = EC_strategy.MRStrategy.argus_benchmark_mode(
        #     price_330, history_data_lag5, apc_curve_lag5, curve_today)
        

        # calculate the data needed for PNL analysis for this strategy
        strategy_data = EC_strategy.MRStrategy.gen_strategy_data(
                                                        history_data_lag5, 
                                                         apc_curve_lag5, 
                                                         curve_today,
                                                         strategy_name=\
                                                             "benchmark")
        
        # set resposne price.
        entry_price, exit_price, stop_loss = EC_strategy.MRStrategy.set_EES_APC(
                                                        direction, curve_today)
        EES = [entry_price, exit_price, stop_loss]
               
        #make bucket for storage
        bucket = dict_contracts_quant_signals
        
        # put all the data in a singular list
        data = [forecast_date, full_contract_symbol] + strategy_data + \
                [quant_330UKtime] + EES + [direction, full_price_code]
        
        # Storing the data    
        dict_contracts_quant_signals = EC_strategy.MRStrategy.\
                                        store_to_bucket_single(bucket, data)

    dict_contracts_quant_signals = pd.DataFrame(dict_contracts_quant_signals)
    
    #sort by date
    dict_contracts_quant_signals = dict_contracts_quant_signals.\
                                    sort_values(by='APC forecast period')
    
    return dict_contracts_quant_signals

def gen_signal_vector(signal_data, history_data, loop_start_date = ""):
    # make a vectoralised way to perform signal generation

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


@util.save_csv("benchmark_signal_test.csv")
def run_gen_MR_signals():
    # input is a dictionary or json file
    
    # run meanreversion signal generation on the basis of individual programme  
    # Loop the whole list in one go with all the contracts or Loop it one contract at a time?
    
    #inputs: Portara data (1 Minute and Daily), APC
    
    signal_filename = "./APC_latest_CL.csv"
    filename_daily = "../test_MS/data_zeroadjust_intradayportara_attempt1/Daily/CL.day"
    filename_minute = "../test_MS/data_zeroadjust_intradayportara_attempt1/intraday/1 Minute/CL.001"

    start_date = "2024-01-10"
    start_date_2 = "2024-01-01"
    end_date = "2024-03-13"
    categories = 'Argus Nymex WTI month 1, Daily'
    keywords = "WTI"
    symbol = "CL"
    
    
    # download the relevant APC data from the server
    #if update == True:
    #    update_db.download_latest_APC_list() #something like that

    # load the master table in memory and test multple strategies
    # input APC file
    signal_data = EC_read.read_apc_data(signal_filename)
   
    # input history file
    # start_date2 is a temporary solution
    history_data_daily = EC_read.read_portara_daily_data(filename_daily,symbol,
                                                 start_date_2,end_date)
    history_data_minute = EC_read.read_portara_minute_data(filename_minute,symbol, 
                                                   start_date_2, end_date,
                                                   start_filter_hour=30, 
                                                   end_filter_hour=331)
    history_data = EC_read.merge_portara_data(history_data_daily, 
                                              history_data_minute)

    # need to make sure start date of portara is at least 5days ahead of APC data
    # need to make sure the 5 days lag of the APC and history data matches

    # Deal with the date problem in Portara data
    history_data = EC_read.portara_data_handling(history_data)
    
    # Checking function to make sure the input of the strategy is valid (maybe dumb them in a class)
    # check date and stuff
    
    # make an empty signal dictionary for storage
    #dict_contracts_quant_signals = EC_strategy.MRStrategy.make_signal_bucket(strategy_name='benchmark')
    dict_contracts_quant_signals = EC_strategy.MRStrategy.make_signal_bucket(
                                                        strategy_name='mode')
    
    # experiment with lag data extraction
    #extract_lag_data(signal_data, history_data_daily, "2024-01-10")
    
    # The strategy will be ran in loop_signal decorator
    dict_contracts_quant_signals = loop_signal(signal_data, history_data, 
                                               dict_contracts_quant_signals, 
                                               history_data_daily, 
                                               start_date, end_date)
    
    # there are better ways than looping. here is a vectoralised method
    return dict_contracts_quant_signals

if __name__ == "__main__":
    dict_contracts_quant_signals = run_gen_MR_signals()


