#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 23 06:46:41 2025

@author: dexter
"""
# python import
from dataclasses import dataclass
from enum import Enum

@dataclass
class SignalType(Enum):
    """
    A simple class that contains the avaliable status for signals.
    
    """
    BUY = "Buy" # When the position is added but not filled
    SELL = "Sell" # When the position is executed
    NEUTRAL = "Neutral" # When the position is cancelled
    
@dataclass
class SignalStatus(Enum):
     ACTIVE = "Active"
     INACTIVE = "Inactive"
    
@dataclass
class Signal(object):
    """
    """
    typ: SignalType
    status: SignalStatus
    duration: tuple | list#(start_time, end_time), The effective duration of the signal
    EES: tuple | list#(entry_price, exit_price, stoploss_price)
    time_window: tuple | list#(start_time, end_time) The time window in which 
    conditions: dict[str]

