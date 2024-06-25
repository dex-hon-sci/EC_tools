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
                                        ARGUS_BENCHMARK_SIGNAL_FILE_LOC, TEST_FILE_LOC
                                        
from EC_tools.read import merge_portara_data
import EC_tools.utility as util
from run_preprocess import run_preprocess
from run_gen_MR_dir import run_gen_MR_signals_list, run_gen_MR_signals_preloaded_list


@util.time_it
def load_source_data():
    #load the pkl 
    SIGNAL_PKL = util.load_pkl("crudeoil_future_APC_full.pkl")
    HISTORY_DAILY_PKL = util.load_pkl("crudeoil_future_daily_full.pkl")
    HISTORY_MINUTE_PKL = util.load_pkl("crudeoil_future_minute_full.pkl")
    OPENPRICE_PKL = util.load_pkl("crudeoil_future_openprice_full.pkl")

    SAVE_SIGNAL_FILENAME_LIST = TEST_FILE_LOC
    
    return SIGNAL_PKL, HISTORY_DAILY_PKL, HISTORY_MINUTE_PKL, OPENPRICE_PKL,\
                SAVE_SIGNAL_FILENAME_LIST


def quick_backtest():
    
    return

if __name__ == "__main__":

    # data management
    
    #run_data_management
    print("===============Data Management=============")
    
    # run preprocessing (calculate earliest entry and update all database )
    print("============Running Preprocessing==========")
    
    run_preprocess()
    print("============Loading Source Files===========")
    

    
    SIGNAL_PKL, HISTORY_DAILY_PKL, HISTORY_MINUTE_PKL, OPENPRICE_PKL,\
                                SAVE_SIGNAL_FILENAME_LIST = load_source_data()
    
    start_date = "2024-03-10"
    end_date = "2024-05-18"
    
    print("=========Generating Buy/Sell Signals=======")
    
    # run strategy, let the user to choose strategy here (add strategy id)
    
    run_gen_MR_signals_preloaded_list(SAVE_SIGNAL_FILENAME_LIST, 
                                      start_date, end_date,
                           SIGNAL_PKL, HISTORY_DAILY_PKL, OPENPRICE_PKL,
                           save_or_not = True)
    
    print("=========Running Back-Testing =============")
    
    
    quick_backtest()

# =============================================================================
# SIGNAL_LIST = list(APC_FILE_LOC.values())
# HISTORY_DAILY_LIST = list(HISTORY_DAILY_FILE_LOC.values())
# HISTORY_MINUTE_LIST = list(HISTORY_MINTUE_FILE_LOC.values())
# 
# 
# run_gen_MR_signals_list(SAVE_SIGNAL_FILENAME_LIST, CAT_LIST, 
#                         KEYWORDS_LIST, SYMBOL_LIST, 
#                             start_date, end_date,
#                             SIGNAL_LIST, HISTORY_DAILY_LIST, 
#                             HISTORY_MINUTE_LIST)
# 
# =============================================================================


#merge_CSV_table
# opne_pickle


# run backtest- let the user to generate backtest data using their method
#run_backtest_portfolio

# Visualise PNL plot and metrics.
#run_PNL