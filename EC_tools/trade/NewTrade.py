#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May  6 23:18:42 2025

@author: dexter

A trade is defined by a unique trade_id and can only work on one Portfolio.
It is also relevant to only one signal, i.e. one set of EES (Entry-Exit-StopLoss)
and its derivative (including dynamic TP and SL).

"""
from numpy import np
from EC_tools.trade import Trade

class NewTrade(Trade):
    def __init__(self, portfolio, 
                 trade_id: int = 0,
                 trail_price_delta: float = 0,
                 direction: str ='Neutral'):
        
        super().__init__(portfolio)
        self.trade_id = trade_id
        
        # A set of points for execute_position function to take record. 
        # Only the final decision is taken as class variables
        # This is the defacto state for the trade as the execution function looks
        # at these to make a decision
        self._TE_pt = (np.nan,np.nan) # Target Entry Point: (datetime, price)
        self._TP_pt = (np.nan,np.nan) # Take Profit Point: (datetime, price)
        self._SL_pt = (np.nan,np.nan) # Stop-Loss Point: (datetime, price)
        
        self._close_pt = (np.nan,np.nan)
        
        # the price difference for the trailing differences for dynamic SL
        if direction == 'Buy':
            self._trail_price_delta = trail_price_delta 
        elif direction =='Sell':
            self._trail_price_delta = -1.0*trail_price_delta
        else:
            self._trail_price_delta = 0
            
        # scenario for cross-sections decision]
        self._cross_decision = 'SL_B'
        
    def choose_EES_values(EES_dict: dict) -> tuple[tuple, tuple, tuple, tuple]:
        return 

    def open_positions():
        # Open all positions based on a decision dictionary
        # This function is also used to add orders to the portfolio object
        return
    
    def execute_positions():
        # execute the right position based on predertermined logic
        return 
    
    def run_trade():
        return 