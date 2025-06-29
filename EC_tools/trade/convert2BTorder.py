#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 26 12:19:52 2025

@author: dexter

v0.2: Asset: dict
v0.3: Asset: Asset_Obj
"""
from EC_tools.order.order import Order
from EC_tools.order.cqg_order import CQGOrder

default = {'Numer': {"name":"USD", "unit":"dollars"}, # Numeriare
           'Cash': {"name":"USD", "unit":"dollars"}, 
           'Futures': {"unit":"Contracts"}}

def convert2BTorder(order_: CQGOrder,
                    asset_type: str) -> Order:
    # A function that convert from live-trading order object to backtest object.
    if not order_.open ^ order_.close:
        raise Exception("An order cannot be simutaneosuly open and close")
    
    elif order_.open:  
        get_obj = {'name': CQGOrder.asset_name, 
                   'quantity': CQGOrder.qty, 
                   'unit': default[asset_type]['unit'],
                   'asset_type': asset_type}
        give_obj = {'name': default['Cash']['name'],
                    'quantity':0,
                    'unit': default['Cash']['unit'],
                    'asset_type': "Cash"}

    elif order_.close:
        get_obj = {'name': default['Cash']['name'],
                    'quantity':0,
                    'unit': default['Cash']['unit'],
                    'asset_type': "Cash"}

        give_obj = {'name': CQGOrder.asset_name, 
                   'quantity': CQGOrder.qty, 
                   'unit': default[asset_type]['unit'],
                   'asset_type': asset_type}
    size = 1
    price = give_obj['quantity'] / (get_obj['quantity']*size)

    new_bt_order = Order(give_obj, get_obj, price)

    return new_bt_order
# =============================================================================
#     # key attributes
#     give_obj: dict # Asset
#     get_obj: dict # Asset
#     _price: float
#     status: OrderStatus = OrderStatus.PENDING
#     portfolio: Portfolio = None
#     
#     # optional asset control
#     size: float = 1 # contract lots
#     fee: dict = None
#     order_type: str = 'Long-Buy'
#     
#     # order attribute adjustable
#     open_time: datetime = datetime.datetime.now() 
#     fill_time: datetime = None
#     void_time: datetime = None
#     auto_adjust: bool = True
#     order_id: str = util.random_string()  
# =============================================================================
