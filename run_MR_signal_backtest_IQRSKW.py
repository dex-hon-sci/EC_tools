#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 12 13:10:53 2025

@author: dexter
"""

# Common package import

#from numba import jit
# EC_tools import
from EC_tools.base.read import render_PNL_xlsx, open_portfolio
import EC_tools.utility as util
from EC_tools.trade import OneTradePerDay, BiDirectionalTrade
from EC_tools.backtest import LoopType
from EC_tools.portfolio import PortfolioLog
from EC_tools.strategy.ArgusIQRStrategy import ArgusIQRStrategy
#from EC_tools.strategy.ArgusTailStrangleStrategy import ArgusTailStrangleStrategy,\
#                                                        argus_tailstrangle_format

# application import
from app.run_preprocess import run_preprocess
#from app.run_gen_MR_dir import MR_STRATEGIES_0, run_gen_signal_bulk
from app.run_gen_IQR_dir import run_gen_signal_bulk
from app.run_backtest import run_backtest_bulk


# Import global constants
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
                                  ARGUS_EXACT_PNL_EARLY_FILE_LOC,\
                                  DAILY_MINUTE_DATA_INDI_PKL
                                        
from crudeoil_future_const import ARGUS_BENCHMARK_SIGNAL_AMB_FILE_LOC, \
                                  ARGUS_BENCHMARK_SIGNAL_AMB_BUY_FILE_LOC, \
                                  ARGUS_BENCHMARK_SIGNAL_AMB_SELL_FILE_LOC


                  
@util.time_it
def load_source_data_signal() -> tuple:
    #load the pkl 
    SIGNAL_PKL = util.load_pkl(DATA_FILEPATH+"/pkl_vault/crudeoil_future_APC_full.pkl")
    HISTORY_DAILY_PKL = util.load_pkl(DATA_FILEPATH+"/pkl_vault/crudeoil_future_daily_full.pkl")
    #HISTORY_MINUTE_PKL = util.load_pkl(DATA_FILEPATH+"/pkl_vault/crudeoil_future_minute_full.pkl")
    #OPENPRICE_PKL = util.load_pkl(DATA_FILEPATH+"/pkl_vault/crudeoil_future_openprice_full.pkl")
    
    #SAVE_FILENAME_LOC = TEST_FILE_LOC #ARGUS_BENCHMARK_SIGNAL_FILE_LOC #TEST_FILE_LOC
    #SAVE_FILENAME_LOC = TEST_FILE_PNL_LOC #ARGUS_BENCHMARK_SIGNAL_FILE_LOC #TEST_FILE_LOC
    
    return SIGNAL_PKL, HISTORY_DAILY_PKL

@util.time_it
def load_source_data_bt(filenames_loc) -> dict:
    master_dict = {}
    for filename in filenames_loc:
        temp_dict = util.load_pkl(filename)
        master_dict = dict(master_dict, **temp_dict)
        
    return master_dict

#@jit(nopython=True)
#@util.time_it
def run_main(strategy_name, 
             trade_method,
             start_date: str, end_date: str,         
             buy_range: tuple = ([0.2,0.25],[0.75,0.8],0.05),
             sell_range: tuple = ([0.75,0.8],[0.2,0.25],0.95), 
             give_obj_name: str = 'USD',
             get_obj_quantity: int = 1,
             preprocess: bool = False, 
             load: bool = True,
             signal_gen_runtype: str = "preload",
             backtest_runtype: str = "preload",
             plot_PNL_or_not: bool = False, **kwargs) -> None:
    
    default_kwargs = {'give_obj_name':'USD',
                      'get_obj_quantity': 1,
                      'open_hr_dict': WRONG_OPEN_HR_DICT, 
                      'close_hr_dict': CLOSE_HR_DICT, 
                      'preprocess': False, 
                      'signal_gen_runtype': "preload", 
                      'backtest_runtype': "preload", 
                      'plot_PNL_or_not':False,
                      'breakout_quant':{'Buy':0.8, 'Sell':0.2}}
    
    kwargs = dict(default_kwargs, **kwargs)

    FILE_LOC = TEST_FILE_LOC
    FILE_PNL_LOC = TEST_FILE_PNL_LOC
    #FILE_LOC = ARGUS_EXACT_SIGNAL_EARLY_FILE_LOC# ARGUS_EXACT_SIGNAL_AMB4_3ROLL_FILE_LOC
    #FILE_PNL_LOC = ARGUS_EXACT_PNL_EARLY_FILE_LOC
        
    if preprocess:
        print("===============Data Preprocessing=============")
        # preprocess merge raw CSV data into pkl format 
        #run_preprocess()
    elif load:
        SIGNAL_PKL, HISTORY_DAILY_PKL = load_source_data_signal()
        HISTORY_MINUTE_PKL = load_source_data_bt(list(DAILY_MINUTE_DATA_INDI_PKL.values()))
        
        print('HISTORY_MINUTE_PKL',HISTORY_MINUTE_PKL)
        #raise Exception('?')
    print("=========Generating Buy/Sell Signals=======")
    
    #strategy_name = 'argus_exact_mode'
    #strategy = MR_STRATEGIES_0[strategy_name]
    strategy = ArgusIQRStrategy
    
    #SAVE_SIGNAL_FILENAME_LIST = list(FILE_LOC.values())
   
    #MASTER_SIGNAL_FILENAME = RESULT_FILEPATH + '/consistency/Argus_sample_with_mybacktest_newcode/Argus_sample_signals_2.csv'
    #MASTER_SIGNAL_FILENAME = RESULT_FILEPATH + '/consistency/live_trade_vs_backtest_newcode/live_trade_compare_signals_TP25SL10_normalopen.csv'
    #MASTER_SIGNAL_FILENAME = RESULT_FILEPATH + '/EC_benchmark/20240814_argusexact_cross_P25S35_0330_entry_signal_full.csv'
    #MASTER_SIGNAL_FILENAME = RESULT_FILEPATH + '/ArgusTailStrangle/20240814_argutailstrangle_cross_TE45SL35_0330_entry_signal_full.csv'
    MASTER_SIGNAL_FILENAME = RESULT_FILEPATH + '/ArgusIQRSKW/20240814_argusIQRSKW_cross_WIQR38WSKW10_TETPOBOSSL45_0330_entry_signal_full.csv'
    
    run_gen_signal_bulk(strategy,
                        start_date, end_date,
                        buy_range = buy_range, 
                        sell_range = sell_range,
                        runtype = signal_gen_runtype,
                        master_signal_filename = MASTER_SIGNAL_FILENAME,
                        open_hr_dict = WRONG_OPEN_HR_DICT, 
                        close_hr_dict = CLOSE_HR_DICT, 
                        save_or_not=True,
                        merge_or_not=True,
                        window_IQR = 38,#38,
                        window_SKW = 10)#22)
    

    print("=========Running Back-Testing =============")
    
    #MASTER_PNL_FILENAME = RESULT_FILEPATH + '/consistency/Argus_sample_with_mybacktest_newcode/Argus_sample_PNL_with_mybacktest_newcode.pkl' 
    #MASTER_PNL_FILENAME = RESULT_FILEPATH + '/consistency/live_trade_vs_backtest_newcode/live_trade_compare_portoflio_TP25SL10_normalopen.pkl' 
    #MASTER_PNL_FILENAME = RESULT_FILEPATH + '/EC_benchmark/20240814_argusexact_cross_P25S35_0330_entry_PNL_full.pkl'
    #MASTER_PNL_FILENAME = RESULT_FILEPATH + '/ArgusTailStrangle/20240814_argutailstrangle_cross_TE45SL35_0330_entry_PNL_full.pkl'
    MASTER_PNL_FILENAME = RESULT_FILEPATH + '/ArgusIQRSKW/20240814_argusIQRSKW_cross_WIQR38WSKW10_TETPOBOSSL45_0330_entry_PNL_full.pkl'
    
    #SAVE_PNL_FILENAME_LIST = FILE_PNL_LOC
    print("HISTORY_MINUTE_PKL", HISTORY_MINUTE_PKL)
    run_backtest_bulk(trade_method, 
                      start_date, end_date, 
                      method = backtest_runtype, 
                      master_signal_filename = MASTER_SIGNAL_FILENAME,
                      master_pnl_filename=MASTER_PNL_FILENAME,
                      histroy_intraday_data_pkl = HISTORY_MINUTE_PKL,
                      give_obj_name = give_obj_name,
                      get_obj_quantity = get_obj_quantity,
                      open_hr_dict = WRONG_OPEN_HR_DICT, 
                      close_hr_dict= CLOSE_HR_DICT,
                      save_or_not=True, 
                      merge_or_not=True,
                      loop_type= LoopType.CROSSOVER,
                      selected_directions = ["Buy", "Sell"],
                      price_proxy='High')
    
    print("=========Running PNL EXCEL File =============")
    if backtest_runtype == 'list':
        render_PNL_xlsx([MASTER_PNL_FILENAME], 
                        number_contracts_list = [5,10,15,20,25,50], 
                        suffix='_.xlsx')
        
    if backtest_runtype == "preload":

        P = open_portfolio(MASTER_PNL_FILENAME)
        PL = PortfolioLog(P)
        #PL.tradebook_filename = RESULT_FILEPATH + "/consistency/Argus_sample_with_mybacktest_newcode/Argus_sample_PNL_with_mybacktest_newcode.csv"
        #PL.tradebook_filename = RESULT_FILEPATH + "/consistency/live_trade_vs_backtest_newcode/live_trade_compare_pnl_TP25SL10_normalopen.csv"
        #PL.tradebook_filename = RESULT_FILEPATH + "/EC_benchmark/20240814_argusexact_cross_P25S35_0330_entry_PNL_full.csv"
        #PL.tradebook_filename = RESULT_FILEPATH + "/ArgusTailStrangle/20240814_argutailstrangle_cross_TE45SL35_0330_entry_PNL_full.csv"
        PL.tradebook_filename = RESULT_FILEPATH + "/ArgusIQRSKW/20240814_argusIQRSKW_cross_WIQR38WSKW10_TETPOBOSSL45_0330_entry_PNL_full.csv"
        
        PL.render_tradebook()
        PL.render_tradebook_xlsx()
        
    if plot_PNL_or_not: 	pass
     

if __name__ == "__main__":
    #start_date = "2022-01-05"
    #end_date = "2022-01-19"
    
    # Argus test date range
    #start_date = "2022-01-05"
    #end_date = "2024-06-28"
    
    # Total date range
    start_date = "2021-01-11"
    end_date = "2024-08-14"
    
    # live trade test date range
    #start_date = "2025-02-19"
    #end_date = "2025-02-18"
    
    #end_date = "2025-02-25"
    #start_date = "2025-01-13"

    run_main('argus_exact', 
             OneTradePerDay, #OneTradePerDay, #onetrade_simple, #BiDirectionalTrade, 
             start_date, end_date,        
             buy_range = (0.4,0.6,0.05),
             sell_range =(0.6,0.4,0.95),
             #buy_range = ([0.25,0.4],[0.8,0.75],0.05),
             #sell_range = ([0.6,0.75],[0.25,0.2],0.95), 
             give_obj_name = 'USD',
             get_obj_quantity = 1,
             preprocess = False, 
             signal_gen_runtype='preload',
             backtest_runtype = "preload")
    ## Visualise PNL plot and metrics.
    ##run_PNL
    #cumPNL_plot()
