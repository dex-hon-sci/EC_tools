#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 23 06:46:41 2025

@author: dexter
"""
# python import
from dataclasses import dataclass
from enum import Enum

class SignalType(Enum):
    """
    A simple class that contains the avaliable status for signals.
    
    """
    BUY = "Buy" # Good for Long Call 
    SELL = "Sell" # Good for Long Put
    NEUTRAL = "Neutral" # Good for Long Butterfly/Iron Condor or collar
    BIDIR_INWARD = "BiDirectional_Inward" # Good for Long Butterfly/Iron Condor
    BIDIR_OUTWARD = "BiDierctional_Outward" # Good for Long Straddle/strangle
    
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
    EES: tuple | list #(entry_price, exit_price, stoploss_price), EES with time tag
    time_window: tuple | list#(start_time, end_time) The time window in which this signal is active
    decay_factor: float 
    conditions: dict[str] #trigger condition for a trade based on this signal
    actions: dict[str] # What to do, trade what concepts?


if __name__ == "__main__":
    entry_list = []