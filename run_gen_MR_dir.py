#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 13 19:51:24 2024

@author: dexter

A modified script based on the Mean-Reversion Method developed by Abbe Whitford.

"""
# python import
import datetime as datetime

# package imports
import pandas as pd 
import numpy as np
from scipy.interpolate import CubicSpline

# EC_tools imports
import EC_tools.strategy as strategy
import EC_tools.read as read
import EC_tools.utility as util
from EC_tools.bookkeep import Bookkeep
import EC_tools.math_func as mfunc
import update_db as update_db


__all__ = ['loop_signal','gen_signal_vector','run_gen_MR_signals', 
           'run_gen_MR_signals_list']

__author__="Dexter S.-H. Hon"


SAVE_FILENAME_LIST = ["benchmark_signal_CLc2_full.csv", 
                 "benchmark_signal_HOc2_full.csv", 
                 "benchmark_signal_RBc2_full.csv", 
                 "benchmark_signal_QOc2_full.csv",
                 "benchmark_signal_QPc2_full.csv" ]


CAT_LIST = ['Argus Nymex WTI month 2, Daily', 
               'Argus Nymex Heating oil month 2, Daily', 
               'Argus Nymex RBOB Gasoline month 2, Daily', 
               'Argus Brent month 2, Daily', 
               'Argus ICE gasoil month 2, Daily']

KEYWORDS_LIST = ["WTI","Heating", "Gasoline",'Brent', "gasoil"]
SYMBOL_LIST = ['CLc2', 'HOc2', 'RBc2', 'QOc2', 'QPc2']

SIGNAL_LIST= [ "/home/dexter/Euler_Capital_codes/EC_tools/data/APC_latest/APC_latest_CLc2.csv",
              "/home/dexter/Euler_Capital_codes/EC_tools/data/APC_latest/APC_latest_HOc2.csv",
              "/home/dexter/Euler_Capital_codes/EC_tools/data/APC_latest/APC_latest_RBc2.csv",
              "/home/dexter/Euler_Capital_codes/EC_tools/data/APC_latest/APC_latest_QOc2.csv",
            "/home/dexter/Euler_Capital_codes/EC_tools/data/APC_latest/APC_latest_QPc2.csv"]

HISTORY_DAILY_LIST = [    
     "/home/dexter/Euler_Capital_codes/EC_tools/data/history_data/Day/CL_d01.day",
    "/home/dexter/Euler_Capital_codes/EC_tools/data/history_data/Day/HO_d01.day",
    "/home/dexter/Euler_Capital_codes/EC_tools/data/history_data/Day/RB_d01.day",
    "/home/dexter/Euler_Capital_codes/EC_tools/data/history_data/Day/QO_d01.day",
    "/home/dexter/Euler_Capital_codes/EC_tools/data/history_data/Day/QP_d01.day"]
                      

HISTORY_MINUTE_LIST = [
    "/home/dexter/Euler_Capital_codes/EC_tools/data/history_data/Minute/CL_d01.001",
    "/home/dexter/Euler_Capital_codes/EC_tools/data/history_data/Minute/HO_d01.001",
    "/home/dexter/Euler_Capital_codes/EC_tools/data/history_data/Minute/RB_d01.001",
    "/home/dexter/Euler_Capital_codes/EC_tools/data/history_data/Minute/QO_d01.001",
    "/home/dexter/Euler_Capital_codes/EC_tools/data/history_data/Minute/QP_d01.001" ]




def find_open_price(history_data_daily, history_data_minute, open_hr='0330'): #tested
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
        open_hr_dt, open_price = read.find_closest_price(day_data,
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

def loop_signal(signal_data, history_data, open_price_data, start_date, end_date, 
                  strategy_name='benchmark',
                  contract_symbol_condse = False): #WIP
    
    # make an empty signal dictionary for storage
    book = Bookkeep(bucket_type = 'mr_signals')
    dict_contracts_quant_signals = book.make_bucket(keyword='benchmark')
    
    # Define a small window of interest
    APCs_dat = signal_data[(signal_data['Forecast Period'] > start_date) & 
                                      (signal_data['Forecast Period'] < end_date)]
    
    portara_dat = history_data[(history_data['Date'] > start_date) & 
                                      (history_data['Date'] < end_date)]
    
    open_price_data = open_price_data[(open_price_data['Date'] > start_date) & 
                                      (open_price_data['Date'] < end_date)]

    
    #print("length", len(portara_dat), len(APCs_dat), len(open_price_data))
    print('Start looping signal ...')
    # check if history data and opening price data are the same dimension
    
    # loop through every forecast date and contract symbol 
    for i in np.arange(len(portara_dat)): 
        this_date = portara_dat["Date"].iloc[i]
        
        # cross reference the APC list to get the APC of this date
        APCs_this_date = APCs_dat[APCs_dat['Forecast Period']==this_date] #<-- here add a condition matching the symbols
        forecast_date = APCs_this_date['Forecast Period'].to_list()[0] 
        # This is the APC number only
        curve_this_date = APCs_this_date.to_numpy()[0][1:-1]


        # create input for bookkepping
        price_code = APCs_this_date['symbol'].to_list()[0]
        
        # The conidtions to decide whether we trim the full_contract_symbol
        # CLA2024J or CL24J
        if contract_symbol_condse == True:
            temp = portara_dat['Contract Code'].to_list()[0]
            full_contract_symbol = str(temp)[0:2] + str(temp)[5:7] + str(temp)[-1]
        elif contract_symbol_condse == False:
            full_contract_symbol = portara_dat['Contract Code'].to_list()[0]

        # find the quantile of the opening price
        price_330 = open_price_data[open_price_data['Date']==this_date]['Open Price'].item()

        # Find the quantile of the opening price
        quant0 = np.arange(0.0025, 0.9975, 0.0025)
        price_330_quant = mfunc.find_quant(curve_this_date, quant0, price_330)
        
        # Get the extracted 5 days Lag data 
        apc_curve_lag5, history_data_lag5 = read.extract_lag_data(signal_data, 
                                                             history_data, 
                                                             forecast_date)
        
        #print("apc_curve_lag5, history_data_lag5", apc_curve_lag5, history_data_lag5)

        # Run the strategy        
        direction = strategy.MRStrategy.argus_benchmark_strategy(
             price_330, history_data_lag5, apc_curve_lag5, APCs_this_date)
        
        #direction = EC_strategy.MRStrategy.argus_benchmark_mode(
        #     price_330, history_data_lag5, apc_curve_lag5, APCs_this_date)
        
        # calculate the data needed for PNL analysis for this strategy
        strategy_data = strategy.MRStrategy.gen_strategy_data(
                                                        history_data_lag5, 
                                                         apc_curve_lag5, 
                                                         curve_this_date,
                                                         strategy_name=\
                                                             "benchmark")
        
        print(forecast_date, full_contract_symbol,'MR signal generated!', i)
        print(open_price_data[open_price_data['Date']==this_date]['Time'].item(), price_330)
    
        # set resposne price.
        entry_price, exit_price, stop_loss = strategy.MRStrategy.set_EES_APC(
                                                        direction, curve_this_date)
        EES = [entry_price, exit_price, stop_loss]
                       
        # put all the data in a singular list
        data = [forecast_date, full_contract_symbol] + strategy_data + \
                [price_330_quant] + EES + [direction, price_code]
                
        # Storing the data    
        dict_contracts_quant_signals = book.store_to_bucket_single(data)       
        
        
    dict_contracts_quant_signals = pd.DataFrame(dict_contracts_quant_signals)
    
    #sort by date
    dict_contracts_quant_signals = dict_contracts_quant_signals.\
                                    sort_values(by='APC forecast period')
    
    return dict_contracts_quant_signals
        
def gen_signal_vector(signal_data, history_data, loop_start_date = ""): # WIP
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
def run_gen_MR_signals(auth_pack, asset_pack, start_date, end_date,
                       signal_filename, filename_daily, filename_minute,
                       update_apc = False):
    # input is a dictionary or json file
    
    # run meanreversion signal generation on the basis of individual programme  
    # Loop the whole list in one go with all the contracts or Loop it one contract at a time?
    
    symbol = asset_pack['symbol']

    # download the relevant APC data from the server
    if update_apc == True:
        update_db.download_latest_APC(auth_pack, asset_pack)
    # The reading part takes the longest time: 13 seconds. The loop itself takes 
    # input 1, APC. Load the master table in memory and test multple strategies   
    signal_data =  read.read_reformat_APC_data(signal_filename)
   
    # input 2, Portara history file.
    # start_date2 is a temporary solution 
    history_data_daily = read.read_reformat_Portara_daily_data(filename_daily)
    history_data_minute = read.read_reformat_Portara_minute_data(filename_minute)

    # Find the opening price at 03:30 UK time. If not found, 
    #loop through the next 30 minutes to find the opening price
    price_330 = find_open_price(history_data_daily, history_data_minute)
    
    # The strategy will be ran in loop_signal decorator
    dict_contracts_quant_signals = loop_signal(signal_data, 
                                               history_data_daily, 
                                               price_330,
                                               start_date, end_date)
    
    # there are better ways than looping. here is a vectoralised method    
    return dict_contracts_quant_signals


# make a function to run multiple signal generation from a list
# tested
@util.time_it
def run_gen_MR_signals_list(filename_list, categories_list, keywords_list, symbol_list, 
                            start_date, end_date,
                            signal_list, history_daily_list, 
                            history_minute_list,save_or_not=False):
    # a function to download the APC of a list of asset
    # input username and password.json
    auth_pack = None
    output_dict = dict()
    for filename, cat, key, sym, signal, history_daily, history_minute in zip(\
        filename_list, categories_list, keywords_list, symbol_list, signal_list, \
                                        history_daily_list, history_minute_list):
        @util.time_it
        @util.save_csv("{}".format(filename), save_or_not=save_or_not)
        def run_gen_MR_signals_indi(cat, key, sym):
            asset_pack = {'categories': cat, 'keywords': key, 'symbol': sym}
            signal_data = run_gen_MR_signals(auth_pack, asset_pack, 
                                             start_date, end_date,
                                             signal, history_daily, 
                                             history_minute) #WIP
            print("name {}".format(filename))

            return signal_data
        
        signal_data = run_gen_MR_signals_indi(cat, key, sym)
        output_dict[sym] = signal_data
        print("All asset signal generated!")
    return output_dict

if __name__ == "__main__":

    
    start_date = "2024-01-10"
    end_date = "2024-05-18"
    
    auth_pack = {'username': "dexter@eulercapital.com.au",
                'password':"76tileArg56!"}
    

    #maybe I need an unpacking function here ro handle payload from json files
# =============================================================================
# 
#     run_gen_MR_signals_list(SAVE_FILENAME_LIST, CAT_LIST, KEYWORDS_LIST, SYMBOL_LIST, 
#                             start_date, end_date,
#                             SIGNAL_LIST, HISTORY_DAILY_LIST, 
#                             HISTORY_MINUTE_LIST)
# 
# =============================================================================

    asset_pack = {"categories" : 'Argus Nymex Heating oil month 1 Daily',
                  "keywords" : "Heating",
                  "symbol": "HOc1"}

    #inputs: Portara data (1 Minute and Daily), APC
    signal_filename = "/home/dexter/Euler_Capital_codes/EC_tools/data/APC_latest/APC_latest_HOc2.csv"
    filename_daily = "/home/dexter/Euler_Capital_codes/EC_tools/data/history_data/Day/HO_d01.day"
    filename_minute = "/home/dexter/Euler_Capital_codes/EC_tools/data/history_data/Minute/HO_d01.001"

    # run signal for the individual asset
    dict_contracts_quant_signals = run_gen_MR_signals(auth_pack, asset_pack, 
                                                      start_date,  
                                                      end_date, signal_filename, 
                                                      filename_daily, 
                                                      filename_minute)



