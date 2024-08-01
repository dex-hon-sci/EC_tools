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
from EC_tools.read import merge_raw_data, render_PNL_xlsx
import EC_tools.utility as util

from run_preprocess import run_preprocess
from run_gen_MR_dir import MR_STRATEGIES_0, run_gen_signal
from run_backtest import run_backtest_portfolio_preloaded_list
from run_PNL_plot import cumPNL_plot

# CSV list -> Signal Gen - > Backtest ->PNL
# Preloaded PKL input ->
RunType = {"list", 'preloaded'}

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

def gen_signal(method = 'gen_signal_MR_list'):
    
    {'gen_signal_MR': run_gen_MR_signals_list, 
     'gen_signal_MR_list': run_gen_MR_signals_list,
     'gen_signal_MR_preloaded_list': run_gen_MR_signals_preloaded_list}
    
    run_gen_MR_signals_preloaded_list(SAVE_SIGNAL_FILENAME_LIST, 
                                      start_date, end_date,
                            SIGNAL_PKL, HISTORY_DAILY_PKL, OPENPRICE_PKL,
                            save_or_not = True, 
                            buy_range=(0.4,0.6,0.1), sell_range=(0.6,0.4,0.9))
    
        
    run_gen_MR_signals_list(strategy,
                            SAVE_FILENAME_LIST, CAT_LIST, KEYWORDS_LIST, SYMBOL_LIST, 
                            start_date, end_date,
                            SIGNAL_LIST, HISTORY_DAILY_LIST, HISTORY_MINUTE_LIST,
                            OPEN_HR_DICT, CLOSE_HR_DICT, TIMEZONE_DICT,
                            buy_range=([0.25,0.4],[0.7,0.8],0.1), 
                            sell_range =([0.6,0.75],[0.2,0.3],0.9),
                            save_or_not=True)


    merge_raw_data(SIGNAL_LIST, MASTER_SIGNAL_FILENAME, sort_by="Date")
    return 

@util.pickle_save("/home/dexter/Euler_Capital_codes/EC_tools/results/test2_portfolio_nonconcurrent_10contracts_full.pkl")
def backtest(master_buysell_signals_data, histroy_intraday_data_pkl,
                                                       start_date, end_date):
    
    PP = run_backtest_portfolio_preloaded_list(master_buysell_signals_data, 
                                              histroy_intraday_data_pkl,
                                              start_date, end_date, 
                                              get_obj_quantity = 10)
    # merge table outputs
    merge_raw_data(PNL_LIST, MASTER_PNL_FILENAME, sort_by="Entry_Date")

    #make PNL xlsx
    render_PNL_xlsx([])
    return PP



def run_main(start_date, end_date,         
             buy_range = ([0.2,0.25],[0.75,0.8],0.1),
             sell_range = ([0.75,0.8],[0.2,0.25],0.9), 
             preprocess = False, 
             runtype = "list"):
    

    if runtype == "list":
        
        print("============Loading Source Files===========")
        
        print("=========Generating Buy/Sell Signals=======")
        
        start_date = "2024-03-03"
        #start_date = "2021-01-11"
        end_date = "2024-06-17"
        SAVE_FILENAME_LIST = list(TEST_FILE_LOC.values())

        #maybe I need an unpacking function here to handle payload from json files
        SIGNAL_LIST = list(APC_FILE_LOC.values())
        HISTORY_DAILY_LIST = list(HISTORY_DAILY_FILE_LOC.values())

        strategy_name = 'argus_exact'
        strategy = MR_STRATEGIES_0[strategy_name]

        
        run_gen_signal(strategy, SAVE_FILENAME_LIST,
                        SIGNAL_LIST, HISTORY_DAILY_LIST, 
                        start_date, end_date,
                        buy_range = buy_range, 
                        sell_range = sell_range,
                        runtype = 'list',
                        save_or_not=True,
                        merge_or_not=True)

        print("=========Running Back-Testing =============")
    
    
        print("=========Running PNL EXCEL File =============")
        render_PNL_xlsx()
    
    elif runtype=='preload':
        
        if preprocess:
            print("===============Data Preprocessing=============")
            # preprocess merge raw CSV data into pkl format 
            run_preprocess()
            
        print("============Loading Source PKL Files===========")
        SIGNAL_PKL, HISTORY_DAILY_PKL, HISTORY_MINUTE_PKL, OPENPRICE_PKL,\
                                 SAVE_SIGNAL_FILENAME_LIST = load_source_data()
                                 
                                 
        print("=========Generating Buy/Sell Signals=======")

        print("=========Running Back-Testing =============")

    
    return 

if __name__ == "__main__":

    # data management
    
    #run_data_management
    print("===============Data Management=============")
    
    # run preprocessing (calculate earliest entry and update all database )
    
    run_preprocess()
    
    print("============Loading Source Files===========")
# =============================================================================
#     
#     SIGNAL_PKL = util.load_pkl(
#         "/home/dexter/Euler_Capital_codes/EC_tools/data/pkl_vault/crudeoil_future_APC_full.pkl")
#     HISTORY_DAILY_PKL = util.load_pkl(
#         "/home/dexter/Euler_Capital_codes/EC_tools/data/pkl_vault/crudeoil_future_daily_full.pkl")
#     #HISTORY_MINUTE_PKL = util.load_pkl("crudeoil_future_minute_full.pkl")
#     OPENPRICE_PKL = util.load_pkl(
#         "/home/dexter/Euler_Capital_codes/EC_tools/data/pkl_vault/crudeoil_future_openprice_full.pkl")
# 
# =============================================================================
#     SAVE_SIGNAL_FILENAME_LIST = [
#      "/home/dexter/Euler_Capital_codes/EC_tools/results/argus_exact_signal/argus_exact_signal_CLc1_full.csv", 
#      "/home/dexter/Euler_Capital_codes/EC_tools/results/argus_exact_signal/argus_exact_signal_CLc2_full.csv", 
#      "/home/dexter/Euler_Capital_codes/EC_tools/results/argus_exact_signal/argus_exact_signal_HOc1_full.csv", 
#      "/home/dexter/Euler_Capital_codes/EC_tools/results/argus_exact_signal/argus_exact_signal_HOc2_full.csv", 
#      "/home/dexter/Euler_Capital_codes/EC_tools/results/argus_exact_signal/argus_exact_signal_RBc1_full.csv", 
#      "/home/dexter/Euler_Capital_codes/EC_tools/results/argus_exact_signal/argus_exact_signal_RBc2_full.csv", 
#      "/home/dexter/Euler_Capital_codes/EC_tools/results/argus_exact_signal/argus_exact_signal_QOc1_full.csv",
#      "/home/dexter/Euler_Capital_codes/EC_tools/results/argus_exact_signal/argus_exact_signal_QOc2_full.csv",
#      "/home/dexter/Euler_Capital_codes/EC_tools/results/argus_exact_signal/argus_exact_signal_QPc1_full.csv",
#      "/home/dexter/Euler_Capital_codes/EC_tools/results/argus_exact_signal/argus_exact_signal_QPc2_full.csv" 
#      ]
# =============================================================================
     #= #TEST_FILE_LOC #ARGUS_BENCHMARK_SIGNAL_AMB_FILE_LOC
#     #ARGUS_BENCHMARK_SIGNAL_FILE_LOC #TEST_FILE_LOC
#     
#     #SIGNAL_PKL, HISTORY_DAILY_PKL, HISTORY_MINUTE_PKL, OPENPRICE_PKL,\
#     #                            SAVE_SIGNAL_FILENAME_LIST = load_source_data()
#     
#     start_date = "2022-01-01"
#     end_date = "2024-06-15"
#     
#     print("=========Generating Buy/Sell Signals=======")
#     
#     # run strategy, let the user to choose strategy here (add strategy id)
#     run_gen_MR_signals_preloaded_list
#     run_gen_MR_signals_preloaded_list(SAVE_SIGNAL_FILENAME_LIST, 
#                                       start_date, end_date,
#                            SIGNAL_PKL, HISTORY_DAILY_PKL, OPENPRICE_PKL,
#                            save_or_not = True, 
#                            buy_range=(0.4,0.6,0.1), sell_range=(0.6,0.4,0.9))
# =============================================================================
    
# =============================================================================
#     print("---------merge signals tables--------------")
#     
#     #SIGNAL_LIST = list(SAVE_SIGNAL_FILENAME_LIST.values())   
#     #SIGNAL_LIST = list(TEST_FILE_LOC.values())   
#     SIGNAL_LIST = list(ARGUS_EXACT_SIGNAL_AMB3_FILE_LOC.values())
#     MASTER_SIGNAL_FILENAME = "/home/dexter/Euler_Capital_codes/EC_tools/results/argus_exact_signal_amb3.csv"
#     merge_raw_data(SIGNAL_LIST, MASTER_SIGNAL_FILENAME, sort_by="Date")
# 
#     print("=========Running Back-Testing =============")
#     start_date = "2024-03-15"
#     end_date = "2024-06-15"
#     
#     #MASTER_SIGNAL_FILENAME = "/home/dexter/Euler_Capital_codes/EC_tools/results/benchmark_signal_full.csv"
#     #HISTORY_MINUTE_PKL_FILENAME ="/home/dexter/Euler_Capital_codes/EC_tools/data/pkl_vault/crudeoil_future_minute_full.pkl"
# 
# # =============================================================================
# # 
# #     @util.time_it
# #     def quick_backtest_time():
# #         PP =  quick_backtest(MASTER_SIGNAL_FILENAME, HISTORY_MINUTE_PKL_FILENAME,start_date, end_date)
# #         return PP
# # =============================================================================
#     
#     #PP = quick_backtest_time()
#     PNL_LIST = list(ARGUS_EXACT_PNL_AMB3_LOC.values())
#     MASTER_PNL_FILENAME = "/home/dexter/Euler_Capital_codes/EC_tools/results/argus_exact_PNL_amb3_full.csv"
#     merge_raw_data(PNL_LIST, MASTER_PNL_FILENAME, sort_by="Entry_Date")
# =============================================================================
    
    ## Visualise PNL plot and metrics.
    ##run_PNL
    #cumPNL_plot()