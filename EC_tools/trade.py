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

import EC_tools.portfolio as port

# there are two ways to backtest strategies, 
# (1) is to loop through every unit time interval and make a judgement call
# (2) is collapsing the intraday data into a smaller set of data, search for 
#the point of interest and execute the trade

@dataclass
class Trade(object):

    def  __init__(self):
        self.trade_open =  (np.nan, np.nan) #(datetime.time, price)
        self.trade_close = (np.nan, np.nan)
        
    def trade_choice_simple(self, EES_dict): 
        # LEGACY code before the development of trade and portfolio modules
        # a function that control which price to buy and sell
        # Trading choice should be a class on its own. This is just a prototype.
        # I need a whole module of classes related to trade. to operate on portfolio and so on
        
        # add the amount of exchange
                
        # Trade logic
        if len(EES_dict['entry']) == 0: # entry price not hit. No trade that day.
            pass
        else:
            # choose the entry point
            self.trade_open = EES_dict['entry'][0]
            if len(EES_dict['stop']) == 0: # if the stop loss wasn't hit
                pass
            else:
                self.trade_close = EES_dict['stop'][0] #set the trade close at stop loss
                
            if len(EES_dict['exit']) == 0:
                self.trade_close = EES_dict['close']
            else:
                # make sure the exit comes after the entry point
                for i, exit_cand in enumerate(EES_dict['exit']):  
                    if exit_cand[0] > self.trade_open[0]:
                        self.trade_close = exit_cand
                        break
                    else:
                        pass
                    
        return self.trade_open, self.trade_close

    def trade_choice_simple_portfolio(self, EES_dict): 
        # Add new position into the pending list
        pos = port.Positions()
                
        # Trade logic
        if len(EES_dict['entry']) == 0: # entry price not hit. No trade that day.
            pass
        else:
            # choose the entry point
            self.trade_open = EES_dict['entry'][0]
            
            # Open position here
            
            if len(EES_dict['stop']) == 0: # if the stop loss wasn't hit
                pass
            else:
                self.trade_close = EES_dict['stop'][0] #set the trade close at stop loss
                
            if len(EES_dict['exit']) == 0:
                self.trade_close = EES_dict['close']
            else:
                # make sure the exit comes after the entry point
                for i, exit_cand in enumerate(EES_dict['exit']):  
                    if exit_cand[0] > self.trade_open[0]:
                        self.trade_close = exit_cand
                        break
                    else:
                        pass
                    
        return self.trade_open, self.trade_close
    
#(object, tradde_open, trade_closetrade_closetrade_close)

@dataclass
class TradeBot:
    
    exchange: None
    trading_startegy: None
    
    