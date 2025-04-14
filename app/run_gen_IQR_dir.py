#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr  9 20:16:53 2025

@author: dexter

The IQR Strategy signal can be pulled directly from the APC server.
Or, alternatively, we can calculate it ourself.
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
import EC_tools.base.read as read
import EC_tools.utility as util
from EC_tools.portfolio.bookkeep import Bookkeep

from crudeoil_future_const import DAILY_DATA_PKL, DAILY_APC_PKL,\
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
__author__="Dexter S.-H. Hon"

DEFAULT_KWARGS= {'signal_list': list(APC_FILE_LOC.values()),
                 'history_daily_list': list(HISTORY_DAILY_FILE_LOC.values()),
                 'history_minute_list': list(HISTORY_MINTUE_FILE_LOC.values()),
                 'signal_pkl': DAILY_APC_PKL,
                 'history_daily_pkl': DAILY_DATA_PKL,
                 'open_hr_dict': OPEN_HR_DICT, 
                 'close_hr_dict': CLOSE_HR_DICT, 
                 'timezone_dict': TIMEZONE_DICT,
                 'save_filenames_loc':TEST_FILE_LOC,
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
                signal_data: pd.DataFrame, 
                history_data: pd.DataFrame, 
                start_date: datetime.datetime, 
                end_date: datetime.datetime,
                buy_range: tuple = ([0.25,0.4],[0.6,0.75],0.05), 
                sell_range: tuple = ([0.6,0.75],[0.25,0.4],0.95), 
                **kwargs) -> pd.DataFrame: 
    """
    The main loop used to generate Buy/Sell signals.

    Parameters
    ----------
    strategy : strategy object
        The function of signal generation from the strategy module.
    book : bookkeep object
        The bookkeeping object from the bookkeep module.
    signal_data : dataframe
        The dataframe of the signal data, e.g.the APCs.
    history_data : dataframe
        The dataframe of the history daily pricing data.
    open_price_data : dataframe
        The dataframe of the history opening pricing data.
    start_date : datetime
        The starting datetime.
    end_date : datetime
        The ending datetime.
    buy_range : tuple, optional
        The range for buy action. The default is ([0.25,0.4],[0.6,0.75],0.05).
    sell_range : tuple, optional
        The range for sell action. The default is ([0.6,0.75],[0.25,0.4],0.95).

    Returns
    -------
    dataframe
        The generated signals

    """
    default_kwargs = DEFAULT_KWARGS
    kwargs = dict(default_kwargs,**kwargs)

    #make bucket
    bucket = book.make_bucket(keyword=strategy().strategy_name) # 'argus_exact_mode')#
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
        APCs_this_date = signal_data[(signal_data['PERIOD']==this_date)]
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
            
            # Get the extracted 5 days Lag data. This is the main input to be
            # put into the Stragey function
            apc_curve_lag, history_data_lag = read.extract_lag_data(\
                                                                 signal_data, 
                                                                 history_data, 
                                                                 forecast_date,
                                                                 lag_size=5)
            
            # Apply the strategy, The Strategy is variable
            strategy_output = strategy(curve_this_date).\
                                        apply_strategy(history_data, 
                                                       signal_data, 
                                                       buy_range=buy_range, 
                                                       sell_range=sell_range,   
                                                       quantile = kwargs['quantile'],
                                                       total_lag_days=2)

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
