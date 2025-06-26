#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 26 11:53:42 2025

@author: dexter

A replication of order.proto from CQG Web API. 
This is to ensure the cqg_order object conform to a live-trading setting.

"""
from enum import Enum, auto

__all__ = ["OrderSide", "OrderType", "OrderExecInstruction", 
           "OrderDuration", "OrderTrailingPeg", "OrderOpenCloseInstruction"]

class OrderSide(Enum):
    # Describes purchasing side of a trade.
    SIDE_BUY = 1
    # Describes selling side of a trade.
    SIDE_SELL = 2

    
class OrderType(Enum):
    # Market order, buy or sell by the best available opposite price.
    ORDER_TYPE_MKT = 1
    # Limit order, buy or sell by price that is the same or better then 
    #specified limit price.
    ORDER_TYPE_LMT = 2
    # Stop order, Order becomes a Market when market reaches 
    # order's stop price (which is on opposite side of market).
    ORDER_TYPE_STP = 3
    # Stop-limit order, Order becomes a Limit when market 
    #reaches order's stop price.
    ORDER_TYPE_STL = 4
    # Cross order type. See also CrossOrderParameters message.
    ORDER_TYPE_CROSS = 5
    
class OrderExecInstruction(Enum):
    # None (this means "plain order without any exec instructions").
    # This value shall not be explicitly provided in OrderRequest.
    EXEC_INSTRUCTION_NONE = 12
    # All or None (fill order only completely).
    EXEC_INSTRUCTION_AON = 1
    # Iceberg (show only part of order size).
    EXEC_INSTRUCTION_ICEBERG = 2
    # Quantity triggered (aka DOM Triggered, honor additional quantity 
    # threshold for triggering).
    EXEC_INSTRUCTION_QT = 3
    # Trailing order (price of the order is following market one direction 
    # by specific offset).
    EXEC_INSTRUCTION_TRAIL = 4
    # Funari (Limit order becomes a Market on Close).
    EXEC_INSTRUCTION_FUNARI = 5
    # Market if Touched (Limit order becomes a Market when market reaches 
    # order's limit price).
    EXEC_INSTRUCTION_MIT = 6
    # Market Limit Market is a limit order that is used to place a buy order 
    # above the best offer
    # to fill by the best offer or a sell order below the best bid to fill 
    # by the best bid.
    EXEC_INSTRUCTION_MLM = 7
    # Post-only order. Ensures the limit order will be added to the order 
    # book and not match with
    # a pre-existing order.
    EXEC_INSTRUCTION_POSTONLY = 8
    # Market with leftover as Limit (market order then unexecuted quantity 
    # becomes limit order at last price).
    EXEC_INSTRUCTION_MTL = 10
    # An auction order is an order to buy or sell in the market at the 
    # Calculated Opening Price (COP).
    # Unmatched auction orders are converted to limit orders on the market open.
    EXEC_INSTRUCTION_AUCTION = 11
    # At Any Price Orders are US-Style Market Orders.
    EXEC_INSTRUCTION_ATANYPRICE = 13
    # Limit order with prearranged transaction flag (IntentToCross) set.
    EXEC_INSTRUCTION_LMT_PRARGD = 14
    # Internal Cross Only.
    # This order type is used by OTC to pull up to order size quantity 
    # from the exchange on the opposite side.
    EXEC_INSTRUCTION_ICO = 15
    #reserved 9, 100 to 199;
 
class OrderDuration(Enum):
    # Day order. Order is working through the current trading day only.
    DURATION_DAY = 1
    # Good Til Canceled. Order is working until canceled or until the 
    # contract is no longer available for trading.
    DURATION_GTC = 2
    # Good Til Date. Order is working through the specified trade date 
    # (good_thru_date) for the contract.
    # Note: Exchange must have a trading session for the contract for 
    # the specified trade date.
    DURATION_GTD = 3
    # Good Til Time. Order is working until the specified time.
    DURATION_GTT = 4
    # Fill and Kill. Immediately fill as many as possible and cancel the rest.
    DURATION_FAK = 5
    # Fill Or Kill. Immediately fill this order completely or cancel.
    DURATION_FOK = 6
    # At The Open. Buy or sell at the very beginning of the trading day.
    DURATION_ATO = 7
    # At The Close. Buy or sell at the close of the market, or as near to 
    # the closing price as possible.
    DURATION_ATC = 8
    # Good for auction. Order only valid for the next auction.
    DURATION_GFA = 9
 
class OrderTrailingPeg(Enum):
    # Trail the best bid.
    TRAILING_PEG_BESTBID = 1
    # Trail the best ask.
    TRAILING_PEG_BESTASK = 2
    # Trail the last trade.
    TRAILING_PEG_LASTTRADE = 3
  
class OrderOpenCloseInstruction(Enum):
    # Specifies what the order is intended to do:
    # open (or extend) a position on the same side as the order or 
    # close (or reduce) an opposite position.
    # Applicable only if ContractMetadata.open_close_type is either 
    # OPEN_CLOSE_TYPE_OPTIONAL or OPEN_CLOSE_TYPE_REQUIRED.

    # Opening a new today position.
    OPEN_CLOSE_INSTRUCTION_OPEN = 1
    # Closing or reducing (today only if ContractMetadata.position_tracking 
    # is LONG_SHORT_WITH_EXPLICIT_CLOSE,
    # today or yesterday if LONG_SHORT_WITH_IMPLIED_CLOSE).
    OPEN_CLOSE_INSTRUCTION_CLOSE = 2
    # Closing or reducing a yesterday position
    # (if ContractMetadata.position_tracking is LONG_SHORT_WITH_EXPLICIT_CLOSE).
    OPEN_CLOSE_INSTRUCTION_CLOSE_YESTERDAY = 3
 
