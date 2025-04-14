#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 27 18:08:14 2025

@author: dexter
"""
import numpy as np
import datetime
import pickle

import EC_tools.utility as util
import EC_tools.utility.math_func as mfunc

from crudeoil_future_const import DAILY_APC_PKL, DAILY_MINUTE_DATA_INDI_PKL,DAILY_DATA_PKL

APC = util.load_pkl(DAILY_APC_PKL)
DAY = util.load_pkl(DAILY_DATA_PKL)

quant_array = np.arange(0.0025, 0.9975, 0.0025)
APC_LENGTH = len(quant_array)

def cal_apc_val(sym, save_filename):
    MINUTE = util.load_pkl(DAILY_MINUTE_DATA_INDI_PKL[sym])
    TRADING_DAYS = DAY[sym]['Date'].to_list()

    # Define start and end dates
    start_date = APC[sym]['PERIOD'].iloc[0]
    end_date = MINUTE[sym]['Date'].iloc[-1]   
    
    # select the range of APC
    sub_history = MINUTE[sym][(MINUTE[sym]['Date']>=start_date)&(MINUTE[sym]['Date']<=end_date)]

    apc_quant_open_bucket, apc_quant_high_bucket = [], []
    apc_quant_low_bucket, apc_quant_settle_bucket = [], []
    cached_date = datetime.datetime(2020,12,31)
    # loop through every elements to calculate the APC quantile value
    for i in range(len(sub_history)):
        date_interest = sub_history['Date'].iloc[i]
        time_ = sub_history['Time'].iloc[i]

        open_price = sub_history['Open'].iloc[i]
        high_price = sub_history['High'].iloc[i]
        low_price = sub_history['Low'].iloc[i]
        settle_price = sub_history['Settle'].iloc[i]
                 
        # Only search for the APC if the current date is not the same as the cached date
        # O(n) search is not the fastest but APC file is small enough to do that
        if date_interest in TRADING_DAYS:
            if cached_date!=date_interest:
                print(date_interest, cached_date, 'TRADING_DAYS')
                  #APC[sym][APC[sym]['PERIOD'] == date_interest].to_numpy())

                curve = APC[sym][APC[sym]['PERIOD'] == date_interest].to_numpy()[0][-1-APC_LENGTH:-1]
                # cache the curve by date
                cached_date = date_interest
            
            # if the time is between 21:00-23:59 and 00:00-03:29, return nan
            if (time_ <= datetime.time(23,59) and time_ >= datetime.time(21,0))or\
                (time_ <= datetime.time(3,29) and time_ >= datetime.time(0,0)):
                #print('date_interest', i, date_interest, time_, 'Bad hours')
                apc_quant_open = np.nan
                apc_quant_high = np.nan
                apc_quant_low = np.nan
                apc_quant_settle = np.nan

            else:
            # Calculate the apc quantile values
                #print('date_interest',i, date_interest, time_)
                apc_quant_open = mfunc.find_quant(curve,quant_array, open_price) 
                apc_quant_high = mfunc.find_quant(curve,quant_array, high_price) 
                apc_quant_low = mfunc.find_quant(curve,quant_array, low_price) 
                apc_quant_settle = mfunc.find_quant(curve,quant_array, settle_price) 
        else:
            print(date_interest, cached_date, 'Not TRADING_DAYS')

            apc_quant_open = np.nan
            apc_quant_high = np.nan
            apc_quant_low = np.nan
            apc_quant_settle = np.nan

        # saving the numbers
        apc_quant_open_bucket.append(apc_quant_open)
        apc_quant_high_bucket.append(apc_quant_high)
        apc_quant_low_bucket.append(apc_quant_low)
        apc_quant_settle_bucket.append(apc_quant_settle)
        
    sub_history['apc_quant_open'] = apc_quant_open_bucket
    sub_history['apc_quant_high'] = apc_quant_high_bucket
    sub_history['apc_quant_low'] = apc_quant_low_bucket
    sub_history['apc_quant_settle'] = apc_quant_settle_bucket
    print(sub_history)
    
    # Saving to pkl
    print("Saving")
    output = open(save_filename, 'wb')
    pickle.dump({sym: sub_history}, output)
    print("Saved")

    output.close()  
    return 

cal_apc_val('QPc2', save_filename='crudeoil_future_minute_QPc2_apc_val.pkl')