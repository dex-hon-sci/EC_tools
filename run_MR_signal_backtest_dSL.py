#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May  7 17:32:22 2025

@author: dexter
"""
import datetime 

from EC_tools.base.read import render_PNL_xlsx, open_portfolio
import EC_tools.utility as util
from EC_tools.trade import OneTradePerDay
#from EC_tools.simple_trade import onetrade_simple
from EC_tools.backtest import LoopType
from EC_tools.portfolio import PortfolioMetrics, PortfolioLog, PortfolioLog

# application import
from app.run_preprocess import run_preprocess
from app.run_gen_MR_dir_dSL import run_gen_signal_bulk
from app.run_gen_MR_dir import MR_STRATEGIES_0
from app.run_backtest_dSL import run_backtest_bulk, OneTradePerDay_DYNSL

from crudeoil_future_const import OPEN_HR_DICT, CLOSE_HR_DICT, SIZE_DICT, \
                                  WRONG_OPEN_HR_DICT,\
                                  DATA_FILEPATH, RESULT_FILEPATH,\
                                  TIMEZONE_DICT,\
                                  ARGUS_EXACT_SIGNAL_FILE_LOC, \
                                  TEST_FILE_LOC, TEST_FILE_PNL_LOC,\
                                  DAILY_MINUTE_DATA_PKL, MINUTE_CUMAVG_MONTH_PKL,\
                                  DAILY_MINUTE_DATA_INDI_PKL,\
                                  OIL_FUTURES_FEE, OIL_FUTURES_FEES
@util.time_it
def load_source_data_signal() -> tuple:
    #load the pkl 
    SIGNAL_PKL = util.load_pkl(DATA_FILEPATH+"/pkl_vault/crudeoil_future_APC_full.pkl")
    HISTORY_DAILY_PKL = util.load_pkl(DATA_FILEPATH+"/pkl_vault/crudeoil_future_daily_full.pkl")
    
    return SIGNAL_PKL, HISTORY_DAILY_PKL

@util.time_it
def load_source_data_bt(filenames_loc) -> dict:
    master_dict = {}
    for filename in filenames_loc:
        temp_dict = util.load_pkl(filename)
        master_dict = dict(master_dict, **temp_dict)
        
    return master_dict

def run_main(strategy_name, 
             trade_method,
             start_date: str, end_date: str,         
             buy_range: tuple = ([0.2,0.25],[0.75,0.8],0.05),
             sell_range: tuple = ([0.75,0.8],[0.2,0.25],0.95), 
             TE_time: tuple[datetime.time] = (), # A pair of datetime in a tuple
             TP_time: tuple[datetime.time] = (), # A pair of datetime in a tuple
             dSL_time: list[datetime.time] = [], # A list of pairs of datetime in a tuple
             dSL: list[float] = [], # A list of float in the form of quant distance from the entry
             give_obj_name: str = 'USD',
             get_obj_quantity: int = 1,
             preprocess: bool = False, 
             load: bool = True,
             signal_gen_runtype: str = "preload",
             backtest_runtype: str = "preload",
             plot_PNL_or_not: bool = False, **kwargs) -> None:
    
    default_kwargs = {'give_obj_name':'USD',
                      'get_obj_quantity': 1,
                      'open_hr_dict': OPEN_HR_DICT, 
                      'close_hr_dict': CLOSE_HR_DICT, 
                      'preprocess': False, 
                      'signal_gen_runtype': "preload", 
                      'backtest_runtype': "preload", 
                      'plot_PNL_or_not':False}
    
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
    strategy = MR_STRATEGIES_0[strategy_name]
    #SAVE_SIGNAL_FILENAME_LIST = list(FILE_LOC.values())
   
    #MASTER_SIGNAL_FILENAME = RESULT_FILEPATH + '/consistency/Argus_sample_with_mybacktest_newcode/Argus_sample_signals_2.csv'
    #MASTER_SIGNAL_FILENAME = RESULT_FILEPATH + '/consistency/live_trade_vs_backtest_newcode/live_trade_compare_signals_TP25SL10_normalopen.csv'
    #MASTER_SIGNAL_FILENAME = RESULT_FILEPATH + '/EC_benchmark/20240814_argusexact_cross_P25S35_0330_entry_signal_full.csv'
    MASTER_SIGNAL_FILENAME = RESULT_FILEPATH + '/test_results/test_master_signal_file.csv'
    
    run_gen_signal_bulk(strategy,
                        start_date, end_date,
                        buy_range = buy_range, 
                        sell_range = sell_range,
                        TE_time = TE_time, # A pair of datetime in a tuple
                        TP_time = TP_time, # A pair of datetime in a tuple
                        dSL_time = dSL_time, # A list of pairs of datetime in a tuple
                        dSL = dSL, # A list of float in the form of quant distance from the entry
                        runtype = signal_gen_runtype,
                        master_signal_filename = MASTER_SIGNAL_FILENAME,
                        open_hr_dict = WRONG_OPEN_HR_DICT, 
                        close_hr_dict = CLOSE_HR_DICT, 
                        save_or_not=True,
                        merge_or_not=True)
    

    print("=========Running Back-Testing =============")
    
    #MASTER_PNL_FILENAME = RESULT_FILEPATH + '/consistency/Argus_sample_with_mybacktest_newcode/Argus_sample_PNL_with_mybacktest_newcode.pkl' 
    #MASTER_PNL_FILENAME = RESULT_FILEPATH + '/consistency/live_trade_vs_backtest_newcode/live_trade_compare_portoflio_TP25SL10_normalopen.pkl' 
    #MASTER_PNL_FILENAME = RESULT_FILEPATH + '/EC_benchmark/20240814_argusexact_cross_P25S35_0330_entry_PNL_full.pkl'
    MASTER_PNL_FILENAME = RESULT_FILEPATH + '/test_results/test_master_pnl.pkl'
    
    #SAVE_PNL_FILENAME_LIST = FILE_PNL_LOC
    print("HISTORY_MINUTE_PKL", HISTORY_MINUTE_PKL)
    run_backtest_bulk(trade_method, 
                      #FILE_LOC, FILE_PNL_LOC, 
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
        PL.tradebook_filename = RESULT_FILEPATH + "/test_results/test_master_pnl.csv"
        
        PL.render_tradebook()
        PL.render_tradebook_xlsx()
        
    if plot_PNL_or_not: 	pass


if __name__ == "__main__":
    # Total date range
    start_date = "2021-01-19"
    end_date = "2021-01-21"
    
    TE_TIME = (datetime.time(3,30,0), datetime.time(16,0,0)) 
    TP_TIME = (datetime.time(3,30,0), datetime.time(23,0,0))
    # A list of pairs of datetime in a tuple
    dSL_TIME = [(datetime.time(3,30,0), datetime.time(8,0,0)),
                (datetime.time(8,0,0), datetime.time(11,0,0)),
                (datetime.time(11,0,0), datetime.time(13,0,0)),
                (datetime.time(13,0,0), datetime.time(23,0,0))] 
    # A list of float in the form of quant distance from the entry
    dSL = [0.0,0.05,0.1,0.25] 

    
    run_main('argus_exact', 
             OneTradePerDay_DYNSL, #OneTradePerDay, #onetrade_simple, #BiDirectionalTrade, 
             start_date, end_date,         
             buy_range = ([0.25,0.4],[0.65,0.75],0.05),
             sell_range = ([0.6,0.75],[0.25,0.35],0.95), 
             TE_time=TE_TIME,
             TP_time=TP_TIME,
             dSL_time=dSL_TIME,
             dSL = dSL,
             give_obj_name = 'USD',
             get_obj_quantity = 1,
             preprocess = False, 
             signal_gen_runtype='preload',
             backtest_runtype = "preload")