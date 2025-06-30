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
from dataclasses import dataclass, InitVar, field
from EC_tools.order.cqg_enums import OrderSide, OrderType, OrderDuration

@dataclass
class CQGOrder(object):
    # Order object ompataible with CQG live-trading operation.
    # For CQGOrders, we do not know the current price of the asset
    asset_name: str
    side: OrderSide # Buy/Sell
    type_: OrderType # MKT/LMT
    qty: int
    open_: bool = True
    close_: bool = False
    duration: OrderDuration = OrderDuration.DURATION_GTC
    #extra_args: field(default_factory=dict) = None
    kwargs: field(default_factory=dict) = None

    def __post_init__(self):
        if self.type_ == OrderType.ORDER_TYPE_LMT:
            self.LMT_price = self.kwargs['LMT_price']
        if self.type_ == OrderType.ORDER_TYPE_MKT:
            self.MKT_time = self.kwargs['MKT_time']

    
# =============================================================================
# new_order_request(
#                                     client, request_id, 
#                                     account_id, contract_id, 
#                                     cl_order_id, ORDER_TYPE_LMT, 
#                                     DURATION_DAY, SIDE_BUY, 
#                                     qty_significant, qty_exponent, 
#                                     is_manual,
#                                     scaled_limit_price=SCALED_LIMIT_PRICE)
# =============================================================================
