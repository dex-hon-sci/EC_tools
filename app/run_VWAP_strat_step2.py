#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 26 13:06:00 2025

@author: dexter

# New Backtest
# Save in object format, make function to redner it to 
# Signal_generation: def: use strategy, generate signals 
# Signal contains precise execution instructions (MKT: time, LMT:price, Dynamic) 
# Backtest use Trade method to calculate the correct entry/exit point (class attr)
# Trade method also add the correct exeuciton record to the Portfolio object

# input config, Define data (Signal list, historical price) input 
#####
# Backtest type

# Independent: process backtest by signals in a list intead of time
# Concurrent: process backtest by time instead of signal

# LMT order calculation method (RANGE VS CROSSOVER)
# OneActive Signal vs MultActive Signals per asset
#########
# Define Backtest, 
# loop start, define time increment (by signal or by fixed time)
# Look for Signal Segementation (isolate segment to calculate trade return)

# Indepednet:
# 0) Find active signal in a day (basetime setting)
# 1) Group signals by start_time
# 2) Extract intraday_minute_data (based on the ACTIVE signal of that asset)
# 3) Use Trade method, calculate correct entry/exit points
# 3.1) For Dynamic SL, trade caclculation is predefined segment loop.
# 4) Use the exit_point of Trade method, check if the signal in siganl_list comes after it
# If not, pop it. (garbage_signals)

# Concurrent:
# Group all assets signals and price data by date (or any time interval)
# Process all signals simultaneously
# Run crossover point check, align all cross-over points of all asset in
# one sequence sorted by time.
# Process each cross-over point one-by-one and after each step, calculate if 
# there is any factor changes if the strategy relies on aggegrated feedbacks
"""

import pandas as pd
from EC_tools.portfolio import Portfolio

def backtest_engine(portfo: Portfolio,
                    signals: dict[str, pd.DataFrame],
                    histroy: dict[str, pd.DataFrame], 
                    **kwargs):
    # The main loop for backtesting
    return
# =============================================================================
# def loop_portfolio_preloaded_dSL(portfo: Portfolio, 
#                                  trade_method,
#                                  signal_table: pd.DataFrame, 
#                                  histroy_intraday_data_pkl: dict[str, pd.DataFrame], 
#                                  **kwargs):
#     # Loop through signal master table and execute trade in the intraday data
#     # Within this custom loop, there is another loop that go through a series of
#     # sections and calculate entry point and exit point individually.
#     default_kwargs = DEFAULT_KWARGS
#     kwargs = dict(default_kwargs,**kwargs)
# 
#     for i in range(len(signal_table)):
# 
#         # setup trade inputs ###########
#         item = signal_table.iloc[i]
#                 
#         symbol = item['Price_Code']
#         date_interest = item['Date']
#         get_obj_name = item['Price_Code']
# 
#         open_hr = kwargs['open_hr_dict'][symbol]
#         close_hr = kwargs['close_hr_dict'][symbol]
#         
#         histroy_intraday_data = histroy_intraday_data_pkl[symbol]
#         
#         day = backtest.extract_intraday_minute_data(histroy_intraday_data, 
#                                                     date_interest, 
#                                                     open_hr=open_hr, 
#                                                     close_hr=close_hr)
#         
#         open_hr_dt, open_price = read.find_closest_price(day,
#                                                          target_hr= open_hr,
#                                                          direction='forward')
#         
#         close_hr_dt, close_price = read.find_closest_price(day,
#                                                            target_hr= close_hr,
#                                                            direction='backward')
#             
#         # The time to open all positions
#         pos_open_dt = datetime.datetime.combine(date_interest.date(), open_hr_dt)
#         
#         print('===============================')
#         print(i, pos_open_dt, symbol)
#         #print('day', day)
#         #print('Time', day['Time'].iloc[0], type(day['Time'].iloc[0]))
#         # Target EES global (the initial targets)
#         global_target_entry = item['Entry_Price']
#         global_target_exit = item['Exit_Price']
#         global_stop_exit = item['StopLoss_Price']
# 
#         # Build up sections, the output is a dict containing the EES for each 
#         # section
#         sections = load_EES_from_signal_dynamic(item)
#         #print('sections', sections)
#         # Setup trade ##########
#         trade_id = i #direction + str(i)
#         direction = sections['0']['direction'][1]
#         # Make a list of SL for universal access
#         dyn_list = item[['StopLoss_Price_1', 'StopLoss_Price_2', 
#                          'StopLoss_Price_3','StopLoss_Price_4']].to_list()
# 
#         # Initialise trade 
#         T = trade_method(portfo, trade_id, 
#                          trail_price_delta=kwargs['trail_price_delta'], 
#                          direction=direction,
#                          cross_decision=kwargs['cross_decision'],
#                          dyn_list = dyn_list)
#         
#         # Setup the close hour exit point (remember to change the close_hr_dt 
#         # from time to datetime)
#         T._close_pt = (datetime.datetime.combine(date_interest, close_hr_dt), close_price)
#         
#         # Loop Through each section to find the suitable EES point, 
#         # Store them in the class variable in the Trade object
#         for num in sections:
#             # Isolate day_section from day data according to the time range
#             # of the EES
#             start_time = datetime.datetime.strptime(sections[num]['stop_exit'][0][0], 
#                                                     '%H:%M:%S').time()
#             end_time = datetime.datetime.strptime(sections[num]['stop_exit'][0][1], 
#                                                   '%H:%M:%S').time()
#             
#             day_section = day[(day['Time']>=start_time) & (day['Time']<=end_time)]
#             #print('day_section', day_section)
#             
#             if len(day_section) == 0:
#                 print('day_section is empty!')
#                 break
#             
#             # The EES for this section
#             target_entry = sections[num]['target_entry'][1]
#             target_exit = sections[num]['target_exit'][1]
#             stop_exit = sections[num]['stop_exit'][1]
#             
#             print_SL_price = T._dyn_list[int(num)]
#             
#             print(f'--------section {num}: {start_time} to {end_time}, "{direction}"--------')
#             print(f'TE: {target_entry}, TP: {target_exit}, SL: {print_SL_price}')
#             print('------------------------------------------------------')
# 
#             # set the open_hr to the time specific to this section
#             open_hr_dt, close_hr_dt = start_time, end_time
# 
#             # Generate truncation dictionary in this section of the day
#             trunc_dict, target_entry, \
#             target_exit, stop_exit = backtest.gen_trunc_dict(LoopType.CROSSOVER,
#                                                              day_section, 
#                                                              target_entry, 
#                                                              target_exit, 
#                                                              print_SL_price, 
#                                                              open_hr_dt, 
#                                                              close_hr_dt, 
#                                                              direction)
#             #print(trunc_dict)
#             
#             
#             # Choose the earliest EES for this section
#             T.choose_EES_values(trunc_dict, dyn_list, int(num),
#                                 trail_price_delta = TRAIL_PRICE_DELTA[symbol],
#                                 direction=direction)
#             print('------------------------------------------------------')
#         print('------------------------------------------------------')
# 
#         # Export the trade object defacto EES points
#         # A list of initial target prices for opening position, it will be 
#         # changed during execute_order based on EES_pt_list
#         EES_target_price_list = [global_target_entry, global_target_exit, 
#                                  global_stop_exit, close_price]
#         
#         # A list of final EES points
#         EES_pt_list = [T._TE_pt, T._TP_pt, T._SL_pt, T._close_pt]
#         
#         ORDER_TYPE = {'Buy': 'Long', 'Sell':'Short'}
#         #print('EES_target_list', EES_target_price_list)
#         print('EES_pt_list', EES_pt_list)
#         
#         # Open position and add them in the portfolio
#         pos_list = T.open_positions(kwargs['give_obj_name'], 
#                                     get_obj_name, 
#                                     kwargs['get_obj_quantity'],
#                                     EES_target_price_list, 
#                                     ORDER_TYPE[direction],
#                                     size=SIZE_DICT[get_obj_name],
#                                     fee=OIL_FUTURES_FEE, 
#                                     open_time = open_hr_dt)
#         #print('pos_list', pos_list)
#         print('------------------------------------------------------')
# 
#         # Execute and exit position in the portfolio
#         trade_open, trade_close, \
#         pos_list, exec_pos_list = T.execute_positions(EES_pt_list, 
#                                                       pos_list, 
#                                                       order_type = \
#                                                       ORDER_TYPE[direction])
#         
#         #print('pos_list', pos_list)
#         #print(exec_pos_list)
#         print('------------------------------------------------------')
# 
#         #backtest.plot_in_backtest(date_interest,get_obj_name, trunc_dict, direction, 
#         #                          plot_or_not=kwargs['plot_or_not'])
#                                                  
# 
#     return portfo
# =============================================================================
