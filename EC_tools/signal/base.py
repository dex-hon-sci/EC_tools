#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 20 10:41:05 2025

@author: dexter
"""
from datetime import datetime
from dataclasses import dataclass
from typing import Callable
# Python package imports
import numpy as np
# EC_tools imports
from EC_tools.signal.enums import (
    SignalType,
    SignalStatus
    )

@dataclass
class Signal:
    """
    A Signal Object is generated in a Strategy. 
    
    "type_" is a dataclass object defined by the user's strategy. 
    It usually means the anticipated price movement of one particular asset
    
    "start_time" and "end_time":
    All signals operate within a given time interval [start_time, end_time]. 
    The time range is an absolute. Backtest engines only process data within 
    this given time.
    
    "decay_func" is the function used to calculate the decaying strength 
    of the signal. It is a function of time amoung other parameters (user define).
    The default is a lambda function of a constant value
    
    "actions" contain a list of Order objects (CQG compatible).
    For backtesting, the script should check and unpack the orders to calculate 
    the quantity of interest.
    
    "actions" may contain Orders of different assets. (action should be a tree?)
    
    Changing orders. In backtest or live-trading, we often want to change the 
    order based on the newest information.
    
    "remarks" is a human-readable str for users
    
    The __post_init__ method checks for 
    1) if actions list is empty
    2) if there is at least an 
    3) if there is a closing order object 
    in the action list within the valid time interval.

    """
    type_: SignalType # The type of signal, user defined quality. Condition for triggering is also user defined
    status: SignalStatus # Status for deciding if signal is used
    start_time: datetime  
    end_time: datetime
    actions: list[dict[str|float]] # What to do, trade what concepts? has to have the same dim as conditions
    decay_func: Callable = None # or a function
    remarks: str = ""

    def __post_init__(self):
        # check coditions and actions dim
        
        # For Neutral Signal (regardless of the direction), Actions can be empty.
        
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
    
    def confidence(self, time): # WIP # Input to be some observables: time, price, volume, IV,...
        # Between 0 and 1, a probability of the confidence level of this signal
        # Assume exponential decay 
        # Decay_factor a function of feature
        
        return np.exp(-1.0*self.decay_factor*time)
    
class CompositeSignal(object):
    """
    WIP 
    
    A class that combine multiple `Signal` into one.
    
    It allows for overriding the actions in the input Signals.
    
    For example, there are three signals for Asset A at the same time.
        Signal_1: type_ = UP, actions = [#BUY @low, #SELL @high] (Long Asset A)
        Signal_2: type_ = CONVERGENCE, actions = [#Long Butterfly (...), #CLOSE Trade @some time] (Long Buttefly)
        Signal_3: type_ = PLATYKURTIC, actions = [#Long Condor Asset, #CLOSE Trade @some time] (Tail Hedge)

    Functions in this class define the `policy` to pick the right action in
    this situation.
    Factors like Signal decay time, and confidence level, as well as final
    possible payoffs should be considered. 
    
    One can either pick a set of action from one of the Signal or make a new 
    action based on actions.
    
    """
    def __init__(self, policy: Callable, signals: list[Signal]):
        self.policy = policy
        self.signals = signals

    def assemble(self) -> Signal: 
        # Produce a new signal objecy based on some policy
        return 