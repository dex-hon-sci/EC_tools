#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May  7 23:46:42 2024

@author: dexter
"""
import datetime as datetime
import time
import pickle
import pandas as pd
from enum import Enum
import getpass
import EC_tools.read as read
import EC_tools.backtest as backtest
import EC_tools.utility as util
from EC_tools.trade import OneTradePerDay, trade_choice_simple, \
                            trade_choice_simple_2, trade_choice_simple_3
from EC_tools.portfolio import Asset, Portfolio
from crudeoil_future_const import OPEN_HR_DICT, CLOSE_HR_DICT, \
                                  DATA_FILEPATH, RESULT_FILEPATH,\
                                  ARGUS_EXACT_SIGNAL_FILE_LOC, \
                                  ARGUS_EXACT_PNL_SHORT_LOC, HISTORY_MINTUE_FILE_LOC,\
                                  ARGUS_EXACT_PNL_LOC, \
                                  ARGUS_EXACT_SIGNAL_AMB_FILE_LOC, ARGUS_EXACT_PNL_AMB_LOC,\
                                  ARGUS_EXACT_SIGNAL_AMB2_FILE_LOC, ARGUS_EXACT_PNL_AMB2_LOC,\
                                  ARGUS_EXACT_SIGNAL_AMB3_FILE_LOC, ARGUS_EXACT_PNL_AMB3_LOC,\
                                  ARGUS_EXACT_SIGNAL_MODE_FILE_LOC, ARGUS_EXACT_PNL_MODE_LOC,\
                                  TEST_FILE_LOC, TEST_FILE_PNL_LOC\


__all__ = ['run_backtest','run_backtest_list', 
           'run_backtest_portfolio', 'run_backtest_portfolio_preloaded']

__author__="Dexter S.-H. Hon"


class BacktestType(Enum):
    BACKTEST_SINGLE = "backtest_single"
    BACKTEST_LIST = "backtest_list"
    BACKTEST_PORTFOLIO = "backtest_portfolio"
    BACKTEST_PORTFOLIO_LIST = "backtest_portfolio"


@util.time_it
def run_backtest(trade_choice, 
                 filename_minute: str,
                 filename_buysell_signals: str, 
                 start_date: datetime.datetime, end_date: datetime.datetime, 
                 open_hr: str = '0800', close_hr: str = '1630') -> pd.DataFrame:
    """
    
    The simplest backtest method. It uses the basic 'loop_date' to iterate 
    the data. At the moment it uses cross-over loop.
    
    The current method only allows one singular direction signal per day 
    and a set of constant EES
    
    Parameters
    ----------
    trade_choice : TYPE
        DESCRIPTION.
    filename_minute : str
        The filename of the historical minute data.
    filename_buysell_signals : str
        The filename of the trading signals data.
    start_date : datetime.datetime
        The start date.
    end_date : datetime.datetime
        The end date.
    open_hr : str, optional
        The opening hour. The default is '0800'.
    close_hr : str, optional
        The closing hour. The default is '1630'.

    Returns
    -------
    dict_trade_PNL : ataFrame
        The resulting PNL file.

    """

    # read the reformatted minute history data
    history_data = read.read_reformat_Portara_minute_data(filename_minute)
    
    # Find the date for trading
    trade_date_table = backtest.prepare_signal_interest(filename_buysell_signals, 
                                                        trim = False)

    start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")# datetime.datetime(2023,1,1)
    end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")##datetime.datetime(2023,12,30)
    
    # Select for the date interval for investigation
    history_data = history_data[(history_data['Date'] >= start_date) & 
                                (history_data['Date'] <= end_date)]
    
    trade_date_table = trade_date_table[(trade_date_table['Date'] >= start_date) & 
                                        (trade_date_table['Date'] <= end_date)]
    
    # loop through the date and set the EES prices for each trading day   
    dict_trade_PNL = backtest.loop_date(trade_choice, 
                                        trade_date_table, history_data, 
                                        open_hr=open_hr, close_hr=close_hr,
                                        plot_or_not = False)    


    return dict_trade_PNL

def run_backtest_list(trade_choice, 
                      save_filename_list: list[str], 
                      symbol_list: list[str],
                      signal_filename_list: list[str], 
                      history_minute_filename_list: list[str],
                      start_date, end_date,
                      open_hr_dict = OPEN_HR_DICT, close_hr_dict=CLOSE_HR_DICT, 
                      save_or_not: bool = False):

    
    output_dict = dict()
    for save_filename, sym, signal_filename, history_minute_file in zip(\
        save_filename_list, symbol_list, signal_filename_list, \
                                         history_minute_filename_list):
        
        open_hr = open_hr_dict[sym]
        close_hr = close_hr_dict[sym]
        print("Running backtest on {}".format(sym))
        @util.save_csv("{}".format(save_filename), save_or_not=save_or_not)
        def run_backtest_indi(trade_choice, 
                              filename_minute,filename_buysell_signals, 
                         start_date, end_date, open_hr='0300', close_hr='2200'):

            backtest_data = run_backtest(trade_choice, 
                                       filename_minute,filename_buysell_signals, 
                                        start_date, end_date, 
                                        open_hr=open_hr, close_hr=close_hr)
            return backtest_data
                       
            
        backtest_data = run_backtest_indi(trade_choice, 
                                          history_minute_file, signal_filename,
                                          start_date, end_date, 
                                          open_hr=open_hr, close_hr=close_hr)
        
        output_dict[sym] = backtest_data
    print("All Backtest PNL generated!")

    return output_dict

def run_backtest_portfolio(TradeMethod,
                           filename_minute: str, 
                           filename_buysell_signals: str, 
                           start_date: str, end_date: str):
    """
    The basic backtest method utilising the Portfolio module.
    
    The current method only allows one singular direction signal per day 
    and a set of constant EES


    Parameters
    ----------
    TradeMethod : TYPE
        DESCRIPTION.
    filename_minute : str
        The filename of the historical minute data.
    filename_buysell_signals : str
        The filename of the trading signals data.
    start_date : str
        The start date.
    end_date : str
        The end date.

    Returns
    -------
    P1 : TYPE
        DESCRIPTION.

    """
    # master function that runs the backtest itself.

    # read the reformatted minute history data
    history_data = read.read_reformat_Portara_minute_data(filename_minute)

    # Find the date for trading, only "Buy" or "Sell" date are taken.
    trade_date_table = backtest.prepare_signal_interest(filename_buysell_signals, trim = False)
    
    # Turn the start and end date from str to datetime.datetime
    start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")# datetime.datetime(2023,1,1)
    end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")##datetime.datetime(2023,12,30)
    
    # Select for the date interval for investigation
    history_data = history_data[(history_data['Date'] >= start_date) & 
                                (history_data['Date'] <= end_date)]
    
    trade_date_table = trade_date_table[(trade_date_table['Date'] >= start_date) & 
                                        (trade_date_table['Date'] <= end_date)]
    
    # Initialise Portfolio
    P1 = Portfolio()
    USD_initial = Asset("USD", 10_300_000, "dollars", "Cash") # initial fund
    P1.add(USD_initial,datetime=datetime.datetime(2020,12,31))
    
    # loop through the date and set the EES prices for each trading day   
    P1 = backtest.loop_date_portfolio(P1, TradeMethod,
                                      trade_date_table, history_data,
                                            give_obj_name = "USD", get_obj_name = "HOc1",
                                            get_obj_quantity = 10,
                                            open_hr='1300', close_hr='1828', 
                                            plot_or_not = False)    
    print('master_table', P1.master_table)

    return P1

#@util.pickle_save("/home/dexter/Euler_Capital_codes/EC_tools/results/test3_portfolio_nonconcurrent_1contracts_full.pkl")
def run_backtest_portfolio_preloaded(TradeMethod,
                                     master_buysell_signals_filename: str, 
                                     histroy_intraday_data_pkl: dict,
                                     start_date: str, end_date: str,
                                     give_obj_name: str = "USD", 
                                     get_obj_quantity: int = 1): 
    """
    

    Parameters
    ----------
    TradeMethod : TYPE
        DESCRIPTION.
    master_buysell_signals_filename : str
        DESCRIPTION.
    histroy_intraday_data_pkl : TYPE
        The dictionary of the preloaded historical minute data.
    start_date : str
        The start date.
    end_date : str
        The end date.
    give_obj_name : str, optional
        The name of the give object. The default is "USD".
    get_obj_quantity : int, optional
        The name of the get object. The default is 1.

    Returns
    -------
    P1 : TYPE
        DESCRIPTION.

    """
    t1 = time.time()
    start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')

    #histroy_intraday_data_pkl = util.load_pkl(histroy_intraday_data_pkl_filename)
    # Find the date for trading, only "Buy" or "Sell" date are taken.
    trade_date_table = backtest.prepare_signal_interest(master_buysell_signals_filename, 
                                               trim = False)
    #start_date_lag = datetime.datetime.strptime(start_date, '%Y-%m-%d') - \
    #                        datetime.timedelta(days= start_date_pushback)
    trade_date_table = trade_date_table[(trade_date_table['Date'] >= start_date) & 
                                        (trade_date_table['Date'] <= end_date)]
    
    # Initialise Portfolio
    P1 = Portfolio()
    USD_initial = {'name':"USD", 'quantity': 10_000_000, 'unit':"dollars", 
                   'asset_type': "Cash", 'misc':{}} # initial fund
    P1.add(USD_initial,datetime=datetime.datetime(2020,12,31))
    
    # a list of input files
    P1 = backtest.loop_portfolio_preloaded_list(P1, 
                                                TradeMethod,
                                                trade_date_table, 
                                                histroy_intraday_data_pkl)
    
    t2 = time.time()-t1
    print("It takes {} seconds to run the backtest".format(t2))

    return P1

    
def run_backtest_bulk(TradeMethod, 
                      signal_file_loc: dict, save_file_loc: dict, 
                      start_date: str, end_date: str, 
                      method: str = "list", 
                      master_signal_filename: str = "", 
                      master_pnl_filename: str = '',
                      open_hr_dict = OPEN_HR_DICT, 
                      close_hr_dict=CLOSE_HR_DICT,
                      save_or_not: bool = True, merge_or_not: bool = True):
            
    if method == "list":
        SAVE_FILENAME_LIST = list(save_file_loc.values())
        SIGNAL_FILENAME_LIST = list(signal_file_loc.values())
        SYMBOL_LIST = list(signal_file_loc.keys())
        HISTORY_MINUTE_FILENAME_LIST = list(HISTORY_MINTUE_FILE_LOC.values())
    
        
        backtest_result = run_backtest_list(TradeMethod, 
                        SAVE_FILENAME_LIST, SYMBOL_LIST,
                          SIGNAL_FILENAME_LIST, HISTORY_MINUTE_FILENAME_LIST,
                                    start_date, end_date,
                                    open_hr_dict = open_hr_dict, 
                                    close_hr_dict=close_hr_dict, 
                                    save_or_not=save_or_not)
                      
        if merge_or_not:
            #merge_filename = getpass.getpass(prompt="please enter the name for the merged file :") 
            #MASTER_SIGNAL_FILENAME = RESULT_FILEPATH + merge_filename

            read.merge_raw_data(SAVE_FILENAME_LIST, 
                                master_pnl_filename, sort_by="Entry_Date")
        
    elif method == "portfolio":
        
        backtest_result =  run_backtest_portfolio(FILENAME_MINUTE, 
                                                  FILENAME_BUYSELL_SIGNALS, 
                                   start_date, end_date)
        
    elif method == "preload":
        #MASTER_SIGNAL_FILENAME
        HISTORY_MINUTE_PKL = util.load_pkl(DATA_FILEPATH+"/pkl_vault/crudeoil_future_minute_full.pkl")

        PP = run_backtest_portfolio_preloaded(OneTradePerDay,
                                                master_signal_filename, 
                                              HISTORY_MINUTE_PKL,
                                              start_date, end_date)
        backtest_result = PP
        if save_or_not:
            file = open(master_pnl_filename, 'wb')
            pickle.dump(PP, file)
        
    
    return backtest_result

if __name__ == "__main__":
    
    Backtest_Lib = {"run_backtest": run_backtest,
                "run_backtest_list": run_backtest_list,
                "run_backtest_portfolio": run_backtest_portfolio,
                "run_backtest_portfolio_preloaded": run_backtest_portfolio_preloaded}
    
    # master function that runs the backtest itself.
    FILENAME_MINUTE = "/home/dexter/Euler_Capital_codes/EC_tools/data/history_data/Minute/CL.001"
    FILENAME_BUYSELL_SIGNALS = "/home/dexter/Euler_Capital_codes/EC_tools/results/argus_exact_signal_short/argus_exact_signal_CLc1_short.csv"
    #SIGNAL_FILENAME = "/home/dexter/Euler_Capital_codes/EC_tools/results/benchmark_signals/benchmark_signal_CLc1_full.csv"   
    #APC_FILENAME = "/home/dexter/Euler_Capital_codes/EC_tools/data/APC_latest/APC_latest_HOc2.csv"  
    
    MASTER_SIGNAL_FILENAME = "/home/dexter/Euler_Capital_codes/EC_tools/results/argus_exact_signal_full.csv"
    HISTORY_MINUTE_PKL_FILENAME ="/home/dexter/Euler_Capital_codes/EC_tools/data/pkl_vault/crudeoil_future_minute_full.pkl"

    SAVE_FILENAME_LIST = list(ARGUS_EXACT_PNL_AMB3_LOC.values())
    SIGNAL_FILENAME_LIST = list(ARGUS_EXACT_SIGNAL_AMB3_FILE_LOC.values())
    SYMBOL_LIST = list(ARGUS_EXACT_PNL_AMB3_LOC.keys())
    HISTORY_MINUTE_FILENAME_LIST = list(HISTORY_MINTUE_FILE_LOC.values())

# =============================================================================
#     FILEPATH = "/home/dexter/Euler_Capital_codes/EC_tools/results/"
#     MASTER_PNL_FILENAME = FILEPATH+'argus_exact_PNL_amb3_full.csv'
# =============================================================================

    start_date = "2024-03-04"
    #start_date = "2021-01-11"
    end_date = "2024-06-17"
    
    run_backtest_bulk(trade_choice_simple_3, TEST_FILE_LOC, TEST_FILE_PNL_LOC, 
                            start_date, end_date, 
                     method = "preload", master_pnl_filename='',
                     open_hr_dict = OPEN_HR_DICT, close_hr_dict=CLOSE_HR_DICT,
                     save_or_not=True, merge_or_not=True)
    
    #run_backtest(trade_choice_simple_2,FILENAME_MINUTE, FILENAME_BUYSELL_SIGNALS, 
    #             "2022-01-03", "2024-06-17")

# =============================================================================
#     backtest_result = run_backtest_list(trade_choice_simple_3, 
#                       SAVE_FILENAME_LIST, SYMBOL_LIST,
#                           SIGNAL_FILENAME_LIST, HISTORY_MINUTE_FILENAME_LIST,
#                                     start_date, end_date,
#                                     OPEN_HR_DICT, CLOSE_HR_DICT, 
#                                     save_or_not=True)
#                        
#     read.merge_raw_data(SAVE_FILENAME_LIST, MASTER_PNL_FILENAME, sort_by="Entry_Date")
# 
#     #run_backtest_portfolio(FILENAME_MINUTE, FILENAME_BUYSELL_SIGNALS, 
#     #                       '2023-06-01', '2023-12-30')
#     
#     #PP = run_backtest_portfolio_preloaded_list(OneTradePerDay,
#     #                                        MASTER_SIGNAL_FILENAME, 
#     #                                      HISTORY_MINUTE_PKL_FILENAME,
#     #                                      '2022-06-30', '2024-06-30')
#     
# =============================================================================

