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
    """
    LEGACY code before the development of trade and portfolio modules
    a function that control which price to buy and sell

    Parameters
    ----------
    EES_dict : TYPE
        DESCRIPTION.

    Returns
    -------
    TYPE
        DESCRIPTION.

    """

    
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
                
    return trade_open, trade_close 
    
class Trade(object):
    """
    Parent class for all trading strategy. Universal functions are written here.
    
    """
    def  __init__(self, portfolio):
        self._portfolio = portfolio
        self.position_book = []
        
    def add_position(self, give_obj_name, get_obj_name, get_obj_quantity, 
                     target_price):
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
        
        pos = Position(give_obj, get_obj, target_price, portfolio= self._portfolio)
        
        self.position_book.append(pos)
        return pos


class OneTradePerDay(Trade):
    """
    A class that perform one trade per day, the simplest form of trading.
    
    Four possible outcomes:
    1) Find the earliest entry point in the price action chart, 
    2) exit the position  as soon as the price it the target entry. 
    3) If the price hit the stop loss first, exit at stop loass. 
    4) If netiher the target exit nor the stop loss is hit, exit the trade 
        at the closing hour.
        
    """
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
    
    #@staticmethod
    def open_positions(self,give_obj_name, get_obj_name, 
                              get_obj_quantity, EES_target_list, pos_type):
        """
        

        Parameters
        ----------
        give_obj_name : TYPE
            DESCRIPTION.
        get_obj_name : TYPE
            DESCRIPTION.
        get_obj_quantity : TYPE
            DESCRIPTION.
        EES_target_list : TYPE
            DESCRIPTION.
        pos_type : TYPE
            DESCRIPTION.

        Returns
        -------
        pos_list : TYPE
            DESCRIPTION.

        """
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
        """
        A method that execute the a list posiiton given a EES_dict.
        It search the EES_dict the find the appropiate entry, exit, stop loss,
        and close time for the trade.

        Parameters
        ----------
        EES_dict : TYPE
            DESCRIPTION.
        pos_list : TYPE
            DESCRIPTION.
        pos_type : TYPE, optional
            DESCRIPTION. The default is "Long".

        Returns
        -------
        TYPE
            DESCRIPTION.

        """
        # Unpack inputs
        entry_pos, exit_pos, stop_pos, close_pos = pos_list[0], pos_list[1], \
                                                    pos_list[2], pos_list[3]
              
        # Search for the appropiate time for entry, exit, stop loss,
        # and close time for the trade                                    
        entry_pt, exit_pt, stop_pt, close_pt = self.find_EES_values(EES_dict)


        # initialise trade_open and trade_close time and prices
        trade_open, trade_close = (np.nan,np.nan), (np.nan,np.nan)
        opening_pos, closing_pos = None, None
        
        # Run diagnosis to decide which outcome it is for the day
        # Case 1: No trade because entry is not hit
        if entry_pt == (np.nan,np.nan):
            print("No trade")
            # Cancel all order positions
            ExecutePosition(entry_pos).cancel_pos(void_time=close_pt[0])
            ExecutePosition(exit_pos).cancel_pos(void_time=close_pt[0])
            ExecutePosition(stop_pos).cancel_pos(void_time=close_pt[0])
            ExecutePosition(close_pos).cancel_pos(void_time=close_pt[0])   
            
            return trade_open, trade_close

        # Case 2: An exit is hit, normal exit
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
            
        # Case 3: stop loss
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
            
       # Case 4: Neither an exit or stop loss is hit, exit position at close time
        elif exit_pt== (np.nan,np.nan) and stop_pt == (np.nan,np.nan):
            print("Sell at close")
            trade_open, trade_close = entry_pt, close_pt
            opening_pos, closing_pos = entry_pos, close_pos

            # change the closing price
            closing_pos.price = round(1/close_pt[1],9)
            
            # Cancel all order positions
            ExecutePosition(stop_pos).cancel_pos(void_time=trade_close[0])
            ExecutePosition(exit_pos).cancel_pos(void_time=trade_close[0])
            
        # change the price for the open position
        opening_pos.price = entry_pt[1]
        
        # Execute the positions
        ExecutePosition(opening_pos).fill_pos(fill_time = trade_open[0], 
                                            pos_type=pos_type)
        
        ExecutePosition(closing_pos).fill_pos(fill_time = trade_close[0], 
                                           pos_type=pos_type)
        
        # pack the outputs objects into lists
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
        pos_list = self.open_positions(give_obj_name, get_obj_name, get_obj_quantity, EES_target_list, pos_type=pos_type)


        trade_open, trade_close, pos_list, exec_pos_list = self.execute_position(EES_dict, pos_list)

        # the search function for entry and exit time should be completely sepearate to the trading actions
        return EES_dict, trade_open, trade_close, pos_list, exec_pos_list            

    
# =============================================================================
#  under construction
# @dataclass
# class TradeBot:
#     
#     exchange: None
#     trading_startegy: None
#     
# =============================================================================
    