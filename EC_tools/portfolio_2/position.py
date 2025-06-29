#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 27 14:55:05 2025

@author: dexter
"""
from dataclasses import dataclass, field, replace
from typing import Protocol
import datetime

from EC_tools.order.enums import OrderSide

@dataclass
class Position(object):
    # Cash and Asset pairs only
    # Two Orders with the same asset_name, qty, and a pairing 
    # order types (open_+close_) becomes a position 
    # !! A position is only made after a closing order is executed. !!
    # This is made only to calculate the PNL from exited positions
    # This is an object made in the Portfolio to track the PNL for each trade
    asset_name: str
    qty: int # lot size
    start_side: OrderSide
    start_time: datetime.datetime # A position needs a start_time and start_price
    start_price: float
    close_side: OrderSide
    close_time: datetime.datetime
    close_price: float
    currency: str = "USD"
    
    def __post_init__(self):
        # Type checking
        if type(self.start_side) != OrderSide and type(self.close_side) != OrderSide:
            raise Exception("start_side and close_side must be a Orderside enum.")
        
        # Check if it fulfils both 
        closed_cond1 = (self.start_side == OrderSide.BUY and self.close_side == OrderSide.SELL)
        closed_cond2 = (self.start_side == OrderSide.SELL and self.close_side == OrderSide.BUY)
        print(closed_cond1, closed_cond2)
        if not (closed_cond1 or closed_cond2):
            raise Exception("The starting and closing orders cannot be the same.")

        # Define Position Type (Long or Short)
        if self.start_side == OrderSide.BUY:
            self.pos_side = "Long" 
        elif self.start_side == OrderSide.SELL:
            self.pos_side = "Short" 
            
        # change the attribute for sides to str
        self.start_side =  self.start_side.value
        self.close_side = self.close_side.value
        # Change the datetime to str
        self.start_time = self.start_time.strftime("%Y-%m-%d, %H:%M:%S")
        self.close_time = self.close_time.strftime("%Y-%m-%d, %H:%M:%S")

        # Compute PNL
        if self.pos_side == "Long": # Long Position
            self.PNL = self.qty*(self.close_price - self.start_price)
        elif self.pos_side == "Short" : # Short Position
            self.PNL = self.qty*(self.start_price-self.close_price)

