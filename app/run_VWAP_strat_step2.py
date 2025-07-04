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
import copy

import pickle
import pandas as pd
import numpy as np

from EC_tools.portfolio import Portfolio, PortfolioLog
import EC_tools.utility as util
#from EC_tools.trade_2 import Trade

def load_source_data_bt(filenames_loc: list) -> dict:
    master_dict = {}
    for filename in filenames_loc:
        temp_dict = util.load_pkl(filename)
        master_dict = dict(master_dict, **temp_dict)
        
    return master_dict

def to_datetime(date64:np.datetime64):
    """
    Converts a numpy datetime64 object to a python datetime object 
    Input:
      date64 - a np.datetime64 object
    Output:
      DATE - a python datetime object
    """
    timestamp = ((date64 - np.datetime64('1970-01-01T00:00:00'))
                 / np.timedelta64(1, 's'))
    return datetime.datetime.utcfromtimestamp(timestamp)

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


import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

def plot_VWAP(df, title='', 
              upmakersx=[],upmakersy=[],
              downmakersx=[],downmakersy=[],
              artists=[],
              open_times =[],open_prices=[], 
              close_times=[], close_prices=[],
              txts = []):
    fig, axs = plt.subplots(1, 1, figsize=(10, 4), layout='constrained')
    fmt = mdates.DateFormatter("%H:%M:%S")

    axs.plot(df['Datetime'].to_list(), df['VWAP'].to_list(), 'o-', 
             color= 'grey', ms=1)
    axs.plot(df['Datetime'].to_list(), (df['VWAP']+1.28*df['VWAP_DEV']).to_list(), 
             '-', lw=1,color="#c5486a")
    axs.plot(df['Datetime'].to_list(), (df['VWAP']-1.28*df['VWAP_DEV']).to_list(), 
             '-', lw=1, color="#c5486a")
    axs.plot(df['Datetime'].to_list(), (df['VWAP']+2.01*df['VWAP_DEV']).to_list(), 
             '-', lw=1, color="#c5486a")
    axs.plot(df['Datetime'].to_list(), (df['VWAP']-2.01*df['VWAP_DEV']).to_list(), 
             '-', lw=1,color="#c5486a")
    axs.plot(df['Datetime'].to_list(), (df['VWAP']+2.51*df['VWAP_DEV']).to_list(), 
             '--', lw=1,color="#c5486a")
    axs.plot(df['Datetime'].to_list(), (df['VWAP']-2.51*df['VWAP_DEV']).to_list(), 
             '--', lw=1, color="#c5486a")
    axs.plot(df['Datetime'].to_list(), (df['VWAP']+3.09*df['VWAP_DEV']).to_list(), 
             '--', lw=1,color="#c5486a")
    axs.plot(df['Datetime'].to_list(), (df['VWAP']-3.09*df['VWAP_DEV']).to_list(), 
             '--', lw=1, color="#c5486a")
    axs.plot(df['Datetime'].to_list(), (df['VWAP']+4.01*df['VWAP_DEV']).to_list(), 
             '--', lw=1, color="#c5486a")
    axs.plot(df['Datetime'].to_list(), (df['VWAP']-4.01*df['VWAP_DEV']).to_list(), 
             '--', lw=1,color="#c5486a")
    
    # Plot raw OHLC data
    axs.plot(df['Datetime'].to_list(), df['Open'].to_list(), 'o-', 
             color='r',ms=1,lw=1)
    axs.plot(df['Datetime'].to_list(), df['Settle'].to_list(), 'o-', 
             color='b',ms=1,lw=1)
    axs.plot(df['Datetime'].to_list(), df['High'].to_list(), '-')
    axs.plot(df['Datetime'].to_list(), df['Low'].to_list(), '-')
    axs.fill_between(df['Datetime'].to_list(), df['Low'].to_list(), 
                     df['High'].to_list(), color='g',alpha=0.3)
    # draw boxes
    for art in artists:
        axs.add_patch(art)
        
    date_str = df['Datetime'].to_list()[0].strftime('%Y-%m-%d')
    
    # Add all the open and close pt to the plot
    for opentime, openprice, closetime, closeprice in \
        zip(open_times,open_prices, close_times, close_prices):
        
        entryexitpoints(axs, entry_time=opentime, 
                            exit_time=closetime, 
                            entry_price= openprice,
                            exit_price= closeprice)
    # Draw the PNL on the topleft of the 
    for x,y,z,colour in txts:
        axs.text(x,y+0.05,z,color=colour, fontsize =8, fontweight='bold', zorder =40)
        

    axs.plot(upmakersx, upmakersy,'+',color="green", ms=15)
    axs.plot(downmakersx, downmakersy,'_',color="green",ms=15)
    
    axs.xaxis.set_major_formatter(fmt)
    axs.grid()
    axs.set_title(title)
    axs.set_ylabel('Price')
    axs.set_xlabel('Time')
    #plt.legend()
    plt.show()
    #plt.savefig(RESULT_FILEPATH+f"/VWAP_Inversion/plot_PNL/VWAP_{date_str}.png", 
    #            dpi=150)


class Trade(object):
    def __init__(self):
        #self.open_pt = (np.nan,np.nan)
        #self.close_pt = (np.nan,np.nan)
        pass
    
from EC_tools.strategy_2.signal import SignalStatus, Signal, SignalType
from EC_tools.order.cqg_enums import OrderType
from EC_tools.order.cqg_order import CQGOrder
from EC_tools.order.enums import OrderSideExtend
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
                
                hit_times = list(time_list[hit_cand['all'][0]])
                hit_prices = list(price_list[hit_cand['all'][0]])
                #print("LMT hittime", hit_times)
                # Convert numpy datetime64 to datetime
                hit_times = [to_datetime(dt64) for dt64 in hit_times]

                # Select for the earliest one that is after the open.
                hit_pts = [(time, price) for time, price in zip(hit_times, hit_prices)]
                print("LMT order, hit_pts", hit_pts)

        return hit_pts
        
    def choose_hit_pts(self)->list: # WIP
        print('----choose_hit_pts------')
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
                open_orders += [action]*len(ht_pts)
                
                assert len(open_hit_pts) == len(open_orders)

            elif action.close_:
                seek_direction = 'backward'
                ht_pts = self.find_hit_pts(action, 
                                           MKT_seek_direction = seek_direction)
                close_hit_pts += ht_pts
                close_orders += [action]*len(ht_pts)
                print("length", len(close_hit_pts) , len(close_orders))
                assert len(close_hit_pts) == len(close_orders)
        print('==========================')

        print("open_hit_pts", open_hit_pts)
        print("open_orders", open_orders)
        # Find open_pt and open_order. Choose the Earliest one
        open_dt_list = [dt for dt,_ in open_hit_pts]
        min_open_val = open_dt_list[0] # First guess
        min_open_index = 0
        for i in range(len(open_dt_list)):
            if open_dt_list[i] < min_open_val:
                min_open_val = open_dt_list[i]
                min_open_index = i
        # Save the open_pt and open_order
        self.open_pt = open_hit_pts[min_open_index]
        self.open_order = open_orders[min_open_index]
        print('Defacto open', self.open_pt, self.open_order)
        print('--------------')
        print("close_hit_pts", close_hit_pts)
        print("close_orders", close_orders)

        # Find close_pt and close_order. Choose the Earliest one that comes
        # after the de facto open_pt
        close_dt_list = [dt for dt,_ in close_hit_pts]
        min_close_val = close_dt_list[0] # First guess
        min_close_index = 0
        #print("close_dt_list!!", close_dt_list)
        for i in range(len(close_dt_list)):
            if close_dt_list[i] < min_close_val and self.open_pt[0]< close_dt_list[i]:
                min_close_val = close_dt_list[i]
                min_close_index = i
        self.close_pt = close_hit_pts[min_close_index]
        self.close_order = close_orders[min_close_index]
        print('Defacto close',self.close_pt, self.close_order)
        print('==========================')
    
    def open_positions(self):
        # Add Order (BT format) to class attribute
        # convert2BTorder() here
        # 
        MKT_price_open, MKT_price_close = np.nan , np.nan
        if self.open_order.type_ == OrderType.ORDER_TYPE_MKT:
            MKT_price_open = self.open_pt[1]
        # Convert De facto open_order to Backtest order format
        self.open_order = convert2BTorder(self.open_order, 'future', 
                                          MKT_price = MKT_price_open)
        
        if self.close_order.type_ == OrderType.ORDER_TYPE_MKT:
            MKT_price_close = self.close_pt[1]
        # Convert De facto close_order to Backtest order format
        self.close_order = convert2BTorder(self.close_order, 'future', 
                                          MKT_price = MKT_price_close)
        # Add the same trade_id to the open and close orders
        self.open_order.order_id = self.trade_id
        self.close_order.order_id = self.trade_id
        print("BTORDER_OPEN", self.open_order)
        print("BTORDER_CLOSE", self.close_order)
        return 
    
    def execute_positions(self):
        
        long_cond = (self.open_order.order_type == OrderSideExtend.LONG_BUY)\
                and (self.close_order.order_type == OrderSideExtend.LONG_SELL)
        short_cond = (self.open_order.order_type == OrderSideExtend.SHORT_BORROW)\
                 and (self.close_order.order_type == OrderSideExtend.SHORT_BUYBACK)

        if long_cond:
            order_type1 = 'Long-Buy' #OrderSideExtend.LONG_BUY
            order_type2 = 'Long-Sell' #OrderSideExtend.LONG_SELL

        elif short_cond:
            order_type1 = 'Short-Borrow' #OrderSideExtend.SHORT_BORROW
            order_type2 = 'Short-Buyback' #OrderSideExtend.SHORT_BUYBACK
            
        self.open_order.price = self.open_pt[1]
        self.close_order.price = round(self.close_pt[1],9)
        print('----------------------------')
        print('open_pt', self.open_pt, 'close_pt', self.close_pt)
        # Put the orders in the portfolio
        self.open_order.portfolio =self.portfolio
        self.close_order.portfolio =self.portfolio
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
        print('---------After Order Execution------')
        print('open_order', self.open_order.status, self.open_order.fill_time)
        print('close_order',self.close_order.status, self.close_order.fill_time)
        
        # Store order to order_pool
        self.portfolio._order_pool.append(copy.copy(self.open_order))
        self.portfolio._order_pool.append(copy.copy(self.close_order))
        
    def run_trade(self):
        
        # Go through the actions list        
        self.choose_hit_pts()
        
        self.open_positions()
        
        # Execute only the open_order and close_order 
        self.execute_positions()
        
        print("---Trde Done, Check Portfolio-----")
        #print(self.portfolio.pool)
        
        #return self.portfolio
    
def activate_signal(signal, latest_datetime):
    print('------------------------------------------')
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
    
    active_signals = pd.DataFrame()

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
            # For plot_check
            active_signal_row ={'Datetime':signal.start_time,'signal':signal}
            
            print(f"======{active_signal_row}======")
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
            
            active_signals = pd.concat([active_signals, 
                                        pd.DataFrame([active_signal_row])])
        
    return portfo, active_signals


def entryexitpoints(ax, 
                    entry_time: datetime.datetime = datetime.datetime.today(), 
                    exit_time: datetime.datetime = datetime.datetime.today(), 
                    entry_price: float =  86.05,
                    exit_price: float = 85.70):
    
    print(entry_time, entry_price)
    print(exit_time, exit_price)
    ax.scatter(entry_time, entry_price, s=80, facecolors='none', 
               edgecolors='b', zorder=50)
    ax.plot(entry_time, entry_price, 'x', ms=16, c='blue', zorder=50, 
            label = 'Entry_Point')

    ax.scatter(exit_time, exit_price, s=80, facecolors='none', 
               edgecolors='g', zorder=50)
    ax.plot(exit_time, exit_price, 'x', ms=16, c='green', zorder=50,
            label = 'Exit_Point')
    
def add_text(ax, x, y, s, fontsize=8, color ='g'):
    ax.text(x, y, s, )
    return 

def plot_check(history_data, signals_df, PNL_df):
    DT = PNL_df['Entry_Datetime'].to_list()
    DT = [datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S") 
                    for date_str in DT]
    PNL_df['Datetime'] = DT

    
    unique_dates = list(set([datetime.datetime.combine(dt.date(),
                        datetime.time(0,0,0)) for dt in DT]))
    print(unique_dates)

    # Loop everyday in the xlsx file
    for date in unique_dates:
        print(f"========={date}=========")
        start_dt = datetime.datetime.combine(date.date(), 
                                             datetime.time(hour =3, minute=30))
        end_dt = datetime.datetime.combine(date.date(), 
                                           datetime.time(hour =19, minute=59))
        
        # Isolate the day for plot
        sub_history_data = history_data[(history_data['Datetime'] >=start_dt) &
                                        (history_data['Datetime'] <=end_dt)]
        
        # Isolate the Signals of this day
        sub_signals_df = signals_df[(signals_df['Datetime']>=start_dt)&
                                    (signals_df['Datetime']<=end_dt)]
        sub_signals = sub_signals_df['signal'].to_list()\

        # Draw signal range Box ()
        artists, topleft_coord= [], []
        for S in sub_signals:
            print(S.start_time, S.type_)
            time_width = S.end_time-S.start_time
            price_width = S.actions[1].kwargs['LMT_price'] - S.actions[2].kwargs['LMT_price']
            print('price_width', price_width)
            box_origin_pt = (S.start_time, S.actions[2].kwargs['LMT_price'])
            
            openline_origin_pt = (S.start_time, S.actions[0].kwargs['MKT_price'])
            openprice_width = 0.01
            
            Long_colour, Short_colour = "cyan", "#e1b865"
            
            if S.type_ == SignalType.BUY:
                Edge_colour = Long_colour
            elif  S.type_ == SignalType.SELL:
                Edge_colour = Short_colour
                
            # Define top-left coordinate (for texts later)
            coord = (S.start_time, max(S.actions[1].kwargs['LMT_price'],
                                      S.actions[2].kwargs['LMT_price']))
            topleft_coord.append(coord)

            # Add signal effective range
            artists.append(mpatches.Rectangle(box_origin_pt, 
                                              time_width,  price_width,
                                              ec=Edge_colour, facecolor='None',lw=1.5,
                                              zorder =30))
            # Add open order line
            artists.append(mpatches.Rectangle(openline_origin_pt, 
                                              time_width,  openprice_width,
                                              ec=Edge_colour, facecolor='None', lw=1.5,
                                              zorder =30))


        # Isolate the Trades of this day
        sub_PNL_df = PNL_df[(PNL_df['Datetime'] >=start_dt)&
                            (PNL_df['Datetime'] <=end_dt)]
        
        # Get open and close points
        open_times = sub_PNL_df['Entry_Datetime'].to_list()
        open_times = [datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S") 
                      for date_str in open_times]
        close_times = sub_PNL_df['Exit_Datetime'].to_list()
        close_times = [datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S") 
                      for date_str in close_times]

        open_prices = sub_PNL_df['Entry_Price'].to_list()
        close_prices = sub_PNL_df['Exit_Price'].to_list()
        PNLs = sub_PNL_df['scaled returns from trades'].to_list()
        # Generate PNL text
        topleft_coord
        txt_list = []
        for (x, y), s in zip(topleft_coord, PNLs):
            if s > 0:
                colour = '#b0fe83'
            elif s<0:
                colour = '#fc7878'
            txt = (x,y, f'PNL: {round(s,1)}', colour)
            txt_list.append(txt)
            
        # Plotting
        plot_VWAP(sub_history_data,
                  title=f'{date.strftime("%Y-%m-%d")}', 
                  artists = artists,
                  open_times=open_times, open_prices=open_prices, 
                  close_times=close_times, close_prices=close_prices,
                  txts = txt_list)
    return 

def run_backtest(TradeMethod, signals, 
                 daily_minute_data_pkl, start_date, end_date, **kwargs):
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
        #print(histroy_data)
        # No resample, run the backtest in 1Min intervals
        histroy_data = histroy_data[(histroy_data['Datetime'] >=start_date) &
                                    (histroy_data['Datetime'] <=end_date)]
        
        signals = signals[(signals['signal_datetime'] >=start_date) &
                          (signals['signal_datetime'] <=end_date)]
        
        P1, active_signals = backtest_engine(TradeMethod, P1, signals, histroy_data)
                
        # Save the portfolio
        if kwargs['save_or_not']: # save pkl portfolio
            file = open(kwargs['master_pnl_filename'], 'wb')
            pickle.dump(P1, file)

    return P1,active_signals

if __name__ == "__main__":
    from crudeoil_future_const import DAILY_MINUTE_DATA_INDI_PKL, RESULT_FILEPATH

    #start_date = datetime.datetime(2024,10,4,0,0,0)
    #end_date = datetime.datetime(2024,10,10,23,59,59)
    start_date = "2021-01-01"
    end_date = "2021-01-06"

    #end_date = "2021-12-31"

    # Load signals
    Q = util.load_pkl(RESULT_FILEPATH+"/VWAP_Inversion/VWAP_Inversion_sigma_0_68_signal_CLc1_2021_TP1_5_SL3_full.pkl")
    MASTER_PNL_FILENAME = RESULT_FILEPATH + "/VWAP_Inversion/VWAP_Inversion_sigma_0_68_PNL_CLc1_2021_TP1_5_SL3.pkl"

    # run backtest
    P, AS = run_backtest(OneTradePerSeg, Q, DAILY_MINUTE_DATA_INDI_PKL, 
                    start_date, end_date,
                    master_pnl_filename = MASTER_PNL_FILENAME,
                    save_or_not = True)
    
    P = read.open_portfolio(MASTER_PNL_FILENAME)
    PL = PortfolioLog(P)
    PL.tradebook_filename = RESULT_FILEPATH + "/VWAP_Inversion/VWAP_Inversion_sigma_0_68_PNL_CLc1_2021_TP1_5_SL3.csv"
    
    PL.render_tradebook()
    PL.render_tradebook_xlsx()
    ################
    from app.run_VWAP_strat_step1 import add_VWAP2df, add_ATR

    EXCHANGE = {'CLc1': "NYSE",
                'CLc2': "NYSE",
                'HOc1': "NYSE",
                'HOc2': "NYSE",
                'RBc1': "NYSE",
                'RBc2': "NYSE",
                'QOc1': "ICE",
                'QOc2': "ICE",
                'QPc1': "ICE",
                'QPc2': "ICE",
                            }
    #Plot_check
    symbol = "CLc1"
    open_hr, close_hr = '0330','1959'
    XL_filename = RESULT_FILEPATH + "/VWAP_Inversion/VWAP_Inversion_sigma_0_68_PNL_CLc1_2021_TP1_5_SL3_.xlsx"
    
    XL_df = read.read_xl_file(XL_filename, sheet_name = symbol)

    # plot check
    HISTORY_MINUTE_PKL = load_source_data_bt([DAILY_MINUTE_DATA_INDI_PKL[symbol]])
    unique_dates = util.get_trading_date(datetime.datetime.strptime(start_date, "%Y-%m-%d"),
                                         datetime.datetime.strptime(end_date, "%Y-%m-%d"), 
                                         exchange=EXCHANGE[symbol])

    # reindexing with time
    history_data = reindex_dt(HISTORY_MINUTE_PKL[symbol])
    history_data = add_VWAP2df(history_data, unique_dates, open_hr, close_hr)
    history_data = add_ATR(history_data)

    plot_check(history_data, AS, XL_df)

