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
                                  OPEN_HR_DICT_EARLY, CLOSE_HR_DICT_EARLY,\
                                  WRONG_OPEN_HR_DICT, WRONG_CLOSE_HR_DICT, \
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
                                  ARGUS_EXACT_SIGNAL_MODE_FILE_LOC, ARGUS_EXACT_PNL_MODE_LOC,\
                                  ARGUS_EXACT_SIGNAL_AMB4_3ROLL_FILE_LOC, \
                                  ARGUS_EXACT_PNL_AMB4_3ROLL_FILE_LOC, \
                                  ARGUS_EXACT_SIGNAL_MODE_WRONGTIME_FILE_LOC,\
                                  ARGUS_EXACT_MODE_PNL_WRONGTIME_LOC,\
                                  ARGUS_EXACT_SIGNAL_EARLY_FILE_LOC, \
                                  ARGUS_EXACT_PNL_EARLY_FILE_LOC
                                        
from crudeoil_future_const import ARGUS_BENCHMARK_SIGNAL_AMB_FILE_LOC, \
                                  ARGUS_BENCHMARK_SIGNAL_AMB_BUY_FILE_LOC, \
                                  ARGUS_BENCHMARK_SIGNAL_AMB_SELL_FILE_LOC
                                    
from EC_tools.read import render_PNL_xlsx
import EC_tools.utility as util
from EC_tools.trade import trade_choice_simple_3, OneTradePerDay

from run_preprocess import run_preprocess
from run_gen_MR_dir import MR_STRATEGIES_0, run_gen_signal_bulk
from run_backtest import run_backtest_bulk


@util.time_it
def load_source_data() -> tuple:
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
def run_main(strategy_name, 
             trade_method,
             start_date: str, end_date: str,         
             buy_range: tuple = ([0.2,0.25],[0.75,0.8],0.1),
             sell_range: tuple = ([0.75,0.8],[0.2,0.25],0.9), 
             preprocess: bool = False, 
             runtype: str = "list",
             signal_gen_runtype: str = "preload",
             backtest_runtype: str = "preload",
             plot_PNL_or_not: bool = False) -> None:
    
    
    #FILE_LOC = TEST_FILE_LOC
    #FILE_PNL_LOC = TEST_FILE_PNL_LOC
    FILE_LOC = ARGUS_EXACT_SIGNAL_EARLY_FILE_LOC# ARGUS_EXACT_SIGNAL_AMB4_3ROLL_FILE_LOC
    FILE_PNL_LOC = ARGUS_EXACT_PNL_EARLY_FILE_LOC
        
    if preprocess:
        print("===============Data Preprocessing=============")
        # preprocess merge raw CSV data into pkl format 
        run_preprocess()
    
    print("=========Generating Buy/Sell Signals=======")
    
    #strategy_name = 'argus_exact_mode'
    strategy = MR_STRATEGIES_0[strategy_name]
    #SAVE_SIGNAL_FILENAME_LIST = list(FILE_LOC.values())
   
    MASTER_SIGNAL_FILENAME = RESULT_FILEPATH + '/argus_exact_early_test.csv'

    
    run_gen_signal_bulk(strategy, FILE_LOC,
                        start_date, end_date,
                        buy_range = buy_range, 
                        sell_range = sell_range,
                        runtype = signal_gen_runtype,
                        master_signal_filename = MASTER_SIGNAL_FILENAME,
                        open_hr_dict = OPEN_HR_DICT_EARLY, 
                        close_hr_dict = CLOSE_HR_DICT_EARLY, 
                        save_or_not=True,
                        merge_or_not=True)
    


    print("=========Running Back-Testing =============")
    
    MASTER_PNL_FILENAME = RESULT_FILEPATH + '/argus_exact_early_PNL_test.csv'
    #SAVE_PNL_FILENAME_LIST = FILE_PNL_LOC

    run_backtest_bulk(trade_method, 
                      FILE_LOC, FILE_PNL_LOC, 
                      start_date, end_date, 
                      method = backtest_runtype, 
                      master_pnl_filename=MASTER_PNL_FILENAME,
                      open_hr_dict = OPEN_HR_DICT_EARLY, 
                      close_hr_dict= CLOSE_HR_DICT_EARLY,
                      save_or_not=True, 
                      merge_or_not=True)
    
    
    print("=========Running PNL EXCEL File =============")
    if backtest_runtype == 'list':
        render_PNL_xlsx([MASTER_PNL_FILENAME], 
                    number_contracts_list = [5,10,15,20,25,50], 
                    suffix='_.xlsx')

    if plot_PNL_or_not:
    	pass
     

if __name__ == "__main__":

    #start_date = "2024-03-04"
    start_date = "2021-01-11"
    end_date = "2024-08-15"
    
    run_main('argus_exact', 
             trade_choice_simple_3,
             start_date, end_date,         
             #buy_range = (-0.1, 0.1, -0.45), 
             #sell_range = (0.1, -0.1, +0.45),
             buy_range = ([0.25,0.4],[0.6,0.75],0.1),
             sell_range = ([0.6,0.75],[0.35,0.4],0.9), 
             preprocess = False, 
             signal_gen_runtype='preload',
             backtest_runtype = "list")
   
    ## Visualise PNL plot and metrics.
    ##run_PNL
    #cumPNL_plot()
