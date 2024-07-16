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

# EC_tools imports
#from EC_tools.strategy import MRStrategy
from EC_tools.strategy import MRStrategyArgus
import EC_tools.read as read
import EC_tools.utility as util
from EC_tools.bookkeep import Bookkeep
import EC_tools.math_func as mfunc
from crudeoil_future_const import CAT_LIST, KEYWORDS_LIST, SYMBOL_LIST, \
                                APC_FILE_LOC, HISTORY_DAILY_FILE_LOC,\
                                    HISTORY_MINTUE_FILE_LOC, TIMEZONE_DICT,\
                                        OPEN_HR_DICT, CLOSE_HR_DICT


__all__ = ['loop_signal','gen_signal_vector','run_gen_MR_signals', 
           'run_gen_MR_signals_list', 'run_gen_MR_signals_preloaded_list']

__author__="Dexter S.-H. Hon"


MR_STRATEGIES_0 = {"argus_exact": MRStrategyArgus}


def loop_signal(book, signal_data, history_data, open_price_data,  
                   Strategy: MRStrategyArgus, start_date, end_date,
                   strategy_name='benchmark', 
                   buy_range=(0.4,0.6,0.1), sell_range =(0.6,0.4,0.9), 
                   open_hr='', close_hr='',
                   commodity_name = '', Timezone= "",
                  contract_symbol_condse = False, loop_symbol = None): #WIP

    #make bucket
    bucket = book.make_bucket(keyword=strategy_name)
    print('Start looping signal: {}...'.format(loop_symbol))
    
    # Find the index of the start_date and end_date here.
    start_index = history_data.index[history_data['Date'] == start_date].item()    
    end_index = history_data.index[history_data['Date'] == end_date].item()
        

    # loop through every forecast date and contract symbol 
    for i in np.arange(start_index,end_index): 
        
        this_date = history_data["Date"][i]
        this_symbol = history_data["symbol"][i]
                
        # cross reference the APC list to get the APC of this date and symbol
        APCs_this_date = signal_data[(signal_data['Forecast Period']==this_date)]
#                                  & (APCs_dat['symbol']== this_symbol)] #<-- here add a condition matching the symbols
        
        if len(APCs_this_date) == 0:
            print("APC data of {} from the date {} is missing".format(this_symbol, 
                                                                      this_date.date()))
            pass
        else:
            #print(this_date, this_symbol, APCs_this_date['Forecast Period'].iloc[0])
            forecast_date = APCs_this_date['Forecast Period'].to_list()[0] 
                        
            # This is the APC number only
            curve_this_date = APCs_this_date.to_numpy()[0][1:-1]
    
            # create input for bookkepping
            price_code = APCs_this_date['symbol'].to_list()[0]
            
            # find the quantile of the opening price
            price_330 = open_price_data[open_price_data['Date']==this_date]['Open Price'].item()
            
            # The conidtions to decide whether we trim the full_contract_symbol
            # CLA2024J or CL24J
            if contract_symbol_condse == True:
                temp = history_data['Contract Code'][i]
                full_contract_symbol = str(temp)[0:2] + str(temp)[5:7] + str(temp)[-1]
            elif contract_symbol_condse == False:
                full_contract_symbol = history_data['Contract Code'][i]
            
            # Get the extracted 5 days Lag data. This is the main input to be
            # put into the Stragey function
            apc_curve_lag5, history_data_lag5 = read.extract_lag_data(signal_data, 
                                                                 history_data, 
                                                                 forecast_date)
            

            # Apply the strategy, The Strategy is variable
            strategy_output = Strategy(curve_this_date).apply_strategy(
                                     history_data_lag5, apc_curve_lag5, price_330)

            # Rename the strategy ouputs
            direction = strategy_output['direction']
            strategy_data = strategy_output['data']
            
            print('====================================')
            print(forecast_date, full_contract_symbol,'MR signal generated!', 
                   direction,i)
        

            # make a list of data to be written into bookkeep
            static_info = [commodity_name, full_contract_symbol, \
                           Timezone, open_hr, close_hr]
                
            # put all the data in a singular list
            data = [forecast_date, price_code] + [direction] + \
                    static_info + strategy_data
            
            # Storing the data    
            bucket = book.store_to_bucket_single(data)       
        
    dict_contracts_quant_signals = pd.DataFrame(bucket)

    #sort by date (the first column)
    dict_contracts_quant_signals = dict_contracts_quant_signals.sort_values(by=
                                    dict_contracts_quant_signals.columns.values[0])
    
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


def run_gen_MR_signals(asset_pack, start_date, end_date,
                       signal_filename, filename_daily, filename_minute, 
                       buy_range=(0.4,0.6,0.1),sell_range =(0.6,0.4,0.9),
                       open_hr='', close_hr='',
                       commodity_name = '', Timezone= "",
                       start_date_pushback = 20):
    
    # run meanreversion signal generation on the basis of individual programme  
    # Loop the whole list in one go with all the contracts or Loop it one contract at a time?
    
    symbol = asset_pack['symbol']
    commodity_name = asset_pack['keywords']

    # The reading part takes the longest time: 13 seconds. The loop itself takes 
    # input 1, APC. Load the master table in memory and test multple strategies   
    signal_data =  read.read_reformat_APC_data(signal_filename)
    
    # input 2, Portara history file.
    # start_date2 is a temporary solution 
    history_data_daily = read.read_reformat_Portara_daily_data(filename_daily)
    history_data_minute = read.read_reformat_Portara_minute_data(filename_minute)
    
    # Add a symbol column
    history_data_daily['symbol'] = [symbol for i in range(len(history_data_daily))]
    history_data_minute['symbol'] = [symbol for i in range(len(history_data_minute))]
    
    # Find the opening price at 03:30 UK time. If not found, 
    #loop through the next 30 minutes to find the opening price
    price_330 = read.find_open_price(history_data_daily, history_data_minute)

    # make an empty signal dictionary for storage
    book = Bookkeep(bucket_type = 'mr_signals')
    
    start_date_lag = datetime.datetime.strptime(start_date, '%Y-%m-%d') - \
                            datetime.timedelta(days= start_date_pushback)
    start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')

    # Define a small window of interest
    APCs_dat = signal_data[(signal_data['Forecast Period'] >= start_date_lag) & 
                                      (signal_data['Forecast Period'] <= end_date)]
    
    portara_dat = history_data_daily[(history_data_daily['Date'] >= start_date_lag) & 
                                      (history_data_daily['Date'] <= end_date)]
    
    open_price_data = price_330[(price_330['Date'] >= start_date_lag) & 
                                      (price_330['Date'] <= end_date)]
    
    #print(APCs_dat, portara_dat, open_price_data)
    
    # The strategy will be ran in loop_signal decorator
    dict_contracts_quant_signals = loop_signal(book, 
                                               APCs_dat, portara_dat, open_price_data,
                                               MRStrategyArgus,
                                               start_date, end_date,
                                               strategy_name= 'argus_exact',
                                               buy_range=buy_range, 
                                               sell_range=sell_range,
                                               open_hr=open_hr, close_hr=close_hr,
                                               commodity_name = commodity_name, 
                                               Timezone= Timezone,
                                               loop_symbol = symbol)
    

    dict_contracts_quant_signals = pd.DataFrame(dict_contracts_quant_signals)
    
    #sort by date
    dict_contracts_quant_signals = dict_contracts_quant_signals.\
                                    sort_values(by='Date')
    # there are better ways than looping. here is a vectoralised method    
    return dict_contracts_quant_signals

# make a function to run multiple signal generation from a list
# tested
@util.time_it
def run_gen_MR_signals_list(Strategy, 
                            filename_list, categories_list, keywords_list, symbol_list, 
                            start_date, end_date,
                            signal_list, history_daily_list, 
                            history_minute_list,
                            open_hr_dict, close_hr_dict, 
                            timezone_dict,
                            save_or_not=False,
                            buy_range=([0.25,0.4],[0.6,0.75],0.05), 
                            sell_range =([0.6,0.75],[0.25,0.4],0.95)):
    
    # a function to download the APC of a list of asset
    # input username and password.json
    output_dict = dict()
    for filename, cat, key, sym, signal, history_daily, history_minute in zip(\
        filename_list, categories_list, keywords_list, symbol_list, signal_list, \
                                        history_daily_list, history_minute_list):
        @util.time_it
        @util.save_csv("{}".format(filename), save_or_not=save_or_not)
        def run_gen_MR_signals_indi(cat, key, sym):
            asset_pack = {'categories': cat, 'keywords': key, 'symbol': sym}
            
            open_hr = open_hr_dict[sym]
            close_hr = close_hr_dict[sym]
            Timezone= timezone_dict[sym]
            
            signal_data = run_gen_MR_signals(asset_pack, 
                                             start_date, end_date,
                                             signal, history_daily, 
                                             history_minute,
                                             buy_range=buy_range, 
                                             sell_range=sell_range,
                                             open_hr=open_hr, close_hr=close_hr,
                                             commodity_name = key, 
                                             Timezone= Timezone
                                             ) #WIP
            print("name {}".format(filename))

            return signal_data
        
        signal_data = run_gen_MR_signals_indi(cat, key, sym)
        output_dict[sym] = signal_data
        print("All asset signal generated!")
    return output_dict



@util.time_it
def run_gen_MR_signals_preloaded_list(filename_list, start_date, end_date,
                       signal_pkl, history_daily_pkl, openprice_pkl, 
                       open_hr_dict, close_hr_dict, timezone_dict,
                       save_or_not = True,
                       buy_range=(0.4,0.6,0.1),sell_range =(0.6,0.4,0.9)):
    
    # run meanreversion signal generation on the basis of individual programme  
    # Loop the whole list in one go with all the contracts or Loop it one contract at a time?
    master_dict = dict()
    symbol_list = list(signal_pkl.keys())
    
    for symbol in symbol_list:
        filename = filename_list[symbol]
        # The reading part takes the longest time: 13 seconds. The loop itself takes 
        # input 1, APC. Load the master table in memory and test multple strategies  
        @util.save_csv("{}".format(filename), save_or_not=save_or_not)
        def run_gen_MR_indi():
            
            book = Bookkeep(bucket_type = 'mr_signals')

            #signal file input
            signal_file = signal_pkl[symbol]
           
            # input 2, Portara history file.
            history_daily_file = history_daily_pkl[symbol]
            #history_minute_file = history_minute_pkl[symbol]
            
            # Find the opening price at 03:30 UK time. If not found, 
            # loop through the next 30 minutes to find the opening price
            open_price = openprice_pkl[symbol]
            
            open_hr = open_hr_dict[symbol]
            close_hr = close_hr_dict[symbol]
            Timezone= timezone_dict[symbol]
            
            # The strategy will be ran in loop_signal decorator
            dict_contracts_quant_signals = loop_signal(book, signal_file, 
                                                       history_daily_file, 
                                                       open_price,
                                                       MRStrategyArgus,
                                                       start_date, end_date,
                                                       strategy_name= 'argus_exact',
                                                       buy_range=buy_range,
                                                       sell_range=sell_range,
                                                       open_hr=open_hr, close_hr=close_hr,
                                                       commodity_name = symbol, 
                                                       Timezone= Timezone,
                                                       loop_symbol=symbol)
            return dict_contracts_quant_signals
        

        master_dict[symbol] = run_gen_MR_indi()
    # there are better ways than looping. here is a vectoralised method    
    return master_dict

if __name__ == "__main__":

    
    #start_date = "2022-01-03"
    start_date = "2021-01-11"
    end_date = "2024-06-17"
    
    
    
    SAVE_FILENAME_LIST = [
    "/home/dexter/Euler_Capital_codes/EC_tools/results/argus_exact_signal/argus_exact_signal_CLc1_full.csv", 
    "/home/dexter/Euler_Capital_codes/EC_tools/results/argus_exact_signal/argus_exact_signal_CLc2_full.csv", 
    "/home/dexter/Euler_Capital_codes/EC_tools/results/argus_exact_signal/argus_exact_signal_HOc1_full.csv", 
    "/home/dexter/Euler_Capital_codes/EC_tools/results/argus_exact_signal/argus_exact_signal_HOc2_full.csv", 
    "/home/dexter/Euler_Capital_codes/EC_tools/results/argus_exact_signal/argus_exact_signal_RBc1_full.csv", 
    "/home/dexter/Euler_Capital_codes/EC_tools/results/argus_exact_signal/argus_exact_signal_RBc2_full.csv", 
    "/home/dexter/Euler_Capital_codes/EC_tools/results/argus_exact_signal/argus_exact_signal_QOc1_full.csv",
    "/home/dexter/Euler_Capital_codes/EC_tools/results/argus_exact_signal/argus_exact_signal_QOc2_full.csv",
    "/home/dexter/Euler_Capital_codes/EC_tools/results/argus_exact_signal/argus_exact_signal_QPc1_full.csv",
    "/home/dexter/Euler_Capital_codes/EC_tools/results/argus_exact_signal/argus_exact_signal_QPc2_full.csv" 
    ]

    

    #maybe I need an unpacking function here to handle payload from json files
    SIGNAL_LIST = list(APC_FILE_LOC.values())
    HISTORY_DAILY_LIST = list(HISTORY_DAILY_FILE_LOC.values())
    HISTORY_MINUTE_LIST = list(HISTORY_MINTUE_FILE_LOC.values())
    
    
    strategy = MR_STRATEGIES_0['argus_exact']
    
    run_gen_MR_signals_list(strategy,
                            SAVE_FILENAME_LIST, CAT_LIST, KEYWORDS_LIST, SYMBOL_LIST, 
                            start_date, end_date,
                            SIGNAL_LIST, HISTORY_DAILY_LIST, HISTORY_MINUTE_LIST,
                            OPEN_HR_DICT, CLOSE_HR_DICT, TIMEZONE_DICT,save_or_not=True)


# =============================================================================
#     asset_pack = {"categories" : 'Argus Nymex Heating oil month 1 Daily',
#                   "keywords" : "Heating",
#                   "symbol": "HOc1"}
# 
#     #inputs: Portara data (1 Minute and Daily), APC
#     signal_filename = "/home/dexter/Euler_Capital_codes/EC_tools/data/APC_latest/APC_latest_HOc1.csv"
#     filename_daily = "/home/dexter/Euler_Capital_codes/EC_tools/data/history_data/Day/HO.day"
#     filename_minute = "/home/dexter/Euler_Capital_codes/EC_tools/data/history_data/Minute/HO.001"
# 
#     # run signal for the individual asset
#     dict_contracts_quant_signals = run_gen_MR_signals(asset_pack, 
#                                                       start_date,  
#                                                       end_date, signal_filename, 
#                                                       filename_daily, 
#                                                       filename_minute)
# 
# 
# =============================================================================

