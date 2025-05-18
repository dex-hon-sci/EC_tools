#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May  8 19:37:02 2025

@author: dexter
"""
import os
import sys
sys.path.insert(0, '/home/dexter/Euler_Capital_codes/EC_tools/app/')

# Python imports
import datetime as datetime
import pandas as pd
# EC_tools imports

import EC_tools.base.read as read
import EC_tools.utility as util
from EC_tools.portfolio import Portfolio
from EC_tools.trade.order import OrderStatus
import EC_tools.backtest as backtest
from EC_tools.backtest import extract_intraday_minute_data, \
                              prepare_signal_interest, plot_in_backtest
from run_backtest_dSL import run_backtest_bulk, \
                                          OneTradePerDay_DYNSL,\
                                          load_EES_from_signal_dynamic

from crudeoil_future_const import DATA_FILEPATH, RESULT_FILEPATH,\
                                  DAILY_MINUTE_DATA_INDI_PKL,\
                                  WRONG_OPEN_HR_DICT, CLOSE_HR_DICT,\
                                  TRAIL_PRICE_DELTA, SIZE_DICT,\
                                  OIL_FUTURES_FEE
                                  

date_interest_no_entry_buy = "2023-12-29" # no entry test case (Buy) Done
date_interest_normal_exit_buy = "2021-04-01" #  normal exit case (Buy) Done
date_interest_stop_loss_buy = "2021-08-04" # stop loss test case (Buy) Done
date_interest_close_exit_buy = "2022-11-18" #  sell at close case (Buy) Done

date_interest_no_entry_sell = "2023-04-13" # no entry test case (Sell) Done
date_interest_normal_exit_sell = "2023-05-24" #  normal exit case (Sell) 
date_interest_stop_loss_sell = "2021-04-14" # stop loss test case (Sell) Done
date_interest_close_exit_sell = "2022-10-27" #  sell at close case (Sell) Done
           
MASTER_SIGNAL_FILENAME = RESULT_FILEPATH + "/test_results/test_master_signal_file.csv"
MASTER_PNL_FILENAME = RESULT_FILEPATH + "/test_results/test_pnl.csv"
HISTORY_MINUTE_PKL = util.load_pkl(DAILY_MINUTE_DATA_INDI_PKL['CLc1'])


DEFAULT_KWARGS= {'price_proxy':'Open',
                 'give_obj_name': 'USD',
                 'get_obj_quantity': 1,
                 'open_hr_dict': WRONG_OPEN_HR_DICT, 
                 'close_hr_dict': CLOSE_HR_DICT, 
                 'strategy_name': "Unamed Strategy",
                 'save_or_not': False,
                 'plot_or_not' : False,
                 'open_hr': '0000', # assume the whole duration of the trading day
                 'close_hr': '2359',
                 'master_signal_filename': 'master_signal.csv', 
                 'master_pnl_filename': 'master_pnl.csv',
                 'histroy_intraday_data_pkl': dict(),
                 'selected_directions': ["Buy", "Sell"],
                 'method': "preload",
                 'trail_price_delta':15,
                 'cross_decision':'SL_A'}

def setup_trade(date_interest, 
                EES: dict, # Initial EES
                dyn_df: pd.DataFrame, # Dyn_dict that contains dynSL and time 
                **kwargs):
    default_kwargs = DEFAULT_KWARGS
    kwargs = dict(default_kwargs,**kwargs)

    # Setup Portfolio
    P1 = Portfolio()
    # Use one day to test if the trade logic works
    USD_initial = {'name':"USD", 'quantity': 10_000_000, 'unit':"dollars", 
                   'asset_type':"Cash", 'misc':{}} # initial fund
    P1.add(USD_initial, datetime= datetime.datetime(2020,12,30))
    
    # Setup Trade
    symbol, get_obj_name = 'CLc1', 'CLc1'

    open_hr = kwargs['open_hr_dict'][symbol]
    close_hr = kwargs['close_hr_dict'][symbol]
    
    histroy_intraday_data = util.load_pkl(DAILY_MINUTE_DATA_INDI_PKL[symbol])[symbol]
    print('histroy_intraday_data', histroy_intraday_data)
    #kwargs['histroy_intraday_data_pkl'][symbol]
    
    day = backtest.extract_intraday_minute_data(histroy_intraday_data, 
                                                date_interest, 
                                                open_hr=open_hr, 
                                                close_hr=close_hr)
    
    open_hr_dt, open_price = read.find_closest_price(day,
                                                     target_hr= open_hr,
                                                     direction='forward')
    
    close_hr_dt, close_price = read.find_closest_price(day,
                                                       target_hr= close_hr,
                                                       direction='backward')
        
    # The time to open all positions
    pos_open_dt = datetime.datetime.combine(date_interest.date(), open_hr_dt)
    
    print('===============================')
    print(pos_open_dt, symbol)
    #print('day', day)
    #print('Time', day['Time'].iloc[0], type(day['Time'].iloc[0]))
    # Target EES global (the initial targets)
    global_target_entry = EES['Entry_Price']
    global_target_exit = EES['Exit_Price']
    global_stop_exit = EES['StopLoss_Price']

    # Build up sections, the output is a dict containing the EES for each 
    # section
    sections = load_EES_from_signal_dynamic(dyn_df.iloc[0])
    #print('sections', sections)
    # Setup trade ##########
    direction = sections['0']['direction'][1]
    # Make a list of SL for universal access
    dyn_list = dyn_df[['StopLoss_Price_1', 'StopLoss_Price_2',\
                       'StopLoss_Price_3','StopLoss_Price_4']].iloc[0].to_list()

    # Initialise trade 
    T = OneTradePerDay_DYNSL(P1, 1, 
                             trail_price_delta=kwargs['trail_price_delta'], 
                             direction=direction,
                             cross_decision=kwargs['cross_decision'],
                             dyn_list = dyn_list)
    
    # Setup the close hour exit point (remember to change the close_hr_dt 
    # from time to datetime)
    T._close_pt = (datetime.datetime.combine(date_interest, close_hr_dt), close_price)
    
    # Loop Through each section to find the suitable EES point, 
    # Store them in the class variable in the Trade object
    for num in sections:
        # Isolate day_section from day data according to the time range
        # of the EES
        start_time = datetime.datetime.strptime(sections[num]['stop_exit'][0][0], 
                                                '%H:%M:%S').time()
        end_time = datetime.datetime.strptime(sections[num]['stop_exit'][0][1], 
                                              '%H:%M:%S').time()
        
        day_section = day[(day['Time']>=start_time) & (day['Time']<=end_time)]
        #print('day_section', day_section)
        
        if len(day_section) == 0:
            print('day_section is empty!')
            break
        
        # The EES for this section
        target_entry = sections[num]['target_entry'][1]
        target_exit = sections[num]['target_exit'][1]
        stop_exit = sections[num]['stop_exit'][1]
        
        print(f'--------section {num}: {start_time} to {end_time}, "{direction}"--------')
        print(f'TE: {target_entry}, TP: {target_exit}, SL: {stop_exit}')
        print('------------------------------------------------------')

        # set the open_hr to the time specific to this section
        open_hr_dt, close_hr_dt = start_time, end_time

        # Generate truncation dictionary in this section of the day
        trunc_dict, target_entry, \
        target_exit, stop_exit = backtest.gen_trunc_dict(backtest.LoopType.CROSSOVER,
                                                         day_section, 
                                                         target_entry, 
                                                         target_exit, 
                                                         stop_exit, 
                                                         open_hr_dt, 
                                                         close_hr_dt, 
                                                         direction)
        #print(trunc_dict)
        
        
        # Choose the earliest EES for this section
        T.choose_EES_values(trunc_dict, dyn_list, int(num),
                            trail_price_delta = TRAIL_PRICE_DELTA[symbol],
                            direction=direction)
        print('------------------------------------------------------')
    print('------------------------------------------------------')

    # Export the trade object defacto EES points
    # A list of initial target prices for opening position, it will be 
    # changed during execute_order based on EES_pt_list
    EES_target_price_list = [global_target_entry, global_target_exit, 
                             global_stop_exit, close_price]
    
    # A list of final EES points
    EES_pt_list = [T._TE_pt, T._TP_pt, T._SL_pt, T._close_pt]
    
    ORDER_TYPE = {'Buy': 'Long', 'Sell':'Short'}
    #print('EES_target_list', EES_target_price_list)
    print('EES_pt_list', EES_pt_list)
    
    # Open position and add them in the portfolio
    pos_list = T.open_positions(kwargs['give_obj_name'], 
                                get_obj_name, 
                                kwargs['get_obj_quantity'],
                                EES_target_price_list, 
                                ORDER_TYPE[direction],
                                size=SIZE_DICT[get_obj_name],
                                fee=OIL_FUTURES_FEE, 
                                open_time = open_hr_dt)
    #print('pos_list', pos_list)
    print('------------------------------------------------------')

    # Execute and exit position in the portfolio
    trade_open, trade_close, \
    pos_list, exec_pos_list = T.execute_positions(EES_pt_list, 
                                                  pos_list, 
                                                  order_type = \
                                                  ORDER_TYPE[direction])
    
    #print('pos_list', pos_list)
    print('------------------------------------------------------')

    #backtest.plot_in_backtest(date_interest,get_obj_name, trunc_dict, direction, 
    #                          plot_or_not=kwargs['plot_or_not'])
                                             

    return P1
 
def test_onetradeperday_buy_normalexit(date_interest,
                                       cross_decision='SL_A')->None:
    date_interest = datetime.datetime.strptime(date_interest, '%Y-%m-%d')
    EES = {'Entry_Price':59.00685, 
           'Exit_Price':59.628044,
           'StopLoss_Price':57.346096}
    d ={'Direction': 'Buy',
        'Target_Entry_Price':59.00685,	
        'TE_start_time':'03:30:00','TE_end_time': '19:59:00',
        'Take_Profit_Price':59.628044,
        'TP_start_time':'03:30:00','TP_end_time':'19:59:00', 
        'StopLoss_Price_1':57.346096, 
        'StopLoss_Price_2':58.00, 
        'StopLoss_Price_3':58.50,
        'StopLoss_Price_4':58.20,
        'SL1_start_time':'03:30:00',	'SL1_end_time':'08:00:00',	
        'SL2_start_time':'08:00:00','SL2_end_time':'11:00:00', 
        'SL3_start_time':'11:00:00','SL3_end_time':'13:00:00',
        'SL4_start_time':'13:00:00','SL4_end_time':'19:59:00'}
    DYN_DF = pd.DataFrame([d])
    							
    P1 = setup_trade(date_interest,EES,DYN_DF, cross_decision)
    return P1

test_onetradeperday_buy_normalexit(date_interest_normal_exit_buy)