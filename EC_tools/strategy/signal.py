#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 23 06:46:41 2025

@author: dexter
"""
# python import
from dataclasses import dataclass
from enum import Enum
import datetime 
import numpy as np

class SignalType(Enum):
    """
    A simple class that contains the avaliable status for signals.
    
    """
    BUY = "Buy" # Good for Long Call 
    SELL = "Sell" # Good for Long Put
    NEUTRAL = "Neutral" # Good for Long Butterfly/Iron Condor or collar
    BI_DIR_INWARD = "BiDirectional_Inward" # Good for Long Butterfly/Iron Condor
    BI_DIR_OUTWARD = "BiDierctional_Outward" # Good for Long Straddle/strangle
    
class SignalStatus(Enum):
     ACTIVE = "Active"
     INACTIVE = "Inactive"
    
class SignalCond(Enum):
    # It is a feature paired with a condition with a type
    # al conditions are some logical operation or a function, although 
    # we encourage selecting feature before using the func option

    # (SignalCond, price, 100.0)
    # (ABOVE, (price1-price2/ time), 10)
    # (Equal, price, 10.0)
    # (WITHIN, time_window, [time1, time2])
    
    WITHIN = "Within" # Trigger when the feature is within some range [num1, num2]
    ABOVE = "Above" # Trigger when the feature is above some numbers
    BELOW = "Below" # Trigger when the feature is below some numbers
    EQUAL = "Equal" # Trigger when the feature is equal to some numbers
    FUNC = "Func" # custom function
    
    #IN_TIME = "In_Time" # Trigger when the time is within the time_window
    #PRICE_ABOVE = "Price_Above" # Trigger when the price is above some numbers
    #PRICE_BELOW = "Price_Above" # Trigger when the price is below some numbers
    #PRICE_EQUAL = "Price_Above" # Trigger when the price is equal to some numbers

class SignalActions(Enum):
    # (Action, Order)
    ORDER = "Action1"
    
@dataclass
class Signal(object):
    """
    
    All signals operate within a given time_window
    """
    typ: SignalType
    status: SignalStatus
    EES: dict[str, list[datetime.datetime|float]] #(entry_price, exit_price, stoploss_price), EES with time tag (list)
    time_window: tuple[datetime.datetime] | list[datetime.datetime]#(start_time, end_time) The time window in which this signal is active
    conditions: list[str] #trigger condition for a trade based on this signal
    actions: list[str] # What to do, trade what concepts? has to have the same dim as conditions
    decay_factor: float # or a function

    def __post_init__():
        # check coditions and actions dim
        return 
    
    def confidence(self, time):
        # Between 0 and 1, a probability of the confidence level of this signal
        # Assume exponential decay 
        # Decay_factor a function of feature
        
        return np.exp(-1.0*self.decay_factor*time)
    
if __name__ == "__main__":
    entry_list = []