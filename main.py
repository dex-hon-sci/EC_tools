#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun 22 23:32:11 2024

@author: dexter
"""
import getpass
#from crudeoil_future_const import *
from crudeoil_future_const import CAT_LIST, KEYWORDS_LIST, SYMBOL_LIST, \
                                    OPEN_HR_DICT, CLOSE_HR_DICT, \
                                    DATA_FILEPATH, RESULT_FILEPATH,\
                                APC_FILE_LOC, HISTORY_DAILY_FILE_LOC, \
                                    HISTORY_MINTUE_FILE_LOC, \
                                        ARGUS_BENCHMARK_SIGNAL_FILE_LOC, \
                                        TEST_FILE_LOC, TEST_FILE_PNL_LOC,\
                                            ARGUS_BENCHMARK_SIGNAL_FILE_LOC,\
                                                ARGUS_EXACT_SIGNAL_FILE_LOC,\
                                            ARGUS_EXACT_SIGNAL_FILE_SHORT_LOC,\
                                            ARGUS_EXACT_PNL_SHORT_LOC, ARGUS_EXACT_PNL_LOC,\
                                            ARGUS_EXACT_SIGNAL_AMB_FILE_LOC, ARGUS_EXACT_PNL_AMB_LOC,\
                                                ARGUS_EXACT_SIGNAL_AMB2_FILE_LOC, ARGUS_EXACT_PNL_AMB2_LOC,\
                                                ARGUS_EXACT_SIGNAL_AMB3_FILE_LOC, ARGUS_EXACT_PNL_AMB3_LOC,\
                                                ARGUS_EXACT_SIGNAL_MODE_FILE_LOC, ARGUS_EXACT_PNL_MODE_LOC

                                        
from crudeoil_future_const import ARGUS_BENCHMARK_SIGNAL_AMB_FILE_LOC, \
                                ARGUS_BENCHMARK_SIGNAL_AMB_BUY_FILE_LOC, \
                                    ARGUS_BENCHMARK_SIGNAL_AMB_SELL_FILE_LOC
                                    
from EC_tools.read import render_PNL_xlsx
import EC_tools.utility as util
from EC_tools.trade import trade_choice_simple_3, OneTradePerDay

from run_preprocess import run_preprocess
from run_gen_MR_dir import MR_STRATEGIES_0, run_gen_signal_bulk
from run_backtest import run_backtest_bulk
from run_PNL_plot import cumPNL_plot

# CSV list -> Signal Gen - > Backtest ->PNL
# Preloaded PKL input ->

@util.time_it
def load_source_data():
    #load the pkl 
    SIGNAL_PKL = util.load_pkl(DATA_FILEPATH+"/pkl_vault/crudeoil_future_APC_full.pkl")
    HISTORY_DAILY_PKL = util.load_pkl(DATA_FILEPATH+"/pkl_vault/crudeoil_future_daily_full.pkl")
    HISTORY_MINUTE_PKL = util.load_pkl(DATA_FILEPATH+"/pkl_vault/crudeoil_future_minute_full.pkl")
    OPENPRICE_PKL = util.load_pkl(DATA_FILEPATH+"/pkl_vault/crudeoil_future_openprice_full.pkl")

    SAVE_FILENAME_LOC = TEST_FILE_LOC #ARGUS_BENCHMARK_SIGNAL_FILE_LOC #TEST_FILE_LOC
    
    return SIGNAL_PKL, HISTORY_DAILY_PKL, \
                HISTORY_MINUTE_PKL,  \
                OPENPRICE_PKL, SAVE_FILENAME_LOC

@util.time_it
def run_main(start_date, end_date,         
             buy_range = ([0.2,0.25],[0.75,0.8],0.1),
             sell_range = ([0.75,0.8],[0.2,0.25],0.9), 
             preprocess = False, 
             runtype = "list"):
    signal_gen_runtype = None
    backtest_runtype = None
    
    FILE_LOC = TEST_FILE_LOC
    FILE_PNL_LOC = TEST_FILE_PNL_LOC

    if runtype == "list":
        
        print("=========Generating Buy/Sell Signals=======")
        
        strategy_name = 'argus_exact'
        strategy = MR_STRATEGIES_0[strategy_name]
        #SAVE_SIGNAL_FILENAME_LIST = list(FILE_LOC.values())
        
        run_gen_signal_bulk(strategy, TEST_FILE_LOC,
                        start_date, end_date,
                        buy_range = buy_range, 
                        sell_range = sell_range,
                        runtype = 'preload',
                        open_hr_dict = OPEN_HR_DICT, 
                        close_hr_dict = CLOSE_HR_DICT, 
                        save_or_not=True,
                        merge_or_not=True)

        print("=========Running Back-Testing =============")
        
        MASTER_PNL_FILENAME = RESULT_FILEPATH + '/test_PNL.csv'
        #SAVE_PNL_FILENAME_LIST = FILE_PNL_LOC

        run_backtest_bulk(trade_choice_simple_3, 
                          FILE_LOC, FILE_PNL_LOC, 
                            start_date, end_date, 
                            method = "list", 
                            master_pnl_filename=MASTER_PNL_FILENAME,
                            open_hr_dict = OPEN_HR_DICT, 
                            close_hr_dict=CLOSE_HR_DICT,
                            save_or_not=True, 
                            merge_or_not=True)
        
        print("=========Running PNL EXCEL File =============")
        
        render_PNL_xlsx([MASTER_PNL_FILENAME], 
                        number_contracts_list = [5,10,15,20,25,50], 
                        suffix='_.xlsx')
    
    elif runtype=='preload':
        
        if preprocess:
            print("===============Data Preprocessing=============")
            # preprocess merge raw CSV data into pkl format 
            run_preprocess()
            
        print("============Loading Source PKL Files===========")
        #SIGNAL_PKL, HISTORY_DAILY_PKL, HISTORY_MINUTE_PKL, OPENPRICE_PKL,\
        #                         SAVE_FILENAME_LOC = load_source_data()
                                 
        SAVE_FILENAME_LOC = TEST_FILE_LOC #ARGUS_BENCHMARK_SIGNAL_FILE_LOC #TEST_FILE_LOC

        print("=========Generating Buy/Sell Signals=======")
        
        strategy_name = 'argus_exact'
        strategy = MR_STRATEGIES_0[strategy_name]
        
        run_gen_signal_bulk(strategy, SAVE_FILENAME_LOC,
                        start_date, end_date,
                        buy_range = buy_range, 
                        sell_range = sell_range,
                        runtype = 'preload',
                        save_or_not=True,
                        merge_or_not=True)

        print("=========Running Back-Testing =============")
        MASTER_SIGNAL_FILENAME = RESULT_FILEPATH + '/test_signal.csv'
        MASTER_PNL_FILENAME = RESULT_FILEPATH + '/test_PNL.pkl'
        
        run_backtest_bulk(OneTradePerDay, 
                          FILE_LOC, FILE_PNL_LOC, 
                            start_date, end_date, 
                            method = "preload", 
                            master_signal_filename = MASTER_SIGNAL_FILENAME,
                            master_pnl_filename=MASTER_PNL_FILENAME,
                            open_hr_dict = OPEN_HR_DICT, 
                            close_hr_dict=CLOSE_HR_DICT,
                            save_or_not=True, 
                            merge_or_not=True)
        
    
     

if __name__ == "__main__":

    start_date = "2024-03-04"
    #start_date = "2021-01-11"
    end_date = "2024-06-17"
    
    run_main(start_date, end_date,         
                 buy_range = ([0.3,0.4],[0.8,0.9],0.1),
                 sell_range = ([0.6,0.7],[0.1,0.2],0.9), 
                 preprocess = False, 
                 runtype = "list")
    
    ## Visualise PNL plot and metrics.
    ##run_PNL
    #cumPNL_plot()