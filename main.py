#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun 22 23:32:11 2024

@author: dexter
"""
#from crudeoil_future_const import *
from crudeoil_future_const import CAT_LIST, KEYWORDS_LIST, SYMBOL_LIST, \
                                APC_FILE_LOC, HISTORY_DAILY_FILE_LOC, \
                                    HISTORY_MINTUE_FILE_LOC, \
                                        ARGUS_BENCHMARK_SIGNAL_FILE_LOC, TEST_FILE_LOC,\
                                            ARGUS_BENCHMARK_SIGNAL_FILE_LOC
                                        
from EC_tools.read import merge_raw_data
import EC_tools.utility as util
from run_preprocess import run_preprocess
from run_gen_MR_dir import run_gen_MR_signals_list, run_gen_MR_signals_preloaded_list
from run_backtest import run_backtest_portfolio_preloaded_list

@util.time_it
def load_source_data():
    #load the pkl 
    SIGNAL_PKL = util.load_pkl("/home/dexter/Euler_Capital_codes/EC_tools/data/pkl_vault/crudeoil_future_APC_full.pkl")
    HISTORY_DAILY_PKL = util.load_pkl("/home/dexter/Euler_Capital_codes/EC_tools/data/pkl_vault/crudeoil_future_daily_full.pkl")
    HISTORY_MINUTE_PKL = util.load_pkl("/home/dexter/Euler_Capital_codes/EC_tools/data/pkl_vault/crudeoil_future_minute_full.pkl")
    OPENPRICE_PKL = util.load_pkl("/home/dexter/Euler_Capital_codes/EC_tools/data/pkl_vault/crudeoil_future_openprice_full.pkl")

    SAVE_SIGNAL_FILENAME_LIST = TEST_FILE_LOC #ARGUS_BENCHMARK_SIGNAL_FILE_LOC #TEST_FILE_LOC
    
    return SIGNAL_PKL, HISTORY_DAILY_PKL, \
                HISTORY_MINUTE_PKL,  \
                OPENPRICE_PKL, SAVE_SIGNAL_FILENAME_LIST

@util.pickle_save("/home/dexter/Euler_Capital_codes/EC_tools/results/portfolio_results/test_run_portfolio.pkl")
def quick_backtest(master_buysell_signals_data, histroy_intraday_data_pkl,
                                                       start_date, end_date):
    
    PP = run_backtest_portfolio_preloaded_list(master_buysell_signals_data, 
                                              histroy_intraday_data_pkl,
                                              start_date, end_date)
    return PP

if __name__ == "__main__":

    # data management
    
    #run_data_management
    print("===============Data Management=============")
    
    # run preprocessing (calculate earliest entry and update all database )
    
    run_preprocess()
    
    print("============Loading Source Files===========")
    
    SIGNAL_PKL = util.load_pkl(
        "/home/dexter/Euler_Capital_codes/EC_tools/data/pkl_vault/crudeoil_future_APC_full.pkl")
    HISTORY_DAILY_PKL = util.load_pkl(
        "/home/dexter/Euler_Capital_codes/EC_tools/data/pkl_vault/crudeoil_future_daily_full.pkl")
    #HISTORY_MINUTE_PKL = util.load_pkl("crudeoil_future_minute_full.pkl")
    OPENPRICE_PKL = util.load_pkl(
        "/home/dexter/Euler_Capital_codes/EC_tools/data/pkl_vault/crudeoil_future_openprice_full.pkl")

    SAVE_SIGNAL_FILENAME_LIST = TEST_FILE_LOC #ARGUS_BENCHMARK_SIGNAL_FILE_LOC #TEST_FILE_LOC
    
    #SIGNAL_PKL, HISTORY_DAILY_PKL, HISTORY_MINUTE_PKL, OPENPRICE_PKL,\
    #                            SAVE_SIGNAL_FILENAME_LIST = load_source_data()
    
    start_date = "2021-01-05"
    end_date = "2024-05-18"
    
    print("=========Generating Buy/Sell Signals=======")
    
    # run strategy, let the user to choose strategy here (add strategy id)
    
    run_gen_MR_signals_preloaded_list(SAVE_SIGNAL_FILENAME_LIST, 
                                      start_date, end_date,
                           SIGNAL_PKL, HISTORY_DAILY_PKL, OPENPRICE_PKL,
                           save_or_not = True)
    print("---------merge signals tables--------------")
    
    SIGNAL_LIST = list(ARGUS_BENCHMARK_SIGNAL_FILE_LOC.values())   
    #SIGNAL_LIST = list(TEST_FILE_LOC.values())   
    
    MASTER_SIGNAL_FILENAME = "/home/dexter/Euler_Capital_codes/EC_tools/results/benchmark_signal_full.csv"
    merge_raw_data(SIGNAL_LIST, MASTER_SIGNAL_FILENAME, sort_by="APC forecast period")

    print("=========Running Back-Testing =============")
    start_date = "2024-01-05"
    end_date = "2024-05-18"
    
    MASTER_SIGNAL_FILENAME = "/home/dexter/Euler_Capital_codes/EC_tools/benchmark_signal_full.csv"
    #HISTORY_MINUTE_PKL = util.load_pkl(
    #    "/home/dexter/Euler_Capital_codes/EC_tools/data/pkl_vault/crudeoil_future_minute_full.pkl")

    
    #PP =  quick_backtest(MASTER_SIGNAL_FILENAME, HISTORY_MINUTE_PKL,start_date, end_date)


#merge_CSV_table
# opne_pickle


# run backtest- let the user to generate backtest data using their method
#run_backtest_portfolio

# Visualise PNL plot and metrics.
#run_PNL