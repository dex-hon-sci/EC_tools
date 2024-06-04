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
class Position(object):
    pos_id: str    
    give_obj: Asset
    get_obj: Asset
    price: float
    status: PositionStatus = PositionStatus.PENDING
    portfolio: Portfolio = None
    
    start_time: datetime = datetime.datetime.now()
    open_time: datetime = None
    close_time: datetime = None
    void_time: datetime = None
    
    
    def __post_init__(self, void_time = datetime.datetime.now()):
        # check if the quantity of both assets are 
        correct_ratio = self.get_obj.quantity / self.give_obj.quantity
        print(correct_ratio, self.price)
        self._check = (self.price == correct_ratio)
        
        print('Position created.')
        #If this value is false, the position is automatically voided.
        if self._check == False:
            self.status = PositionStatus.VOID
            self.void_time = void_time
            print("Position voided.")
    
    
class PositionBook(Portfolio):
    def __init__(self):
        self._pool = list()
        
    def pool(self):
        return self._pool
    
class ExecutePosition(object):
    
    def __init__(self,  Position):
        self.position = Position

        #super().__init__(*args, **kwargs)

    #@classmethod()
    def open_pos(self, open_time = datetime.datetime.now()):
        
        # check if you have the avaliable fund in the portfolio
        if self.position.portfolio.asset_value(
                                    self.position.give_obj.name, open_time) < \
                                            self.position.give_obj.quantity:
            raise Exception('WTF')
        else: pass
    
        self.position.status = PositionStatus.OPEN
        self.open_time = open_time
        return self.position
    
    def close_pos(self, close_time = datetime.datetime.now()):
        # check if the position is open
        if self.position.status == PositionStatus.OPEN:
            pass
        else:
            raise Exception("The position is not yet open.")
            
        # check the condition
        
        #add and sub portfolio
        self.portfolio.add(Position.get_obj)
        self.Portfolio.sub(Position.give_obj)
        self.position.status = PositionStatus.CLOSE
        return self.position
    
    def void_pos():
        
        return 