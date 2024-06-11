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
from typing import Protocol

import EC_tools.portfolio as port
from EC_tools.position import Position, ExecutePosition
from EC_tools.utility import random_string
from EC_tools.portfolio import Asset

def find_crossover(input_array, threshold):
    """
    A function that find the crossover points' indicies. It finds the points right
    after either rise above, or drop below the threshold value.
    
    Parameters
    ----------
    input_array : numpy array
        A 1D numpy array with only numbers.
    threshold : float, list, numpy array
        the threshold value.

    Returns
    -------
    dict
        The 'rise' value contains a numpy array containing the indicies of 
        points that rise above the the threshold.
        The 'drop' value contains a numpy array containing the indicies of 
        points that drop below the the threshold.

    """
    if type(threshold) == str:
        # make a numpy array of the threshold value    
        threshold = np.repeat(threshold, len(input_array)) 
    elif (type(threshold) == list or type(threshold) == np.ndarray) and \
                                        len(threshold) != len(input_array):
        raise Exception("Mismatch input and threshold arraty length.")
    elif type(threshold) == list and len(threshold) == len(input_array):
        # make a numpy array of the threshold value    
        threshold = np.array(threshold)
    elif type(threshold) == np.ndarray and len(threshold) == len(input_array):
        pass
    
    # The difference between the input value and the threshold number
    # Positive values mean the input is higher than threshold
    # Negative values mean the input is lower than threshold
    delta = input_array - threshold
    
    # This is an array 1 unit in the past
    #delta_lag = np.concatenate([delta, np.array([np.nan])])[1:]
    delta_lag = np.concatenate([np.array([np.nan]), delta])[:-1]
    
    # IF delta[i] > delta_lag[i], then the price rise above threshold
    # Because all elements are either +1, -1 or 0, the larger value has to be +1.
    # np.sign(delta) = +1, while np.sign(delta_lag) = -1 means yesterday the value 
    # is lower than threshold and today's value is higher than the threshold-> rise above
    indices_rise_above  = np.where(np.sign(delta) > np.sign(delta_lag))
    
    # IF delta[i] < delta_lag[i], then the price drop below threshold
    indices_drop_below = np.where(np.sign(delta) < np.sign(delta_lag))

    # Produce a dic of indicies for below and above
    return {'rise': indices_rise_above, 
            'drop': indices_drop_below}

def find_minute_EES(histroy_data_intraday, 
                      target_entry, target_exit, stop_exit,
                      open_hr="0330", close_hr="1930", 
                      price_approx = 'Open', time_proxy= 'Time',
                      direction = 'Neutral',
                      close_trade_hr='1925'):
    """
    Set the EES value given a minute intraday data.

    Parameters
    ----------
    histroy_data_intraday : dataframe
        The histort intraday minute data. This assume the file contains the 
        ohlc value of the day
    target_entry : float 
        target entry price.
    target_exit : float
        target exit price.
    stop_exit : float
        target stop loss price.
    open_hr : str, optional
        The opening hour of trade in military time format. 
        The default is "0330".
    close_hr : str, optional
        The closing hour of trade in military time format. 
        The default is "1930".
    price_approx : str, optional
        The price approximator. The default uses the opening price of each 
        minute as the price indicator. It calls in the 'Open' column in the 
        history intradday minute dataframe
        The default is 'Open'.
    time_prox: 
        The time proxy. This function assume the input time data come fomr the 
        'Time' column of the dataframe. 
        The default is 'Time'.
    direction : str, optional
        Trade direction. Either "Buy", "Sell", or "Neutral".
        The default is 'Neutral'.
    close_trade_hr : str, optional
        The final minute to finish off the trade in military time format. 
        The default is '1925'.

    Raises
    ------
    ValueError
        Direction data can only be either "Buy", "Sell", or "Neutral".

    Returns
    -------
    EES_dict : dict
        A dictionary that cantains the possible EES points and time.

    """
    
    # define subsample. turn the pandas series into a numpy array
    price_list = histroy_data_intraday[price_approx].to_numpy()
    time_list = histroy_data_intraday[time_proxy].to_numpy()
    
    date_list = histroy_data_intraday['Date'].to_numpy()
    
    # Find the crossover indices
    entry_pt_dict = find_crossover(price_list, target_entry)
    exit_pt_dict = find_crossover(price_list, target_exit)
    stop_pt_dict = find_crossover(price_list, stop_exit)
    
    if direction == "Neutral":
        print("Neutral")
        # for 'Neutral' action, all info are empty
        entry_pts = []
        entry_times = []
            
        exit_pts = []
        exit_times = []
        
        stop_pts = []
        stop_times = []
    
    elif direction == "Buy":
        print("Buy")
        # for 'Buy' action EES sequence is drop,rise,drop
        entry_pts = price_list[entry_pt_dict['drop'][0]]
        entry_times = time_list[entry_pt_dict['drop'][0]]
            
        exit_pts = price_list[exit_pt_dict['rise'][0]]
        exit_times = time_list[exit_pt_dict['rise'][0]]
        
        stop_pts = price_list[stop_pt_dict['drop'][0]]
        stop_times = time_list[stop_pt_dict['drop'][0]]
            
    elif direction == "Sell":
        print("Sell")
        # for 'Sell' action EES sequence is rise,drop,rise
        entry_pts = price_list[entry_pt_dict['rise'][0]]
        entry_times = time_list[entry_pt_dict['rise'][0]]
            
        exit_pts = price_list[exit_pt_dict['drop'][0]]
        exit_times = time_list[exit_pt_dict['drop'][0]]
        
        stop_pts = price_list[stop_pt_dict['rise'][0]]
        stop_times = time_list[stop_pt_dict['rise'][0]]
    else:
        raise ValueError('Direction has to be either Buy, Sell, or Neutral.')
    
    # Define the closing time and closing price. Here we choose 19:25 for final trade
    #close_time = datetime.time(int(close_trade_hr[:2]),int(close_trade_hr[2:]))
    close_time = close_hr #quick fix. need some work
    close_pt = price_list[np.where(time_list==close_time)[0]][0]
        
    # storage
    EES_dict = {'entry': list(zip(entry_times,entry_pts)),
                'exit': list(zip(exit_times,exit_pts)),
                'stop': list(zip(stop_times,stop_pts)),
                'close': list((close_time, close_pt)) }

    #print('EES_dict', EES_dict)
    return EES_dict


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


class OneTradePerDay(object):
    
    def  __init__(self, portfolio=None):
        self.portfolio = portfolio

    def long():
        return
    
    def short():
        return
    
class Trade(object):

    def  __init__(self, portfolio=None):
        self.portfolio = portfolio

    @staticmethod
    def find_pt_one_trade_per_day(EES_dict):
        # A method that search for correct EES points from a EES_dict
        entry_pt, exit_pt = (np.nan,np.nan), (np.nan,np.nan)
        stop_pt, close_pt = (np.nan,np.nan), (np.nan,np.nan)
        
        earliest_exit, earliest_stop = exit_pt, stop_pt
        # To get the correct EES and close time and price
        if len(EES_dict['entry']) == 0: # entry price not hit. No trade that day.
            pass
        else:
            # choose the entry point
            entry_pt = EES_dict['entry'][0]
            close_pt = EES_dict['close']
            
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
    
    def run_one_trade_per_day(self, 
                                    entry_price, exit_price, stop_price, close_price, 
                                    entry_pt, exit_pt, stop_pt, close_pt,
                                                give_obj_str_dict, get_obj_str_dict, 
                                                get_obj_quantity, pos_type):
        # a method that execute the one trade per day based on the cases of the EES
        
        # initialise trade_open and trade_close time and prices
        trade_open, trade_close = (np.nan,np.nan), (np.nan,np.nan)
        opening_pos, closing_pos = None, None
        
        give_obj_name = give_obj_str_dict['name']
        give_obj_unit = give_obj_str_dict['unit']
        give_obj_type = give_obj_str_dict['type']
        
        get_obj_name = get_obj_str_dict['name']
        get_obj_unit = get_obj_str_dict['unit']
        get_obj_type = get_obj_str_dict['type']
        
        
        # Make positions for initial price estimation
        print('==entry==')
        get_obj_entry = Asset(get_obj_name, get_obj_quantity, get_obj_unit, get_obj_type)
        give_obj_entry = Asset(give_obj_name, entry_price*get_obj_quantity, 
                            give_obj_unit, give_obj_type)

        print('amount',entry_price, get_obj_quantity,get_obj_quantity*entry_price)
        print('entry_price', give_obj_entry.quantity/get_obj_entry.quantity, entry_price)

        entry_pos = Position(give_obj_entry, get_obj_entry, entry_price,
                                                 portfolio= self.portfolio)
        print('==exit==')
        get_obj_exit = Asset(get_obj_name, get_obj_quantity, 
                             get_obj_unit, get_obj_type)
        give_obj_exit= Asset(give_obj_name, get_obj_quantity*exit_price, 
                            give_obj_unit, give_obj_type)
        
        exit_pos = Position(get_obj_exit, give_obj_exit, 1.0/exit_price, 
                                                    portfolio= self.portfolio) 
        
        print('amount', exit_price, get_obj_quantity,get_obj_quantity*exit_price)
        print('exit_price', give_obj_exit.quantity/get_obj_exit.quantity, exit_price)
        print('quantity', get_obj_exit.quantity, give_obj_exit.quantity)

        print('==stop==', get_obj_quantity)
        get_obj_stop = Asset(get_obj_name, get_obj_quantity,
                             get_obj_unit, get_obj_type)
        give_obj_stop = Asset(give_obj_name, get_obj_quantity*stop_price, 
                            give_obj_unit, give_obj_type)
        
        stop_pos = Position(get_obj_stop, give_obj_stop, 1.0/stop_price, 
                                                    portfolio= self.portfolio)
        
        print('amount', stop_price, get_obj_quantity,get_obj_quantity*stop_price)
        print('stop_price', give_obj_stop.quantity/get_obj_stop.quantity, stop_price)
        print('quantity', get_obj_stop.quantity, give_obj_stop.quantity)
        
        print('==close==')
        get_obj_close = Asset(get_obj_name, get_obj_quantity,
                              get_obj_unit, get_obj_type)
        give_obj_close = Asset(give_obj_name, get_obj_quantity*close_price, 
                            give_obj_unit, give_obj_type)
        
        close_pos = Position(get_obj_close, give_obj_close, 1.0/close_price, 
                                                     portfolio= self.portfolio)
        
        print('amount', close_price, get_obj_quantity,get_obj_quantity*close_price)
        print('exit_price',give_obj_close.quantity/get_obj_close.quantity, close_price)
        print('quantity', get_obj_close.quantity, give_obj_close.quantity)

        print('=========')
        
        # Execute the position based on different scenario
        # change the price from the initial position to the closest price 
        # estimation

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
            closing_pos.price = round(1/exit_pt[1],2)
            
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
            closing_pos.price = round(1/stop_pt[1],2)
            
            # Cancel all order positions
            ExecutePosition(exit_pos).cancel_pos(void_time= trade_close[0])
            ExecutePosition(close_pos).cancel_pos(void_time= trade_close[0])  
            
            
        elif exit_pt== (np.nan,np.nan) and stop_pt == (np.nan,np.nan):
            print("Sell at close")
            trade_open, trade_close = entry_pt, close_pt
            opening_pos, closing_pos = entry_pos, close_pos

            # change the closing price
            closing_pos.price = round(1/close_pt[1],2)
            
            # Cancel all order positions
            ExecutePosition(stop_pos).cancel_pos(void_time=trade_close[0])
            ExecutePosition(exit_pos).cancel_pos(void_time=trade_close[0])
            
        opening_pos.price = entry_pt[1]
        # Execute the positions
        ExecutePosition(opening_pos).fill_pos(fill_time = trade_open[0], 
                                            pos_type=pos_type)
        
        ExecutePosition(closing_pos).fill_pos(fill_time = trade_close[0], 
                                           pos_type=pos_type)
        return trade_open, trade_close
    
    def trade_choice_simple_portfolio(self, day, 
                                      give_obj_str_dict, get_obj_str_dict, 
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
        
        # Add new position into the pending list
                
        # establish a pending positions. 
        # Create three main positions into the pending list
        
        # Entry (1, asset_A, asset_B, price(A to B))
        # Exit  (2, asset_B, asset_A, price_target(B to A))
        # Stop  (3, asset_B, asset_A, price_exit(B to A))
        
        # At the closing hour. Open an additional position like this one
        # Close (4, asset_B , asset_A, price_close(B to A))
        
        # IF no entry price, void all four positions.
        
        # If entry price exist, entry price == price(A to B).
        # Then add Asset B, sub Asset A
        # Then change (1..) to resolved.
        # Make the pending positions here
        #################################################################
        
        #Find the minute that the price crosses the EES values
        EES_dict = find_minute_EES(day, target_entry, target_exit, stop_exit,
                          open_hr=open_hr, close_hr=close_hr, 
                          direction = direction)
        
        print('entry_exit', EES_dict['entry'], EES_dict['exit'], EES_dict['stop'], EES_dict['close'])
        
        # Define the EES points for one trade per day
        entry_pt, exit_pt, stop_pt, close_pt = self.find_pt_one_trade_per_day(
                                                                        EES_dict)
        print("entry_pt, exit_pt, stop_pt, close_pt", 
              entry_pt, exit_pt, stop_pt, close_pt)
        # Input the Asset objects

        # make give and get objects here
        # First define the get_obj because this is the target we are aimming at/
        # We then use the get_obj quantity to define the amount we give in the 
        # five_obj quantity

        pos_type= 'Long'
# =============================================================================
#         # Start the position
#         if direction == "Buy":
#             pos_type = 'Long'
#             # The quantity may be subjected to change because the entry price can 
#             # not always be hitted precisely. The position function will handle 
#             # the search for the closest proce during the crossover and readjust 
#             # the get_obj quantity.
#             give_obj= Asset(give_obj_name, target_entry*get_obj_quantity, 
#                             give_obj_unit, give_obj_type)target_entry
#             
#             entry_pos = Position(give_obj, get_obj, EES_dict['entry'][0][1], 
#                                                      portfolio= self.portfolio)
#         
#         elif direction == "Sell":
#             pos_type = 'Short'
#             give_obj= Asset(give_obj_name, -1*target_entry*get_obj_quantity, 
#                             give_obj_unit, give_obj_type, misc={'debt'})
#             
#             entry_pos = Position(give_obj, get_obj, EES_dict['entry'][0][1], 
#                                                      portfolio= self.portfolio)
# =============================================================================

        # run the trade via position module
        trade_open, trade_close = self.run_one_trade_per_day(
                                        target_entry, target_exit, stop_exit, close_pt[1],
                                        entry_pt, exit_pt, stop_pt, close_pt, 
                                        give_obj_str_dict, get_obj_str_dict,
                                        get_obj_quantity, pos_type)
        

        # the search function for entry and exit time should be completely sepearate to the trading actions
        return trade_open, trade_close, EES_dict            
                    

        def trade_choice_dynamic_1(self):
            return
        
        # Execute the Position here
        #ExecutePosition()
        
    
# =============================================================================
#  under construction
# @dataclass
# class TradeBot:
#     
#     exchange: None
#     trading_startegy: None
#     
# =============================================================================
    