#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jun 29 15:28:50 2025

@author: dexter

A test script for convert2BTorder function.

"""
import datetime
from EC_tools.order.convert2BTorder import convert2BTorder
from EC_tools.order.order import Order
from EC_tools.order.cqg_order import CQGOrder
from EC_tools.order.cqg_enums import OrderSide as c_OrderSide
from EC_tools.order.cqg_enums import OrderType as c_OrderType
from EC_tools.order.enums import OrderStatus, OrderSide, OrderSideExtend, OrderType

ASSET_NAME = "CLc1"#"CLM25"
ASSET_TYPE = "future"
MKT_TIME = datetime.datetime.now
# Setup test orders
c_order_MKT_BUY_open = CQGOrder(ASSET_NAME, c_OrderSide.SIDE_BUY, 
                                c_OrderType.ORDER_TYPE_MKT, 10, 
                                open_= True, close_= False,
                                kwargs = {"MKT_time": MKT_TIME})
c_order_LMT_BUY_open = CQGOrder(ASSET_NAME, c_OrderSide.SIDE_BUY, 
                                c_OrderType.ORDER_TYPE_LMT, 10, 
                                open_= True, close_= False, 
                                kwargs = {"LMT_price":60})
c_order_MKT_BUY_close = CQGOrder(ASSET_NAME, c_OrderSide.SIDE_BUY, 
                                 c_OrderType.ORDER_TYPE_MKT, 10, 
                                 open_= False, close_= True,
                                 kwargs = {"MKT_time": MKT_TIME})
c_order_LMT_BUY_close  = CQGOrder(ASSET_NAME, c_OrderSide.SIDE_BUY, 
                                  c_OrderType.ORDER_TYPE_LMT, 10, 
                                  open_= False, close_= True, 
                                  kwargs = {"LMT_price":60})
c_order_MKT_SELL_open = CQGOrder(ASSET_NAME, c_OrderSide.SIDE_SELL, 
                                 c_OrderType.ORDER_TYPE_MKT, 10, 
                                 open_= True, close_= False,
                                 kwargs = {"MKT_time": MKT_TIME})
c_order_LMT_SELL_open = CQGOrder(ASSET_NAME, c_OrderSide.SIDE_SELL, 
                                 c_OrderType.ORDER_TYPE_LMT, 10, 
                                 open_= True, close_= False, 
                                 kwargs = {"LMT_price":60})
c_order_MKT_SELL_close = CQGOrder(ASSET_NAME, c_OrderSide.SIDE_SELL, 
                                  c_OrderType.ORDER_TYPE_MKT, 10, 
                                  open_= False, close_= True,
                                  kwargs = {"MKT_time": MKT_TIME})
c_order_LMT_SELL_close = CQGOrder(ASSET_NAME, c_OrderSide.SIDE_SELL, 
                                  c_OrderType.ORDER_TYPE_LMT, 10, 
                                  open_= False, close_= True, 
                                  kwargs = {"LMT_price":60})

def check_convert2BTorder_type(c_order,**kwargs) -> None:
    # Test if conversion render the correct type
    output = convert2BTorder(c_order, ASSET_TYPE, **kwargs)
    assert type(output) == Order
    
def check_convert2BTorder_pending(c_order,**kwargs) -> None:
    # Check if the order is pending. If so, the price passes the 
    # correct ratio test in Order __post_init__
    output = convert2BTorder(c_order, ASSET_TYPE, **kwargs)
    assert output.status == OrderStatus.PENDING
    
def check_convert2BTorder_MKT(c_order,**kwargs)-> None:
    # Check for the conversion of market orders format
    output = convert2BTorder(c_order, ASSET_TYPE, **kwargs)
    assert output.order_type2 == OrderType.ORDER_TYPE_MKT
    
def check_convert2BTorder_LMT(c_order,**kwargs)-> None:
    # Check for the conversion of market orders format
    output = convert2BTorder(c_order, ASSET_TYPE, **kwargs)
    assert output.order_type2 == OrderType.ORDER_TYPE_LMT
    
def check_convert2BTorder_LONG_BUY(c_order,**kwargs)-> None:
    # Check for the conversion of market orders format
    output = convert2BTorder(c_order, ASSET_TYPE, **kwargs)
    assert output.order_type == OrderSideExtend.LONG_BUY
    
def check_convert2BTorder_LONG_SELL(c_order,**kwargs)-> None:
    # Check for the conversion of market orders format
    output = convert2BTorder(c_order, ASSET_TYPE, **kwargs)
    assert output.order_type == OrderSideExtend.LONG_SELL
    
def check_convert2BTorder_SHORT_BORROW(c_order,**kwargs)-> None:
    # Check for the conversion of market orders format
    output = convert2BTorder(c_order, ASSET_TYPE, **kwargs)
    assert output.order_type == OrderSideExtend.SHORT_BORROW
    
def check_convert2BTorder_LONG_BUYBACK(c_order,**kwargs)-> None:
    # Check for the conversion of market orders format
    output = convert2BTorder(c_order, ASSET_TYPE, **kwargs)
    assert output.order_type == OrderSideExtend.SHORT_BUYBACK


def test_type()-> None:
    all_orders = [c_order_MKT_BUY_open, c_order_LMT_BUY_open, 
                 c_order_MKT_BUY_close, c_order_LMT_BUY_close, 
                 c_order_MKT_SELL_open, c_order_LMT_SELL_open, 
                 c_order_MKT_SELL_close, c_order_LMT_SELL_close]
    for ele in all_orders:
        check_convert2BTorder_type(ele, MKT_price =71)
        
def test_pending()-> None:
    all_orders = [c_order_MKT_BUY_open, c_order_LMT_BUY_open, 
                 c_order_MKT_BUY_close, c_order_LMT_BUY_close, 
                 c_order_MKT_SELL_open, c_order_LMT_SELL_open, 
                 c_order_MKT_SELL_close, c_order_LMT_SELL_close]
    for ele in all_orders:
        check_convert2BTorder_pending(ele)
        
def test_MKT()-> None:
    MKT_orders= [c_order_MKT_BUY_open, c_order_MKT_BUY_close, 
                c_order_MKT_SELL_open, c_order_MKT_SELL_close]
    for ele in MKT_orders:
        check_convert2BTorder_MKT(ele, MKT_price =71)
        
def test_LMT()-> None:
    MKT_orders= [c_order_LMT_BUY_open, c_order_LMT_BUY_close, 
                 c_order_LMT_SELL_open, c_order_LMT_SELL_close]
    for ele in MKT_orders:
        check_convert2BTorder_LMT(ele, MKT_price =71)

def test_LONG_BUY()-> None:
    LONG_BUY_orders = [c_order_LMT_BUY_open, c_order_MKT_BUY_open]
    for ele in LONG_BUY_orders:
        check_convert2BTorder_LONG_BUY(ele, MKT_price =71)
        
def test_LONG_SELL()-> None:
    LONG_SELL_orders = [c_order_LMT_SELL_close, c_order_MKT_SELL_close]
    for ele in LONG_SELL_orders:
        check_convert2BTorder_LONG_SELL(ele, MKT_price =71)
        
def test_SHORT_BORROW()-> None:
    SHORT_BORROW_orders = [c_order_LMT_SELL_open, c_order_MKT_SELL_open]
    for ele in SHORT_BORROW_orders:
        check_convert2BTorder_SHORT_BORROW(ele, MKT_price =71)
        
def test_SHORT_BUYBACK()-> None:
    SHORT_BUYBACK_orders = [c_order_LMT_BUY_close, c_order_MKT_BUY_close]
    for ele in SHORT_BUYBACK_orders:
        check_convert2BTorder_LONG_BUYBACK(ele, MKT_price =71)

test_type()
test_LMT()
test_MKT()
test_LONG_BUY()
test_LONG_SELL()
test_SHORT_BUYBACK()
test_SHORT_BUYBACK()

# =============================================================================
#     asset_name: str
#     side: OrderSide # Buy/Sell
#     type_: OrderType # MKT/LMT
#     qty: int
#     duration: OrderDuration
#     open_: bool 
#     close_: bool
#     def __post_init__(self):
#         
#         if self.type_ == OrderType.ORDER_TYPE_LMT:
#             LMT_price = 0
# =============================================================================
