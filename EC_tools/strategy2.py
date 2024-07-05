#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul  4 04:59:37 2024

@author: dexter
"""
import numpy as np
from scipy.interpolate import CubicSpline
from typing import Protocol

import EC_tools.math_func as mfunc

# round trip fee 15 dollars
__author__="Dexter S.-H. Hon"

class Strategy(Protocol):
    def __init__(self):
        self._buy_cond_list = [False]
        self._sell_cond_list = [False]
        self._buy_cond = False
        self._sell_cond = False
        self._direction = 'Neutral'

    def gen_strategy_data():
        pass
    
    def strategy_cond():
        pass
    
    def set_EES():
        pass
    def apply_strategy():
        pass
    
class MRStrategyArgus(object):
    """
    Mean-Reversion Strategy. 
    
    """
    def __init__(self):
        self._buy_cond_list = [False]
        self._sell_cond_list = [False]
        self._buy_cond = False
        self._sell_cond = False
        self._neutral_cond = False