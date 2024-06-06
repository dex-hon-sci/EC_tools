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
    """
    Position class that create and manage position objects.
    
    """
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
        """
        The post init function that checks if the input price is correct.
        If it is not. the position is voided.
        
        """
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
    """
    A class that execute the position.
    
    """
    
    def __init__(self,  Position):
        self.position = Position
        
        #check if there is a Portfolio attached to the position.
        if not isinstance(self.position.portfolio, Portfolio):
            raise Exception("The position does not belong to a valid \
                            Portfolio.")

    def open_pos(self, open_time = datetime.datetime.now()):
        """
        Open position method.

        Parameters
        ----------
        open_time : datetime, optional
            The opening time. The default is datetime.datetime.now().

        Raises
        ------
        Exception
            If the position status is not pending or there are not enough 
            give_obj in the portfolio.

        Returns
        -------
        position object

        """
        # check if the position is Pending
        if self.position.status == PositionStatus.PENDING:
            pass
        else:
            raise Exception("The position is not yet added.")
            
        #print(self.position.give_obj.quantity)    
        #print(self.position.portfolio.master_table[self.position.portfolio.master_table['name']==self.position.give_obj.name]['quantity'].iloc[0])
        #print(self.position.portfolio.master_table[self.position.portfolio.master_table['name']==self.position.give_obj.name]['quantity'].iloc[0] < self.position.give_obj.quantity)
        port = self.position.portfolio
        # check if you have the avaliable fund in the portfolio
        if port.master_table[port.master_table['name']==self.position.give_obj.name]['quantity'].iloc[0] < self.position.give_obj.quantity:
        
# =============================================================================
#         self.position.portfolio.master_table[self.position.portfolio.\
#                     master_table['name'] == self.position.give_obj]['quantity']\
#             .iloc[0] < self.position.give_obj.quantity:
# =============================================================================
                                                
            raise Exception('You do not have enough {} in your portfolio'.format(
                                                self.position.give_obj.name))
        else: pass
    
        self.position.status = PositionStatus.OPEN
        self.position.open_time = open_time
        return self.position
    
    def close_pos(self, close_time = datetime.datetime.now()):
        # check if the position is open
        if self.position.status == PositionStatus.OPEN:
            pass
        else:
            raise Exception("The position is not yet open.")
                    
        #add and sub portfolio
        self.position.portfolio.add(self.position.get_obj, datetime = close_time)
        self.position.portfolio.sub(self.position.give_obj, datetime= close_time)
        self.position.status = PositionStatus.CLOSE
        self.position.close_time = close_time

        return self.position
    
    def void_pos(self, void_time = datetime.datetime.now()):
        
        # check if the position is Pending
        if self.position.status == PositionStatus.PENDING:
            pass
        else:
            raise Exception("The position is not yet added.")
            
        self.position.status = PositionStatus.VOID
        self.position.void_time = void_time
        return 