#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 20 10:42:37 2025

@author: dexter
"""
from enum import Enum

    
class SignalStatus(Enum):
    """
    To distinguish if a signal is active. 
    Conditions can be made in backtest and live-trading that only active signals
    are to be used.
    """
    ACTIVE = "Active"
    INACTIVE = "Inactive"

class SignalType(Enum): # WIP
    """
    A simple class that contains the avaliable status for signals.
    
    """
    # First-Order Signals
    UP = "Up" # Good for Long Call 
    DOWN = "Down" # Good for Long Put
    NO_MEAN_CHANGE = "No-mean-change" # For Neutral First order signal
    # Second-Order Signals
    CONVERGENCE = "Convergence" # Good for Long Butterfly/Iron Condor
    DIVERGENCE = "Divergence" # Good for Long Straddle/strangle
    NO_VAR_CHANGE = "No-variance-change" # For Neutral Second order signal
    # Third-Order Signals
    UP_SKEW = "Up-skew" # Good for Short Ratio Call Spread 
    DOWN_SKEW = "Down-skew" # Good for Short Ratio Put Spread 
    NO_SKEW_CHANGE = "No-skew" # For Neutral Third order signal
    # Fourth-Order Signals
    LEPTOKURTIC = "Leptokurtic" # Thin tail
    PLATYKURTIC = "Platykurtic" # Fat tail
    MESOKURTIC = "Mesokurtic" # For Neutral Foruth order signal
    
class FirstOrderSignalType(Enum):
    # First-Order Signals
    UP = "Up" # Good for Long Call 
    DOWN = "Down" # Good for Long Put
    NO_MEAN_CHANGE = "No-mean-change" # For Neutral First order signal

    

