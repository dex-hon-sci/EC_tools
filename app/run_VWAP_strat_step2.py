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
import sys
sys.path.insert(0, "/home/dexter/Euler_Capital_codes/EC_tools")

import datetime

import pandas as pd
import numpy as np
from EC_tools.portfolio import Portfolio
import EC_tools.utility as util
#from EC_tools.trade_2 import Trade
def load_source_data_bt(filenames_loc: list) -> dict:
    master_dict = {}
    for filename in filenames_loc:
        temp_dict = util.load_pkl(filename)
        master_dict = dict(master_dict, **temp_dict)
        
    return master_dict

def reindex_dt(df:pd.DataFrame):
    # Add Datetime column into the dataframe
    date_series = [ele.date() for ele in df['Date'].to_list()]
    time_series = df['Time'].to_list()
    datetime_series = [datetime.datetime.combine(date,time) 
                       for date, time in zip(date_series, time_series)]
    
    df['Datetime'] = datetime_series
    df = df.set_index('Datetime')
    #df.reset_index(inplace=True)
    df['Datetime'] = df.index

    return df

def find_closest_price(history_data: pd.DataFrame, 
                       target_dt: datetime.datetime, 
                       direction: str ='forward', 
                       price_proxy: str = 'Open',
                       time_proxy: str = 'Datetime',
                       step: int = 1, 
                       search_time: int = 1000) -> \
                       tuple[datetime.datetime, float]:    
    # If the input is forward, the loop search forward a unit of minute (step)
    if direction == 'forward':
        step = 1.* step
    # If the input is backward, the loop search back a unit of minute (step)
    elif direction == 'backward':
        step = -1* step

    #initial estimation of the target price
    target_price = history_data[history_data[time_proxy] == target_dt][price_proxy]
    #loop through the next 30 minutes to find the opening price    
    for i in range(search_time):    
        if len(target_price) == 0:
            delta = datetime.timedelta(minutes = step)
            target_dt += delta

            target_price = history_data[history_data[time_proxy] == target_dt][price_proxy]
            #print('target_price', target_price)
    print('target_hr_after', target_dt)

    #print(day_minute_data[day_minute_data[time_proxy] == target_hr_dt])
    print('target_price', target_price)
    target_price = [float(target_price.iloc[0])] # make sure that this is float
            
    return target_dt, target_price[0]

class Trade(object):
    def __init__(self):
        #self.open_pt = (np.nan,np.nan)
        #self.close_pt = (np.nan,np.nan)
        pass
    
from EC_tools.strategy_2.signal import SignalStatus, Signal
from EC_tools.order.cqg_enums import OrderType
from EC_tools.order.cqg_order import CQGOrder
from EC_tools.order.order import ExecuteOrder
from EC_tools.order.convert2BTorder import convert2BTorder
import EC_tools.base.read as read

class OneTradePerSeg(Trade):
    # One trde per Segment
    def __init__(self, portfolio: Portfolio, 
                 signal: Signal,
                 history_data: pd.DataFrame,
                 trade_id:int):
        super().__init__()
        self.portfolio = portfolio
        self.signal = signal
        self.history_data = history_data
        self.trade_id = trade_id
        self.open_pt = (np.nan,np.nan)
        self.close_pt = (np.nan,np.nan)
        
        # Note taht the order here is the BT Order, not Signal Order
        self.open_order = None 
        self.close_order = None 
        # Check if the signal is active
        if signal.status is not SignalStatus.ACTIVE:
            raise Exception("The given signal is not active.")
        
    def find_hit_pts(self, action: CQGOrder, 
                     MKT_seek_direction='forward')->\
                     list[tuple[datetime.datetime| float]]:
        # A function that find the hit pts based on the order type
        # MKT order based on time, LMT order based on price
        match action.type_:
            case OrderType.ORDER_TYPE_MKT:
                # Find hit_pt based in MKT_time
                hit_pts = [find_closest_price(self.history_data,
                                            action.kwargs['MKT_time'],
                                            direction=MKT_seek_direction)]
                print("MKT order, hit_pts", hit_pts)
                
                
            case OrderType.ORDER_TYPE_LMT:
                
                price_proxy = 'Open'
                time_proxy = 'Datetime'
                price_list = self.history_data[price_proxy].to_numpy()
                time_list = self.history_data[time_proxy].to_numpy()
                
                target_price = action.kwargs['LMT_price']

                # Hit points candidates
                hit_cand = read.find_crossover(price_list, float(target_price))
                
                hit_times = time_list[hit_cand['all'][0]]
                hit_prices = price_list[hit_cand['all'][0]]
                   
                # Select for the earliest one that is after the open.
                hit_pts = [(time, price) for time, price in zip(hit_times, hit_prices)]
                print("LMT order, hit_pts", hit_pts)

        return hit_pts
        
    def choose_hit_pts(self)->list: # WIP
        # Get the list of hit pts
        # Go through the actions list
        open_hit_pts = [] # a list of points hit by the open orders
        close_hit_pts = [] # a list of points hit by the close orders
        open_orders = [] # a list of open orders matching open_hit_pts
        close_orders = [] # a list of open orders matching close_hit_pts

        # Extract hit pts for each order
        for i, action in enumerate(self.signal.actions):
            if action.open_:
                seek_direction = 'forward'
                
                ht_pts = self.find_hit_pts(action, 
                                           MKT_seek_direction = seek_direction)
                
                open_hit_pts += ht_pts
                open_orders += [action]*len(open_hit_pts)
                
            elif action.close_:
                seek_direction = 'backward'
                ht_pts = self.find_hit_pts(action, 
                                           MKT_seek_direction = seek_direction)
                close_hit_pts += ht_pts
                close_orders += [action]*len(open_hit_pts)
        print('==========================')

        print("open_hit_pts", open_hit_pts)
        print("open_orders", open_orders)
        # Find open_pt and open_order. Choose the Earliest one
        open_dt_list = [dt for dt,_ in open_hit_pts]
        min_val = open_dt_list[0] # First guess
        min_index = 0
        for i in range(len(open_dt_list)):
            if open_dt_list[i] < min_val:
                min_val = open_dt_list[i]
                min_index = i
        # Save the open_pt and open_order
        self.open_pt = open_hit_pts[min_index]
        self.open_order = open_orders[min_index]
        print('Defacto open', self.open_pt, self.open_order)
        print('--------------')
        print("close_hit_pts", close_hit_pts)
        print("close_orders", close_orders)

        # Find close_pt and close_order. Choose the Earliest one that comes
        # after the de facto open_pt
        close_dt_list = [dt for dt,_ in close_hit_pts]
        min_val = close_dt_list[0] # First guess
        min_index = 0
        for i in range(len(open_dt_list)):
            if open_dt_list[i] < min_val and self.open_pt[0]< open_dt_list[i]:
                min_val = open_dt_list[i]
                min_index = i
        self.close_pt = close_hit_pts[min_index]
        self.close_order = close_orders[min_index]
        print('Defacto close',self.close_pt, self.close_order)
        print('==========================')
    
    def open_positions(self):
        # Add Order (BT format) to class attribute
        # convert2BTorder() here
        self.open_order = convert2BTorder()
        return 
    
    def execute_positions(self, order_type: str = "Long"):
        

        if order_type == 'Long':
            order_type1 = 'Long-Buy' #OrderSideExtend.LONG_BUY
            order_type2 = 'Long-Sell' #OrderSideExtend.LONG_SELL

        elif order_type == 'Short':
            order_type1 = 'Short-Borrow' #OrderSideExtend.SHORT_BORROW
            order_type2 = 'Short-Buyback' #OrderSideExtend.SHORT_BUYBACK
            
        self.open_order.price = self.entry_pt[1]
        self.close_order.price = round(self.close_pt[1],9)

        #print('entry_pt[1]', entry_pt[1])
        #print('exit_pt[1]', exit_pt[1])
        #print('stop_pt[1]', stop_pt[1])
        #print('close_pt[1]', close_pt[1])
        #print("After price adjustment", opening_pos, closing_pos)

        # Execute the positions
        ExecuteOrder(self.open_order).fill_pos(fill_time = self.open_pt[0], 
                                              order_type=order_type1)
        
        ExecuteOrder(self.close_order).fill_pos(fill_time = self.close_pt[0], 
                                              order_type=order_type2)
        
    def run_trade(self):
        
        # Go through the actions list        
        self.choose_hit_pts()
        
        self.open_positions()
        
        # Execute only the open_order and close_order 

        #self.execute_positions()
        
        # Compare the time order of things
        
        return self.portfolio
    
def activate_signal(signal, latest_datetime):
    print("activate_signal func", signal.status, signal.start_time)
    print("latest_datetime", latest_datetime)
    print("signal.start_time > latest_datetime", signal.start_time > latest_datetime)
    if signal.status == SignalStatus.INACTIVE and\
       signal.start_time > latest_datetime:
           signal.status = SignalStatus.ACTIVE
    return signal

def backtest_engine(trade_method: Trade,
                    portfo: Portfolio,
                    signals: pd.DataFrame,
                    histroy_data: pd.DataFrame, 
                    **kwargs):
    # The main loop for backtesting

    signal_datetime = signals['signal_datetime'].to_list()
    signal_list = signals['signal'].to_list()
    # Loop through the signal list,  
    # Only test for the ACTIVE signals
    
    # Initiate latest_dateime
    latest_datetime = datetime.datetime(2020,12,31,0,0,0)
    
    # Loop through a list of time-ordered signals
    # This method assumes signals Independent backtest
    for i, signal in enumerate(signal_list):
        print("======================")
        print(i, signal.start_time, signal.type_)
        print('Open',signal.actions[0].kwargs)
        print('TP',signal.actions[1].kwargs)
        print('SL',signal.actions[2].kwargs)
        print('MCO',signal.actions[3].kwargs)
        print("======================")

        #### Signal activation Layer
        # First check and control if this is an active signal
        # Turn on ACTIVE signal if the signal start after 7:30 UTC for enough Volume. 
        if signal.start_time.time() > datetime.time(hour=7,minute=30):
            print("Signal comes after 7:30. Try to activate Signal.")
            # only turn on the signal if the last signal is already resolved
            signal = activate_signal(signal, latest_datetime) #Tested
            print(signal.status)

        #### Trading layer
        # Check if the signal is active
        if signal.status == SignalStatus.ACTIVE:
            
            # Segmentation: isolate price data segment
            seg_start_dt = signal.start_time
            seg_end_dt = signal.end_time
            print("seg_start_dt, seg_end_dt", seg_start_dt, seg_end_dt)
            sub_history_data = histroy_data[(histroy_data['Datetime']>=seg_start_dt) &
                                            (histroy_data['Datetime']<=seg_end_dt)]
            print(sub_history_data)
            # Run_trade
            T = trade_method(portfo, signal, sub_history_data, i)
            T.run_trade()

            # Update the latest_datetime based on the closing trade 
            # of the Trade object for this signal
            latest_datetime = T.close_pt[0]
        
    return portfo

def run_backtest(TradeMethod, signals, 
                 daily_minute_data_pkl, start_date, end_date):
    start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')

    # Run backtest control the range of datetime and signal selections
    # Initialise Portfolio
    P1 = Portfolio()
    USD_initial = {'name':"USD", 'quantity': 10_000_000, 'unit':"dollars", 
                   'asset_type': "Cash", 'misc':{}} # initial fund
    P1.add(USD_initial,datetime=datetime.datetime(2020,12,31))
    
    symbol_list = ['CLc1']
    for symbol in symbol_list:
        # Load Historical data
        HISTORY_MINUTE_PKL = load_source_data_bt([daily_minute_data_pkl[symbol]])
        # reindexing with time
        histroy_data = reindex_dt(HISTORY_MINUTE_PKL[symbol])
        print(histroy_data)
        # No resample, run the backtest in 1Min intervals
        histroy_data = histroy_data[(histroy_data['Datetime'] >=start_date) &
                                    (histroy_data['Datetime'] <=end_date)]
        
        signals = signals[(signals['signal_datetime'] >=start_date) &
                          (signals['signal_datetime'] <=end_date)]
        P1 = backtest_engine(TradeMethod, P1, signals, histroy_data)
    return P1

if __name__ == "__main__":
    from crudeoil_future_const import DAILY_MINUTE_DATA_INDI_PKL

    #start_date = datetime.datetime(2024,10,4,0,0,0)
    #end_date = datetime.datetime(2024,10,10,23,59,59)
    start_date = "2023-10-04"
    end_date = "2023-10-10"

    # Load signals
    Q = util.load_pkl("/home/dexter/Euler_Capital_codes/EC_tools/results/VWAP_Inversion/VWAP_Inversion_signal_CLc1_full.pkl")

    run_backtest(OneTradePerSeg, Q, DAILY_MINUTE_DATA_INDI_PKL, 
                 start_date, end_date)
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


