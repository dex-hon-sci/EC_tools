#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug  7 16:48:40 2024

@author: dexter
"""
from typing import Protocol # use protocol for trade class
import datetime as datetime

import numpy as np
import pandas as pd

from EC_tools.position import Position, ExecutePosition
#from EC_tools.portfolio import Asset
import EC_tools.read as read
import EC_tools.utility as util


# there are two ways to backtest strategies, 
# (1) is to loop through every unit time interval and make a judgement call
# (2) is collapsing the intraday data into a smaller set of data, search for 
#the point of interest and execute the trade

def trade_choice_simple(EES_dict: dict) -> tuple[tuple, tuple]: 
    """
    LEGACY code before the development of trade and portfolio modules
    a function that control which price to buy and sell.

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
    

def trade_choice_simple_2(EES_dict: dict) -> tuple[tuple, tuple]: 
    
    entry_pt, exit_pt = (np.nan,np.nan), (np.nan,np.nan)
    stop_pt, close_pt = (np.nan,np.nan), (np.nan,np.nan)
    
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
        pass
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
            print('both null')
            trade_close = close_pt
        elif exit_pt != (np.nan,np.nan) and stop_pt == (np.nan,np.nan):
            trade_close = exit_pt
            print('stop null')

        elif exit_pt == (np.nan,np.nan) and stop_pt != (np.nan,np.nan):
            trade_close = stop_pt
            print('exit null')

        elif exit_pt != (np.nan,np.nan) and stop_pt != (np.nan,np.nan):
            if exit_pt[0] >= stop_pt[0]:
                print('stop loss')
                trade_close = stop_pt
            elif exit_pt[0] < stop_pt[0]:
                print('exit')
                trade_close = exit_pt
        else:
            raise Exception("WTF")

    if trade_open != (np.nan,np.nan) and trade_close == (np.nan,np.nan):
        print('trade', trade_open, trade_close)
        
    #print('trade', trade_open, trade_close, type(trade_open), type(trade_close))
    return trade_open, trade_close



def trade_choice_simple_3(EES_dict: dict) -> tuple[tuple, tuple]: 
    
    entry_pt, exit_pt = (np.nan,np.nan), (np.nan,np.nan)
    stop_pt, close_pt = (np.nan,np.nan), (np.nan,np.nan)
    
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
        pass
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