#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 10 19:38:52 2024

@author: dexter
"""

import datetime
import random

import pandas as pd
import pandas_market_calendars as mcal

import EC_tools.utility as util
import EC_tools.read as read

from crudeoil_future_const import DAILY_DATA_PKL, DAILY_MINUTE_DATA_PKL

#MARKET_OP_DT = mcal.get_calendar("NYSE").schedule(start_date=datetime.datetime(2021,1,1), 
#                                                  end_date=datetime.datetime.today())['market_open'].to_list()
# Setup all the trading dates and hours
MARKET_VD = mcal.get_calendar("NYSE").valid_days(start_date=datetime.datetime(2021,1,1), 
                                                 end_date=datetime.datetime.today()).to_list()
TRADING_DATES = [ts.to_pydatetime() for ts in MARKET_VD]
TRADING_MINUTES = [(datetime.datetime.combine(datetime.date.today(),
                                              datetime.time(0,0,0))+
                    datetime.timedelta(minutes=1*n)).time() 
                    for n in range(0,1440,1)] #1 minute interval

# Input files
DAY = util.load_pkl(DAILY_DATA_PKL)
MINUTE = util.load_pkl(DAILY_MINUTE_DATA_PKL)


date_interest = datetime.datetime(2022,1,10)

A = MINUTE['CLc1'][MINUTE['CLc1']["Date"] == date_interest]

print(A)
print(A['Time'].iloc[40], type(A['Time'].iloc[40]))




def trade_bytime(df: pd.DataFrame, 
                 t1: datetime.time, 
                 delta_T: datetime.timedelta, 
                 time_proxy: str ='Time', 
                 price_proxy: str ='Open'): # tested
    # random trade, find the return between two time
    # t1 find the closest time
    t1 = datetime.datetime.combine(datetime.date.today(),t1)
    t1_str = datetime.datetime.strftime(t1,"%H%M")
    
    t2 = t1 + delta_T
    t2_str = datetime.datetime.strftime(t2,"%H%M")

    t1, price1 = read.find_closest_price_generic(df, t1_str)
    print('t1, price1', t1, price1.item())


    t2, price2 = read.find_closest_price_generic(df, t2_str)
    print('t2, price2', t2, price2.item())

    r = price2.item()-price1.item()
    print("rrr", r)
    # Calculate the price difference between the two time
    #r = df[df[time_proxy]== t2.time()][price_proxy].item() - \
    #    df[df[time_proxy]== t1][price_proxy].item()
        
    return r

time = datetime.time(21,0,0)
T = datetime.timedelta(seconds=250)
trade_bytime(A,time,T)

def gen_trade_date_list(n: int, date_list: list = TRADING_DATES):
    # pick a list of trading days at random 
    # assume flat probability
    dates = random.sample(date_list, n)
    dates.sort()
    return dates

def gen_open_pos_time_list(n: int, date_list: list = TRADING_MINUTES):
    # pick a list of trading minutes at random 
    # assume flat probability

    return

def gen_pos_duration_list():
    return 

def gen_return_list():
    return





def run_main(minute_data, symbol='CLc1'):
    # read in data
    
    # randomising 
    N_trades = 0
    N_days = 0
    
    delta_T_list = []
    date_list = []
    
    # trade function
    
    
    # plot
    return