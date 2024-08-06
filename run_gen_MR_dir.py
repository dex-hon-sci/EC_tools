#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 13 19:51:24 2024

@author: dexter

A modified script based on the Mean-Reversion Method developed by Abbe Whitford.

"""
# python import
import datetime as datetime
from enum import Enum
import getpass
# package imports
import pandas as pd 
import numpy as np

# EC_tools imports
from EC_tools.strategy import ArgusMRStrategy, ArgusMRStrategyMode
import EC_tools.read as read
import EC_tools.utility as util
from EC_tools.bookkeep import Bookkeep

from crudeoil_future_const import CAT_LIST, KEYWORDS_LIST, SYMBOL_LIST, \
                                APC_FILE_LOC, HISTORY_DAILY_FILE_LOC,\
                                    HISTORY_MINTUE_FILE_LOC, TIMEZONE_DICT,\
                                        OPEN_HR_DICT, CLOSE_HR_DICT,\
                                        ARGUS_EXACT_SIGNAL_FILE_SHORT_LOC,\
                                            ARGUS_EXACT_SIGNAL_FILE_LOC,\
                                            ARGUS_EXACT_SIGNAL_AMB_FILE_LOC,\
                                            ARGUS_EXACT_SIGNAL_AMB2_FILE_LOC, \
                                                ARGUS_EXACT_SIGNAL_AMB3_FILE_LOC,\
                                                ARGUS_EXACT_SIGNAL_MODE_FILE_LOC,\
                                                RESULT_FILEPATH, DATA_FILEPATH, \
                                                TEST_FILE_LOC


__all__ = ['loop_signal','run_gen_MR_signals', 
           'run_gen_MR_signals_list', 'run_gen_MR_signals_preloaded']

__author__="Dexter S.-H. Hon"


MR_STRATEGIES_0 = {"argus_exact": ArgusMRStrategy,
                   "argus_exact_mode": ArgusMRStrategyMode}



class SignalGenMethod(Enum):
    SIGNAL_GEN = "signal_gen"
    SIGNAL_GEN_LIST = "signal_gen_list"
    SIGNAL_GEN_PRELOAD = "signal_gen_preload"

def loop_signal(Strategy, book: Bookkeep, 
                signal_data: pd.DataFrame, 
                history_data: pd.DataFrame, 
                open_price_data: pd.DataFrame,  
                start_date: datetime.datetime, 
                end_date: datetime.datetime,
                buy_range: tuple = ([0.25,0.4],[0.6,0.75],0.05), 
                sell_range: tuple = ([0.6,0.75],[0.25,0.4],0.95), 
                open_hr: str = '', close_hr: str = '',
                asset_name: str = '', Timezone: str = "",
                contract_symbol_condse: bool = False, 
                loop_symbol: bool = None) -> pd.DataFrame: 
    """
    The main loop used to generate Buy/Sell signals.

    Parameters
    ----------
    Strategy : strategy object
        The function of signal generation from the strategy module.
    book : bookkeep object
        The bookkeeping object from the bookkeep module.
    signal_data : dataframe
        The dataframe of the signal data, e.g.the APCs.
    history_data : dataframe
        The dataframe of the history daily pricing data.
    open_price_data : dataframe
        The dataframe of the history opening pricing data.
    start_date : TYPE
        DESCRIPTION.
    end_date : TYPE
        DESCRIPTION.
    buy_range : tuple, optional
        DESCRIPTION. The default is ([0.25,0.4],[0.6,0.75],0.05).
    sell_range : tuple, optional
        DESCRIPTION. The default is ([0.6,0.75],[0.25,0.4],0.95).
    open_hr : str, optional
        A string for the opening hour for the loop in military format. 
        The default is ''.
    close_hr : str, optional
        A string for the closing hour for the loop in military format. 
        The default is ''.
    commodity_name : str, optional
        The name of the asset in our test. The default is ''.
    Timezone : str, optional
        The name of the Timezone for a particular asset. The default is "".
    contract_symbol_condse : bool, optional
        DESCRIPTION. The default is False.
    loop_symbol : bool, optional
        DESCRIPTION. The default is None.

    Returns
    -------
    None.

    """
    #make bucket
    bucket = book.make_bucket(keyword=Strategy().strategy_name)
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
                                     history_data_lag5, apc_curve_lag5, price_330,
                                     buy_range=buy_range, sell_range=sell_range)

            # Rename the strategy ouputs
            direction = strategy_output['direction']
            strategy_data = strategy_output['data']
            
            print('====================================')
            print(forecast_date, full_contract_symbol,'MR signal generated!', 
                   direction,i)
        

            # make a list of data to be written into bookkeep
            static_info = [asset_name, full_contract_symbol, \
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

def run_gen_MR_signals(Strategy, 
                       asset_pack: dict,
                       signal_filename: str, 
                       filename_daily: str, filename_minute: str, 
                       start_date: str, end_date: str,
                       buy_range: tuple = ([0.25,0.4],[0.6,0.75],0.05), 
                       sell_range: tuple = ([0.6,0.75],[0.25,0.4],0.95), 
                       open_hr: str = '', close_hr: str = '',
                       asset_name: str = '', Timezone: str = "",
                       start_date_pushback: int = 20) -> pd.DataFrame:
    """
    The main function that generate MeanRversion signals.
    This particular method uses the bookkeep module to generate CSV file as 
    outputs.

    Parameters
    ----------
    asset_pack : TYPE
        DESCRIPTION.
    start_date : TYPE
        DESCRIPTION.
    end_date : TYPE
        DESCRIPTION.
    signal_filename : TYPE
        DESCRIPTION.
    filename_daily : TYPE
        DESCRIPTION.
    filename_minute : TYPE
        DESCRIPTION.
    buy_range : tuple, optional
        DESCRIPTION. The default is ([0.25,0.4],[0.6,0.75],0.05).
    sell_range : tuple, optional
        DESCRIPTION. The default is ([0.6,0.75],[0.25,0.4],0.95).
    open_hr : TYPE, optional
        DESCRIPTION. The default is ''.
    close_hr : TYPE, optional
        DESCRIPTION. The default is ''.
    commodity_name : TYPE, optional
        DESCRIPTION. The default is ''.
    Timezone : TYPE, optional
        DESCRIPTION. The default is "".
    start_date_pushback : TYPE, optional
        DESCRIPTION. The default is 20.

    Returns
    -------
    dict_contracts_quant_signals : TYPE
        DESCRIPTION.

    """
    
    # run meanreversion signal generation on the basis of individual programme  
    # Loop the whole list in one go with all the contracts or Loop it one contract at a time?
    
    symbol = asset_pack['symbol']
    asset_name = asset_pack['keywords']

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
    dict_contracts_quant_signals = loop_signal(Strategy, book, 
                                               APCs_dat, portara_dat, open_price_data,
                                               start_date, end_date,
                                               buy_range=buy_range, 
                                               sell_range=sell_range,
                                               open_hr=open_hr, close_hr=close_hr,
                                               asset_name = asset_name, 
                                               Timezone= Timezone,
                                               loop_symbol = symbol)
                  
    dict_contracts_quant_signals = pd.DataFrame(dict_contracts_quant_signals)
    
    #sort by date
    dict_contracts_quant_signals = dict_contracts_quant_signals.\
                                    sort_values(by='Date')
    return dict_contracts_quant_signals

# tested
@util.time_it
def run_gen_MR_signals_list(Strategy, 
                            filename_list: list[str], 
                            categories_list: list[str], 
                            keywords_list: list[str], 
                            symbol_list: list[str],
                            signal_list: list, 
                            history_daily_list: list, 
                            history_minute_list: list,
                            start_date: str, end_date: str,
                            open_hr_dict: dict, close_hr_dict: dict, 
                            timezone_dict: dict, 
                            buy_range: tuple = ([0.25,0.4],[0.6,0.75],0.05), 
                            sell_range: tuple =([0.6,0.75],[0.25,0.4],0.95),
                            save_or_not: bool = False) -> dict:
    """
    A method that run Mean Reversion signal generation for a list of inputs.
    
    This method depends upon the function run_gen_MR_signals to iterate over
    the input lists and calculate the signal for each assets independently.

    Parameters
    ----------
    Strategy : strategy object
        The strategy function that is used to generate the trade signals.
    filename_list : list
        The saved filename list.
    categories_list : list
        DESCRIPTION.
    keywords_list : TYPE
        DESCRIPTION.
    signal_list : TYPE
        DESCRIPTION.
    history_daily_list : TYPE
        DESCRIPTION.
    history_minute_list : TYPE
        DESCRIPTION.
    start_date : TYPE
        DESCRIPTION.
    end_date : TYPE
        DESCRIPTION.
    open_hr_dict : TYPE
        DESCRIPTION.
    close_hr_dict : TYPE
        DESCRIPTION.
    timezone_dict : TYPE
        DESCRIPTION.
    buy_range : TYPE, optional
        DESCRIPTION. The default is ([0.25,0.4],[0.6,0.75],0.05).
    sell_range : TYPE, optional
        DESCRIPTION. The default is ([0.6,0.75],[0.25,0.4],0.95).
    save_or_not : TYPE, optional
        DESCRIPTION. The default is False.

    Returns
    -------
    TYPE
        DESCRIPTION.

    """
    
    output_dict = dict()
    for filename, cat, key, sym, signal, history_daily, history_minute in zip(\
        filename_list, categories_list, keywords_list, symbol_list, signal_list, \
                                        history_daily_list, history_minute_list):
        print("filename", filename)
        @util.time_it
        @util.save_csv("{}".format(filename), save_or_not=save_or_not)
        def run_gen_MR_signals_indi(cat: str, key: str, sym: str):
            asset_pack = {'categories': cat, 'keywords': key, 'symbol': sym}
            
            open_hr = open_hr_dict[sym]
            close_hr = close_hr_dict[sym]
            Timezone= timezone_dict[sym]
            
            print("files",signal, history_daily, history_minute)            
            signal_data = run_gen_MR_signals(Strategy, asset_pack, 
                                             signal, history_daily, history_minute,
                                             start_date, end_date,
                                             buy_range=buy_range, 
                                             sell_range=sell_range,
                                             open_hr=open_hr, close_hr=close_hr,
                                             asset_name = key, 
                                             Timezone= Timezone
                                             ) #WIP
            print("name {}".format(filename))

            return signal_data
        
        signal_data = run_gen_MR_signals_indi(cat, key, sym)
        output_dict[sym] = signal_data
        print("All asset signal generated!")
    return output_dict

@util.time_it
def run_gen_MR_signals_preloaded(Strategy, filename_list: list[str], 
                       signal_pkl, history_daily_pkl, openprice_pkl, 
                       start_date: str, end_date: str,
                       open_hr_dict: dict, close_hr_dict: dict, 
                       timezone_dict: dict,
                       buy_range: tuple = (0.4,0.6,0.1),
                       sell_range: tuple = (0.6,0.4,0.9),
                       save_or_not: bool = True) -> pd.DataFrame:
    """
    

    Parameters
    ----------
    Strategy : TYPE
        DESCRIPTION.
    filename_list : TYPE
        DESCRIPTION.
    signal_pkl : TYPE
        DESCRIPTION.
    history_daily_pkl : TYPE
        DESCRIPTION.
    openprice_pkl : TYPE
        DESCRIPTION.
    start_date : TYPE
        DESCRIPTION.
    end_date : TYPE
        DESCRIPTION.
    open_hr_dict : TYPE
        DESCRIPTION.
    close_hr_dict : TYPE
        DESCRIPTION.
    timezone_dict : TYPE
        DESCRIPTION.
    buy_range : TYPE, optional
        DESCRIPTION. The default is (0.4,0.6,0.1).
    sell_range : TYPE, optional
        DESCRIPTION. The default is (0.6,0.4,0.9).
    save_or_not : TYPE, optional
        DESCRIPTION. The default is True.

    Returns
    -------
    TYPE
        DESCRIPTION.

    """
    
    # run meanreversion signal generation on the basis of individual programme  
    # Loop the whole list in one go with all the contracts or Loop it one contract at a time?
    master_dict = dict()
    symbol_list = list(signal_pkl.keys())
    print(symbol_list, filename_list)
    for symbol in symbol_list:
        filename = filename_list[symbol]
        # The reading part takes the longest time: 13 seconds. The loop itself takes 
        # input 1, APC. Load the master table in memory and test multple strategies  
        @util.save_csv("{}".format(filename), save_or_not=save_or_not)
        def run_gen_MR_indi():
            
            book = Bookkeep(bucket_type = 'mr_signals')
            
            print("symbol",symbol)
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
            dict_contracts_quant_signals = loop_signal(Strategy, book, 
                                                       signal_file, 
                                                       history_daily_file, 
                                                       open_price,
                                                       start_date, end_date,
                                                       buy_range=buy_range,
                                                       sell_range=sell_range,
                                                       open_hr=open_hr, close_hr=close_hr,
                                                       asset_name = symbol, 
                                                       Timezone= Timezone,
                                                       loop_symbol=symbol)
            return dict_contracts_quant_signals
        

        master_dict[symbol] = run_gen_MR_indi()

    return master_dict

SignalGen_RunType = {"signal_gen": run_gen_MR_signals,
                     "signal_gen_list": run_gen_MR_signals_list, 
                     "signal_gen_preload": run_gen_MR_signals_preloaded
                                    }

def run_gen_signal_bulk(strategy, save_filename_loc: dict,  
                        start_date: str, end_date: str,
                        open_hr_dict: dict = OPEN_HR_DICT, 
                        close_hr_dict: dict = CLOSE_HR_DICT, 
                        timezone_dict: dict = TIMEZONE_DICT,
                        buy_range: tuple = (0.4,0.6,0.1), 
                        sell_range: tuple = (0.6,0.4,0.9),
                        runtype: str = 'list', 
                        merge_or_not: bool = True, 
                        save_or_not: bool = False):
    
    if runtype == "list":
        # Fixed input filename from constant variables
        SIGNAL_LIST = list(APC_FILE_LOC.values())
        HISTORY_DAILY_LIST = list(HISTORY_DAILY_FILE_LOC.values())
        HISTORY_MINUTE_LIST = list(HISTORY_MINTUE_FILE_LOC.values())

        SAVE_FILENAME_LIST = list(save_filename_loc.values())
        # Run signal generation in a list format
        run_gen_MR_signals_list(strategy, SAVE_FILENAME_LIST, 
                                CAT_LIST, KEYWORDS_LIST, SYMBOL_LIST,
                                SIGNAL_LIST, HISTORY_DAILY_LIST, HISTORY_MINUTE_LIST,
                                start_date, end_date,
                                open_hr_dict, close_hr_dict, timezone_dict,
                                buy_range = buy_range, 
                                sell_range = sell_range,
                                save_or_not=save_or_not)
        
        if merge_or_not:
            merge_filename = getpass.getpass(prompt="please enter the name for the merged file :") 
            MASTER_SIGNAL_FILENAME = RESULT_FILEPATH + merge_filename
            
            read.merge_raw_data(SAVE_FILENAME_LIST, 
                                MASTER_SIGNAL_FILENAME, sort_by="Date")
            
    elif runtype=='preload':
        # Fixed input filename from constant variables
        SIGNAL_PKL = util.load_pkl(DATA_FILEPATH+"/pkl_vault/crudeoil_future_APC_full.pkl")
        HISTORY_DAILY_PKL = util.load_pkl(DATA_FILEPATH+"/pkl_vault/crudeoil_future_daily_full.pkl")
        OPENPRICE_PKL = util.load_pkl(DATA_FILEPATH+"/pkl_vault/crudeoil_future_openprice_full.pkl")

        SAVE_FILENAME_LIST = list(save_filename_loc.values())

        # Run signal generation in a preloaded format
        run_gen_MR_signals_preloaded(strategy, save_filename_loc, 
                                    SIGNAL_PKL, HISTORY_DAILY_PKL, OPENPRICE_PKL,
                                    start_date, end_date,
                                    open_hr_dict, close_hr_dict, timezone_dict,
                                    buy_range = buy_range, 
                                    sell_range = sell_range,
                                    save_or_not = save_or_not)
        if merge_or_not:
            merge_filename = getpass.getpass(prompt="please enter the name for the merged file :") 
            MASTER_SIGNAL_FILENAME = RESULT_FILEPATH + merge_filename
            
            read.merge_raw_data(SAVE_FILENAME_LIST, 
                                MASTER_SIGNAL_FILENAME, sort_by="Date")



if __name__ == "__main__":

    
    start_date = "2024-03-04"
    #start_date = "2021-01-11"
    end_date = "2024-06-17"
    SAVE_FILENAME_LIST = list(TEST_FILE_LOC.values())

    #maybe I need an unpacking function here to handle payload from json files
# =============================================================================
#     SIGNAL_LIST = list(APC_FILE_LOC.values())
#     HISTORY_DAILY_LIST = list(HISTORY_DAILY_FILE_LOC.values())
#     HISTORY_MINUTE_LIST = list(HISTORY_MINTUE_FILE_LOC.values())
# =============================================================================

    strategy_name = 'argus_exact'
    strategy = MR_STRATEGIES_0[strategy_name]
    buy_range = ([0.2,0.25],[0.75,0.8],0.1) # (-0.1,0.1,-0.45)
    sell_range = ([0.75,0.8],[0.2,0.25],0.9) # (0.1,-0.1,0.45)
    
    # master function in running everything
    run_gen_signal_bulk(strategy, TEST_FILE_LOC,
                    start_date, end_date,
                    buy_range = buy_range, 
                    sell_range = sell_range,
                    runtype = 'list',
                    merge_or_not= True,
                    save_or_not=True)
    
# =============================================================================
# # Test the individual list method
#     run_gen_MR_signals_list(strategy,
#                             SAVE_FILENAME_LIST, CAT_LIST, KEYWORDS_LIST, SYMBOL_LIST, 
#                             SIGNAL_LIST, HISTORY_DAILY_LIST, HISTORY_MINUTE_LIST,
#                             start_date, end_date,
#                             OPEN_HR_DICT, CLOSE_HR_DICT, TIMEZONE_DICT,
#                             buy_range=(-0.1,0.1,-0.45), 
#                             sell_range =(0.1,-0.1,0.45),
#                             save_or_not=True)
# =============================================================================

# =============================================================================
# # Test the aggegrate method 
#     run_gen_signal(strategy, SAVE_FILENAME_LIST,
#                     SIGNAL_LIST, HISTORY_DAILY_LIST, 
#                     start_date, end_date,
#                     buy_range = buy_range, 
#                     sell_range = sell_range,
#                     runtype = 'preload',
#                     save_or_not=False)
# =============================================================================


    


# =============================================================================
#     run_gen_MR_signals_list(strategy,
#                             SAVE_FILENAME_LIST, CAT_LIST, KEYWORDS_LIST,  
#                             SIGNAL_LIST, HISTORY_DAILY_LIST, HISTORY_MINUTE_LIST,
#                             start_date, end_date,
#                             OPEN_HR_DICT, CLOSE_HR_DICT, TIMEZONE_DICT,
#                             buy_range=buy_range, 
#                             sell_range =sell_range,
#                             save_or_not=True)
# 
# 
#     MASTER_SIGNAL_FILENAME = "/home/dexter/Euler_Capital_codes/EC_tools/results/argus_exact_signal_amb3.csv"
#     read.merge_raw_data(SAVE_FILENAME_LIST, MASTER_SIGNAL_FILENAME, sort_by="Date")
# =============================================================================

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

