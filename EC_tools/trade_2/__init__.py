"""
Created on Fri May 10 00:16:28 2024

@author: dexter

The Trade module contains relevant classes and functions that control trade 
actions, i.e., the trade decision logic.

Trade class
    Each trade operate on one Portfolio only
    A Trade is a mere exchange of a pair of assets.

New module that is designed to work with CQGOrder (simple version)

 
"""
# import base python
from dataclasses import dataclass
from typing import Protocol # use protocol for trade class
import datetime as datetime
import copy 

# import  common pcakages
import numpy as np
import pandas as pd

# import EC_tools
from EC_tools.portfolio import Portfolio
from EC_tools.trade.order import Order, ExecuteOrder
import EC_tools.base.read as read
import EC_tools.utility as util
from crudeoil_future_const import OIL_FUTURES_FEE, SIZE_DICT, ASSET_DICT

class Trade(object):
    def __init__(self):
        #self.open_pt = (np.nan,np.nan)
        #self.close_pt = (np.nan,np.nan)
        pass
    
# =============================================================================
# class Trade(Protocol):
#     """
#     Parent class for all trading strategy. It controls the setting of a 
#     particular Trade class.
#     
#     Universal functions are written here.
#     
#     
#     """
#     def  __init__(self, #portfolio: Portfolio, 
#                  close_exit_or_not: bool = True, 
#                  save_only_exec_pos: bool = False,
#                  auto_unload_all: bool = False):
#         
#         #self._portfolio = portfolio # the portfolio we operate on
#         self._auto_unload_all = auto_unload_all
#         
#     @property
#     def auto_unload_all(self):
#         return self._auto_unload_all
#         
#     @auto_unload_all.setter
#     def auto_unload_all(self, bool_val: bool):
#         self._auto_unload_all = bool_val
#     
#     # time speciised order type
#     # duration limited order type
#     
#     def add_order(self, 
#                      give_obj_name: str, 
#                      get_obj_name: str, 
#                      get_obj_quantity: str, 
#                      target_price: float, 
#                      size: int = 1, 
#                      fee: int | float = None, 
#                      order_type: str = 'Long',
#                      open_time: datetime.datetime = datetime.datetime.now(),
#                      trade_id: int = 0):
# 
#         get_obj_unit = ASSET_DICT[get_obj_name]['unit']
#         get_obj_type = ASSET_DICT[get_obj_name]['asset_type']
#         
#         give_obj_unit = ASSET_DICT[give_obj_name]['unit']
#         give_obj_type = ASSET_DICT[give_obj_name]['asset_type']
#         
#         # get_obj, asset
#         get_obj = {'name': get_obj_name, 
#                    'quantity': get_obj_quantity, 
#                    'unit': get_obj_unit, 
#                    'asset_type': get_obj_type,
#                    'misc': {}}
#         # give_obj, cash
#         give_obj = {'name': give_obj_name, 
#                     'quantity': target_price*get_obj_quantity*size, 
#                     'unit': give_obj_unit, 
#                     'asset_type': give_obj_type, 
#                     'misc':{}}
#         
#         #print("before add fee", fee, get_obj_quantity)
#         if type(fee) == dict:
#             new_fee = fee.copy()
#             new_fee['quantity'] = fee['quantity']*get_obj_quantity
#         elif fee == None:
#             new_fee = None
#             
#         # Create an order
#         order = Order(give_obj, get_obj, target_price, 
#                        portfolio= self._portfolio, size = size,
#                        fee = new_fee, order_type = order_type, 
#                        open_time = open_time,
#                        order_id = trade_id)
# 
#         return order
# =============================================================================

