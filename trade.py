#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 10 00:16:28 2024

@author: dexter

A module that control trade action. The decision making logics are all stored 
here.
"""
import numpy as np

class Trade:

    def  __init__(self, trade_open=0, trade_close=0):
        self.trade_open =  trade_open
        self.trade_close = trade_close
        
    # tested
    def trade_choice_simple(EES_dict): 
        # a function that control which price to buy and sell
        # Trading choice should be a class on its own. This is just a prototype.
        # I need a whole module of classes related to trade. to operate on portfolio and so on
        
        # add the amount of exchange
        
        # if entry list = None, no trade that day
        # else, choose position x or a list of positions
        trade_open, trade_close = None, None
        
        if len(EES_dict['entry']) == 0: # entry price not hit. No trade that day.
            #print("NO ENTRYYYY")
            trade_open, trade_close = (np.nan, np.nan), (np.nan, np.nan)
    
            pass
        else:
            # choose the entry point
            trade_open = EES_dict['entry'][0]
            if len(EES_dict['stop']) == 0: # if the stop loss wasn't hit
                #print('stop loss NOT hit')
                pass
            else:
                trade_close = EES_dict['stop'][0] #set the trade close at stop loss
                #print('stop loss hit')
                
            if len(EES_dict['exit']) == 0:
                trade_close = EES_dict['close']
            else:
                # choose the exit point
                trade_close = EES_dict['exit'][0]
        
        return trade_open, trade_close