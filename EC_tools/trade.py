#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 10 00:16:28 2024

@author: dexter

A module that control trade action. The decision making logics are all stored 
here.
"""
import numpy as np
from dataclasses import dataclass
from typing import Protocol # use protocol for trade class

from EC_tools.position import Position, ExecutePosition
from EC_tools.portfolio import Asset
import EC_tools.read as read

ASSET_DICT = {"USD": {"unit":'dollars', "asset_type":'Cash'},
              "AUD": {"unit":'dollars',"asset_type":'Cash'},
              "CLc1": {"unit":'contracts',"asset_type":'Future'},
              "CLc2": {"unit":'contracts', "asset_type":'Future'},
              "HOc1": {"unit":'contracts',"asset_type":'Future'},
              "HOc2": {"unit":'contracts',"asset_type":'Future'},
              "RBc1":  {"unit":'contracts',"asset_type":'Future'},
              "RBc2":  {"unit":'contracts',"asset_type":'Future'},
              "QOc1":  {"unit":'contracts',"asset_type":'Future'},
              "QOc2":  {"unit":'contracts',"asset_type":'Future'},
              "QPc1":  {"unit":'contracts',"asset_type":'Future'},
              "QPc2":  {"unit":'contracts',"asset_type":'Future'},
              }


# there are two ways to backtest strategies, 
# (1) is to loop through every unit time interval and make a judgement call
# (2) is collapsing the intraday data into a smaller set of data, search for 
#the point of interest and execute the trade

def trade_choice_simple(EES_dict): 
    # LEGACY code before the development of trade and portfolio modules
    # a function that control which price to buy and sell
    # Trading choice should be a class on its own. This is just a prototype.
    # I need a whole module of classes related to trade. to operate on portfolio and so on
    
    # add the amount of exchange
    trade_open, trade_close = (np.nan,np.nan), (np.nan,np.nan)
    # Trade logic
    if len(EES_dict['entry']) == 0: # entry price not hit. No trade that day.
        pass
    else:
        # choose the entry point
        trade_open = EES_dict['entry'][0]
        if len(EES_dict['stop']) == 0: # if the stop loss wasn't hit
            pass
        else:
            trade_close = EES_dict['stop'][0] #set the trade close at stop loss
            
        if len(EES_dict['exit']) == 0:
            trade_close = EES_dict['close']
        else:
            # make sure the exit comes after the entry point
            for i, exit_cand in enumerate(EES_dict['exit']):  
                if exit_cand[0] > trade_open[0]:
                    trade_close = exit_cand
                    break
                else:
                    pass
                
    return trade_open, trade_close #(open_time, open_price) (close_time, close_price)

    
class Trade(object):

    def  __init__(self, portfolio=None):
        self.portfolio = portfolio
        self.position_book = []
        
    def add_position(self, give_obj_name, get_obj_name, get_obj_quantity, target_price):
        """
        A simple function that make the process of creating a position easier.
        It takes the name of the give_obj and get_obj, as well as the desired 
        quantity of get_obj and target price, to create the Asset objects and 
        Position object.

        The function automatically calculate how much give_obj you are going 
        to spend to purchase it. It assume you have enough within your portfolio.
        
        Parameters
        ----------
        give_obj_name : TYPE
            DESCRIPTION.
        get_obj_name : TYPE
            DESCRIPTION.
        get_obj_quantity : TYPE
            DESCRIPTION.
        target_price : TYPE
            DESCRIPTION.

        Returns
        -------
        pos : TYPE
            DESCRIPTION.

        """
        get_obj_unit = ASSET_DICT[get_obj_name]['unit']
        get_obj_type = ASSET_DICT[get_obj_name]['asset_type']
        
        give_obj_unit = ASSET_DICT[give_obj_name]['unit']
        give_obj_type = ASSET_DICT[give_obj_name]['asset_type']
        
        get_obj = Asset(get_obj_name, get_obj_quantity, 
                        get_obj_unit, get_obj_type)
        give_obj = Asset(give_obj_name, target_price*get_obj_quantity, 
                            give_obj_unit, give_obj_type)
        
        pos = Position(give_obj, get_obj, target_price, portfolio= self.portfolio)
        
        self.position_book.append(pos)
        return pos
    
    @staticmethod
    def find_pt_one_trade_per_day(EES_dict):
        """
        A method to find the appropiate EES values of the day.

        Parameters
        ----------
        EES_dict : TYPE
            DESCRIPTION.

        Returns
        -------
        entry_pt : TYPE
            DESCRIPTION.
        exit_pt : TYPE
            DESCRIPTION.
        stop_pt : TYPE
            DESCRIPTION.
        close_pt : TYPE
            DESCRIPTION.

        """
        # A method that search for correct EES points from a EES_dict
        
        #initialise
        entry_pt, exit_pt = (np.nan,np.nan), (np.nan,np.nan)
        stop_pt, close_pt = (np.nan,np.nan), (np.nan,np.nan)
        
        earliest_exit, earliest_stop = exit_pt, stop_pt
        
        # closr_pt always exist so we do it outside of the switch cases
        close_pt = EES_dict['close']

        # To get the correct EES and close time and price
        if len(EES_dict['entry']) == 0: # entry price not hit. No trade that day.
            pass
        else:
            # choose the entry point
            entry_pt = EES_dict['entry'][0]
            
            if len(EES_dict['exit']) > 0:
                # Find exit point candidates
                for i, exit_cand in enumerate(EES_dict['exit']):  
                    if exit_cand[0] > entry_pt[0]:
                        earliest_exit = exit_cand
                        print('earliest_exit', earliest_exit)
                        break

            if len(EES_dict['stop']) > 0:
                # Finde stop loss point candidates
                for i, stop_cand in enumerate(EES_dict['stop']):
                    if stop_cand[0] > entry_pt[0]:
                        earliest_stop = stop_cand
                        print('earliest_stop', earliest_stop)
                        break
            
            # put in the new exit and stop
            exit_pt = earliest_exit
            stop_pt = earliest_stop

        return entry_pt, exit_pt, stop_pt, close_pt
    
    
    def open_positions_one_trade_per_day(self, give_obj_name, get_obj_name, 
                              get_obj_quantity, EES_target_list, pos_type):
        # a method that execute the one trade per day based on the cases of the EES
        entry_price, exit_price = EES_target_list[0], EES_target_list[1]
        stop_price, close_price = EES_target_list[2], EES_target_list[3]
        
# =============================================================================
#         give_obj_name = give_obj_str_dict['name']
#         give_obj_unit = give_obj_str_dict['unit']
#         give_obj_type = give_obj_str_dict['type']
#         
#         get_obj_name = get_obj_str_dict['name']
#         get_obj_unit = get_obj_str_dict['unit']
#         get_obj_type = get_obj_str_dict['type']
# =============================================================================

        #### Collapse all these into an add_position function
        # Make positions for initial price estimation
        print('==entry==')
        entry_pos = self.add_position(give_obj_name, get_obj_name, 
                                      get_obj_quantity, entry_price)
# =============================================================================
#         
#         get_obj_entry = Asset(get_obj_name, get_obj_quantity, get_obj_unit, get_obj_type)
#         give_obj_entry = Asset(give_obj_name, entry_price*get_obj_quantity, 
#                             give_obj_unit, give_obj_type)
# 
#         print('amount',entry_price, get_obj_quantity,get_obj_quantity*entry_price)
#         print('entry_price', give_obj_entry.quantity/get_obj_entry.quantity, entry_price)
# 
#         entry_pos = Position(give_obj_entry, get_obj_entry, entry_price,
#                                                  portfolio= self.portfolio)
# =============================================================================
        print('==exit==')
        exit_pos = self.add_position(get_obj_name, give_obj_name, 
                          get_obj_quantity*exit_price, 1.0/exit_price)

# =============================================================================
#         get_obj_exit = Asset(get_obj_name, get_obj_quantity, 
#                              get_obj_unit, get_obj_type)
#         give_obj_exit= Asset(give_obj_name, get_obj_quantity*exit_price, 
#                             give_obj_unit, give_obj_type)
#         
#         exit_pos = Position(get_obj_exit, give_obj_exit, 1.0/exit_price, 
#                                                     portfolio= self.portfolio) 
#         
#         print('amount', exit_price, get_obj_quantity,get_obj_quantity*exit_price)
#         print('exit_price', give_obj_exit.quantity/get_obj_exit.quantity, exit_price)
#         print('quantity', get_obj_exit.quantity, give_obj_exit.quantity)
# =============================================================================

        print('==stop==', get_obj_quantity)
        stop_pos = self.add_position(get_obj_name, give_obj_name, 
                          get_obj_quantity*stop_price, 1.0/stop_price)
        
# =============================================================================
#         get_obj_stop = Asset(get_obj_name, get_obj_quantity,
#                              get_obj_unit, get_obj_type)
#         give_obj_stop = Asset(give_obj_name, get_obj_quantity*stop_price, 
#                             give_obj_unit, give_obj_type)
#         
#         stop_pos = Position(get_obj_stop, give_obj_stop, 1.0/stop_price, 
#                                                     portfolio= self.portfolio)
#         
#         print('amount', stop_price, get_obj_quantity,get_obj_quantity*stop_price)
#         print('stop_price', give_obj_stop.quantity/get_obj_stop.quantity, stop_price)
#         print('quantity', get_obj_stop.quantity, give_obj_stop.quantity)
#         
# =============================================================================
        print('==close==')
        close_pos = self.add_position(get_obj_name, give_obj_name, 
                          get_obj_quantity*close_price, 1.0/close_price)
        
# =============================================================================
#         get_obj_close = Asset(get_obj_name, get_obj_quantity,
#                               get_obj_unit, get_obj_type)
#         give_obj_close = Asset(give_obj_name, get_obj_quantity*close_price, 
#                             give_obj_unit, give_obj_type)
#         
#         close_pos = Position(get_obj_close, give_obj_close, 1.0/close_price, 
#                                                      portfolio= self.portfolio)
#         
#         print('amount', close_price, get_obj_quantity,get_obj_quantity*close_price)
#         print('exit_price',give_obj_close.quantity/get_obj_close.quantity, close_price)
#         print('quantity', get_obj_close.quantity, give_obj_close.quantity)
# 
# =============================================================================
        print('=========')
        
        pos_list = [entry_pos, exit_pos, stop_pos, close_pos]

        
# =============================================================================
#         # Execute the position based on different scenario
#         # change the price from the initial position to the closest price 
#         # estimation
# 
#         if entry_pt == (np.nan,np.nan):
#             print("No trade")
#             # Cancel all order positions
#             ExecutePosition(entry_pos).cancel_pos(void_time=close_pt[0])
#             ExecutePosition(exit_pos).cancel_pos(void_time=close_pt[0])
#             ExecutePosition(stop_pos).cancel_pos(void_time=close_pt[0])
#             ExecutePosition(close_pos).cancel_pos(void_time=close_pt[0])   
#             
#             return trade_open, trade_close
# 
#             
#         elif entry_pt and exit_pt != (np.nan,np.nan):
#             print("Noraml exit.")
#             trade_open, trade_close = entry_pt, exit_pt
#             opening_pos, closing_pos = entry_pos, exit_pos
#             
#             # change the closing price
#             closing_pos.price = round(1/exit_pt[1],9)
#             
#             print("trade_open, trade_close", trade_open, trade_close)
#             print(entry_pos.status, exit_pos.status, stop_pos.status, close_pos.status)
#             
#             # Cancel all order positionspen_positions_one_trade_per_day(self, give_obj_name, get_obj_name, 
#                          get_obj_quantity, EES_target_list, pos_type):
#             ExecutePosition(stop_pos).cancel_pos(void_time= trade_close[0])
#             ExecutePosition(close_pos).cancel_pos(void_time= trade_close[0])  
#             
#         elif exit_pt== (np.nan,np.nan) and stop_pt != (np.nan,np.nan):
#             print('stop loss')
#             trade_open, trade_close = entry_pt, stop_pt
#             opening_pos, closing_pos = entry_pos, stop_pos
#             
#             # change the closing price
#             closing_pos.price = round(1/stop_pt[1],9)
#             print(closing_pos.price, round(1/stop_pt[1],9))
#             print(closing_pos.get_obj)
#             
#             # Cancel all order positions
#             ExecutePosition(exit_pos).cancel_pos(void_time= trade_close[0])
#             ExecutePosition(close_pos).cancel_pos(void_time= trade_close[0])  
#             
#             
#         elif exit_pt== (np.nan,np.nan) and stop_pt == (np.nan,np.nan):
#             print("Sell at close")
#             trade_open, trade_close = entry_pt, close_pt
#             opening_pos, closing_pos = entry_pos, close_pos
# 
#             # change the closing price
#             closing_pos.price = round(1/close_pt[1],9)
#             
#             # Cancel all order positions
#             ExecutePosition(stop_pos).cancel_pos(void_time=trade_close[0])
#             ExecutePosition(exit_pos).cancel_pos(void_time=trade_close[0])
#             
#         opening_pos.price = entry_pt[1]
#         # Execute the positions
#         ExecutePosition(opening_pos).fill_pos(fill_time = trade_open[0], 
#                                             pos_type=pos_type)
#         
#         ExecutePosition(closing_pos).fill_pos(fill_time = trade_close[0], 
#                                            pos_type=pos_type)
# =============================================================================
        #exec_pos_list = [opening_pos,closing_pos]
        
        return pos_list
    
    def execute_one_trade_per_day(self, EES_dict, pos_list, pos_type="Long"):
        
        # unpack inputs
        entry_pt, exit_pt, stop_pt, close_pt = self.find_pt_one_trade_per_day(EES_dict)
        entry_pos, exit_pos, stop_pos, close_pos = pos_list[0], pos_list[1], pos_list[2], pos_list[3]

        # initialise trade_open and trade_close time and prices
        trade_open, trade_close = (np.nan,np.nan), (np.nan,np.nan)
        opening_pos, closing_pos = None, None
        
        if entry_pt == (np.nan,np.nan):
            print("No trade")
            # Cancel all order positions
            ExecutePosition(entry_pos).cancel_pos(void_time=close_pt[0])
            ExecutePosition(exit_pos).cancel_pos(void_time=close_pt[0])
            ExecutePosition(stop_pos).cancel_pos(void_time=close_pt[0])
            ExecutePosition(close_pos).cancel_pos(void_time=close_pt[0])   
            
            return trade_open, trade_close

            
        elif entry_pt and exit_pt != (np.nan,np.nan):
            print("Noraml exit.")
            trade_open, trade_close = entry_pt, exit_pt
            opening_pos, closing_pos = entry_pos, exit_pos
            
            # change the closing price
            closing_pos.price = round(1/exit_pt[1],9)
            
            print("trade_open, trade_close", trade_open, trade_close)
            print(entry_pos.status, exit_pos.status, stop_pos.status, close_pos.status)
            
            # Cancel all order positions
            ExecutePosition(stop_pos).cancel_pos(void_time= trade_close[0])
            ExecutePosition(close_pos).cancel_pos(void_time= trade_close[0])  
            
        elif exit_pt== (np.nan,np.nan) and stop_pt != (np.nan,np.nan):
            print('stop loss')
            trade_open, trade_close = entry_pt, stop_pt
            opening_pos, closing_pos = entry_pos, stop_pos
            
            # change the closing price
            closing_pos.price = round(1/stop_pt[1],9)
            print(closing_pos.price, round(1/stop_pt[1],9))
            print(closing_pos.get_obj)
            
            # Cancel all order positions
            ExecutePosition(exit_pos).cancel_pos(void_time= trade_close[0])
            ExecutePosition(close_pos).cancel_pos(void_time= trade_close[0])  
            
            
        elif exit_pt== (np.nan,np.nan) and stop_pt == (np.nan,np.nan):
            print("Sell at close")
            trade_open, trade_close = entry_pt, close_pt
            opening_pos, closing_pos = entry_pos, close_pos

            # change the closing price
            closing_pos.price = round(1/close_pt[1],9)
            
            # Cancel all order positions
            ExecutePosition(stop_pos).cancel_pos(void_time=trade_close[0])
            ExecutePosition(exit_pos).cancel_pos(void_time=trade_close[0])
            
        opening_pos.price = entry_pt[1]
        # Execute the positions
        ExecutePosition(opening_pos).fill_pos(fill_time = trade_open[0], 
                                            pos_type=pos_type)
        
        ExecutePosition(closing_pos).fill_pos(fill_time = trade_close[0], 
                                           pos_type=pos_type)
        
        exec_pos_list = [opening_pos,closing_pos]
        pos_list = [entry_pos, exit_pos, stop_pos, close_pos]
        
        return trade_open, trade_close, pos_list, exec_pos_list
    
    def run_one_trade_per_day_portfolio(self, day, 
                                      give_obj_name, get_obj_name, 
                                      get_obj_quantity,
                                      target_entry, target_exit, stop_exit,
                                      open_hr="0300", close_hr="2000", 
                                      direction = "Buy"): 
        """
        This method only look into the data points that crosses the threashold.
        Thus it is fast but it only perform simple testing. 
        Comprehesive dynamic testing requires other functions

        Parameters
        ----------
        EES_dict : TYPE
            DESCRIPTION.
        give_obj : TYPE
            DESCRIPTION.
        get_obj : TYPE
            DESCRIPTION.

        Returns
        -------
        trade_open : TYPE
            DESCRIPTION.
        trade_close : TYPE
            DESCRIPTION.

        """
        
        #Find the minute that the price crosses the EES values
        EES_dict = read.find_minute_EES(day, target_entry, target_exit, stop_exit,
                          open_hr=open_hr, close_hr=close_hr, 
                          direction = direction)
        
        print('entry_exit', EES_dict['entry'], EES_dict['exit'], EES_dict['stop'], EES_dict['close'])
        

        #print("entry_pt, exit_pt, stop_pt, close_pt", entry_pt, exit_pt, stop_pt, close_pt)
        # Input the Asset objects

        pos_type= 'Long'
        EES_target_list = [target_entry, target_exit, stop_exit, EES_dict['close'][1]] 

        # run the trade via position module
        pos_list = self.open_positions_one_trade_per_day(give_obj_name, get_obj_name, 
                                  get_obj_quantity, EES_target_list, pos_type)


        trade_open, trade_close, pos_list, exec_pos_list = self.execute_one_trade_per_day(EES_dict, pos_list)

        # the search function for entry and exit time should be completely sepearate to the trading actions
        return EES_dict, trade_open, trade_close, pos_list, exec_pos_list            
                    

        def trade_choice_dynamic_1(self):
            return
        
        # Execute the Position here
        #ExecutePosition()


class OneTradePerDay(Trade):
    
    def  __init__(self, portfolio):
        #self.trade_or_not = True
        super().__init__(portfolio)
        
    @staticmethod
    def find_EES_values(EES_dict):
        """
        A method to find the appropiate EES values of the day.

        Parameters
        ----------
        EES_dict : TYPE
            DESCRIPTION.

        Returns
        -------
        entry_pt : TYPE
            DESCRIPTION.
        exit_pt : TYPE
            DESCRIPTION.
        stop_pt : TYPE
            DESCRIPTION.
        close_pt : TYPE
            DESCRIPTION.

        """
        # A method that search for correct EES points from a EES_dict
        
        #initialise
        entry_pt, exit_pt = (np.nan,np.nan), (np.nan,np.nan)
        stop_pt, close_pt = (np.nan,np.nan), (np.nan,np.nan)
        
        earliest_exit, earliest_stop = exit_pt, stop_pt
        
        # closr_pt always exist so we do it outside of the switch cases
        close_pt = EES_dict['close']

        # To get the correct EES and close time and price
        if len(EES_dict['entry']) == 0: # entry price not hit. No trade that day.
            pass
        else:
            # choose the entry point
            entry_pt = EES_dict['entry'][0]
            
            if len(EES_dict['exit']) > 0:
                # Find exit point candidates
                for i, exit_cand in enumerate(EES_dict['exit']):  
                    if exit_cand[0] > entry_pt[0]:
                        earliest_exit = exit_cand
                        print('earliest_exit', earliest_exit)
                        break

            if len(EES_dict['stop']) > 0:
                # Finde stop loss point candidates
                for i, stop_cand in enumerate(EES_dict['stop']):
                    if stop_cand[0] > entry_pt[0]:
                        earliest_stop = stop_cand
                        print('earliest_stop', earliest_stop)
                        break
            
            # put in the new exit and stop
            exit_pt = earliest_exit
            stop_pt = earliest_stop

        return entry_pt, exit_pt, stop_pt, close_pt
    
    @staticmethod
    def open_positions(give_obj_name, get_obj_name, 
                              get_obj_quantity, EES_target_list, pos_type):
        # a method that execute the one trade per day based on the cases of the EES
        entry_price, exit_price = EES_target_list[0], EES_target_list[1]
        stop_price, close_price = EES_target_list[2], EES_target_list[3]
        
        #### Collapse all these into an add_position function
        # Make positions for initial price estimation
        print('==entry==')
        entry_pos = super().add_position(give_obj_name, get_obj_name, 
                                      get_obj_quantity, entry_price)

        print('==exit==')
        exit_pos = super().add_position(get_obj_name, give_obj_name, 
                          get_obj_quantity*exit_price, 1.0/exit_price)


        print('==stop==', get_obj_quantity)
        stop_pos = super().add_position(get_obj_name, give_obj_name, 
                          get_obj_quantity*stop_price, 1.0/stop_price)
        
        print('==close==')
        close_pos = super().add_position(get_obj_name, give_obj_name, 
                          get_obj_quantity*close_price, 1.0/close_price)
        
        print('=========')
        
        pos_list = [entry_pos, exit_pos, stop_pos, close_pos]

        return pos_list
    
    def execute_position(self, EES_dict, pos_list, pos_type="Long"):
        
        # unpack inputs
        entry_pt, exit_pt, stop_pt, close_pt = self.find_EES_values(EES_dict)
        entry_pos, exit_pos, stop_pos, close_pos = pos_list[0], pos_list[1], pos_list[2], pos_list[3]

        # initialise trade_open and trade_close time and prices
        trade_open, trade_close = (np.nan,np.nan), (np.nan,np.nan)
        opening_pos, closing_pos = None, None
        
        if entry_pt == (np.nan,np.nan):
            print("No trade")
            # Cancel all order positions
            ExecutePosition(entry_pos).cancel_pos(void_time=close_pt[0])
            ExecutePosition(exit_pos).cancel_pos(void_time=close_pt[0])
            ExecutePosition(stop_pos).cancel_pos(void_time=close_pt[0])
            ExecutePosition(close_pos).cancel_pos(void_time=close_pt[0])   
            
            return trade_open, trade_close

            
        elif entry_pt and exit_pt != (np.nan,np.nan):
            print("Noraml exit.")
            trade_open, trade_close = entry_pt, exit_pt
            opening_pos, closing_pos = entry_pos, exit_pos
            
            # change the closing price
            closing_pos.price = round(1/exit_pt[1],9)
            
            print("trade_open, trade_close", trade_open, trade_close)
            print(entry_pos.status, exit_pos.status, stop_pos.status, close_pos.status)
            
            # Cancel all order positions
            ExecutePosition(stop_pos).cancel_pos(void_time= trade_close[0])
            ExecutePosition(close_pos).cancel_pos(void_time= trade_close[0])  
            
        elif exit_pt== (np.nan,np.nan) and stop_pt != (np.nan,np.nan):
            print('stop loss')
            trade_open, trade_close = entry_pt, stop_pt
            opening_pos, closing_pos = entry_pos, stop_pos
            
            # change the closing price
            closing_pos.price = round(1/stop_pt[1],9)
            print(closing_pos.price, round(1/stop_pt[1],9))
            print(closing_pos.get_obj)
            
            # Cancel all order positions
            ExecutePosition(exit_pos).cancel_pos(void_time= trade_close[0])
            ExecutePosition(close_pos).cancel_pos(void_time= trade_close[0])  
            
            
        elif exit_pt== (np.nan,np.nan) and stop_pt == (np.nan,np.nan):
            print("Sell at close")
            trade_open, trade_close = entry_pt, close_pt
            opening_pos, closing_pos = entry_pos, close_pos

            # change the closing price
            closing_pos.price = round(1/close_pt[1],9)
            
            # Cancel all order positions
            ExecutePosition(stop_pos).cancel_pos(void_time=trade_close[0])
            ExecutePosition(exit_pos).cancel_pos(void_time=trade_close[0])
            
        opening_pos.price = entry_pt[1]
        
        # Execute the positions
        ExecutePosition(opening_pos).fill_pos(fill_time = trade_open[0], 
                                            pos_type=pos_type)
        
        ExecutePosition(closing_pos).fill_pos(fill_time = trade_close[0], 
                                           pos_type=pos_type)
        
        exec_pos_list = [opening_pos,closing_pos]
        pos_list = [entry_pos, exit_pos, stop_pos, close_pos]
        
        return trade_open, trade_close, pos_list, exec_pos_list
    
    def run_trade(self, day, give_obj_name, get_obj_name, 
                                      get_obj_quantity,
                                      target_entry, target_exit, stop_exit,
                                      open_hr="0300", close_hr="2000", 
                                      direction = "Buy"): 
        """
        This method only look into the data points that crosses the threashold.
        Thus it is fast but it only perform simple testing. 
        Comprehesive dynamic testing requires other functions

        Parameters
        ----------
        EES_dict : TYPE
            DESCRIPTION.
        give_obj : TYPE
            DESCRIPTION.
        get_obj : TYPE
            DESCRIPTION.

        Returns
        -------
        trade_open : TYPE
            DESCRIPTION.
        trade_close : TYPE
            DESCRIPTION.

        """
        
        #Find the minute that the price crosses the EES values
        EES_dict = read.find_minute_EES(day, target_entry, target_exit, stop_exit,
                          open_hr=open_hr, close_hr=close_hr, 
                          direction = direction)
        
        print('entry_exit', EES_dict['entry'], EES_dict['exit'], EES_dict['stop'], EES_dict['close'])
        

        #print("entry_pt, exit_pt, stop_pt, close_pt", entry_pt, exit_pt, stop_pt, close_pt)
        # Input the Asset objects
        pos_type= 'Long'
        EES_target_list = [target_entry, target_exit, stop_exit, EES_dict['close'][1]] 

        # run the trade via position module
        pos_list = self.open_positions(give_obj_name, get_obj_name, 
                                  get_obj_quantity, EES_target_list, pos_type)


        trade_open, trade_close, pos_list, exec_pos_list = self.execute_position(EES_dict, pos_list)

        # the search function for entry and exit time should be completely sepearate to the trading actions
        return trade_open, trade_close, EES_dict, pos_list, exec_pos_list            

    
# =============================================================================
#  under construction
# @dataclass
# class TradeBot:
#     
#     exchange: None
#     trading_startegy: None
#     
# =============================================================================
    