#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan  7 18:43:50 2025

@author: dexter
"""

from numba import jit
# Import EC_tools    
from EC_tools.read import render_PNL_xlsx, open_portfolio
import EC_tools.utility as util
from EC_tools.trade import OneTradePerDay, BiDirectionalTrade
from EC_tools.simple_trade import onetrade_simple
from EC_tools.backtest import LoopType
from EC_tools.portfolio import PortfolioMetrics, PortfolioLog, PortfolioLog

from app.run_preprocess import run_preprocess
from app.run_gen_MR_dir import MR_STRATEGIES_0, run_gen_signal_bulk
from app.run_backtest import run_backtest_bulk

from crudeoil_future_const import TEST_FILE_LOC, DAILY_DATA_PKL, \
                                  DAILY_MINUTE_DATA_PKL, DAILY_APC_PKL,\
                                  DAILY_OPENPRICE_PKL, MONTHLY_APC_PKL,\
                                  WEEKLY_30AVG_APC_PKL, DAILY_CUMAVG_MONTH_PKL,\
                                  MINUTE_CUMAVG_MONTH_PKL, TEST_FILE_PNL_LOC,\
                                  CLOSE_HR_DICT



@util.time_it
def load_source_data() -> tuple:
    #load the pkl 
    SIGNAL_PKL = util.load_pkl(DAILY_APC_PKL)
    HISTORY_DAILY_PKL = util.load_pkl(DAILY_DATA_PKL)
    HISTORY_MINUTE_PKL = util.load_pkl(DAILY_MINUTE_DATA_PKL)
    OPENPRICE_PKL = util.load_pkl(DAILY_OPENPRICE_PKL)

    SAVE_FILENAME_LOC = TEST_FILE_LOC #ARGUS_BENCHMARK_SIGNAL_FILE_LOC #TEST_FILE_LOC
    
    return SIGNAL_PKL, HISTORY_DAILY_PKL, HISTORY_MINUTE_PKL, OPENPRICE_PKL,\
           SAVE_FILENAME_LOC
           
def run_main(strategy_name, 
             trade_method,
             start_date: str, end_date: str,         
             buy_range: tuple = ([0.2,0.25],[0.75,0.8],0.05),
             sell_range: tuple = ([0.75,0.8],[0.2,0.25],0.95), 
             give_obj_name: str = 'USD',
             get_obj_quantity: int = 1,
             preprocess: bool = False, 
             runtype: str = "list",
             signal_gen_runtype: str = "preload",
             backtest_runtype: str = "preload",
             plot_PNL_or_not: bool = False, **kwarg):
    
    # the default is only one loop
    # it takes three sets of filename and parameters
        
    FILE_LOC = TEST_FILE_LOC
    FILE_PNL_LOC = TEST_FILE_PNL_LOC
        
    signal_filenames, portfolio_filenames, tradebook_filenames = [],[],[]
    
    for signal_filename, \
        portfolio_filename,\
        tradebook_filename in zip(signal_filenames, \
                                  portfolio_filenames, tradebook_filenames):
        
        print("=========Generating Buy/Sell Signals=======")
    
        #strategy_name = 'argus_exact_mode'
        strategy = MR_STRATEGIES_0[strategy_name]
       
        MASTER_SIGNAL_FILENAME = signal_filename
    
        
        run_gen_signal_bulk(strategy, FILE_LOC,
                            start_date, end_date,
                            buy_range = buy_range, 
                            sell_range = sell_range,
                            runtype = signal_gen_runtype,
                            master_signal_filename = MASTER_SIGNAL_FILENAME,
                            open_hr_dict = WRONG_OPEN_HR_DICT, 
                            close_hr_dict = CLOSE_HR_DICT, 
                            quantile= [0.05,0.1,0.25,0.4,0.5,0.6,0.75,0.9,0.95],
                            save_or_not=True,
                            merge_or_not=True)
        
        print("=========Running Back-Testing =============")
        
        MASTER_PNL_FILENAME = portfolio_filename
    
        run_backtest_bulk(trade_method, 
                          FILE_LOC, FILE_PNL_LOC, 
                          start_date, end_date, 
                          method = backtest_runtype, 
                          master_signal_filename = MASTER_SIGNAL_FILENAME,
                          master_pnl_filename=MASTER_PNL_FILENAME,
                          give_obj_name = give_obj_name,
                          get_obj_quantity = get_obj_quantity,
                          open_hr_dict = WRONG_OPEN_HR_DICT, 
                          close_hr_dict= CLOSE_HR_DICT,
                          save_or_not=True, 
                          merge_or_not=True,
                          loop_type= LoopType.CROSSOVER,
                          selected_directions = ["Buy", "Sell"])
        
        print("=========Running PNL EXCEL File =============")
        if backtest_runtype == 'list':
            render_PNL_xlsx([MASTER_PNL_FILENAME], 
                            number_contracts_list = [5,10,15,20,25,50], 
                            suffix='_.xlsx')
            
        if backtest_runtype == "preload":
    
            P = open_portfolio(MASTER_PNL_FILENAME)
            PL = PortfolioLog(P)
            PL.tradebook_filename = tradebook_filename
            PL.render_tradebook()
            PL.render_tradebook_xlsx()
            
        if plot_PNL_or_not: 	pass
    return
           
if __name__ == "__main__":
    
    start_date = "2021-01-11"
    end_date = "2024-08-14"
    
    run_main('argus_exact', 
             OneTradePerDay,  
             start_date, end_date,         
             buy_range = ([0.25,0.4],[0.65,0.95],0.3),
             sell_range = ([0.6,0.75],[0.05,0.35],0.7), 
             give_obj_name = 'USD',
             get_obj_quantity = 1,
             signal_gen_runtype='preload',
             backtest_runtype = "preload")