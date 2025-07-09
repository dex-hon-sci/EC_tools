#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul  3 18:55:04 2025

@author: dexter
"""
# Python imports
import datetime
import copy
# Python package imports
import pandas as pd
import numpy as np
# EC_tools imports
from EC_tools.trade_2 import Trade
from EC_tools.portfolio import Portfolio
from EC_tools.strategy_2.signal import SignalStatus, Signal
from EC_tools.order.cqg_enums import OrderType
from EC_tools.order.cqg_order import CQGOrder
from EC_tools.order.enums import OrderSideExtend
from EC_tools.order.order import ExecuteOrder
from EC_tools.order.convert2BTorder import convert2BTorder
import EC_tools.base.read as read
import EC_tools.utility as util

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
                hit_pts = [read.find_closest_price_dt(self.history_data,
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
                hit_times = [util.to_datetime(dt64) for dt64 in hit_times]

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
                
        if not len(open_hit_pts)> 0:
            trade_exist= False
            return trade_exist
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
        trade_exist = True
        return trade_exist
    
    def open_positions(self):
        # Add Order (BT format) to class attribute
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
        strade_exist = self.choose_hit_pts()
        
        if strade_exist:
            self.open_positions()
        
            # Execute only the open_order and close_order 
            self.execute_positions()
        
            print("---Trde Done, Check Portfolio-----")
            #print(self.portfolio.pool)
        else:
            print("No open trades")
            
        #return self.portfolio
    