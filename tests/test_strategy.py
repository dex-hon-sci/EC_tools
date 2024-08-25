#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 31 03:27:22 2024

@author: dexter
"""
import datetime as datetime
import EC_tools.read as read
from EC_tools.strategy import SignalStatus
from crudeoil_future_const import DATA_FILEPATH

SIGNAL = DATA_FILEPATH + "/APC_latest/APC_latest_CLc1.csv"
HISTORY_DAILY = DATA_FILEPATH + "/history_data/Day/CL.day"
HISTORY_MINUTE = DATA_FILEPATH + "/history_data/Minute/CL.001"

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
        self.price_330 = read.find_price_by_time(self.history_data_daily, 
                                                 self.history_data_minute,
                                                 open_hr='0330')
        self.open_price = self.price_330[
            self.price_330['Date']==self.this_date]['Open Price'].item()

        # Find the APC on this date
        self.curve_this_date = self.signal_data[(
                                self.signal_data['Forecast Period']==self.this_date)]\
                                        .to_numpy()[0][1:-1]

        self.direction = SignalStatus.NEUTRAL
