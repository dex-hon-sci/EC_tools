"""
Created on Wed May 29 23:49:08 2024

@author: dexter


Position Module.

"""
# python import
from dataclasses import dataclass, field, replace
from typing import Protocol, Union
from enum import Enum, auto
import datetime as datetime
from attrs import setters

# EC_tools import
from EC_tools.portfolio import Portfolio
import EC_tools.utility as util  
from EC_tools.order import Order, OrderStatus, OrderType
from EC_tools.trade import Trade
    

    
@dataclass
class Position(object):
    
    trade: Trade
    
    def open_positions(self, 
                       give_obj_name: str, 
                       get_obj_name: str, 
                       get_obj_quantity: int | float, 
                       EES_target_list: list, 
                       pos_type: str,
                       size: int | float = 1, 
                       fee: dict = None, 
                       open_time: datetime.datetime = datetime.datetime.now())\
                       -> list[Order]:
        """
        A method to open the entry, exit, stop, and close positions.

        Parameters
        ----------
        give_obj_name : str
            The name of the give object.
        get_obj_name : str
            The name of the get object.
        get_obj_quantity : float
            The quantity of the get object.
        EES_target_list : list
            A list of target EES values [entry_price, exit_price, 
                                         stop_price, close_price].
        pos_type : str
            The type of position to be opened.

        Returns
        -------
        pos_list : list
            The position list: [entry_pos, exit_pos, stop_pos, close_pos].

        """
        if pos_type == 'Long':
            pos_type1 = 'Long-Buy'
            pos_type2 = 'Long-Sell'

        elif pos_type == 'Short':
            pos_type1 = 'Short-Borrow'
            pos_type2 = 'Short-Buyback'
            
        # a method that execute the one trade per day based on the cases of the EES
        entry_price, exit_price = EES_target_list[0], EES_target_list[1]
        stop_price, close_price = EES_target_list[2], EES_target_list[3]
        
        #### Collapse all these into an add_position function
        # Make positions for initial price estimation
        entry_order = super().add_order(give_obj_name, get_obj_name, 
                                         get_obj_quantity, entry_price, 
                                         size = size, fee = None, 
                                         pos_type = pos_type1,
                                         open_time=open_time,
                                         trade_id=self.trade_id)

        exit_order = super().add_order(give_obj_name, get_obj_name, 
                                        get_obj_quantity, exit_price, 
                                        size = size, fee = fee, 
                                        pos_type = pos_type2,
                                        open_time=open_time,
                                        trade_id=self.trade_id)

        stop_order = super().add_order(give_obj_name, get_obj_name, 
                                        get_obj_quantity, stop_price, 
                                        size = size, fee = fee, 
                                        pos_type = pos_type2,
                                        open_time=open_time,
                                        trade_id=self.trade_id)