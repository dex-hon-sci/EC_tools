#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 26 11:58:05 2025

@author: dexter
"""
from enum import Enum

__all__ = ["OrderStatus", "OrderSide", "OrderSideExtend", "OrderType"]

class OrderStatus(Enum):
    """
    A set of possible status for orders.
    
    """
    PENDING = "Pending" # When the order is added but not filled
    FILLED = "Filled" # When the order is executed
    VOID = "Cancelled" # When the order is cancelled
    
class OrderSide(Enum):
    BUY ="Buy"
    SELL = "Sell"

class OrderSideExtend(Enum):
    """
    An extended set of possible types of orders
    """
    LONG_BUY = 'Long-Buy'
    LONG_SELL = 'Long-Sell'
    SHORT_BORROW = 'Short-Borrow'
    SHORT_BUYBACK = 'Short-Buyback'
    #CALL_BUY = 'Call-Buy'
    #CALL_SELL = 'Call-Sell'
    #PUT_BUY = 'Put-Buy'
    #PUT_SELL = 'Put-Sell'

class OrderType(Enum):
    # Market order, buy or sell by the best available opposite price.
    ORDER_TYPE_MKT = "MKT"
    # Limit order, buy or sell by price that is the same or better then 
    #specified limit price.
    ORDER_TYPE_LMT = "LMT"
    # Stop order, Order becomes a Market when market reaches 
    # order's stop price (which is on opposite side of market).
    ORDER_TYPE_STP = "STP"
    # Stop-limit order, Order becomes a Limit when market 
    #reaches order's stop price.
    ORDER_TYPE_STL = "STL"
    # Cross order type. See also CrossOrderParameters message.
    ORDER_TYPE_CROSS = "CROSS"