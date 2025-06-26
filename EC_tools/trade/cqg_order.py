#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 26 11:39:11 2025

@author: dexter

CQGOrder is a compataible data format for live-trading. 
In live-trading, the ordering module in EC_API will unpack the data in 
CQGOrder and send order messages 


CQGOrder object can be converted into Order object for the purpose of 
backtesting. The convert2BTorder function transfer the information 
from CQGOrder object to Order object. In backtesting, "Order" object are used. 


"""
from dataclasses import dataclass
from EC_tools.trade.cqg_enums import OrderSide, OrderType, OrderDuration

@dataclass
class CQGOrder(object):
    # Order object ompataible with CQG live-trading operation.
    asset_name: str
    side: OrderSide
    type_: OrderType
    qty: int
    duration: OrderDuration