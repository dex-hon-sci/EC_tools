#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug  7 16:48:40 2024

@author: dexter
"""
from typing import Protocol # use protocol for trade class
import numpy as np

__author__ = "Dexter S.-H. Hon"
__all__ = ['onetrade_simple_LEGACY', 'onetrade_simple']

def onetrade_simple_LEGACY(EES_dict: dict) -> tuple[tuple, tuple]: 
    """
    LEGACY code before the development of trade and portfolio modules
    a function that control which price to buy and sell.
    
    The trade logic is incorrect in this one (It hit the stop-loss automatically)

    Parameters
    ----------
    EES_dict : dict
        A dictionary containing the points that crosses over the Entry, Exit, 
        and Stop Loss points (EES), as well as the closing time and price of
        the trading day.
        This should be the output of find_minute_EES from EC_tools.read module.

    Returns
    -------
    tuple
        Two tuples containing rhe trade open and trade close in the format of 
        (time. price).

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
    

def onetrade_simple(EES_dict: dict) -> tuple[tuple, tuple]: 
    """
    A simple trading method that returns a pair of trade open and close time
    as long as the price. 
    
    Parameters
    ----------
    EES_dict : dict
        A dictionary containing the points that crosses over the Entry, Exit, 
        and Stop Loss points (EES), as well as the closing time and price of
        the trading day.
        This should be the output of find_minute_EES from EC_tools.read module.

    Returns
    -------
    tuple
        Two tuples containing rhe trade open and trade close in the format of 
        (time. price).
    """
    entry_pt, exit_pt, stop_pt, close_pt = (np.nan,np.nan), (np.nan,np.nan),\
                                           (np.nan,np.nan), (np.nan,np.nan)
    
    earliest_exit, earliest_stop = exit_pt, stop_pt
    
    # closr_pt always exist so we do it outside of the switch cases
    close_pt = EES_dict['close']
    
    if close_pt == (np.nan,np.nan):
        print('no close WTF', EES_dict['entry'])
        print(type(close_pt), close_pt)
    
    # To get the correct EES and close time and price
    if len(EES_dict['entry']) == 0: # entry price not hit. No trade that day.
        #print('no entry', EES_dict['entry'], close_pt)
        trade_open, trade_close =  (np.nan,np.nan), (np.nan,np.nan)
        
    else:
        # choose the entry point
        entry_pt = EES_dict['entry'][0]
        trade_open = entry_pt

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
        #print('SSC_key', exit_pt, stop_pt, close_pt)
        
        #see which points comes the earliest
        if exit_pt == (np.nan,np.nan) and stop_pt == (np.nan,np.nan):
            #print('both null')
            trade_close = close_pt
        elif exit_pt != (np.nan,np.nan) and stop_pt == (np.nan,np.nan):
            trade_close = exit_pt
            #print('stop null')

        elif exit_pt == (np.nan,np.nan) and stop_pt != (np.nan,np.nan):
            trade_close = stop_pt
            #print('exit null')

        elif exit_pt != (np.nan,np.nan) and stop_pt != (np.nan,np.nan):
            if exit_pt[0] >= stop_pt[0]:
                #print('stop loss')
                trade_close = stop_pt
            elif exit_pt[0] < stop_pt[0]:
                #print('exit')
                trade_close = exit_pt
        else:
            raise Exception("WTF")

    if trade_open != (np.nan,np.nan) and trade_close == (np.nan,np.nan):
        raise Exception('trade WTF {},{}'.format(trade_open, trade_close))
        
    #print('trade', trade_open, trade_close, type(trade_open), type(trade_close))
    return trade_open, trade_close