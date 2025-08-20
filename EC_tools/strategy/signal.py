#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 23 06:46:41 2025

@author: dexter
"""
# python import
from dataclasses import dataclass
from enum import Enum
from typing import Callable
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
    
class SignalSide(Enum):
    """
    A simple class that contains the avaliable status for signals.
    
    """
    BUY = "Buy" # Good for Long Call 
    SELL = "Sell" # Good for Long Put
    NEUTRAL = "Neutral" # Good for Long Butterfly/Iron Condor or collar
    BI_DIR_INWARD = "BiDirectional_Inward" # Good for Long Butterfly/Iron Condor
    BI_DIR_OUTWARD = "BiDierctional_Outward" # Good for Long Straddle/strangle

    
class SignalStatus(Enum):
    """
    To distinguish if a signal is active. 
    Conditions can be made in backtest and live-trading that only active signals
    are to be used.
    """
    ACTIVE = "Active"
    INACTIVE = "Inactive"
    
# =============================================================================
# class SignalCond(Enum):
#     # It is a feature paired with a condition with a type
#     # al conditions are some logical operation or a function, although 
#     # we encourage selecting feature before using the func option
# 
#     # (SignalCond, price, 100.0)
#     # (ABOVE, (price1-price2/ time), 10)
#     # (Equal, price, 10.0)
#     # (WITHIN, time_window, [time1, time2])
#     
#     WITHIN = "Within" # Trigger when the feature is within some range [num1, num2]
#     ABOVE = "Above" # Trigger when the feature is above some numbers
#     BELOW = "Below" # Trigger when the feature is below some numbers
#     EQUAL = "Equal" # Trigger when the feature is equal to some numbers
#     FUNC = "Func" # custom function
#     
#     #IN_TIME = "In_Time" # Trigger when the time is within the time_window
#     #PRICE_ABOVE = "Price_Above" # Trigger when the price is above some numbers
#     #PRICE_BELOW = "Price_Above" # Trigger when the price is below some numbers
#     #PRICE_EQUAL = "Price_Above" # Trigger when the price is equal to some numbers
# 
# =============================================================================
@dataclass
class Signal(object):
    """
    A Signal Object is generated in a Strategy. 
    
    "type_" is a datatype defined by the user 
    
    All signals operate within a given time interval [start_time, end_time]. 
    
    "decay_func" is the function used to calculate the decaying strength 
    of the signal. It is a function of time amoung other parameters (user define).
    The default is a lambda function of a constant value
    
    "actions" contain a list of Order objects (CQG compatible).
    For backtesting, the script should check and unpack the orders to calculate 
    the quantity of interest.
    
    "actions" may contain Orders of different assets.
    
    Changing orders. In backtest or live-trading, we often want to change the 
    order based on the newest information.
    
    "remarks" is a human-readable str for users
    
    The __post_init__ method checks for 
    1) if actions list is empty
    2) if there is at least an 
    3) if there is a closing order object 
    in the action list within the valid time interval.

    """
    type_: SignalType # The type of signal, user defined quality.
    side: SignalSide # The side of signal, either Buy/Sell. Exchagne (CQG) compatiable
    status: SignalStatus # Status for deciding if signal is used
    start_time: datetime.datetime  
    end_time: datetime.datetime
    decay_func: Callable # or a function
    remarks: str
    actions: list[dict[str|float]] # What to do, trade what concepts? has to have the same dim as conditions

    def __post_init__(self):
        # check coditions and actions dim
        
        # check if actions is empty
        if len(self.actions) < 0:
            raise Exception("Action list cannot be empty. Each Signal has to \
                            be paired with an action.")
        # check if there is at least a pair of actions (entry order and exit order)
        if len(self.actions) < 2 and len(self.actions) > 0:
            raise Exception("There should be at least two orders in the action\
                            list, one entry and one exit.")
                            
        # Check if all action falls within the parameters of the time window
        list_ = [order.type_ for order in self.actions]
            
        # Calculate 
        return 
    
    def confidence(self, time):
        # Between 0 and 1, a probability of the confidence level of this signal
        # Assume exponential decay 
        # Decay_factor a function of feature
        
        return np.exp(-1.0*self.decay_factor*time)
    
    
if __name__ == "__main__":
    entry_list = []