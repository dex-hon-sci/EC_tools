#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 31 03:27:22 2024

@author: dexter
"""
import datetime as datetime
import numpy as np
import pytest

from EC_tools.strategy import ArgusMRStrategy, SignalStatus
import EC_tools.read as read
import EC_tools.math_func as mfunc
import EC_tools.utility as util

SIGNAL = "/home/dexter/Euler_Capital_codes/EC_tools/data/APC_latest/APC_latest_CLc1.csv"
HISTORY_DAILY = "/home/dexter/Euler_Capital_codes/EC_tools/data/history_data/Day/CL.day"
HISTORY_MINUTE = "/home/dexter/Euler_Capital_codes/EC_tools/data/history_data/Minute/CL.001"

BUY_DATE_STR = "2021-03-02" #Buy date
SELL_DATE_STR = "2022-02-22" #Sell date
NEUTRAL_DATE_STR = "2021-01-27" #Neutral date

class SingleRun():
    """
    A class that load a single date for a run in signal generation. 
    You can use this on unit tests.
    """
    def __init__(self, date_str, 
                 signal_filename = SIGNAL, 
                 filename_daily = HISTORY_DAILY, 
                 filename_minute= HISTORY_MINUTE,
                 symbol= 'CLc1'):
        
        self.this_date = datetime.datetime.strptime(date_str, '%Y-%m-%d')
        # The reading part takes the longest time: 13 seconds. The loop itself takes 
        # input 1, APC. Load the master table in memory and test multple strategies   
        self.signal_data =  read.read_reformat_APC_data(signal_filename)
        
        # input 2, Portara history file.
        # start_date2 is a temporary solution 
        self.history_data_daily = read.read_reformat_Portara_daily_data(filename_daily)
        self.history_data_minute = read.read_reformat_Portara_minute_data(filename_minute)
        
        # Add a symbol column
        self.history_data_daily['symbol'] = [symbol for i in range(len(self.history_data_daily))]
        self.history_data_minute['symbol'] = [symbol for i in range(len(self.history_data_minute))]
        
        # Find the opening price at 03:30 UK time. If not found, 
        #loop through the next 30 minutes to find the opening price
        self.price_330 = read.find_open_price(self.history_data_daily, self.history_data_minute)
        self.open_price = self.price_330[
            self.price_330['Date']==self.this_date]['Open Price'].item()

        # Find the APC on this date
        self.curve_this_date = self.signal_data[(
                                self.signal_data['Forecast Period']==self.this_date)]\
                                        .to_numpy()[0][1:-1]

        self.direction = SignalStatus.NEUTRAL