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

#from EC_tools.backtest import find_minute_EES

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

@dataclass
class Trade(object):

    def  __init__(self, portfolio=None):
        self.portfolio = portfolio


    def trade_choice_simple_portfolio(self, day, give_obj, get_obj, 
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
        
        #Find the minute that the price crosses the EES values
        EES_dict = find_minute_EES(day, target_entry, target_exit, stop_exit,
                          open_hr=open_hr, close_hr=close_hr, 
                          direction = direction)
        
        # initialise trade_open and trade_close time and prices
        trade_open, trade_close = (np.nan,np.nan), (np.nan,np.nan)
        
        # make give and get objects here
        
        
        # Start the position
        entry_pos = Position(random_string(), give_obj, get_obj, EES_dict['entry'][0], 
                                                     portfolio= self.portfolio)
        exit_pos = Position(random_string(), get_obj, give_obj, EES_dict['exit'][0], 
                                                    portfolio= self.portfolio) 
        stop_pos = Position(random_string(), get_obj, give_obj, EES_dict['stop'], 
                                                    portfolio= self.portfolio)
        close_pos = Position(random_string(), get_obj, give_obj, EES_dict['close'], 
                                                     portfolio= self.portfolio)
        
        # To get the correct EES and close time and price
        if len(EES_dict['entry']) == 0: # entry price not hit. No trade that day.
            pass
        else:
            # choose the entry point
            trade_open = EES_dict['entry'][0]
            
            # Open position here
            ExecutePosition(entry_pos).fill_pos()
            
            if len(EES_dict['stop']) == 0: # if the stop loss wasn't hit
                pass
            else:
                trade_close = EES_dict['stop'][0] #set the trade close at stop loss
                
                ExecutePosition(stop_pos).fill_pos()
                
                # Cancel all order positions
                ExecutePosition(exit_pos).cancel_pos()
                ExecutePosition(close_pos).cancel_pos()

                
            if len(EES_dict['exit']) == 0:
                trade_close = EES_dict['close']
                
                ExecutePosition(close_pos).fill_pos()
                
                # Cancel all order positions
                ExecutePosition(stop_pos).cancel_pos()
                ExecutePosition(exit_pos).cancel_pos()
                
            else:
                # make sure the exit comes after the entry point
                for i, exit_cand in enumerate(EES_dict['exit']):  
                    if exit_cand[0] > trade_open[0]:
                        trade_close = exit_cand
                        
                        ExecutePosition(exit_pos).fill_pos()
                        
                        # Cancel all order positions
                        ExecutePosition(stop_pos).cancel_pos()
                        ExecutePosition(close_pos).cancel_pos()     
                        
                        break
                    else:
                        pass
                    
        return trade_open, trade_close
            
                    
        # Perform the trade action on the Portfolio

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
    