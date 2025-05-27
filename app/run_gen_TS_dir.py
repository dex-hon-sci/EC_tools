#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 23 15:46:06 2025

@author: dexter
"""

# Python import
import datetime as datetime
from enum import Enum
from typing import TypeVar

# common package imports
import pandas as pd 
import numpy as np

# EC_tools imports
from EC_tools.strategy import ArgusMRStrategy, ArgusMRStrategyMode, \
                              Strategy, APC_LENGTH
from EC_tools.strategy.ArgusTailStrangleStrategy import ArgusTailStrangleStrategy,\
                                                        argus_tailstrangle_format
import EC_tools.base.read as read
import EC_tools.utility as util
from EC_tools.portfolio.bookkeep import Bookkeep

from crudeoil_future_const import DAILY_DATA_PKL, DAILY_APC_PKL,\
                                  DAILY_MINUTE_DATA_INDI_PKL,\
                                  CAT_LIST, KEYWORDS_LIST, SYMBOL_LIST, \
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


__all__ = ['loop_signal',
           'run_gen_MR_signals_preloaded']

__author__="Dexter S.-H. Hon"

DEFAULT_KWARGS= {'signal_list': list(APC_FILE_LOC.values()),
                 'history_daily_list': list(HISTORY_DAILY_FILE_LOC.values()),
                 'history_minute_list': list(HISTORY_MINTUE_FILE_LOC.values()),
                 'signal_pkl': DAILY_APC_PKL,
                 'history_daily_pkl': DAILY_DATA_PKL,
                 #'history_minute_pkl':DAILY_MINUTE_DATA_INDI_PKL,
                 'open_hr_dict': OPEN_HR_DICT, 
                 'close_hr_dict': CLOSE_HR_DICT, 
                 'timezone_dict': TIMEZONE_DICT,
                 'save_filenames_loc':TEST_FILE_LOC,
                 'breakout_quant': {'Buy':0.95, 'Sell':0.05},
                 'quantile': [0.05,0.1,0.25,0.4,0.5,0.6,0.75,0.9,0.95],
                 'master_signal_filename': "master_signal.csv",
                 'save_or_not': False,
                 'merge_or_not': True,
                 'contract_symbol_condse': False,
                 'loop_symbol': None,
                 'open_hr': '', 
                 'close_hr': '',
                 'asset_name':'', 
                 'Timezone': ""}

def loop_signal(strategy: type[Strategy], 
                book: type[Bookkeep], 
                apc_data: pd.DataFrame, 
                history_data: pd.DataFrame, 
                history_data_minute: pd.DataFrame, 
                start_date: datetime.datetime, 
                end_date: datetime.datetime,
                buy_range: tuple = (0.95, 1.0, 0.9), 
                sell_range: tuple = (0.6,0.4,0.9),
                **kwargs) -> pd.DataFrame: 

    default_kwargs = DEFAULT_KWARGS
    kwargs = dict(default_kwargs,**kwargs)

    #make bucket
    bucket = book.make_bucket(keyword=strategy().strategy_name) 
    print('Start looping signal: {}...'.format(kwargs['loop_symbol']))
    print('Start and end',
          history_data.index[history_data['Date'] == start_date],
          history_data.index[history_data['Date'] == end_date])
    
    # Find the index of the start_date and end_date here.
    start_index = history_data.index[history_data['Date'] == start_date].item()  
    
    print(history_data.index[history_data['Date'] == end_date],end_date)
    end_index = history_data.index[history_data['Date'] == end_date].item()
    
        
    # loop through every forecast date and contract symbol 
    for i in np.arange(start_index,end_index+1): 
        
        this_date = history_data["Date"][i]
        this_symbol = history_data["symbol"][i]
                
        # cross reference the APC list to get the APC of this date and symbol
        APCs_this_date = apc_data[(apc_data['PERIOD']==this_date)]
#                                  & (APCs_dat['symbol']== this_symbol)] #<-- here add a condition matching the symbols
        
        if len(APCs_this_date) == 0:
            print("APC data of {} from the date {} is missing".\
                                          format(this_symbol, this_date.date()))
        else:
            #print(this_date, this_symbol, APCs_this_date['Forecast Period'].iloc[0])
            forecast_date = APCs_this_date['PERIOD'].to_list()[0] 
                        
            # This is the APC number only
            curve_this_date = APCs_this_date.to_numpy()[0][-1-APC_LENGTH:-1]
            # create input for bookkepping
            price_code = APCs_this_date['symbol'].to_list()[0]
                        
            # The conidtions to decide whether we trim the full_contract_symbol
            # CLA2024J or CL24J
            if kwargs['contract_symbol_condse'] == True:
                temp = history_data['Contract Code'][i]
                full_contract_symbol = str(temp)[0:2] + str(temp)[5:7] + str(temp)[-1]
            elif kwargs['contract_symbol_condse'] == False:
                full_contract_symbol = history_data['Contract Code'][i]
            
            history_intraday_data = history_data_minute[history_data_minute['Date'] 
                                                        == this_date]     
            print('breakout_quant', kwargs['breakout_quant'])
            # Apply the strategy, The Strategy is variable
            strategy_output = strategy(curve_this_date).\
                                        apply_strategy(history_intraday_data, 
                                                       buy_range=buy_range, 
                                                       sell_range=sell_range,   
                                                       quantile = kwargs['quantile'],
                                                       breakout_quant = kwargs['breakout_quant'])

            print('====================================')
            print(forecast_date, full_contract_symbol,'MR signal generated!', 
                   strategy_output['direction'],i)
        

            # make a list of data to be written into bookkeep
            static_info = [kwargs['asset_name'], full_contract_symbol, 
                           kwargs['Timezone'], kwargs['open_hr'], 
                           kwargs['close_hr']]
                
            # put all the data in a singular list
            data = [forecast_date, price_code] + \
                    [strategy_output['direction']] + \
                    static_info +  strategy_output['data']
            #print("data", data, len(data))
            # Storing the data    
            bucket = book.store_to_bucket_single(data)       
        
    dict_contracts_quant_signals = pd.DataFrame(bucket)

    #sort by date (the first column)
    dict_contracts_quant_signals = dict_contracts_quant_signals.sort_values(by=
                                    dict_contracts_quant_signals.columns.values[0])
    
    return dict_contracts_quant_signals

@util.time_it
def run_gen_MR_signals_preloaded(strategy: Strategy, 
                                 signal_pkl: dict, 
                                 history_daily_pkl: dict, 
                                 #history_minute_pkl: dict,
                                 start_date: str, end_date: str,
                                 buy_range: tuple[float] = (0.95,1.0,0.9), 
                                 sell_range: tuple[float] = (0.05,0.0,0.1),
                                  **kwargs) -> pd.DataFrame:
    """


    """
    default_kwargs = DEFAULT_KWARGS
    kwargs = dict(default_kwargs,**kwargs)
    
    # run meanreversion signal generation on the basis of individual programme  
    # Loop the whole list in one go with all the contracts or Loop it one contract at a time?
    master_dict, symbol_list = dict(), list(signal_pkl.keys())
     
    print(symbol_list, kwargs['save_filenames_loc'])
    for symbol in symbol_list:
        filename = kwargs['save_filenames_loc'][symbol]
        # The reading part takes the longest time: 13 seconds. The loop itself takes 
        # input 1, APC. Load the master table in memory and test multple strategies  
        @util.save_csv("{}".format(filename), save_or_not=kwargs['save_or_not'])
        def run_gen_MR_indi():
            
            book = Bookkeep(custom_keywords_list = argus_tailstrangle_format)
            
            print("symbol",symbol)
            #signal file input
            signal_file = signal_pkl[symbol]
           
            # input 2, Portara history file.
            history_daily_data = history_daily_pkl[symbol]
            history_minute_data = kwargs['history_minute_pkl'][symbol]
            
            open_hr = kwargs['open_hr_dict'][symbol]
            close_hr = kwargs['close_hr_dict'][symbol]
            Timezone= kwargs['timezone_dict'][symbol]
            
            # The strategy will be ran in loop_signal decorator
            dict_contracts_quant_signals = loop_signal(strategy, book, 
                                                       signal_file, 
                                                       history_daily_data, # Daily data
                                                       history_minute_data, # minute data
                                                       start_date, end_date,
                                                       buy_range=buy_range,
                                                       sell_range=sell_range,
                                                       open_hr=open_hr, 
                                                       close_hr=close_hr,
                                                       quantile = kwargs['quantile'],
                                                       asset_name = symbol, 
                                                       Timezone= Timezone,
                                                       loop_symbol=symbol,
                                                       breakout_quant = kwargs['breakout_quant'])
            return dict_contracts_quant_signals
        

        master_dict[symbol] = run_gen_MR_indi()

    return master_dict

def run_gen_signal_bulk(strategy: type[Strategy], 
                        start_date: str, end_date: str,
                        buy_range: tuple[float] = (0.4,0.6,0.1), 
                        sell_range: tuple[float] = (0.6,0.4,0.9),
                        runtype: str = 'preload', 
                        **kwargs) -> None:

    default_kwargs = DEFAULT_KWARGS
    kwargs = dict(default_kwargs,**kwargs)
    
    SAVE_FILENAME_LIST = list(kwargs['save_filenames_loc'].values())
    
    if runtype=='preload':
        # Fixed input filename from constant variables
        SIGNAL_PKL = util.load_pkl(kwargs['signal_pkl'])
        HISTORY_DAILY_PKL = util.load_pkl(kwargs['history_daily_pkl'])
        
        # Run signal generation in a preloaded format
        run_gen_MR_signals_preloaded(strategy, 
                                     SIGNAL_PKL, 
                                     HISTORY_DAILY_PKL, 
                                     start_date, end_date,
                                     buy_range = buy_range, 
                                     sell_range = sell_range,
                                     history_minute_pkl = kwargs['history_minute_pkl'], 
                                     open_hr_dict = kwargs['open_hr_dict'],
                                     close_hr_dict = kwargs['close_hr_dict'], 
                                     timezone_dict = kwargs['timezone_dict'],
                                     save_filenames = kwargs['save_filenames_loc'],
                                     quantile = kwargs['quantile'],
                                     save_or_not = kwargs['save_or_not'],
                                     breakout_quant = kwargs['breakout_quant'])
    if kwargs['merge_or_not']:
        #SAVE_FILENAME_LIST = list(kwargs['save_filenames_loc'].values())
        MASTER_SIGNAL_FILENAME = kwargs['master_signal_filename']       
        
        read.merge_raw_data(SAVE_FILENAME_LIST, 
                            MASTER_SIGNAL_FILENAME, sort_by="Date")
if __name__ == "__main__":
    
    def load_source_data_bt(filenames_loc) -> dict:
        master_dict = {}
        for filename in filenames_loc:
            temp_dict = util.load_pkl(filename)
            master_dict = dict(master_dict, **temp_dict)
            
        return master_dict

    #start_date = "2024-03-04"
    #start_date = "2021-01-11"
    start_date = "2022-01-05"
    end_date = "2022-06-28"
    SAVE_FILENAME_LIST = list(TEST_FILE_LOC.values())
    
    HISTORY_MINUTE_PKL= load_source_data_bt(list(DAILY_MINUTE_DATA_INDI_PKL.values()))

    strategy_name = 'argus_exact'
    strategy = ArgusTailStrangleStrategy
    buy_range = (0.95,1.0,0.9)
    sell_range =(0.05,0.0,0.1)
    
    breakout_quant = {'Buy':0.95, 'Sell':0.05}
    # master function in running everything
    run_gen_signal_bulk(strategy, 
                        start_date, end_date,
                        buy_range = buy_range, 
                        sell_range = sell_range,
                        runtype = 'preload',
                        save_filenames_loc = TEST_FILE_LOC,
                        history_minute_pkl = HISTORY_MINUTE_PKL,
                        breakout_quant = breakout_quant,
                        merge_or_not= True,
                        save_or_not=True)