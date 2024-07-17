#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May  7 23:46:42 2024

@author: dexter
"""
import datetime as datetime
import time

import EC_tools.read as read
import EC_tools.backtest as backtest
import EC_tools.utility as util
from EC_tools.trade import OneTradePerDay, trade_choice_simple
from EC_tools.portfolio import Asset, Portfolio
from crudeoil_future_const import OPEN_HR_DICT, CLOSE_HR_DICT, \
                                ARGUS_EXACT_PNL_SHORT_LOC, ARGUS_EXACT_SIGNAL_FILE_LOC, \
                                    ARGUS_EXACT_PNL_SHORT_LOC, HISTORY_MINTUE_FILE_LOC,\
                                    ARGUS_EXACT_PNL_LOC


__author__="Dexter S.-H. Hon"

@util.time_it
def run_backtest(trade_choice, filename_minute,filename_buysell_signals, 
                 start_date, end_date, open_hr='0800', close_hr='1630'):
    # The current method only allows one singular direction signal perday. and a set of constant EES

    # read the reformatted minute history data
    history_data = read.read_reformat_Portara_minute_data(filename_minute)
    
    # Find the date for trading
    trade_date_table = backtest.prepare_signal_interest(filename_buysell_signals, trim = False)

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
                      save_filename_list, symbol_list,
                      signal_filename_list, history_minute_filename_list,
                        start_date, end_date,
                        open_hr_dict, close_hr_dict, 
                        save_or_not=False):

    
    output_dict = dict()
    for save_filename, sym, signal_filename, history_minute_file in zip(\
        save_filename_list, symbol_list, signal_filename_list, \
                                         history_minute_filename_list):
        
        open_hr = open_hr_dict[sym]
        close_hr = close_hr_dict[sym]
        
        @util.save_csv("{}".format(save_filename), save_or_not=save_or_not)
        def run_backtest_indi(trade_choice, 
                              filename_minute,filename_buysell_signals, 
                         start_date, end_date, open_hr='0300', close_hr='2200'):

            backtest_data = run_backtest(trade_choice, 
                                       filename_minute,filename_buysell_signals, 
                                        start_date, end_date, 
                                        open_hr=open_hr, close_hr=close_hr)
            return backtest_data
                       
            
        backtest_data = run_backtest_indi(trade_choice_simple, 
                                          history_minute_file, signal_filename,
                                          start_date, end_date, 
                                          open_hr=open_hr, close_hr=close_hr)
        
        output_dict[sym] = backtest_data
    print("All Backtest PNL generated!")

    return output_dict

def run_backtest_portfolio(TradeMethod,
                            filename_minute, filename_buysell_signals, 
                           start_date, end_date):
    # master function that runs the backtest itself.
    # The current method only allows one singular direction signal perday. and a set of constant EES

    # read the reformatted minute history data
    history_data = read.read_reformat_Portara_minute_data(filename_minute)

    # Find the date for trading, only "Buy" or "Sell" date are taken.
    trade_date_table = backtest.prepare_signal_interest(filename_buysell_signals, trim = False)
    
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
def run_backtest_portfolio_preloaded_list(TradeMethod,
                                          master_buysell_signals_filename, 
                                          histroy_intraday_data_pkl_filename,
                                          start_date, end_date,
                                          give_obj_name = "USD", 
                                          get_obj_quantity = 1): 
    t1 = time.time()
    start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')

    histroy_intraday_data_pkl = util.load_pkl(histroy_intraday_data_pkl_filename)
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
    P1 = backtest.loop_list_portfolio_preloaded_list(P1, TradeMethod,
                                                     trade_date_table, 
                                           histroy_intraday_data_pkl)
    
    t2 = time.time()-t1
    print("It takes {} seconds to run the backtest".format(t2))

    return P1

if __name__ == "__main__":
    # master function that runs the backtest itself.
    FILENAME_MINUTE = "/home/dexter/Euler_Capital_codes/EC_tools/data/history_data/Minute/CL.001"
    FILENAME_BUYSELL_SIGNALS = "/home/dexter/Euler_Capital_codes/EC_tools/results/argus_exact_signal_short/argus_exact_signal_CLc1_short.csv"
    #SIGNAL_FILENAME = "/home/dexter/Euler_Capital_codes/EC_tools/results/benchmark_signals/benchmark_signal_CLc1_full.csv"   
    #APC_FILENAME = "/home/dexter/Euler_Capital_codes/EC_tools/data/APC_latest/APC_latest_HOc2.csv"  
    
    MASTER_SIGNAL_FILENAME = "/home/dexter/Euler_Capital_codes/EC_tools/results/argus_exact_signal_full.csv"
    HISTORY_MINUTE_PKL_FILENAME ="/home/dexter/Euler_Capital_codes/EC_tools/data/pkl_vault/crudeoil_future_minute_full.pkl"

    #run_backtest(trade_choice_simple,FILENAME_MINUTE, FILENAME_BUYSELL_SIGNALS, "2022-01-03", "2024-06-17")
    SAVE_FILENAME_LIST = list(ARGUS_EXACT_PNL_LOC.values())
    SIGNAL_FILENAME_LIST = list(ARGUS_EXACT_SIGNAL_FILE_LOC.values())
    SYMBOL_LIST = list(ARGUS_EXACT_PNL_LOC.keys())
    HISTORY_MINUTE_FILENAME_LIST = list(HISTORY_MINTUE_FILE_LOC.values())
        
    #start_date = "2022-01-03"
    start_date = "2021-01-11"
    end_date = "2024-06-17"
    
    run_backtest_list(trade_choice_simple, 
                      SAVE_FILENAME_LIST, SYMBOL_LIST,
                          SIGNAL_FILENAME_LIST, HISTORY_MINUTE_FILENAME_LIST,
                                    start_date, end_date,
                                    OPEN_HR_DICT, CLOSE_HR_DICT, 
                                    save_or_not=True)
                         
    #run_backtest_portfolio(FILENAME_MINUTE, FILENAME_BUYSELL_SIGNALS, 
    #                       '2023-06-01', '2023-12-30')
    
    #PP = run_backtest_portfolio_preloaded_list(OneTradePerDay,
    #                                        MASTER_SIGNAL_FILENAME, 
    #                                      HISTORY_MINUTE_PKL_FILENAME,
    #                                      '2022-06-30', '2024-06-30')
    
    