#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May  7 23:46:42 2024

@author: dexter
"""
import datetime as datetime

import EC_tools.read as read
import EC_tools.backtest as backtest
import EC_tools.utility as util
from EC_tools.portfolio import Asset, Portfolio
from crudeoil_future_const import OPEN_HR_DICT

__author__="Dexter S.-H. Hon"

@util.time_it
def run_backtest(filename_minute,filename_buysell_signals, 
                 start_date, end_date):
    # The current method only allows one singular direction signal perday. and a set of constant EES

    # read the reformatted minute history data
    history_data = read.read_reformat_Portara_minute_data(filename_minute)
    
    # Find the date for trading
    trade_date_table = backtest.prepare_signal_interest(filename_buysell_signals, trim = False)
    
    start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")# datetime.datetime(2023,1,1)
    end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")##datetime.datetime(2023,12,30)
    
    # Select for the date interval for investigation
    history_data = history_data[(history_data['Date'] > start_date) & 
                                (history_data['Date'] < end_date)]
    
    trade_date_table = trade_date_table[(trade_date_table['Date'] > start_date) & 
                                        (trade_date_table['Date'] < end_date)]
    # loop through the date and set the EES prices for each trading day   
    dict_trade_PNL = backtest.loop_date(trade_date_table, history_data, 
                                        open_hr='0800', close_hr='1630',
                                        plot_or_not = False)    

    print(dict_trade_PNL[['date']])

    return dict_trade_PNL

def run_backtest_list():
    
    return

def run_backtest_portfolio(filename_minute, filename_buysell_signals, 
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
    history_data = history_data[(history_data['Date'] > start_date) & 
                                (history_data['Date'] < end_date)]
    
    trade_date_table = trade_date_table[(trade_date_table['Date'] > start_date) & 
                                        (trade_date_table['Date'] < end_date)]
    
    # Initialise Portfolio
    P1 = Portfolio()
    USD_initial = Asset("USD", 10_300_000, "dollars", "Cash") # initial fund
    P1.add(USD_initial,datetime=datetime.datetime(2020,12,31))
    
    # loop through the date and set the EES prices for each trading day   
    P1 = backtest.loop_date_portfolio(P1, trade_date_table, history_data,
                                            give_obj_name = "USD", get_obj_name = "HOc1",
                                            get_obj_quantity = 10,
                                            open_hr='1300', close_hr='1828', 
                                            plot_or_not = False)    
    print('master_table', P1.master_table)

    return P1

def run_backtest_portfolio_preloaded_list(master_buysell_signals_filename, 
                                          histroy_intraday_data_pkl_filename,
                                          start_date, end_date,
                                          give_obj_name = "USD", 
                                          get_obj_quantity = 3): 
    
    histroy_intraday_data_pkl = util.load_pkl(histroy_intraday_data_pkl_filename)
    # Find the date for trading, only "Buy" or "Sell" date are taken.
    trade_date_table = backtest.prepare_signal_interest(master_buysell_signals_filename, 
                                               trim = False)
    
    trade_date_table = trade_date_table[(trade_date_table['Date'] > start_date) & 
                                        (trade_date_table['Date'] < end_date)]
    
    # Initialise Portfolio
    P1 = Portfolio()
    USD_initial = {'name':"USD", 'quantity': 10_000_000, 'unit':"dollars", 
                   'asset_type': "Cash", 'misc':{}} # initial fund
    P1.add(USD_initial,datetime=datetime.datetime(2020,12,31))
    
    # a list of input files
    P1 = backtest.loop_list_portfolio_preloaded_list(P1, trade_date_table, 
                                           histroy_intraday_data_pkl)
    return P1

if __name__ == "__main__":
    # master function that runs the backtest itself.
    FILENAME_MINUTE = "/home/dexter/Euler_Capital_codes/test_MS/data_zeroadjust_intradayportara_attempt1/intraday/1 Minute/HO.001"
    FILENAME_BUYSELL_SIGNALS = "/home/dexter/Euler_Capital_codes/EC_tools/results/benchmark_signals/benchmark_signal_HOc1_full.csv"
    SIGNAL_FILENAME = "/home/dexter/Euler_Capital_codes/EC_tools/data/benchmark_signal_test.csv"   
    
    APC_FILENAME = "/home/dexter/Euler_Capital_codes/EC_tools/data/APC_latest/APC_latest_HOc1.csv"  
    
    MASTER_SIGNAL_FILENAME = "/home/dexter/Euler_Capital_codes/EC_tools/results/benchmark_signal_full.csv"
    HISTORY_MINUTE_PKL_FILENAME ="/home/dexter/Euler_Capital_codes/EC_tools/data/pkl_vault/crudeoil_future_minute_full.pkl"
                                                    
    #run_backtest_portfolio(FILENAME_MINUTE, FILENAME_BUYSELL_SIGNALS, 
    #                       '2023-01-01', '2023-12-30')
    
    PP = run_backtest_portfolio_preloaded_list(MASTER_SIGNAL_FILENAME, 
                                          HISTORY_MINUTE_PKL_FILENAME,
                                          '2023-01-01', '2023-12-30')
    
    