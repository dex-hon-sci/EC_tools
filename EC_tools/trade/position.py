#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 29 23:49:08 2024

@author: dexter

A position consist of two filled orders
"""
# python import
from dataclasses import dataclass, field, replace
from typing import Protocol, Union
from enum import Enum, auto
import datetime as datetime
from attrs import setters

# EC_tools import
from EC_tools.portfolio import Portfolio
from EC_tools.trade.order import Order, OrderStatus
import EC_tools.utility as util  


__author__="Dexter S.-H. Hon"

    
@dataclass
class Position(object):
    """
    A Position object consist of two filled order
    
    """
    
    entry_order: Order = None
    exit_order: Order = None
    entry_time: datetime.datetime = None
    exit_time: datetime.datetime = None
    duration: datetime.timedelta = None
    net_change: float | int = None
    pos_id: str = util.random_string()  

    
    def __post_init__(self):
        #check if the two orders are filled already
        if self.entry_order.status != OrderStatus.FILLED:
            raise Exception("The Entry order is not in the filled state.")
        elif self.exit_order.status != OrderStatus.FILLED:
            raise Exception("The Exit order is not in the filled state.")

        # check if the asset align 
        if self.entry_order.give_obj != self.exit_order.get_obj or \
           self.entry_order.get_obj != self.exit_order.give_obj:
            raise Exception("The asset in the entry and exit orders does not align.")
            
        if self.entry_order.get_obj['quantity'] != self.exit_order.give_obj['quantity']:
            raise Exception("Orders are not the same size.\
                            A position is defined by two orders with the same size.")
            
        self.entry_time = self.entry_order.fill_time
        self.exit_time = self.exit_order.fill_time
        self.duration = self.exit_order.fill_time - self.entry_order.fill_time
        
        if self.entry_order.type == 'Long-Buy':
            self.net_change = self.exit_order.price - self.entry_order.price
        elif self.entry_order.type == 'Short-Borrow':
            self.net_change = self.entry_order.price - self.exit_order.price 
            
            
    # auto blanace the order and position amount

