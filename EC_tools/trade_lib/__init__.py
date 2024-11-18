"""
Created on Fri May 10 00:16:28 2024

@author: dexter

A module that control trade action. The decision making logics are all stored 
here.
"""
from dataclasses import dataclass
from typing import Protocol # use protocol for trade class
import datetime as datetime

import numpy as np
import pandas as pd

from EC_tools.position import Position, ExecutePosition
#from EC_tools.portfolio import Asset
import EC_tools.read as read
import EC_tools.utility as util

class Trade(Protocol):
    """
    Parent class for all trading strategy. Universal functions are written here.
    
    """
    def  __init__(self, portfolio):
        self._portfolio = portfolio
        self.position_book = []
        
    def add_position(self, give_obj_name: str, get_obj_name: str, 
                     get_obj_quantity: str, 
                     target_price: float, 
                     size: int = 1, fee: int | float = None, 
                     pos_type: str = 'Long',
                     open_time: datetime.datetime = datetime.datetime.now()):
        """
        A simple function that make the process of creating a position easier.
        It takes the name of the give_obj and get_obj, as well as the desired 
        quantity of get_obj and target price, to create the Asset objects and 
        Position object.

        The function automatically calculate how much give_obj you are going 
        to spend to purchase it. It assume you have enough within your portfolio.
        
        Parameters
        ----------
        give_obj_name : str
            The name of the give object.
        get_obj_name : str
            The name of the get object.
        get_obj_quantity : float
            The quantity of the get object.
        target_price : float
            An initial target price for the position. It is subject to slight 
            changes during the backtest.

        Returns
        -------
        pos : Position object
            The trade opsition .

        """
        get_obj_unit = ASSET_DICT[get_obj_name]['unit']
        get_obj_type = ASSET_DICT[get_obj_name]['asset_type']
        
        give_obj_unit = ASSET_DICT[give_obj_name]['unit']
        give_obj_type = ASSET_DICT[give_obj_name]['asset_type']
        
# =============================================================================
#         get_obj = Asset(get_obj_name, get_obj_quantity, 
#                         get_obj_unit, get_obj_type)
#         give_obj = Asset(give_obj_name, target_price*get_obj_quantity, 
#                             give_obj_unit, give_obj_type)
# =============================================================================
        get_obj = {'name': get_obj_name, 'quantity': get_obj_quantity, 
                     'unit': get_obj_unit, 'asset_type': get_obj_type,
                     'misc': {}}
        give_obj = {'name': give_obj_name, 'quantity': target_price*get_obj_quantity, 
                     'unit':give_obj_unit, 'asset_type': give_obj_type, 
                     'misc':{}}
# =============================================================================
#         # make position
#         pos = Position(give_obj, get_obj, target_price, 
#                         portfolio= self._portfolio, size = size,
#                         fee = fee, pos_type = pos_type, open_time=open_time)
# =============================================================================
        
        # different type of posiitons
        if pos_type == 'Long-Buy':
            # an example, get_obj is the asset, give_obj is the cash
            # Setup the amount of asset we want
            get_obj = {'name': get_obj_name, 'quantity': get_obj_quantity, 
                         'unit': get_obj_unit, 'asset_type': get_obj_type,
                         'misc': {}}

            # calculate the money we have to pay
            give_obj = {'name': give_obj_name, 'quantity': target_price*get_obj_quantity*size, 
                         'unit':give_obj_unit, 'asset_type': give_obj_type, 
                         'misc':{}}
            
            pos = Position(give_obj, get_obj, target_price, 
                           portfolio= self._portfolio, size = size,
                           fee = fee, pos_type = pos_type, open_time=open_time)
            
        elif pos_type == 'Long-Sell':
            # an example, get_obj is the asset, give_obj is the cash
            get_obj = {'name': get_obj_name, 'quantity': get_obj_quantity, 
                         'unit': get_obj_unit, 'asset_type': get_obj_type,
                         'misc': {}}
            give_obj = {'name': give_obj_name, 'quantity': target_price*get_obj_quantity*size, 
                         'unit':give_obj_unit, 'asset_type': give_obj_type, 
                         'misc':{}}
            
            pos = Position(give_obj, get_obj, target_price, 
                           portfolio= self._portfolio, size = size,
                           fee = fee, pos_type = pos_type, open_time=open_time)
            
        elif pos_type == 'Short-Borrow':
            # an example, get_obj is the asset, give_obj is the cash
            get_obj = {'name': get_obj_name, 'quantity': get_obj_quantity, 
                         'unit': get_obj_unit, 'asset_type': get_obj_type,
                         'misc': {}}
            give_obj = {'name': give_obj_name, 'quantity': target_price*get_obj_quantity*size, 
                         'unit':give_obj_unit, 'asset_type': give_obj_type, 
                         'misc':{}}  
            
            pos = Position(give_obj, get_obj, target_price, 
                           portfolio= self._portfolio, size = size,
                           fee = fee, pos_type = pos_type, open_time=open_time)
            
        elif pos_type == 'Short-Buyback':
            # an example, get_obj is the asset, give_obj is the cash
            get_obj = {'name': get_obj_name, 'quantity': get_obj_quantity, 
                         'unit': get_obj_unit, 'asset_type': get_obj_type,
                         'misc': {}}
            give_obj = {'name': give_obj_name, 'quantity': target_price*get_obj_quantity*size, 
                         'unit':give_obj_unit, 'asset_type': give_obj_type, 
                         'misc':{}}  
            
            pos = Position(give_obj, get_obj, target_price, 
                           portfolio= self._portfolio, size = size,
                           fee = fee, pos_type = pos_type, open_time=open_time)
            
            
        # Add posiyion in the position book
        #self.position_book.append(pos)
        
        return pos

