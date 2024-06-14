#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 10 00:16:28 2024

@author: dexter

A module that control trade action. The decision making logics are all stored 
here.
"""
from dataclasses import dataclass
from typing import Protocol # use protocol for trade class
import datetime as datetime

import numpy as np

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
              "QPc2":  {"unit":'contracts',"asset_type":'Future'}
              }

num_per_contract = {
    'CLc1': 1000.0,
    'CLc2': 1000.0,
    'HOc1': 42000.0,
    'HOc2': 42000.0,
    'RBc1': 42000.0,
    'RBc2': 42000.0,
    'QOc1': 1000.0,
    'QOc2': 1000.0,
    'QPc1': 100.0,
    'QPc2': 100.0
}

round_turn_fees = {
    'CLc1': 24.0,
    'CLc2': 24.0,
    'HOc1': 25.2,
    'HOc2': 25.2,
    'RBc1': 25.2,
    'RBc2': 25.2,
    'QOc1': 24.0,
    'QOc2': 24.0,
    'QPc1': 24.0,
    'QPc2': 24.0
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
                     target_price, size = 1, fee = None, pos_type = 'Long',
                     open_time = datetime.datetime.now()):
        """
        A simple function that make the process of creating a position easier.
        It takes the name of the give_obj and get_obj, as well as the desired 
        quantity of get_obj and target price, to create the Asset objects and 
        Position object.

        The function automatically calculate how much give_obj you are going 
        to spend to purchase it. It assume you have enough within your portfolio.
        
        Parameters
        ----------
        give_obj_name : str
            The name of the give object.
        get_obj_name : str
            The name of the get object.
        get_obj_quantity : float
            The quantity of the get object.
        target_price : TYPE
            An initial target price for the position. It is subject to slight 
            changes during the backtest.

        Returns
        -------
        pos : Position object
            The trade opsition .

        """
        get_obj_unit = ASSET_DICT[get_obj_name]['unit']
        get_obj_type = ASSET_DICT[get_obj_name]['asset_type']
        
        give_obj_unit = ASSET_DICT[give_obj_name]['unit']
        give_obj_type = ASSET_DICT[give_obj_name]['asset_type']
        
        get_obj = Asset(get_obj_name, get_obj_quantity, 
                        get_obj_unit, get_obj_type)
        give_obj = Asset(give_obj_name, target_price*get_obj_quantity, 
                            give_obj_unit, give_obj_type)
        
        # different type of posiitons
        if pos_type == 'Long-Buy':
            # an example, get_obj is the asset, give_obj is the cash
            # Setup the amount of asset we want
            get_obj = Asset(get_obj_name, get_obj_quantity, 
                            get_obj_unit, get_obj_type)
            # calculate the money we have to pay
            give_obj = Asset(give_obj_name, target_price*get_obj_quantity*size, 
                                give_obj_unit, give_obj_type)
            
            print('Long-Buy', target_price, target_price*get_obj_quantity*size, get_obj_quantity)
            print("Addposition", get_obj, give_obj)
            pos = Position(give_obj, get_obj, target_price, 
                           portfolio= self._portfolio, size = size,
                           fee = fee, pos_type = pos_type, open_time=open_time)
            
        elif pos_type == 'Long-Sell':
            # an example, get_obj is the asset, give_obj is the cash
            get_obj = Asset(get_obj_name, get_obj_quantity, 
                            get_obj_unit, get_obj_type)
            give_obj = Asset(give_obj_name, target_price*get_obj_quantity*size, 
                                give_obj_unit, give_obj_type)
            
            print('Long-Sell', target_price, target_price*get_obj_quantity*size, get_obj_quantity)
            print("Addposition", get_obj, give_obj)

            pos = Position(give_obj, get_obj, target_price, 
                           portfolio= self._portfolio, size = size,
                           fee = fee, pos_type = pos_type, open_time=open_time)
            
        elif pos_type == 'Short-Borrow':
            # an example, get_obj is the asset, give_obj is the cash
            get_obj = Asset(get_obj_name, get_obj_quantity, 
                            get_obj_unit, get_obj_type)
            give_obj = Asset(give_obj_name, target_price*get_obj_quantity*size, 
                                give_obj_unit, give_obj_type)
            
            print('Short-Borrow', target_price, target_price*get_obj_quantity*size, get_obj_quantity)
            print("Addposition", get_obj, give_obj)
            
            pos = Position(give_obj, get_obj, target_price, 
                           portfolio= self._portfolio, size = size,
                           fee = fee, pos_type = pos_type, open_time=open_time)
            
        elif pos_type == 'Short-Buyback':
            # an example, get_obj is the asset, give_obj is the cash
            get_obj = Asset(get_obj_name, get_obj_quantity, 
                            get_obj_unit, get_obj_type)
            give_obj = Asset(give_obj_name, target_price*get_obj_quantity*size, 
                                give_obj_unit, give_obj_type)
            
            print('Short-Buyback', target_price, target_price*get_obj_quantity*size, get_obj_quantity)
            print("Addposition", get_obj, give_obj)
            
            pos = Position(give_obj, get_obj, target_price, 
                           portfolio= self._portfolio, size = size,
                           fee = fee, pos_type = pos_type, open_time=open_time)
        # Add posiyion in the position book
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
    def __init__(self, portfolio):
        #self.trade_or_not = True
        super().__init__(portfolio)
        
    @staticmethod
    def find_EES_values(EES_dict):
        """
        A method to find the appropiate EES values of the day. 
        In the case of one trade per day, we only search for the earliest exit
        and stop loss price after entry price was hit.

        Parameters
        ----------
        EES_dict : dict
            A dictionary for all possible EES values.

        Returns
        -------
        entry_pt : tuple
            The time and price of the entry moment.
        exit_pt : tuple
            The time and price of the exit moment.
        stop_pt : tuple
            The time and price of the stop loss moment.
        close_pt : tuple
            The time and price of the close hour exit moment.


        """
        # A method that search for correct EES points from a EES_dict
        
        # initialise
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
    
    def open_positions(self, give_obj_name, get_obj_name, 
                              get_obj_quantity, EES_target_list, pos_type,
                              size = 1, fee = None, 
                              open_time = datetime.datetime.now()):
        """
        A method to open the entry, exit, stop, and close positions

        Parameters
        ----------
        give_obj_name : str
            The name of the give object.
        get_obj_name : str
            The name of the get object.
        get_obj_quantity : float
            The quantity of the get object.
        EES_target_list : list
            A list of target EES values [entry_price, exit_price, 
                                         stop_price, close_price].
        pos_type : str
            The type of position to be opened.

        Returns
        -------
        pos_list : list
            The position list: [entry_pos, exit_pos, stop_pos, close_pos].

        """
        if pos_type == 'Long':
            pos_type1 = 'Long-Buy'
            pos_type2 = 'Long-Sell'
            #pos_type1 = 'Long'
            #pos_type2 = 'Long'

        elif pos_type == 'Short':
            pos_type1 = 'Short-Borrow'
            pos_type2 = 'Short-Buyback'
            
        # a method that execute the one trade per day based on the cases of the EES
        entry_price, exit_price = EES_target_list[0], EES_target_list[1]
        stop_price, close_price = EES_target_list[2], EES_target_list[3]
        
        #### Collapse all these into an add_position function
        # Make positions for initial price estimation
        print('==entry==')
        print(pos_type1, pos_type2)
        entry_pos = super().add_position(give_obj_name, get_obj_name, 
                                      get_obj_quantity, entry_price, 
                                      size = size, fee = None, pos_type = pos_type1,
                                      open_time=open_time)
        print(entry_pos.status)

        print('==exit==')
        exit_pos = super().add_position(give_obj_name, get_obj_name, 
                          get_obj_quantity, exit_price, 
                          size = size, fee = fee, pos_type = pos_type2,
                          open_time=open_time)

        print(exit_pos.status)

        print('==stop==', get_obj_quantity)
        stop_pos = super().add_position(give_obj_name, get_obj_name, 
                          get_obj_quantity, stop_price, 
                          size = size, fee = fee, pos_type = pos_type2,
                          open_time=open_time)
        print(stop_pos.status)

        
        print('==close==')
        close_pos = super().add_position(give_obj_name, get_obj_name, 
                          get_obj_quantity, close_price,
                          size = size, fee = fee, pos_type = pos_type2,
                          open_time=open_time)
        print(close_pos.status)

        print('=========')
  
# =============================================================================
#         print('==entry==')
#         entry_pos = super().add_position(give_obj_name, get_obj_name, 
#                                       get_obj_quantity, entry_price, 
#                                       size = size, fee = fee, pos_type = pos_type1,
#                                       open_time=open_time)
# 
#         print('==exit==')
#         exit_pos = super().add_position(get_obj_name, give_obj_name, 
#                           get_obj_quantity*exit_price, 1.0/exit_price, 
#                           size = size, fee = fee, pos_type = pos_type2,
#                           open_time=open_time)
# 
# 
#         print('==stop==', get_obj_quantity)
#         stop_pos = super().add_position(get_obj_name, give_obj_name, 
#                           get_obj_quantity*stop_price, 1.0/stop_price, 
#                           size = size, fee = fee, pos_type = pos_type2,
#                           open_time=open_time)
# 
#         
#         print('==close==')
#         close_pos = super().add_position(get_obj_name, give_obj_name, 
#                           get_obj_quantity*close_price, 1.0/close_price,
#                           size = size, fee = fee, pos_type = pos_type2,
#                           open_time=open_time)
# 
#         
#         print('=========')
#         
# =============================================================================
        pos_list = [entry_pos, exit_pos, stop_pos, close_pos]

        return pos_list
    
    def execute_position(self, EES_dict, pos_list, pos_type="Long"):
        """
        A method that execute the a list posiiton given a EES_dict.
        It search the EES_dict the find the appropiate entry, exit, stop loss,
        and close time for the trade.

        Parameters
        ----------
        EES_dict : dict
            A dictionary for all possible EES values.
        pos_list : list
            The position list: [entry_pos, exit_pos, stop_pos, close_pos].
        pos_type : str, optional
            The type of position. The default is "Long".

        Returns
        -------
        trade_open : 2-elements tuple 
            The trade open time and price
        trade_close : 2-elements tuple 
            The trade close time and price
        pos_list : list
            The position list: [entry_pos, exit_pos, stop_pos, close_pos].
        exec_pos_list : list
            The [opening_pos, closing_pos] .

        """
        if pos_type == 'Long':
            pos_type1 = 'Long-Buy'
            pos_type2 = 'Long-Sell'

        elif pos_type == 'Short':
            pos_type1 = 'Short-Borrow'
            pos_type2 = 'Short-Buyback'
            
        # Unpack inputs
        entry_pos, exit_pos, stop_pos, close_pos = pos_list[0], pos_list[1], \
                                                    pos_list[2], pos_list[3]
              
        # Search for the appropiate time for entry, exit, stop loss,
        # and close time for the trade                                    
        entry_pt, exit_pt, stop_pt, close_pt = self.find_EES_values(EES_dict)


        # initialise trade_open and trade_close time and prices
        trade_open, trade_close = (np.nan,np.nan), (np.nan,np.nan)
        opening_pos, closing_pos = None, None
        
        # pack the outputs objects into lists
        exec_pos_list = [opening_pos,closing_pos]

        # Run diagnosis to decide which outcome it is for the day
        # Case 1: No trade because entry is not hit
        if entry_pt == (np.nan,np.nan):
            print("No trade")
            # Cancel all order positions
            ExecutePosition(entry_pos).cancel_pos(void_time=close_pt[0])
            ExecutePosition(exit_pos).cancel_pos(void_time=close_pt[0])
            ExecutePosition(stop_pos).cancel_pos(void_time=close_pt[0])
            ExecutePosition(close_pos).cancel_pos(void_time=close_pt[0])   
            
            return trade_open, trade_close, pos_list, exec_pos_list

        # Case 2: An exit is hit, normal exit
        elif entry_pt and exit_pt != (np.nan,np.nan):
            print("Noraml exit.")
            trade_open, trade_close = entry_pt, exit_pt
            opening_pos, closing_pos = entry_pos, exit_pos
            
            print("clos_get_obj", closing_pos.get_obj)
            # change the closing price
            closing_pos.price = round(exit_pt[1],9)
            print("clos_get_obj", closing_pos.get_obj)

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
            closing_pos.price = round(stop_pt[1],9)
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
            closing_pos.price = round(close_pt[1],9)
            
            # Cancel all order positions
            ExecutePosition(stop_pos).cancel_pos(void_time=trade_close[0])
            ExecutePosition(exit_pos).cancel_pos(void_time=trade_close[0])
            
        # change the price for the open position
        opening_pos.price = entry_pt[1]
        
        print('Before execution', pos_type1, pos_type2)
        # Execute the positions
        ExecutePosition(opening_pos).fill_pos(fill_time = trade_open[0], 
                                            pos_type=pos_type1)
        
        ExecutePosition(closing_pos).fill_pos(fill_time = trade_close[0], 
                                           pos_type=pos_type2)
        
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
        EES_dict : dict
            A dictionary for all possible EES values.
        give_obj_name :
            
        get_obj_name :
            
        get_obj_quantity :
            
        target_entry :
            
        target_exit :
            
        stop_exit :
            
        open_hr :
        
        close_hr : 
        
        direction :
            "Buy"

        Returns
        -------
        EES_dict, trade_open, trade_close, pos_list, exec_pos_list

        """
        
        #Find the minute that the price crosses the EES values
        EES_dict = read.find_minute_EES(day, target_entry, target_exit, stop_exit,
                          open_hr=open_hr, close_hr=close_hr, 
                          direction = direction)
        
        print('entry_exit', EES_dict['entry'], EES_dict['exit'], 
              EES_dict['stop'], EES_dict['close'])
        

        #print("entry_pt, exit_pt, stop_pt, close_pt", entry_pt, exit_pt, stop_pt, close_pt)
        # Input the position type
        if direction == 'Buy':
            pos_type= 'Long'
        elif direction == 'Sell':
            pos_type = 'Short'
            
        EES_target_list = [target_entry, target_exit, 
                           stop_exit, EES_dict['close'][1]] 
        
        fee = Asset('USD', 24.0, 'dollars', 'Cash')
        # run the trade via position module
        pos_list = self.open_positions(give_obj_name, get_obj_name, \
                                       get_obj_quantity, EES_target_list, \
                                           pos_type=pos_type, 
                                           size=num_per_contract[get_obj_name],
                                           fee=fee)


        trade_open, trade_close, pos_list, exec_pos_list = \
                                        self.execute_position(EES_dict, pos_list,
                                                              pos_type=pos_type)

        # the search function for entry and exit time should be completely 
        # sepearate to the trading actions
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
    