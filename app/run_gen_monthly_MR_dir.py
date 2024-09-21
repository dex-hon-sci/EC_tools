#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 16 12:42:50 2024

@author: dexter
"""
# python import
import datetime as datetime
from enum import Enum
from typing import TypeVar
import getpass
# package imports
import pandas as pd 
import numpy as np

# EC_tools imports
from EC_tools.strategy import ArgusMRStrategy, ArgusMRStrategyMode, Strategy, \
                              APC_LENGTH, ArgusMonthlyStrategy
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
                                  TEST_FILE_LOC, TEST_FILE_LOC_SHORT,\
                                  WEEKLY_30AVG_APC_PKL, DAILY_CUMAVG_MONTH_PKL,\
                                  MONTHLY_APC_PKL

__author__="Dexter S.-H. Hon"


MONTHLY_BOOK_COLS = ['Date', 'Price_Code', 'Direction', 'Commodity_name',
                    'Contract_Month','Timezone', 
                    'Valid_From_localtz_timestr', 'Valid_To_localtz_timestr', 
                    'Target_Lower_Entry_Price', 'Target_Upper_Entry_Price',
                    'Target_Lower_Exit_Price', 'Target_Upper_Exit_Price',
                    'Stop_Exit_Price',
                    'NCUM_CONS', 'NCONS', 'NROLL', 
                    'Signal_NCUM_CONS', 'Signal_NCONS', 'Signal_NROLL',	
                    'Quant_Close_Price_Lag_1', 'Quant_Close_Price_Lag_2',	
                    'Quant_Close_Price_Lag_3', 'Quant_Close_Price_Lag_4',	
                    'Quant_Close_Price_Lag_5', 'Quant_Close_Price_Lag_1_rm_5',	
                    'Q0.05', 'Q0.1','Q0.25', 'Q0.4', 'Q0.5', 
                    'Q0.6', 'Q0.75', 'Q0.9', 'Q0.95',
                    'Entry_Price', 'Exit_Price', 'StopLoss_Price',
                    'strategy_name']

def loop_signal(strategy: type[Strategy], 
                book: Bookkeep, 
                signal_daily_data: pd.DataFrame, 
                signal_monthly_data: pd.DataFrame, 
                history_data: pd.DataFrame, 
                daily_cumavg_data: pd.DataFrame,  
                start_date: datetime.datetime, 
                end_date: datetime.datetime,
                buy_range: tuple = ([0.10,0.35],[0.50,0.90],0.05), 
                sell_range: tuple = ([0.65,0.90],[0.10,0.50],0.95),
                open_hr: str = '', close_hr: str = '',
                quantile = [0.05,0.1,0.25,0.4,0.5,0.6,0.75,0.9,0.95],
                asset_name: str = '', Timezone: str = "",
                contract_symbol_condse: bool = False, 
                loop_symbol: bool = None) -> pd.DataFrame: 
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
        Whether we condense the contract symbol. 
        If False, it is going to
        If True
        The default is False.
    loop_symbol : str, optional
        The name of the loop to be printed. The default is None.

    Returns
    -------
    dataframe
        The generated signals

    """
    #make bucket
    bucket = book.make_bucket(keyword=strategy().strategy_name) # 'argus_exact_mode')#
    print('Start looping signal: {}...'.format(loop_symbol))

    # Find the index of the start_date and end_date here.
    start_index = history_data.index[history_data['Date'] == start_date].item()    
    end_index = history_data.index[history_data['Date'] == end_date].item()
        
    # loop through every forecast date and contract symbol 
    month_curve_index = 0
    for i in np.arange(start_index,end_index): 
        
        this_date = history_data["Date"][i]
        this_symbol = history_data["symbol"][i]
                
        ################################################################
        ####PAY ATTENTION TO HOW TO SELECT FOR THE RIGHT MONTHLY APC.. WIP
        ## USE TWO POINTERS
        #APCs_this_week = signal_monthly_data[(signal_monthly_data['PERIOD'] <= this_date)]
        if this_date >= signal_monthly_data['PUBLICATION_DATE'].iloc[month_curve_index]\
            and this_date < signal_monthly_data['PUBLICATION_DATE'].iloc[month_curve_index+1]:
                
                APCs_this_week = signal_monthly_data.iloc[month_curve_index]
                
        elif this_date >= signal_daily_data['PUBLICATION_DATE'].iloc[month_curve_index+1]:
            month_curve_index = month_curve_index +1
            APCs_this_week = signal_monthly_data.iloc[month_curve_index]
            
        print("this_date", this_date)
        print('Publication date', signal_monthly_data['PUBLICATION_DATE'].iloc[month_curve_index]) 
        print('period', signal_monthly_data['PERIOD'].iloc[month_curve_index])
        #if this_date > signal_daily_data['PERIOD'].iloc[month_curve_index]:
        #    month_curve_index = month_curve_index +1 
        #    APCs_this_week = signal_monthly_data.iloc[month_curve_index]
        
        #print("APCs_this_week", APCs_this_week)
        
        
        ################################################################
        # cross reference the APC list to get the APC of this date and symbol
        APCs_this_date = signal_daily_data[(signal_daily_data['PERIOD']==this_date)]
#                                  & (APCs_dat['symbol']== this_symbol)] #<-- here add a condition matching the symbols

        if len(APCs_this_date) == 0:
            print("APC data of {} from the date {} is missing".\
                                          format(this_symbol, this_date.date()))
        else:
            #print(this_date, this_symbol, APCs_this_date['Forecast Period'].iloc[0])
            forecast_date = APCs_this_date['PERIOD'].to_list()[0] 
                        
            # This is the APC number only
            daily_APC = APCs_this_date.to_numpy()[0][-1-APC_LENGTH:-1]
            weekly_APC = APCs_this_week.to_numpy()[-1-APC_LENGTH:-1]
            #print("daily_APC", daily_APC)
            #monthly_APC = APCs_this_week.to_numpy()[-1-APC_LENGTH:-1]
            # create input for bookkepping
            price_code = APCs_this_date['symbol'].to_list()[0]
            
            # find the quantile of the opening price
            #price_330 = open_price_data[open_price_data['Date']==this_date]\
            #                                                ['Open Price'].item()
            
            daily_cumavg = daily_cumavg_data[daily_cumavg_data['Date'] == this_date]\
                                            ['cumavg_price'].item()
            prev_cum_n = daily_cumavg_data[daily_cumavg_data['Date'] == this_date]\
                                            ['prev_cum_n'].item()                         
                                            # 'cumavg_price', 
                                            #'prev_cum_n'])
                                            
            # The conidtions to decide whether we trim the full_contract_symbol
            # CLA2024J or CL24J
            if contract_symbol_condse == True:
                temp = history_data['Contract Code'][i]
                full_contract_symbol = str(temp)[0:2] + str(temp)[5:7] + str(temp)[-1]
            elif contract_symbol_condse == False:
                full_contract_symbol = history_data['Contract Code'][i]
            
            # Get the extracted 5 days Lag data. This is the main input to be
            # put into the Stragey function
            apc_curve_lag, history_data_lag = read.extract_lag_data(\
                                                                 signal_daily_data, 
                                                                 history_data, 
                                                                 forecast_date,
                                                                 lag_size=5)
            
            # Apply the strategy, The Strategy is variable
            strategy_output = strategy(weekly_APC, daily_APC).\
                                        apply_strategy(history_data_lag, 
                                                       apc_curve_lag, 
                                                       daily_cumavg,
                                                       prev_cum_n,
                                                       buy_range=buy_range, 
                                                       sell_range=sell_range,   
                                                       quantile = quantile)

            print('====================================')
            print(forecast_date, full_contract_symbol,'MR signal generated!', 
                   strategy_output['direction'],i)
        

            # make a list of data to be written into bookkeep
            static_info = [asset_name, full_contract_symbol, \
                           Timezone, open_hr, close_hr]
                
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
def run_gen_MR_signals_preloaded_monthly(strategy: type[Strategy], 
                                         filename_list: list[str], 
                                         signal_daily_pkl: dict, 
                                         signal_monthly_pkl: dict, 
                                         history_daily_pkl: dict, 
                                         daily_cumavg_pkl: dict, 
                                         start_date: str, end_date: str,
                                         open_hr_dict: dict, 
                                         close_hr_dict: dict, 
                                         timezone_dict: dict,
                                         buy_range: tuple = ([0.10,0.35],
                                                             [0.50,0.90],0.05), 
                                         sell_range: tuple = ([0.65,0.90],
                                                              [0.10,0.50],0.95),
                                         quantile: list[float] = [0.05,0.1,
                                                                  0.25,0.4,
                                                                  0.5,0.6,
                                                                  0.75,0.9,
                                                                  0.95],
                                         save_or_not: bool = True) -> pd.DataFrame:
    """
    A method that run Mean Reversion signal generation form a preloaded 
    dictionary. The dictionary contains a key-value pairs with the asset name 
    as keys and a dataframe as value. 
    
    This method depends upon the function run_gen_MR_signals to iterate over
    the input lists and calculate the signal for each assets independently.

    Parameters
    ----------
    Strategy : strategy object
        The strategy function in use in generating the signal.
    filename_list : list
        The saved filename list.
    signal_pkl : dict
        A dictionary read from a pkl file that contains the signal data in 
        a dataframe as values and keywords as key.
    history_daily_pkl : dict
        A dictionary read from a pkl file that contains the daily historical 
        data in a dataframe as values and keywords as key.
    openprice_pkl : dict
        A dictionary read from a pkl file that contains the daily openning price 
        data in a dataframe as values and keywords as key..
    start_date : str
        The starting date.
    end_date : str
        The ending date.
    open_hr_dict : dict
        A dictionary for the input opening hour strings.
    close_hr_dict : dict
        A dictionary for the input closing hour strings.
    timezone_dict : dict
        A dictionary for the Time Zone name strings.
    buy_range : tuple, optional
        The buy range in the format of (entry, exit, stop loss). 
        The default is ([0.25,0.4],[0.6,0.75],0.05).
    sell_range : tuple, optional
        The sell range in the format of (entry, exit, stop loss). 
        The default is ([0.6,0.75],[0.25,0.4],0.95).
    save_or_not : bool, optional
        A boolean value to indicate whether to save the result in a file or not. 
        The default is False.

    Returns
    -------
    dataframe
        signal data.

    """
    
    # run meanreversion signal generation on the basis of individual programme  
    # Loop the whole list in one go with all the contracts or Loop it one contract at a time?
    master_dict, symbol_list = dict(), list(signal_monthly_pkl.keys())
     
    
    print(symbol_list, filename_list)
    for symbol in symbol_list:
        filename = filename_list[symbol]
        print('filename', filename)
        # The reading part takes the longest time: 13 seconds. The loop itself takes 
        # input 1, APC. Load the master table in memory and test multple strategies  
        @util.save_csv("{}".format(filename), save_or_not=save_or_not)
        def run_gen_MR_indi():
            
            book = Bookkeep(bucket_type = 'None', 
                            custom_keywords_list = MONTHLY_BOOK_COLS)
            
            print("symbol",symbol)
            #signal file input
            signal_daily_file = signal_daily_pkl[symbol]
            signal_monthly_file = signal_monthly_pkl[symbol]
            
            # Prepare monthly APC file ** Crucial step in making the whole sctip works
            signal_monthly_file = signal_monthly_file[
                                    signal_monthly_file['CONTINUOUS_FORWARD'] == 2]
           
            # input 2, Portara history file.
            history_daily_file = history_daily_pkl[symbol]
            
            
            #history_minute_file = history_minute_pkl[symbol]
            
            # Find the opening price at 03:30 UK time. If not found, 
            # loop through the next 30 minutes to find the opening price
            daily_cumavg_file = daily_cumavg_pkl[symbol]
            
            open_hr = open_hr_dict[symbol]
            close_hr = close_hr_dict[symbol]
            Timezone= timezone_dict[symbol]
            
            # The strategy will be ran in loop_signal decorator
            dict_contracts_quant_signals = loop_signal(strategy, book, 
                                                       signal_daily_file, 
                                                       signal_monthly_file,
                                                       history_daily_file, 
                                                       daily_cumavg_file,
                                                       start_date, end_date,
                                                       buy_range=buy_range,
                                                       sell_range=sell_range,
                                                       open_hr=open_hr, 
                                                       close_hr=close_hr,
                                                       quantile = quantile,
                                                       asset_name = symbol, 
                                                       Timezone= Timezone,
                                                       loop_symbol=symbol)
            return dict_contracts_quant_signals
        

        master_dict[symbol] = run_gen_MR_indi()

    return master_dict


if __name__ == "__main__":
    #start_date = "2024-03-04"
    #end_date = "2024-06-17"
    SIGNAL_PKL = util.load_pkl(DATA_FILEPATH+"/pkl_vault/crudeoil_future_APC_full.pkl")
    HISTORY_DAILY_PKL = util.load_pkl(DATA_FILEPATH+"/pkl_vault/crudeoil_future_daily_full.pkl")
    MONTHLY_SIGNAL_PKL = util.load_pkl(MONTHLY_APC_PKL)
    CUMAVG = util.load_pkl(DAILY_CUMAVG_MONTH_PKL)
    
    start_date = "2021-01-11"
    end_date = "2024-08-12"
    
    strategy_name = 'argus_monthly'
    strategy = ArgusMonthlyStrategy
    #buy_range = ([0.2,0.25],[0.75,0.8],0.1) # (-0.1,0.1,-0.45)
    #sell_range = ([0.75,0.8],[0.2,0.25],0.9) # (0.1,-0.1,0.45)
    run_gen_MR_signals_preloaded_monthly(strategy,
                                         filename_list = TEST_FILE_LOC_SHORT, 
                                         signal_daily_pkl = SIGNAL_PKL, 
                                         signal_monthly_pkl = MONTHLY_SIGNAL_PKL, 
                                         history_daily_pkl = HISTORY_DAILY_PKL, 
                                         daily_cumavg_pkl = CUMAVG, 
                                         start_date = start_date, 
                                         end_date = end_date,
                                         open_hr_dict = OPEN_HR_DICT, 
                                         close_hr_dict = CLOSE_HR_DICT, 
                                         timezone_dict = TIMEZONE_DICT)
    
    SAVE_FILENAME_LIST = list(TEST_FILE_LOC_SHORT.values())

    
    MASTER_SIGNAL_FILENAME = RESULT_FILEPATH +'/monthly_test/test_master_signal.csv'           
    read.merge_raw_data(SAVE_FILENAME_LIST, 
                        MASTER_SIGNAL_FILENAME, sort_by="Date")