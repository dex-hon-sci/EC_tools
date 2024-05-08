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
from scipy.interpolate import CubicSpline
# import EC_tools
import EC_strategy as EC_strategy
import EC_read as EC_read
import update_db as update_db
import utility as util


__all__ = ['loop_signal','gen_signal_vector','run_gen_MR_signals', 
           'run_gen_MR_signals_list']

__author__="Dexter S.-H. Hon"


save_filename_list = ["benchmark_signal_CL.csv", 
                 "benchmark_signal_HO.csv", 
                 "benchmark_signal_RB.csv", 
                 "benchmark_signal_QO.csv",
                 "benchmark_signal_QP.csv" ]

categories_list = ['Argus Nymex WTI month 1, Daily', 
               'Argus Nymex Heating oil month 1, Daily', 
               'Argus Nymex RBOB Gasoline month 1, Daily', 
               'Argus Brent month 1, Daily', 
               'Argus ICE gasoil month 1, Daily']

keywords_list = ["WTI","Heating", "Gasoline",'Brent', "gasoil"]
symbol_list = ['CLc1', 'HOc1', 'RBc1', 'QOc1', 'QPc1']

signal_list = ['./APC_latest_CL.csv',
              './APC_latest_HO.csv',
              './APC_latest_RB.csv',
              './APC_latest_QO.csv',
              './APC_latest_QP.csv']

history_daily_list = ['../test_MS/data_zeroadjust_intradayportara_attempt1/Daily/CL.day',
                      '../test_MS/data_zeroadjust_intradayportara_attempt1/Daily/HO.day',
                      '../test_MS/data_zeroadjust_intradayportara_attempt1/Daily/RB.day',
                      '../test_MS/data_zeroadjust_intradayportara_attempt1/Daily/QO.day',
                      '../test_MS/data_zeroadjust_intradayportara_attempt1/Daily/QP.day']
                      

history_minute_list = ["../test_MS/data_zeroadjust_intradayportara_attempt1/intraday/1 Minute/CL.001",
                       "../test_MS/data_zeroadjust_intradayportara_attempt1/intraday/1 Minute/HO.001",
                       "../test_MS/data_zeroadjust_intradayportara_attempt1/intraday/1 Minute/RB.001",
                       "../test_MS/data_zeroadjust_intradayportara_attempt1/intraday/1 Minute/QO.001",
                       "../test_MS/data_zeroadjust_intradayportara_attempt1/intraday/1 Minute/QP.001"
                       ]

#%%
def loop_signal(signal_data, history_data, 
                history_data_daily, start_date, end_date, strategy_name='benchmark'):
    """
    A method taken from Abbe's original method. It is not necessary to loop 
    through each date and run evaluation one by one. But this is a rudamentary 
    method.
    
    LEGACY function structure from Abbe.

    Parameters
    ----------
    signal_data : pandas dataframe table
        The signal data (assuming the signal is from APC).
    history_data : pandas dataframe table
        The historical data (assuming the data is from Portara).
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
    # make an empty signal dictionary for storage
    dict_contracts_quant_signals = EC_strategy.MRStrategy.make_signal_bucket(
                                                        strategy_name=strategy_name)
    
    # Define a small window of interest
    APCs_dat = signal_data[signal_data['Forecast Period'] > start_date]
    # APCs_dat = signal_data[signal_data['Forecast Period'] < end_date]

    # leave the end date open because on some date there are no APC published, 
    # leading to a mismatch of history and signal data. Now this method use the 
    # history data as anchor to search for relevant APC date.
    
    portara_dat = history_data[history_data["Date only"] > start_date]
    #portara_dat = history_data[history_data["Date only"] < end_date]
    
    #print("length", len(portara_dat), len(APCs_dat))
    
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
        dat_330 = dat_330[dat_330['Contract Symbol'].apply(lambda x: str(x)[:-3])==str(symbol)[:-2]]
        
        quant_330UKtime = np.NaN 
                        
        if dat_330.shape[0] > 0:
                
            price_330 = dat_330.iloc[0].to_numpy()[1] # 330 UK time 
                    
            if np.isnan(price_330):
                continue 
        else: 
            continue # data not available! 
        #-------------------------------#
        portara_dat_filtered = portara_dat[portara_dat['Contract Symbol'].apply(lambda x: str(x)[:-3] == str(symbol)[:-2])]
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
        
        print(forecast_date, full_contract_symbol, 'MR signal generated!')
    
        
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

@util.time_it
@util.save_csv("benchmark_signal_test.csv")
def run_gen_MR_signals(auth_pack, asset_pack, start_date, start_date_2, end_date,
                       signal_filename, filename_daily, filename_minute,
                       update_apc = False):
    # input is a dictionary or json file
    
    # run meanreversion signal generation on the basis of individual programme  
    # Loop the whole list in one go with all the contracts or Loop it one contract at a time?
    
    symbol = asset_pack['symbol']

    # download the relevant APC data from the server
    if update_apc == True:
        update_db.download_latest_APC_list(auth_pack, save_filename_list, 
                                           categories_list, keywords_list, 
                                           symbol_list) 

    # The reading part takes the longest time: 13 seconds. The loop itself takes 

    # input 1, APC. Load the master table in memory and test multple strategies
    signal_data = EC_read.read_apc_data(signal_filename)
   
    # input 2, Portara history file.
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

    # experiment with lag data extraction
    #extract_lag_data(signal_data, history_data_daily, "2024-01-10")
    
    # The strategy will be ran in loop_signal decorator
    dict_contracts_quant_signals = loop_signal(signal_data, history_data, 
                                               history_data_daily, 
                                               start_date, end_date)
    
    # there are better ways than looping. here is a vectoralised method    
    return dict_contracts_quant_signals



# make a function to run multiple signal generation from a list
# tested
def run_gen_MR_signals_list(filename_list, categories_list, keywords_list, symbol_list, 
                            start_date, start_date_2, end_date,
                            signal_filename, filename_daily, 
                            filename_minute):
    # a function to download the APC of a list of asset
    # input username and password.json

    for filename, cat, key, sym, signal, history_daily, history_minute in zip(\
        filename_list, categories_list, keywords_list, symbol_list, signal_list, history_daily_list, history_minute_list):
        
        @util.time_it
        @util.save_csv("{}".format(filename))
        def run_gen_MR_signals_indi(cat, key, sym):
            asset_pack = {'categories': cat, 'keywords': key, 'symbol': sym}
            signal_data = run_gen_MR_signals(auth_pack, asset_pack, 
                                             start_date, start_date_2, end_date,
                                             signal, history_daily, 
                                             history_minute) #WIP
            print("name {}".format(filename))

            return signal_data
        
        run_gen_MR_signals_indi(cat, key, sym)
    
    return "All asset signal generated!"

if __name__ == "__main__":

    start_date = "2024-01-10"
    start_date_2 = "2024-01-01" # make it at least 5 days before the start_date
    end_date = "2024-03-13"
    
    auth_pack = {'username': "dexter@eulercapital.com.au",
                'password':"76tileArg56!"}
# =============================================================================
#     #maybe I need an unpacking function here ro handle payload from json files
#     
#     run_gen_MR_signals_list(save_filename_list, categories_list, keywords_list, symbol_list, 
#                             start_date, start_date_2, end_date,
#                             signal_list, history_daily_list, 
#                             history_minute_list)
# =============================================================================
    
    asset_pack = {"categories" : 'Argus Nymex WTI month 1, Daily',
                  "keywords" : "WTI",
                  "symbol": "CL"}

    #inputs: Portara data (1 Minute and Daily), APC
    signal_filename = "./APC_latest_CL.csv"
    filename_daily = "../test_MS/data_zeroadjust_intradayportara_attempt1/Daily/CL.day"
    filename_minute = "../test_MS/data_zeroadjust_intradayportara_attempt1/intraday/1 Minute/CL.001"

    # run signal for the individual asset
    dict_contracts_quant_signals = run_gen_MR_signals(auth_pack, asset_pack, 
                                                      start_date, start_date_2, 
                                                      end_date, signal_filename, 
                                                      filename_daily, 
                                                      filename_minute)

