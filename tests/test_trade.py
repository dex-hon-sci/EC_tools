#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 29 16:50:39 2024

@author: dexter
"""

# make a Portfolio

from EC_tools.portfolio import Asset, Portfolio
from EC_tools.position import Position, ExecutePosition
from EC_tools.trade import Trade, trade_choice_simple
from EC_tools.backtest import extract_intraday_minute_data, find_minute_EES, \
                            prepare_signal_interest, plot_in_backtest
import EC_tools.read as read


FILENAME_MINUTE = "/home/dexter/Euler_Capital_codes/test_MS/data_zeroadjust_intradayportara_attempt1/intraday/1 Minute/CL.001"
FILENSME_BUYSELL_SIGNALS = "/home/dexter/Euler_Capital_codes/EC_tools/results/benchmark_signals/benchmark_signal_CLc1_full.csv"
SIGNAL_FILENAME = "/home/dexter/Euler_Capital_codes/EC_tools/data/APC_latest/APC_latest_CLc1.csv"   


def setup_test():
    return 

# test Buy case, 1) no trade, normal exit, stop loss, close case
# test Sell case, 1) no trade, normal exit, stop loss, close case

#date_interest = "2023-12-29" # no entry test case (Buy) Done
#date_interest = "2023-12-06" # stop loss test case (Buy) Done
#date_interest = "2021-03-17" #  sell at close case (Buy) Done
#date_interest = "2021-04-01" #  normal exit case (Buy) 

def test_trade_choice_simple_portfolio_buy_normalexit()->None:
    # Setting up the trade itself. First load the parameters
    direction = 'Buy'
    open_hr, close_hr = '0330', '2000'
    #date_interest = "2023-12-29" # no entry test case (Buy) Done
    #date_interest = "2023-12-06" # stop loss test case (Buy) Done
    #date_interest = "2021-03-17" #  sell at close case (Buy) Done
    date_interest = "2021-04-01" #  normal exit case (Buy) 
    
    # Use one day to test if the trade logic works
    P1 = Portfolio()
    USD_initial = Asset("USD", 1000000, "dollars", "Cash") # initial fund
    P1.add(USD_initial)
    
    histroy_intraday_data = read.read_reformat_Portara_minute_data(FILENAME_MINUTE)
    signal_table = prepare_signal_interest(FILENSME_BUYSELL_SIGNALS, trim = False)
    
    
    day = extract_intraday_minute_data(histroy_intraday_data, date_interest, 
                                 open_hr=open_hr, close_hr=close_hr)
    signal_table = signal_table[signal_table['APC forecast period'] == date_interest] 
    
    print(signal_table)
    
    
    target_entry, target_exit, stop_exit = float(signal_table['target entry'].iloc[0]), \
                                            float(signal_table['target exit'].iloc[0]), \
                                            float(signal_table['stop exit'].iloc[0])
    
    print(day['Date'].iloc[0], direction, target_entry, target_exit, stop_exit)
    
    open_hr_dt, open_price = read.find_closest_price(day,
                                                       target_hr= open_hr,
                                                       direction='forward')
    
    print('open',open_hr_dt, open_price)
    
    close_hr_dt, close_price = read.find_closest_price(day,
                                                       target_hr= close_hr,
                                                       direction='backward')
    print('close', close_hr_dt, close_price)

    
# =============================================================================
# 
#     if direction == "Buy":
#         give_obj_str_dict = {'name':"USD", 'unit':'dollars', 'type':'Cash'}
#         get_obj_str_dict = {'name':"CLc1", 'unit':'contracts', 'type':'Future'}
#         
#     elif direction == "Sell":
# 
#         give_obj_str_dict = {'name':"CLc1", 'unit':'contracts', 'type':'Future'}
#         get_obj_str_dict = {'name':"USD", 'unit':'dollars', 'type':'Cash'}
#         
# =============================================================================
    give_obj_name = "USD"
    get_obj_name = "CLc1"
    
    EES_dict, trade_open, trade_close, pos_list, exec_pos_list =\
                                Trade(P1).run_one_trade_per_day_portfolio( day, 
                                                                  give_obj_name, get_obj_name, 
                                                                  50,
                                                                  target_entry, target_exit, stop_exit,
                                                                  open_hr="0300", close_hr="2000", 
                                                                  direction = "Buy")
    
    plot_in_backtest(date_interest, EES_dict, direction, plot_or_not=False)

    print(P1.pool)

    print(P1.master_table)
    
  #  assert 
    print(pos_list[0].status, pos_list[1].status, pos_list[2].status, pos_list[3].status)
    print(exec_pos_list[0].status, exec_pos_list[1].status)
    print(pos_list, exec_pos_list)
#    print(P1.log)

test_trade_choice_simple_portfolio_buy_normalexit()
