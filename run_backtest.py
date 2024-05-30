#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May  7 23:46:42 2024

@author: dexter
"""
import EC_tools.read as read
import EC_tools.backtest as backtest
import EC_tools.utility as util

@util.time_it
@util.save_csv('benchmark_PNL_QPc2_full.csv')
def run_backtest(filename_minute,filename_buysell_signals):
    # The current method only allows one singular direction signal perday. and a set of constant EES

    # read the reformatted minute history data
    history_data = read.read_reformat_Portara_minute_data(filename_minute)
    
    # Find the date for trading
    trade_date_table = backtest.prepare_signal_interest(filename_buysell_signals, trim = False)
        
    # loop through the date and set the EES prices for each trading day   
    dict_trade_PNL = backtest.loop_date(trade_date_table, history_data, 
                                        open_hr='0800', close_hr='1630',
                                        plot_or_not = False)    

    print(dict_trade_PNL[['date']])

    return dict_trade_PNL

def run_backtest_crude_oil():
    
    return

if __name__ == "__main__":
    # master function that runs the backtest itself.
    filename_minute = "../test_MS/data_zeroadjust_intradayportara_attempt1/intraday/1 Minute/QP_d01.001"
    filename_buysell_signals = "./benchmark_signal_QPc2_full.csv"
    
    run_backtest(filename_minute, filename_buysell_signals)