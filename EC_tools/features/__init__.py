#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 18 21:35:29 2024

@author: dexter
"""

# Make a class that can load features

# Define input types OHLCV?
import pandas as pd


feature_dict = {}

class Features():
    def __init__(self, data: pd.DataFrame):
        self.data = data 
        self.new_data = data
        self._func_dict = {}
        
    def add(self, feature_name:str, **kwrags):
        feature = self._func_dict
        self.new_data[feature_name] = feature
        return self.new_data
    
    
## Usage 
# new_df = Features(OHLC).add("VWAP", **para)