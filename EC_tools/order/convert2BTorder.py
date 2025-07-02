#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 26 12:19:52 2025

@author: dexter


A temporary solution for converting from new order object system with 
the old order system. 

v0.2: Asset: dict
v0.3: Asset: Asset_Obj
"""
from EC_tools.order.order import Order
from EC_tools.order.cqg_order import CQGOrder
from EC_tools.order.cqg_enums import OrderSide as c_OrderSide
from EC_tools.order.cqg_enums import OrderType as c_OrderType

from EC_tools.order.enums import OrderSideExtend, OrderType

default = {'Numer': {"name":"USD", "unit":"dollars"}, # Numeriare
           'Cash': {"name":"USD", "unit":"dollars"}, 
           'future': {"unit":"Contracts"}}

SIZE_DICT = {
    'CLc1': 1000.0,
    'CLc2': 1000.0,
    'HOc1': 42000.0,
    'HOc2': 42000.0,
    'RBc1': 42000.0,
    'RBc2': 42000.0,
    'QOc1': 1000.0,
    'QOc2': 1000.0,
    'QPc1': 100.0,
    'QPc2': 100.0
    } # num_per_contract


def convert2BTorder(order_: CQGOrder,
                    asset_type: str, 
                    **kwargs) -> Order:
    # A function that convert from live-trading order object to backtest object.
    # For LMT order, use the price supplied by the CQGOrder Object
    # For MKR order, use the price supplied by the user as key arguments
    if not order_.open_ ^ order_.close_:
        raise Exception("An order cannot be simutaneosuly open and close")
    
    # Define the price for the different order types and convert side format
    match order_.type_: 
        case c_OrderType.ORDER_TYPE_MKT:
            price = kwargs['MKT_price']
            order_type2 = OrderType.ORDER_TYPE_MKT 

        case c_OrderType.ORDER_TYPE_LMT:
            price = order_.LMT_price
            order_type2 = OrderType.ORDER_TYPE_LMT
        
    match order_.side: 
        case c_OrderSide.SIDE_BUY:
            # convert side format
            if order_.open_:
                order_type = OrderSideExtend.LONG_BUY
            elif order_.close_:
                order_type = OrderSideExtend.SHORT_BUYBACK

        case c_OrderSide.SIDE_SELL:  # If it is an open order Sell->Short
            if order_.open_:
                order_type = OrderSideExtend.SHORT_BORROW
            elif order_.close_:
                order_type = OrderSideExtend.LONG_SELL

    # get_obj is assumed to be the asset, even in close order
    # With the same logic, give_obj is cash, even in close order.
    # The trade and ExecuteOrder should handle the add/sub of asset and 
    # cash to a Portfolio based on this logic (see ExecuteOrder.fill_pos)
    
    get_obj = {'name': order_.asset_name, 
               'quantity': order_.qty, 
               'unit': default[asset_type]['unit'],
               'asset_type': asset_type}
    
    size = SIZE_DICT[get_obj['name']]

    give_obj = {'name': default['Cash']['name'],
                'quantity':get_obj['quantity']*size*price,
                'unit': default['Cash']['unit'],
                'asset_type': "Cash"}
    
    FEE = {'name':'USD', 'quantity': 15.0*order_.qty, 
                   'unit':'dollars', 'asset_type': 'Cash'}
    
    #if order_.open_: # Open order (Cash -> Asset)
    if order_.open_:
        # If this is not a close order, do not charge transaction fee
        fee = None
    elif order_.close_:
        fee = FEE

    # create a new Backtest compatiable Order object
    new_bt_order = Order(give_obj, get_obj, price, 
                         order_type = order_type, # This is side, temporary name
                         order_type2 = order_type2, # This is typr, MKT/LMT
                         size = size,
                         fee = fee)

    return new_bt_order

# =============================================================================
#         # convert side format
#         match order_.side: 
#             case c_OrderSide.SIDE_BUY: # If it is an open order Buy->Long
#                 order_type = OrderSideExtend.LONG_BUY
#             case c_OrderSide.SIDE_SELL:  # If it is an open order Sell->Short
#                 order_type = OrderSideExtend.SHORT_BORROW
#         
# =============================================================================

        
# =============================================================================
#     elif order_.close_: # Close order (Asset -> Cash)
#     
#         give_obj = {'name': order_.asset_name, 
#                    'quantity': order_.qty, 
#                    'unit': default[asset_type]['unit'],
#                    'asset_type': asset_type}
#         
#         size = SIZE_DICT[give_obj['name']]
#         FEE = {'name':'USD', 'quantity': 15.0*order_.qty, 
#                'unit':'dollars', 'asset_type': 'Cash'}
# 
#         get_obj = {'name': default['Cash']['name'],
#                    'quantity': give_obj['quantity']/(price*size),
#                     'unit': default['Cash']['unit'],
#                     'asset_type': "Cash"}
#         # If this is a close order, charge transaction fee
#         fee = FEE
# =============================================================================
                

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
