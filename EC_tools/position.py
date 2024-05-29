#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 29 23:49:08 2024

@author: dexter
"""
import pandas as pd
from dataclasses import dataclass, field
from typing import Protocol
from enum import Enum, auto
from functools import cached_property
import datetime as datetime

import EC_tools.read as read
from EC_tools.portfolio import Asset, Portfolio
    
class PositionStatus(Enum):
    """
    A set of possible status for positions.
    """
    PENDING = "Pending"
    OPEN = "Open"
    CLOSE = "Close"
    VOID = "Void"
    
@dataclass
class Positions(object):
    pos_id: str    
    give_obj: Asset
    get_obj: Asset
    price: float
    start_time: datetime = None
    open_time: datetime = None
    close_time: datetime = None
    void_time: datetime = None
    _status: PositionStatus = PositionStatus.PENDING
    portfolio: Portfolio = None
    #_check: bool = False
    
    #@property
    #def check_balance(self):
    
    def __post_init__(self):
        # check if the quantity of both assets are 
        correct_ratio = self.get_obj.quantity / self.give_obj.quantity
        print(correct_ratio, self.price)
        self._check = (self.price == correct_ratio)
        
        #If this value is false, the position is automatically voided.
        if self._check == False:
            self._status = PositionStatus.VOID
            self.void_time = datetime.datetime.now()
            
        #return self._check 
    
    
    # attribute of which portfolio does it belong to
    
    # The position class constitue the exchanges i.e. trade, add(asset), sub(asset)
    # Auto load position 
    # Long Cash baseline
    
    #(Position id, give_asset, get_asset, Entry ,Exit, Stoploss, close_arg=S, active = False, datetime= None)
    #(Position id, asset_obj_A, asset_obj_B, entry_datetime, entry_price (payA buyB))
    #(Position id, asset_obj_A, asset_obj_B, exit_datetime)
    
    #pend_pos_list: list[int] = field(default_factory=list)
    #open_pos_list: list[int] = field(default_factory=list)
    #close_pos_list: list[int] = field(default_factory=list)
    
    # Entry (1, asset_A, asset_B, price(A to B))
    # Exit  (2, asset_B, asset_A, price_target(B to A))
    # Stop  (3, asset_B, asset_A, price_exit(B to A))
    # Close (4, asset_B , asset_A, price_close(B to A))
    
    # PositionStatus: Pending, Open, Close, Voided
    
    

class PositionBook(Portfolio):
    def __init__():
        return
    
class PositionExecute(Protocol):
    
    def __init__(self,_):
        self._ = _
        
    def execute():
        # check position size before executions
        #if price_cond==True: then initiate trade add A sub B  
        return