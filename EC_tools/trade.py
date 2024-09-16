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
import pandas as pd
from EC_tools.portfolio import Portfolio
from EC_tools.position import Position, ExecutePosition
import EC_tools.read as read
import EC_tools.utility as util
from crudeoil_future_const import OIL_FUTURES_FEE, SIZE_DICT, ASSET_DICT

import copy 


class Trade(Protocol):
    """
    Parent class for all trading strategy. Universal functions are written here.
    
    """
    def  __init__(self, portfolio: Portfolio, 
                 close_exit_or_not: bool = True, 
                 save_only_exec_pos: bool = False,
                 auto_unload_all: bool = False):
        
        self._portfolio = portfolio
        self._close_exit_or_not = close_exit_or_not
        self._save_only_exec_pos = save_only_exec_pos
        self._auto_unload_all = auto_unload_all
            
    @property
    def close_exit_or_not(self):
        return self._close_exit_or_not
    
    @property
    def save_only_exec_pos(self):
        return self._save_only_exec_pos
    
    @property
    def auto_unload_all(self):
        return self._auto_unload_all
    
    @close_exit_or_not.setter
    def close_exit_or_not(self, bool_val: bool) -> None:
        self._close_exit_or_not = bool_val
        
    @save_only_exec_pos.setter
    def save_only_exec_pos(self, bool_val: bool) -> None:
        self._save_only_exec_pos = bool_val
        
    @auto_unload_all.setter
    def auto_unload_all(self, bool_val: bool):
        self._auto_unload_all = bool_val
    
    def add_position(self, 
                     give_obj_name: str, 
                     get_obj_name: str, 
                     get_obj_quantity: str, 
                     target_price: float, 
                     size: int = 1, 
                     fee: int | float = None, 
                     pos_type: str = 'Long',
                     open_time: datetime.datetime = datetime.datetime.now(),
                     trade_id: int = 0):
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
        target_price : float
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
        
        # get_obj, asset
        get_obj = {'name': get_obj_name, 
                   'quantity': get_obj_quantity, 
                   'unit': get_obj_unit, 
                   'asset_type': get_obj_type,
                   'misc': {}}
        # give_obj, cash
        give_obj = {'name': give_obj_name, 
                    'quantity': target_price*get_obj_quantity*size, 
                    'unit': give_obj_unit, 
                    'asset_type': give_obj_type, 
                    'misc':{}}
        
        #print("before add fee", fee, get_obj_quantity)
        if type(fee) == dict:
            new_fee = fee.copy()
            new_fee['quantity'] = fee['quantity']*get_obj_quantity
        elif fee == None:
            new_fee = None
            
        # Create a position
        pos = Position(give_obj, get_obj, target_price, 
                       portfolio= self._portfolio, size = size,
                       fee = new_fee, pos_type = pos_type, 
                       open_time = open_time,
                       pos_id = trade_id)

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
    def __init__(self, portfolio, trade_id: int = 0):
        super().__init__(portfolio)
        self.trade_id = trade_id

    @staticmethod
    def choose_EES_values(EES_dict: dict) -> tuple[tuple, tuple, tuple, tuple]:
        """
        A method to find the appropiate EES values of the day. 
        In the case of one trade per day, we only search for the earliest exit
        and stop loss price after entry price was hit.
        
        You may supply either a EES_dict from 
        
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
                        #print('earliest_exit', earliest_exit)
                        break

            if len(EES_dict['stop']) > 0:
                # Finde stop loss point candidates
                for i, stop_cand in enumerate(EES_dict['stop']):
                    if stop_cand[0] > entry_pt[0]:
                        earliest_stop = stop_cand
                        #print('earliest_stop', earliest_stop)
                        break
            
            # put in the new exit and stop
            exit_pt = earliest_exit
            stop_pt = earliest_stop

        return entry_pt, exit_pt, stop_pt, close_pt
    
    def open_positions(self, 
                       give_obj_name: str, 
                       get_obj_name: str, 
                       get_obj_quantity: int | float, 
                       EES_target_list: list, 
                       pos_type: str,
                       size: int | float = 1, 
                       fee: dict = None, 
                       open_time: datetime.datetime = datetime.datetime.now())\
                       -> list[Position]:
        """
        A method to open the entry, exit, stop, and close positions.

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

        elif pos_type == 'Short':
            pos_type1 = 'Short-Borrow'
            pos_type2 = 'Short-Buyback'
            
        # a method that execute the one trade per day based on the cases of the EES
        entry_price, exit_price = EES_target_list[0], EES_target_list[1]
        stop_price, close_price = EES_target_list[2], EES_target_list[3]
        
        #### Collapse all these into an add_position function
        # Make positions for initial price estimation
        entry_pos = super().add_position(give_obj_name, get_obj_name, 
                                         get_obj_quantity, entry_price, 
                                         size = size, fee = None, 
                                         pos_type = pos_type1,
                                         open_time=open_time,
                                         trade_id=self.trade_id)

        exit_pos = super().add_position(give_obj_name, get_obj_name, 
                                        get_obj_quantity, exit_price, 
                                        size = size, fee = fee, 
                                        pos_type = pos_type2,
                                        open_time=open_time,
                                        trade_id=self.trade_id)

        stop_pos = super().add_position(give_obj_name, get_obj_name, 
                                        get_obj_quantity, stop_price, 
                                        size = size, fee = fee, 
                                        pos_type = pos_type2,
                                        open_time=open_time,
                                        trade_id=self.trade_id)
        
        close_pos = super().add_position(give_obj_name, get_obj_name, 
                                         get_obj_quantity, close_price,
                                         size = size, fee = fee, 
                                         pos_type = pos_type2,
                                         open_time=open_time,
                                         trade_id=self.trade_id)

        pos_list = [entry_pos, exit_pos, stop_pos, close_pos]
        #print("pos_list", pos_list)
        return pos_list
    
    def execute_positions(self, 
                          trunc_dict: dict, 
                          pos_list: list, 
                          pos_type: str = "Long"):
        """
        A method that execute the a list posiiton given a EES_dict.
        It search the EES_dict the find the appropiate entry, exit, stop loss,
        and close time for the trade.

        Parameters
        ----------
        trunc_dict : dict
            A truncation dictionary for all possible EES values.
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
        entry_pt, exit_pt, stop_pt, close_pt = self.choose_EES_values(trunc_dict)

        # initialise trade_open and trade_close time and prices
        trade_open, trade_close = (np.nan,np.nan), (np.nan,np.nan)
        opening_pos, closing_pos = None, None
        
        # pack the outputs objects into lists
        exec_pos_list = [opening_pos,closing_pos]

        # Run diagnosis to decide which outcome it is for the day
        # Case 1: No trade because entry is not hit
        if entry_pt == (np.nan,np.nan):
            #print("No trade.")
            # Cancel all order positions
            ExecutePosition(entry_pos).cancel_pos(void_time=close_pt[0])
            ExecutePosition(exit_pos).cancel_pos(void_time=close_pt[0])
            ExecutePosition(stop_pos).cancel_pos(void_time=close_pt[0])
            ExecutePosition(close_pos).cancel_pos(void_time=close_pt[0])   
            
            return trade_open, trade_close, pos_list, exec_pos_list
            
        # Case 2: An exit is hit, normal exit
        elif entry_pt and exit_pt != (np.nan,np.nan):
            #print("Noraml exit.")
            trade_open, trade_close = entry_pt, exit_pt
            opening_pos, closing_pos = entry_pos, exit_pos
            #print("Before price adjustment", opening_pos, closing_pos)

            # change the closing price
            closing_pos.price = round(exit_pt[1],9)
            
            # Cancel all order positions
            ExecutePosition(stop_pos).cancel_pos(void_time= trade_close[0])
            ExecutePosition(close_pos).cancel_pos(void_time= trade_close[0])  
            
        # Case 3: stop loss
        elif exit_pt== (np.nan,np.nan) and stop_pt != (np.nan,np.nan):
            #print('Stop loss.')
            trade_open, trade_close = entry_pt, stop_pt
            opening_pos, closing_pos = entry_pos, stop_pos
            #print("Before price adjustment", opening_pos, closing_pos)

            # change the closing price
            closing_pos.price = round(stop_pt[1],9)
            
            # Cancel all order positions
            ExecutePosition(exit_pos).cancel_pos(void_time= trade_close[0])
            ExecutePosition(close_pos).cancel_pos(void_time= trade_close[0])  
            
       # Case 4: Neither an exit or stop loss is hit, exit position at close time
        elif exit_pt== (np.nan,np.nan) and stop_pt == (np.nan,np.nan):
            #print("Sell at close.")
            trade_open, trade_close = entry_pt, close_pt
            opening_pos, closing_pos = entry_pos, close_pos
            #print("Before price adjustment", opening_pos, closing_pos)

            # change the closing price
            closing_pos.price = round(close_pt[1],9)
            
            # Cancel all order positions
            ExecutePosition(stop_pos).cancel_pos(void_time=trade_close[0])
            ExecutePosition(exit_pos).cancel_pos(void_time=trade_close[0])
        
        # change the price for the open position
        opening_pos.price = entry_pt[1]
        
        #print('entry_pt[1]', entry_pt[1])
        #print('exit_pt[1]', exit_pt[1])
        #print('stop_pt[1]', stop_pt[1])
        #print('close_pt[1]', close_pt[1])
        #print("After price adjustment", opening_pos, closing_pos)

        # Execute the positions
        ExecutePosition(opening_pos).fill_pos(fill_time = trade_open[0], 
                                              pos_type=pos_type1)
        
        ExecutePosition(closing_pos).fill_pos(fill_time = trade_close[0], 
                                              pos_type=pos_type2)


        # pack the outputs objects into lists
        exec_pos_list = [opening_pos, closing_pos]
        pos_list = [entry_pos, exit_pos, stop_pos, close_pos]
        
        #print("exec_pos_list", exec_pos_list)
        
        for pos in pos_list: # Add position in the position book
            self._portfolio._position_pool.append(copy.copy(pos))

        return trade_open, trade_close, pos_list, exec_pos_list
    
    def run_trade(self, 
                  trunc_dict: dict, #day: pd.DataFrame, 
                  give_obj_name: str, 
                  get_obj_name: str, 
                  get_obj_quantity: float | int,
                  target_entry: float, 
                  target_exit: float, 
                  stop_exit: float,
                  open_hr: str = "0300", 
                  close_hr: str = "2000", 
                  direction: str = "Buy",
                  fee: dict =  OIL_FUTURES_FEE,
                  open_time: datetime.datetime = None) -> \
                  tuple[tuple, tuple, list, list]: 
        """

        Note that run_trade method is agnoistic to the loop type, i.e.,
        You can use LoopType.CROSSOVER, LoopType.RANGE, or LoopType.FULL

        Parameters
        ----------
        trunc_dict : dict
            Truncation dictionary. It contains the relevant points selected 
            by some given EES values or EES ranges.
            This assume you are running a crossover or range loop.
        give_obj_name : str
            The name of the give_obj, e.g. 'USD'.
        get_obj_name : str
            The name of the get_obj, e.g. 'CLc1'.
        get_obj_quantity : int or float
            The quanity of get_obj you wish to order.
        target_entry : float
            The target entry time and price.
        target_exit : float
            The exit entry time and price.
        stop_exit : float
            The stop loss time and price.
        open_hr : str
            The opening hour of the trade
        close_hr : str
            The closing hour of the trade
        direction : str
            The default is "Buy"

        Returns
        -------
        EES_dict, trade_open, trade_close, pos_list, exec_pos_list

        """
        
        #Find the minute that the price crosses the EES values
        # Input the position type
        if direction == 'Buy':
            pos_type= 'Long'
        elif direction == 'Sell':
            pos_type = 'Short'
            
        # Note that this is not the EES_dict object from find_minute_EES.
        # This is just an initial estimation of the EES values for the 
        # open_position function in the begining of the day. As the positions
        # are executed, the prices will change according to the data.
        EES_target_list = [target_entry, target_exit, 
                           stop_exit, trunc_dict['close'][1]] 
        
        # run the trade via position module
        pos_list = self.open_positions(give_obj_name,
                                       get_obj_name, 
                                       get_obj_quantity, 
                                       EES_target_list, 
                                       pos_type=pos_type, 
                                       size=SIZE_DICT[get_obj_name],
                                       fee=fee, 
                                       open_time = open_time,
                                       trade_id= self.trade_id)

        # Execute the positions. As the function is ran, it chooses the 
        # appropiate EES values based on the choose_EES_values method of 
        # this class
        trade_open, trade_close, \
        pos_list, exec_pos_list = self.execute_positions(trunc_dict, pos_list,
                                                         pos_type = pos_type)

        # the search function for entry and exit time should be completely 
        # sepearate to the trading actions
        return trade_open, trade_close, pos_list, exec_pos_list            


class BiDirectionalTrade(Trade):
    """
    Bi-Directional Trade (Hedging position). The idea is to open two position,
    both Buy and Sell at trade-open given a set of entry and exit prices. 
    If the price moves past the entry point of either direction, we fill the 
    Buy/Sell order and enter the position. When the exit value is hit, we 
    exit and close the position. 
    
    The entry and exit range can be asymmetrical. User can manually input the 
    range they want for either trades.
    
    At the moment, this method is limited to trading one Buy or Sell position 
    per day, i.e., the maximum number of trades per day is one Buy plus one 
    Sell.
    
    This method also assume the Buy and Sell action are independent from each 
    other, that is, the two trade can be calculated and executed in parallel. 
    
    
    """
    def __init__(self, portfolio):
        super().__init__(portfolio)
        
    @staticmethod
    def choose_EES_values(self, trunc_dict: dict) -> tuple[tuple, tuple, tuple, tuple]:
        """
        Same method as OneTradePerDay

        """
        #print(self.portfolio)

        return OneTradePerDay(self._portfolio).choose_EES_values(trunc_dict)
    
    def open_positions(self, 
                       give_obj_name: str, 
                       get_obj_name: str, 
                       get_obj_quantity: int | float, 
                       EES_target_list: list, 
                       pos_type: str,
                       size: int | float = 1, 
                       fee: dict = None, 
                       open_time: datetime.datetime = datetime.datetime.now(),
                       trade_id: int = 0)\
                       -> list[Position]:
        """
        Same method as OneTradePerDay

        """
        return OneTradePerDay(self._portfolio).open_positions(give_obj_name,
                                                             get_obj_name,
                                                             get_obj_quantity, 
                                                             EES_target_list,
                                                             pos_type, size,
                                                             fee, open_time,
                                                             trade_id)
    
    def execute_positions(self, 
                         EES_dict: dict, 
                         pos_list: list, 
                         pos_type: str = "Long"):
        """
        Same method as OneTradePerDay

        """
        return OneTradePerDay(self._portfolio).execute_positions(EES_dict, 
                                                                pos_list, 
                                                                pos_type)
    
    def run_trade(self, 
                  day: pd.DataFrame, 
                  give_obj_name: str, 
                  get_obj_name: str, 
                  get_obj_quantity: float | int,
                  target_entry: dict[str, float] | \
                                dict[str,list[float] | \
                                tuple[float]], 
                  target_exit: dict[str, float] | \
                               dict[str,list[float] | \
                               tuple[float]], 
                  stop_exit: dict[str, float],
                  open_hr: str = "0300", 
                  close_hr: str = "2000",
                  direction: str = "Buy",
                  fee: dict =  OIL_FUTURES_FEE,
                  open_time: datetime.datetime = None,
                  trade_id: int = 0) -> \
                  tuple[dict, tuple, tuple, list, list]: 
        """
        This method only look into the data points that crosses the threashold.
        Thus it is fast but it only perform simple testing. 
        Comprehesive dynamic testing requires other functions

        Parameters
        ----------
        EES_dict : dict
            A dictionary for all possible EES values. This assume you are 
            running a crossover loop.
        give_obj_name : str
            The name of the give_obj, e.g. 'USD'.
        get_obj_name : str
            The name of the get_obj, e.g. 'CLc1'.
        get_obj_quantity : int or float
            The quanity of get_obj you wish to order.
        target_entry : dict
            The target entry price in the form of dict. 
            The keys are "Buy" and "Sell" to indicating the prices for 
            the two directions
        target_exit : dict
            The target exit price in the form of dict.
            The keys are "Buy" and "Sell" to indicating the prices for 
            the two directions
        stop_exit : dict
            The stop loss price in the form of dict.
            The keys are "Buy" and "Sell" to indicating the prices for 
            the two directions
        open_hr : str
            The opening hour of the trade
        close_hr : str
            The closing hour of the trade
        direction : str
            The default is "Buy"

        Returns
        -------
        EES_dict, trade_open, trade_close, pos_list, exec_pos_list

        """
        target_entry_buy =  target_entry['Buy']
        target_exit_buy = target_exit['Buy']
        stop_exit_buy = stop_exit['Buy']
        
        target_entry_sell = target_entry['Sell']
        target_exit_sell = target_exit['Sell']
        stop_exit_sell = stop_exit['Sell']
        
        #Find the minute that the price crosses the EES values
        EES_dict_buy = read.find_minute_EES(day, 
                                            target_entry_buy, 
                                            target_exit_buy, 
                                            stop_exit_buy,
                                            open_hr=open_hr, 
                                            close_hr=close_hr, 
                                            direction = 'Buy')
        
        EES_dict_sell = read.find_minute_EES(day, 
                                             target_entry_sell, 
                                             target_exit_sell, 
                                             stop_exit_sell,
                                             open_hr=open_hr, 
                                             close_hr=close_hr, 
                                             direction = 'Sell')
    

        EES_buy_target_list = [target_entry_buy, target_exit_buy, 
                               stop_exit_buy, EES_dict_buy['close'][1]] 
        EES_sell_target_list = [target_entry_sell, target_exit_sell, 
                               stop_exit_sell, EES_dict_sell['close'][1]] 

        
        # Note that the trading for Buy and Sell directions are executed 
        # independently (in Parallel). Therefore, the resulting Portfolio
        # pool and position pool are not going to be sorted perfectly by 
        # entry time.
        trade_id_buy = 'Buy' + str(trade_id)
        trade_id_sell = 'Sell' + str(trade_id) 
        # Buy
        pos_list_buy = self.open_positions(give_obj_name, get_obj_name, \
                                           get_obj_quantity, 
                                           EES_buy_target_list, \
                                           pos_type='Long', 
                                           size=SIZE_DICT[get_obj_name],
                                           fee=fee, 
                                           open_time = open_time,
                                           trade_id= trade_id_buy)
            
        trade_open_buy, trade_close_buy,\
        pos_list_buy, exec_pos_list_buy = self.execute_positions(EES_dict_buy, 
                                                                 pos_list_buy,
                                                                 pos_type='Long')
        
        # Sell
        pos_list_sell = self.open_positions(give_obj_name, get_obj_name, \
                                            get_obj_quantity, 
                                            EES_sell_target_list, \
                                            pos_type='Short', 
                                            size=SIZE_DICT[get_obj_name],
                                            fee=fee, 
                                            open_time = open_time,
                                            trade_id= trade_id_sell)

        trade_open_sell, trade_close_sell,\
        pos_list_sell, exec_pos_list_sell = self.execute_positions(EES_dict_sell, 
                                                                   pos_list_sell,
                                                                   pos_type='Short')
                                        
        # Now Bundle all the data together
        EES_dict, \
        trade_open, trade_close, \
        pos_dict, exec_pos_dict = dict(), dict(), dict(), dict(), dict()
        
        EES_dict['Buy'], EES_dict['Sell']  = EES_dict_buy, EES_dict_sell
        trade_open['Buy'], trade_open['Sell'] = trade_open_buy, trade_open_sell
        trade_close['Buy'], trade_close['Sell'] = trade_close_buy, trade_close_sell
        
        pos_dict['Buy'], pos_dict['Sell'] = pos_list_buy, pos_list_sell
        exec_pos_dict['Buy'], exec_pos_dict['Sell'] = exec_pos_list_buy, exec_pos_list_sell
                                        
        return EES_dict, trade_open, trade_close, pos_dict, exec_pos_dict

    
class OneTradePerDay_2(Trade):
    """
    A class that perform one trade per day, the simplest form of trading.
    
    Four possible outcomes:
    1) Find the earliest entry point in the price action chart, 
    2) exit the position  as soon as the price it the target entry. 
    3) If the price hit the stop loss first, exit at stop loass. 
    4) If netiher the target exit nor the stop loss is hit, exit the trade 
        at the closing hour.
        
    """
    def __init__(self, 
                 portfolio: Portfolio, 
                 trade_id: int=0):
        
        super().__init__(portfolio)
        self.trade_id = trade_id
        self.pos_dict = dict()
        self.exec_pos_dict = dict()
        self.extra_pos_dict = dict()
        self.extra_exec_pos_dict = dict()

        self.key_pos_dict = None
        self.extra_key_pos_dict = None
        
        self.EES_type = None
        self.EES_para_num = 1
        
    def store_to_position_pool(self, 
                               key_dict: dict, 
                               pos_dict: dict,
                               exec_pos_dict: dict) -> None:
        # Choose whether to save all positions or just to filled ones.
        if self.save_only_exec_pos:
            key_dict = exec_pos_dict
        else:
            key_dict = pos_dict
            
         # Add position in the position book
        for pos in list(key_dict.values()):
            self._portfolio._position_pool.append(copy.copy(pos))
                     
    @staticmethod
    def choose_EES_values(EES_dict: dict) -> tuple[tuple, tuple, tuple, tuple]:
        """
        A method to find the appropiate EES values of the day. 
        In the case of one trade per day, we only search for the earliest exit
        and stop loss price after entry price was hit.
        
        You may supply either a EES_dict from 
        
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
                        #print('earliest_exit', earliest_exit)
                        break

            if len(EES_dict['stop']) > 0:
                # Finde stop loss point candidates
                for i, stop_cand in enumerate(EES_dict['stop']):
                    if stop_cand[0] > entry_pt[0]:
                        earliest_stop = stop_cand
                        #print('earliest_stop', earliest_stop)
                        break
            
            # put in the new exit and stop
            exit_pt = earliest_exit
            stop_pt = earliest_stop

        return entry_pt, exit_pt, stop_pt, close_pt
    
    def open_positions(self, 
                       give_obj_name: str, 
                       get_obj_name: str, 
                       get_obj_quantity: int | float, 
                       EES_target_list: list, 
                       pos_type: str,
                       pos_dict: dict,
                       size: int | float = 1, 
                       fee: dict = None, 
                       open_time: datetime.datetime = datetime.datetime.now())\
                       -> list[Position]:
        """
        A method to open the entry, exit, stop, and close positions.

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
        pos_dict : dict
            The position list: [entry_pos, exit_pos, stop_pos, close_pos].

        """
        if pos_type == 'Long':
            pos_type1 = 'Long-Buy'
            pos_type2 = 'Long-Sell'

        elif pos_type == 'Short':
            pos_type1 = 'Short-Borrow'
            pos_type2 = 'Short-Buyback'
            
        # a method that execute the one trade per day based on the cases of the EES
        entry_price, exit_price = EES_target_list[0], EES_target_list[1]
        stop_price, close_price = EES_target_list[2], EES_target_list[3]
        
        #### Collapse all these into an add_position function
        # Make positions for initial price estimation
        entry_pos = super().add_position(give_obj_name, get_obj_name, 
                                         get_obj_quantity, entry_price, 
                                         size = size, fee = None, 
                                         pos_type = pos_type1,
                                         open_time=open_time,
                                         trade_id=self.trade_id)

        exit_pos = super().add_position(give_obj_name, get_obj_name, 
                                        get_obj_quantity, exit_price, 
                                        size = size, fee = fee, 
                                        pos_type = pos_type2,
                                        open_time=open_time,
                                        trade_id=self.trade_id)

        stop_pos = super().add_position(give_obj_name, get_obj_name, 
                                        get_obj_quantity, stop_price, 
                                        size = size, fee = fee, 
                                        pos_type = pos_type2,
                                        open_time=open_time,
                                        trade_id=self.trade_id)
        
        # Store the positions in the position dictionary pos_dict
        pos_dict['entry_pos'] = entry_pos
        pos_dict['exit_pos'] = exit_pos
        pos_dict['stop_pos'] = stop_pos
            
        if self.close_exit_or_not == True: 
            close_pos = super().add_position(give_obj_name, get_obj_name, 
                                             get_obj_quantity, close_price,
                                             size = size, fee = fee, 
                                             pos_type = pos_type2,
                                             open_time=open_time,
                                             trade_id=self.trade_id)
            pos_dict['close_pos'] = close_pos

        return pos_dict
    
    def choose_positions(self, 
                         trunc_dict: dict, 
                         pos_dict: dict, 
                         exec_pos_dict: dict):
        print("choose_positions")
        # Search for the appropiate time for entry, exit, stop loss,
        # and close time for the trade        
        entry_pt, exit_pt, stop_pt, close_pt = self.choose_EES_values(trunc_dict)

        # initialise trade_open and trade_close time and prices
        trade_open, trade_close = (np.nan,np.nan), (np.nan,np.nan)
        opening_pos, closing_pos = None, None
        
        # pack the outputs objects into dict
        exec_pos_dict['opening_pos'] = opening_pos
        exec_pos_dict['closing_pos'] = closing_pos
        
        # Run diagnosis to decide which outcome it is for the day
        # Case 1: No trade because entry is not hit
        if entry_pt == (np.nan,np.nan):
            #print("No trade.")
            # Cancel all order positions in a loop
            for pos in list(pos_dict.values()):
                ExecutePosition(pos).cancel_pos(void_time=close_pt[0])
            
            return trade_open, trade_close
            
        # Case 2: An exit is hit, normal exit
        elif entry_pt and exit_pt != (np.nan,np.nan):
            #print("Noraml exit.")
            trade_open, trade_close = entry_pt, exit_pt
            opening_pos, closing_pos = pos_dict['entry_pos'], pos_dict['exit_pos']

            # change the closing price
            closing_pos.price = round(exit_pt[1],9)
            
            # Cancel all order positions
            ExecutePosition(pos_dict['stop_pos']).cancel_pos(void_time = 
                                                                  trade_close[0])
            
            if self.close_exit_or_not: 
                ExecutePosition(pos_dict['close_pos']).cancel_pos(void_time = 
                                                                       trade_close[0])  

        # Case 3: stop loss
        elif exit_pt== (np.nan,np.nan) and stop_pt != (np.nan,np.nan):
            #print('Stop loss.')
            trade_open, trade_close = entry_pt, stop_pt
            opening_pos, closing_pos = pos_dict['entry_pos'], pos_dict['stop_pos']
            #print("Before price adjustment", opening_pos, closing_pos)

            # change the closing price
            closing_pos.price = round(stop_pt[1],9)
            
            # Cancel all order positions
            ExecutePosition(pos_dict['exit_pos']).cancel_pos(void_time = 
                                                                  trade_close[0])
            
            if self.close_exit_or_not: 
                ExecutePosition(pos_dict['close_pos']).cancel_pos(void_time = 
                                                                       trade_close[0])  
            
        # Case 4: Neither an exit or stop loss is hit, exit position at close time
        elif exit_pt== (np.nan,np.nan) and stop_pt == (np.nan,np.nan):
            #print("Sell at close.")
            trade_open = entry_pt
            opening_pos = pos_dict['entry_pos']
            #print("Before price adjustment", opening_pos, closing_pos)

            
            # Cancel all order positions
            ExecutePosition(pos_dict['stop_pos']).cancel_pos(void_time=
                                                                  trade_close[0])
            ExecutePosition(pos_dict['exit_pos']).cancel_pos(void_time=
                                                                  trade_close[0])
            if self.close_exit_or_not:
                trade_close = close_pt
                closing_pos = pos_dict['close_pos']
                
                # change the closing price
                closing_pos.price = round(close_pt[1],9)
                
        # pack the outputs objects into dict
        exec_pos_dict['opening_pos'] = opening_pos
        exec_pos_dict['closing_pos'] = closing_pos
        
        return trade_open, trade_close
    
    def execute_positions(self, 
                          trunc_dict: dict, 
                          pos_type: str = "Long"):
                          
        """
        A method that execute the a list posiiton given a EES_dict.
        It search the EES_dict the find the appropiate entry, exit, stop loss,
        and close time for the trade.

        Parameters
        ----------
        trunc_dict : dict
            A truncation dictionary for all possible EES values.
        pos_dict : dict
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

        #print(pos_dict.values(), type(pos_dict.values()))
        trade_open, trade_close = self.choose_positions(trunc_dict, self.pos_dict, 
                                                        self.exec_pos_dict)

        # Execute the open position
        if self.exec_pos_dict['opening_pos'] != None:
            self.exec_pos_dict['opening_pos'].price = trade_open[1]
            ExecutePosition(self.exec_pos_dict['opening_pos']).fill_pos(
                                                     fill_time = trade_open[0], 
                                                     pos_type=pos_type1)
         
        # Execute the closing position
        if self.exec_pos_dict['closing_pos'] != None:
            #print("closing_pos_testest_Before",closing_pos)
            #print("closing_pos_testest",self.pos_dict['exit_pos'])
            ExecutePosition(self.exec_pos_dict['closing_pos']).fill_pos(
                                                    fill_time = trade_close[0], 
                                                    pos_type=pos_type2)
            ##print("closing_pos_testest_After",closing_pos)
            #print("closing_pos_testest",pos_dict['exit_pos'])

        self.store_to_position_pool(key_dict = self.key_pos_dict, 
                                    pos_dict = self.pos_dict,
                                    exec_pos_dict = self.exec_pos_dict)

        return trade_open, trade_close, self.pos_dict, self.exec_pos_dict
    
    def execute_extra_positions(self, 
                                trunc_dict: dict, 
                                extra_pos_type: str = "Long"):
        # This method does not require entry because we already have something
        # Assume you already have some thing in the Portfolio and want to unload them
        # The function of execute_extra_positions is connected to execute_positions
        # If the conditions of execute_positions is triggered, and if auto_unload_all
        # is turned on, this function will unload
        if extra_pos_type == 'Long':
            # For extra position, Long-Buy is omitted, this variable does not matter
            pos_type1 = 'Long-Buy' 
            # Only Long-Sell is done to unload existing assets
            pos_type2 = 'Long-Sell'

        elif extra_pos_type == 'Short':
            # For extra position in Short, the first action is to sell your 
            # extra assets, thus it is a 'Long-Sell'
            pos_type1 = 'Long-Sell' 
            # The second action is to Buyback. But because there is no debt 
            # involved, it is a 'Long-Buy', instead of 'Short-Buyback'.
            # Alternatively, because this is autounload all, the second position is
            # irrelevant
            pos_type2 = 'Long-Buy' #


        # load all data from trunc_dict and choose opening_pos and closing_pos
        trade_open, trade_close = self.choose_positions(trunc_dict, 
                                                        self.extra_pos_dict, 
                                                        self.extra_exec_pos_dict)
        print("pos_type1, pos_type2", pos_type1, pos_type2)
        # For regular 'Long', the entry position is cancelled
        if extra_pos_type == 'Long' and\
            self.extra_exec_pos_dict['opening_pos'] != None:
            # cancel the open position
            self.extra_exec_pos_dict['opening_pos'].price = trade_open[1]
            ExecutePosition(self.extra_exec_pos_dict['opening_pos']).cancel_pos(\
                                                    void_time = trade_open[0])            
        elif extra_pos_type == 'Short' and\
             self.extra_exec_pos_dict['opening_pos'] != None:
            # Execute the open position
            self.extra_exec_pos_dict['opening_pos'].price = trade_open[1]
            ExecutePosition(self.extra_exec_pos_dict['opening_pos']).fill_pos(\
                                                    fill_time = trade_open[0], 
                                                    pos_type = pos_type1)
            
        
        # define the closing position and execute it if we set it to auto close
        if extra_pos_type == 'Long' and\
            self.extra_exec_pos_dict['closing_pos'] != None:            
            # Execute the closing position
            ExecutePosition(self.extra_exec_pos_dict['closing_pos']).fill_pos(
                                                    fill_time = trade_close[0], 
                                                    pos_type = pos_type2)
        elif extra_pos_type == 'Short' and\
            self.extra_exec_pos_dict['closing_pos'] != None:            
            # Execute the closing position
            ExecutePosition(self.extra_exec_pos_dict['closing_pos']).cancel_pos(
                                                    void_time = trade_close[0])
                
            
        self.store_to_position_pool(key_dict = self.extra_key_pos_dict, 
                                    pos_dict = self.extra_pos_dict,
                                    exec_pos_dict = self.extra_exec_pos_dict)

        return trade_open, trade_close, \
               self.extra_pos_dict, self.extra_exec_pos_dict 
    

    def run_trade(self, 
                  trunc_dict: dict, #day: pd.DataFrame, 
                  give_obj_name: str, 
                  get_obj_name: str, 
                  get_obj_quantity: float | int,
                  target_entry: float, 
                  target_exit: float, 
                  stop_exit: float,
                  open_hr: str = "0300", 
                  close_hr: str = "2000", 
                  direction: str = "Buy",
                  fee: dict =  OIL_FUTURES_FEE,
                  open_time: datetime.datetime = None) -> \
                  tuple[tuple, tuple, list, list]: 
        """

        Note that run_trade method is agnoistic to the loop type, i.e.,
        You can use LoopType.CROSSOVER, LoopType.RANGE, or LoopType.FULL

        Parameters
        ----------
        trunc_dict : dict
            Truncation dictionary. It contains the relevant points selected 
            by some given EES values or EES ranges.
            This assume you are running a crossover or range loop.
        give_obj_name : str
            The name of the give_obj, e.g. 'USD'.
        get_obj_name : str
            The name of the get_obj, e.g. 'CLc1'.
        get_obj_quantity : int or float
            The quanity of get_obj you wish to order.
        target_entry : float
            The target entry time and price.
        target_exit : float
            The exit entry time and price.
        stop_exit : float
            The stop loss time and price.
        open_hr : str
            The opening hour of the trade
        close_hr : str
            The closing hour of the trade
        direction : str
            The default is "Buy"

        Returns
        -------
        EES_dict, trade_open, trade_close, pos_list, exec_pos_list

        """
        
        #Find the minute that the price crosses the EES values
        # Input the position type
        if direction == 'Buy':
            pos_type= 'Long'
        elif direction == 'Sell':
            pos_type = 'Short'
            
        # Note that this is not the EES_dict object from find_minute_EES.
        # This is just an initial estimation of the EES values for the 
        # open_position function in the begining of the day. As the positions
        # are executed, the prices will change according to the data.
        EES_target_list = [target_entry, target_exit, 
                           stop_exit, trunc_dict['close'][1]] 
        
        # run the trade via position module
        pos_dict = self.open_positions(give_obj_name,
                                       get_obj_name, 
                                       get_obj_quantity, 
                                       EES_target_list, 
                                       pos_type=pos_type, 
                                       pos_dict=self.pos_dict,
                                       size=SIZE_DICT[get_obj_name],
                                       fee=fee, 
                                       open_time = open_time)
        
        if self.auto_unload_all == True: 
            extra_quantity = self._portfolio._remainder_dict[get_obj_name] 
            extra_pos_dict = self.open_positions(give_obj_name,
                                                 get_obj_name, 
                                                 extra_quantity, 
                                                 EES_target_list, 
                                                 pos_type=pos_type, 
                                                 pos_dict=self.extra_pos_dict,
                                                 size=SIZE_DICT[get_obj_name],
                                                 fee=fee, 
                                                 open_time = open_time)
            
        # Execute the positions. As the function is ran, it chooses the 
        # appropiate EES values based on the choose_EES_values method of 
        # this class
        trade_open, trade_close, \
        pos_dict, exec_pos_dict = self.execute_positions(trunc_dict,
                                                         pos_type = pos_type)
        
        if self.auto_unload_all == True: 
            extra_trade_open, extra_trade_close, \
            extra_pos_dict, extra_exec_pos_dict = self.execute_extra_positions(\
                                                                    trunc_dict, 
                                                                    extra_pos_type =\
                                                                    pos_type)
                
        # the search function for entry and exit time should be completely 
        # sepearate to the trading actions
        return trade_open, trade_close, pos_dict, exec_pos_dict           

# =============================================================================
# class MultiTradePerDay(Trade): # WIP
#     """
#     A class that perform multiple trade per day, the simplest form of trading.
#     
#     Four possible outcomes:
#     1) Find the earliest entry point in the price action chart, 
#     2) exit the position  as soon as the price it the target entry. 
#     3) If the price hit the stop loss first, exit at stop loass. 
#     4) If netiher the target exit nor the stop loss is hit, exit the trade 
#         at the closing hour.
#     But if the exit position is triggered, it find the next best open position.
#         
#     """
#     def __init__(self, portfolio):
#         #self.trade_or_not = True
#         super().__init__(portfolio)
#         
#     @staticmethod
#     def find_EES_values(self, EES_dict: dict):
#         return OneTradePerDay(self.portfolio).find_EES_values(EES_dict)
#     
#     def open_positions(self, give_obj_name, get_obj_name, 
#                        get_obj_quantity, EES_target_list, pos_type,
#                        size = 1, fee = None, 
#                        open_time = datetime.datetime.now()):
#         
#         if pos_type == 'Long':
#             pos_type1 = 'Long-Buy'
#             pos_type2 = 'Long-Sell'
# 
#         elif pos_type == 'Short':
#             pos_type1 = 'Short-Borrow'
#             pos_type2 = 'Short-Buyback'
#             
#         # a method that execute the one trade per day based on the cases of the EES
#         entry_price, exit_price = EES_target_list[0], EES_target_list[1]
#         stop_price, close_price = EES_target_list[2], EES_target_list[3]
#         
#         #### Collapse all these into an add_position function
#         # Make positions for initial price estimation
#         entry_pos = super().add_position(give_obj_name, get_obj_name, 
#                                       get_obj_quantity, entry_price, 
#                                       size = size, fee = None, 
#                                       pos_type = pos_type1,
#                                       open_time=open_time)
# 
#         exit_pos = super().add_position(give_obj_name, get_obj_name, 
#                           get_obj_quantity, exit_price, 
#                           size = size, fee = fee, 
#                           pos_type = pos_type2,
#                           open_time=open_time)
# 
#         stop_pos = super().add_position(give_obj_name, get_obj_name, 
#                           get_obj_quantity, stop_price, 
#                           size = size, fee = fee, 
#                           pos_type = pos_type2,
#                           open_time=open_time)
#         
#         close_pos = super().add_position(give_obj_name, get_obj_name, 
#                           get_obj_quantity, close_price,
#                           size = size, fee = fee, 
#                           pos_type = pos_type2,
#                           open_time=open_time)
# 
#         pos_list = [entry_pos, exit_pos, stop_pos, close_pos]
# 
#         return pos_list
#         
#     
#     def execute_position(self, EES_dict, pos_list, pos_type="Long"):
#         # A method that search for correct EES points from a EES_dict
#         
#         # initialise
#         entry_pt, exit_pt = (np.nan,np.nan), (np.nan,np.nan)
#         stop_pt, close_pt = (np.nan,np.nan), (np.nan,np.nan)
#         
#         earliest_exit, earliest_stop = exit_pt, stop_pt
#         
#         # closr_pt always exist so we do it outside of the switch cases
#         close_pt = EES_dict['close']
# 
#         # To get the correct EES and close time and price
#         if len(EES_dict['entry']) == 0: # entry price not hit. No trade that day.
#             pass
#         else:
#             # choose the entry point
#             entry_pt = EES_dict['entry'][0]
#             
#             if len(EES_dict['exit']) > 0:
#                 # Find exit point candidates
#                 for i, exit_cand in enumerate(EES_dict['exit']):  
#                     if exit_cand[0] > entry_pt[0]:
#                         earliest_exit = exit_cand
#                         #print('earliest_exit', earliest_exit)
#                         break
# 
#             if len(EES_dict['stop']) > 0:
#                 # Finde stop loss point candidates
#                 for i, stop_cand in enumerate(EES_dict['stop']):
#                     if stop_cand[0] > entry_pt[0]:
#                         earliest_stop = stop_cand
#                         #print('earliest_stop', earliest_stop)
#                         break
#             
#             # put in the new exit and stop
#             exit_pt = earliest_exit
#             stop_pt = earliest_stop
# 
#         return entry_pt, exit_pt, stop_pt, close_pt
#         
#     def run_trade(self, day, 
#                   give_obj_name, get_obj_name, 
#                   get_obj_quantity,
#                   target_entry, target_exit, stop_exit,
#                   open_hr="0300", close_hr="2000", 
#                   direction = "Buy",
#                   fee = {}):
#         
#         #Find the minute that the price crosses the EES values
#         EES_dict = read.find_minute_EES(day, 
#                                         target_entry, target_exit, stop_exit,
#                                         open_hr=open_hr, close_hr=close_hr, 
#                                         direction = direction)
#         
#         open_hr_dt = None
#     
#         # Input the position type
#         if direction == 'Buy':
#             pos_type= 'Long'
#         elif direction == 'Sell':
#             pos_type = 'Short'
#             
# 
#         pos_list_bundle = []
#         for i in range(10):
#             open_hr_dt = None
#             EES_target_list = [target_entry, target_exit, 
#                                stop_exit, EES_dict['close'][1]] 
#             # run the trade via position module
#             pos_list = self.open_positions(give_obj_name, get_obj_name, \
#                                            get_obj_quantity, EES_target_list, \
#                                            pos_type=pos_type, 
#                                            size = SIZE_DICT[get_obj_name],
#                                            fee=fee, open_time = open_hr)
#                                                #open_time = open_hr_dt)  # add open time in position
#         
#         
#             trade_open, trade_close, pos_list, exec_pos_list = \
#                                             self.execute_position(EES_dict, pos_list,
#                                                                   pos_type=pos_type)
# 
#         # the search function for entry and exit time should be completely 
#         # sepearate to the trading actions
#         return EES_dict, trade_open, trade_close, pos_list, exec_pos_list 
#     
# 
#         
#         
# =============================================================================
        
# =============================================================================
#  under construction
# @dataclass
# class TradeBot:
#     
#     exchange: None
#     trading_startegy: None
#     
# =============================================================================
    