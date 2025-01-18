#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan  7 18:43:50 2025

@author: dexter
"""
import datetime
from pathlib import Path
import numpy as np
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
                                  OPEN_HR_DICT, CLOSE_HR_DICT, RESULT_FILEPATH,\
                                  SYMBOL_LIST, WRONG_OPEN_HR_DICT
                                  
from main import run_main


@util.time_it
def load_source_data() -> tuple:
    #load the pkl 
    SIGNAL_PKL = util.load_pkl(DAILY_APC_PKL)
    HISTORY_DAILY_PKL = util.load_pkl(DAILY_DATA_PKL)
    HISTORY_MINUTE_PKL = util.load_pkl(DAILY_MINUTE_DATA_PKL)
    OPENPRICE_PKL = util.load_pkl(DAILY_OPENPRICE_PKL)
    
    return SIGNAL_PKL, HISTORY_DAILY_PKL, HISTORY_MINUTE_PKL, OPENPRICE_PKL
        
import builtins
          
def make_path_list(folder_name: str = '', 
                   file_prefix: str | list[str] = '', 
                   file_suffix: str | list[str] = '.csv',  
                   path: str = RESULT_FILEPATH,
                   syms: list[str] = SYMBOL_LIST) -> list[str]: # tested
    
    match type(file_prefix):
        case builtins.list: 
            if len(file_prefix) != len(syms): 
                raise Exception("file_prefix must match the \
                                dimension of syms if it is a list")
            else: pass
        
        case builtins.str:
            file_prefix_ele = file_prefix
            file_prefix = [file_prefix_ele for ele in range(len(syms))]
            
    match type(file_suffix):
        case builtins.list:
            if len(file_suffix) != len(file_prefix): 
                raise Exception("file_suffix must match the \
                                dimension of syms if it is a list")
            else: pass
        case builtins.str:
            file_suffix_ele = file_suffix
            file_suffix = [file_suffix_ele for ele in range(len(syms))]            
        
    
    bucket = list()
    for i, sym in enumerate(syms): 
        file_path = Path(path) / folder_name 
        bucket.append(str(file_path / str(file_prefix[i] + sym + file_suffix[i])))
    return bucket
           

def build_filename_matrix(x_axis_list: list[str], 
                          y_axis_list: list[str],
                          folder_name: str = 'heatmap', 
                          file_prefix: str = 'PNL_argusexact_',
                          file_suffix: str = '_.xlsx'):
    master_list = []
    for i in range(len(y_axis_list)):
        temp = [ele + y_axis_list[i] for ele in x_axis_list]
        #print(temp)
        Q = make_path_list(folder_name = folder_name, 
                           file_prefix=file_prefix,
                           file_suffix=file_suffix, 
                           syms=temp)
        master_list.append(Q)
    
    
    filename_matrix = np.array(master_list)
    #print(filename_matrix)
    return filename_matrix

    
def make_timedict_inputs(initial_dict: dict, steps: int = 5, 
                         time_delta: int = 30, 
                         direction: str = 'negative') -> list:
    
    master_dict = dict()
    syms = list(initial_dict.keys())
    for sym in syms:
        input_str = initial_dict[sym]
        
        master_list = []
        for i in range(steps):
            if direction == 'positive':
                new_data = datetime.datetime.strptime(input_str, "%H%M") +\
                           datetime.timedelta(minutes=time_delta*i)
            elif direction == 'negative':
                new_data = datetime.datetime.strptime(input_str, "%H%M") -\
                           datetime.timedelta(minutes=time_delta*i)
            else:
                raise Exception("Input must be either Positive or Negative")
            print(i,new_data)
            new_data_str = new_data.strftime('%H%M')
            master_list.append(new_data_str)
            
        master_dict[sym]=master_list
        
    # fracgmentation
    frag_list = [{sym: master_dict[sym][i] for sym in syms} for i in range(steps)]
    
    # return a matrix of dict with str in it
    return frag_list    

def build_para_matrix(x_axis_list: list, 
                      y_axis_list: list) -> np.array:
    master_list = []
    for i in range(len(y_axis_list)):
        temp = [(ele, y_axis_list[i]) for ele in x_axis_list]
        master_list.append(temp)
    para_matrix = np.array(master_list)
    return para_matrix

def run_seq_backtest(strategy_name, 
                     trade_method,
                     para_matrix,
                     signal_filename_matrix,
                     portfolio_filename_matrix,
                     tradebook_filename_matrix,
                     start_date: str, end_date: str,         
                     buy_range: tuple = ([0.2,0.25],[0.75,0.8],0.05),
                     sell_range: tuple = ([0.75,0.8],[0.2,0.25],0.95), 
                     **kwargs): # temp solution
    
    default_kwargs = {'give_obj_name':'USD',
                      'get_obj_quantity': 1,
                      'open_hr_dict': OPEN_HR_DICT, 
                      'close_hr_dict': CLOSE_HR_DICT, 
                      'preprocess': False, 
                      'signal_gen_runtype': "preload", 
                      'backtest_runtype': "preload", 
                      'plot_PNL_or_not':False}
    
    kwargs = dict(default_kwargs, **kwargs)
    
    # the default is only one loop
    # it takes three sets of filename and parameters
    FILE_LOC = TEST_FILE_LOC
    FILE_PNL_LOC = TEST_FILE_PNL_LOC
        
    parameters = para_matrix[4]

    signal_filenames = signal_filename_matrix[4]
    portfolio_filenames = portfolio_filename_matrix[4]
    tradebook_filenames = tradebook_filename_matrix[4]
     
    for parameter, signal_filename, portfolio_filename, tradebook_filename \
        in zip(parameters, signal_filenames, portfolio_filenames, \
               tradebook_filenames):
    
            
        print("=========Generating Buy/Sell Signals=======")
        # Run signal generations
        #strategy_name = 'argus_exact_mode'
        strategy = MR_STRATEGIES_0[strategy_name]
       
        MASTER_SIGNAL_FILENAME = signal_filename
    
        run_gen_signal_bulk(strategy, FILE_LOC,
                            start_date, end_date,
                            buy_range = buy_range, 
                            sell_range = sell_range,
                            runtype = kwargs['signal_gen_runtype'],
                            master_signal_filename = MASTER_SIGNAL_FILENAME,
                            open_hr_dict = parameter[0], #kwargs['open_hr_dict'], 
                            close_hr_dict = parameter[1], #kwargs['close_hr_dict'], 
                            quantile= [0.05,0.1,0.25,0.4,0.5,0.6,0.75,0.9,0.95],
                            save_or_not=True,
                            merge_or_not=True)
        
        print("=========Running Back-Testing =============")
        # Run Backtest
        MASTER_PNL_FILENAME = portfolio_filename
    
        run_backtest_bulk(trade_method, 
                          FILE_LOC, FILE_PNL_LOC, 
                          start_date, end_date, 
                          method = kwargs['backtest_runtype'], 
                          master_signal_filename = MASTER_SIGNAL_FILENAME,
                          master_pnl_filename=MASTER_PNL_FILENAME,
                          give_obj_name = kwargs['give_obj_name'],
                          get_obj_quantity = kwargs['get_obj_quantity'],
                          open_hr_dict = parameter[0], #kwargs['open_hr_dict'], 
                          close_hr_dict = parameter[1], #kwargs['close_hr_dict'], 
                          save_or_not=True, 
                          merge_or_not=True,
                          loop_type= LoopType.CROSSOVER,
                          selected_directions = ["Buy", "Sell"])
        
        print("=========Running PNL EXCEL File =============")
        # make tradebook files
        if kwargs['backtest_runtype'] == 'list':
            render_PNL_xlsx([MASTER_PNL_FILENAME], 
                            number_contracts_list = [5,10,15,20,25,50], 
                            suffix='_.xlsx')
            
        if kwargs['backtest_runtype'] == "preload":
    
            P = open_portfolio(MASTER_PNL_FILENAME)
            PL = PortfolioLog(P)
            PL.tradebook_filename = tradebook_filename
            PL.render_tradebook()
            PL.render_tradebook_xlsx()
            
        if kwargs['plot_PNL_or_not']: pass
    return None
           
if __name__ == "__main__":
    
    start_date = "2021-01-11"
    end_date = "2024-08-14"
    
    # make Open hour and Close hr dict


    
    openhr_str = ['Open0h0m','Open0h30m',
                  'Open1h0m','Open1h30m',
                  'Open2h0m']
    closehr_str = ['Close0h0m','Close0h30m',
                   'Close1h0m','Close1h30m',
                   'Close2h0m']
    #openhr_str = ['Open0h0m','Open0h15m','Open0h30m', 'Open0h45m',
    #              'Open1h0m', 'Open1h15m', 'Open1h30m','Open1h40m',
    #              'Open2h0m']
    #closehr_str = ['Close0h0m','Close0h15m','Close0h30m', 'Close0h45m', 
    #              'Close1h0m', 'Close1h15m', 'Close1h30m','Close1h45m',
    #               'Close2h0m']
    
    # Build filenames for signals
    signal_filename_matrix = build_filename_matrix(openhr_str, closehr_str,
                                                    folder_name='beyondmarketopen2',
                                                    file_prefix='20240813_argusexact_cross_TP25SL10_',
                                                    file_suffix='_signal.csv')
    portfolio_filename_matrix = build_filename_matrix(openhr_str, closehr_str,
                                                      folder_name='beyondmarketopen2',
                                                      file_prefix='20240813_argusexact_cross_TP25SL10_',
                                                      file_suffix='_PNL.pkl')
    tradebook_filename_matrix = build_filename_matrix(openhr_str, closehr_str,
                                                      folder_name='beyondmarketopen2',
                                                      file_prefix='20240813_argusexact_cross_TP25SL10_',
                                                      file_suffix='_PNL.csv')
    # make a list of inputs variations. In this case, it generate a list of 
    # Opening or closing hours with some given steps
    OPEN_HR_VAR = make_timedict_inputs(WRONG_OPEN_HR_DICT, steps=5, time_delta=30)
    CLOSE_HR_VAR = make_timedict_inputs(CLOSE_HR_DICT, steps=5, time_delta=30, 
                                        direction='positive')

    # Build the parameter matrixs for the simulation
    para_matrix = build_para_matrix(OPEN_HR_VAR, CLOSE_HR_VAR)
    
    
# =============================================================================
#     print('signal',signal_filename_matrix)
#     print('port',portfolio_filename_matrix)
#     print('tb',tradebook_filename_matrix)
#     print('para',para_matrix)
#     
# =============================================================================
    run_seq_backtest('argus_exact', 
             OneTradePerDay,
             para_matrix,
             signal_filename_matrix,
             portfolio_filename_matrix,
             tradebook_filename_matrix,
             start_date = start_date, 
             end_date = end_date,         
             buy_range =([0.2,0.4],[0.65,0.8],0.3),
             sell_range = ([0.6,0.8],[0.2,0.35],0.7))
    

