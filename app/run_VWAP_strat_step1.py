#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 24 17:31:37 2025

@author: dexter
"""
import sys
sys.path.insert(0, "/home/dexter/Euler_Capital_codes/EC_tools")
import datetime
import pandas as pd
import numpy as np

import EC_tools.utility as util
from crudeoil_future_const import DAILY_MINUTE_DATA_INDI_PKL

def load_source_data_bt(filenames_loc: list) -> dict:
    master_dict = {}
    for filename in filenames_loc:
        temp_dict = util.load_pkl(filename)
        master_dict = dict(master_dict, **temp_dict)
        
    return master_dict

def reindex_dt(df:pd.DataFrame):
    date_series = [ele.date() for ele in df['Date'].to_list()]
    time_series = df['Time'].to_list()
    datetime_series = [datetime.datetime.combine(date,time) for date, time in zip(date_series, time_series)]
    
    df['Datetime'] = datetime_series
    df = df.set_index('Datetime')
    #df.reset_index(inplace=True)

    return df

def resample(df: pd.DataFrame, time_interval = "15Min"):
    ohlc_dict = {'Date':'first',
                 #'Time': '',
                'Open': 'first',
                'High': 'max',
                'Low': 'min',
                'Settle': 'last',
                'Volume': 'sum'  # Include if volume data is present
                }

    new_df = df.resample(time_interval).apply(ohlc_dict)
    new_df['Datetime'] = new_df.index

    return new_df


def cal_VWAP(df:pd.DataFrame):
    # high + low + close
    TPrice = (df['High'] + df['Low'] + df['Settle'])/3
    TPVolume_cumsum = (TPrice*df['Volume']).cumsum() #vwapsum
    TP2Volume_cumsum = (TPrice*TPrice*df['Volume']).cumsum() #v2sum
    volume_cumsum = df['Volume'].cumsum()
    
    # Calculate the VWAP value
    vwap = TPVolume_cumsum/volume_cumsum
    # Calculate the std of the vwap
    dev = np.sqrt((TP2Volume_cumsum/volume_cumsum-vwap*vwap))
    print('vwap',vwap, 'dev',dev)
    df['VWAP'] = vwap
    df['VWAP_DEV'] = dev
    return df
import matplotlib.dates as mdates
import matplotlib.pyplot as plt

def plot_VWAP(df, title=''):
    fig, axs = plt.subplots(1, 1, figsize=(10, 4), layout='constrained')
    fmt = mdates.DateFormatter("%H:%M:%S")

    axs.plot(df['Datetime'].to_list(), df['Open'].to_list(), 'o-')
    axs.plot(df['Datetime'].to_list(), df['VWAP'].to_list(), 'o-', color= 'grey', ms=3)
    axs.plot(df['Datetime'].to_list(), (df['VWAP']+1.28*df['VWAP_DEV']).to_list(), 'r-', ms=3)
    axs.plot(df['Datetime'].to_list(), (df['VWAP']-1.28*df['VWAP_DEV']).to_list(), 'r-', ms=3)
    axs.plot(df['Datetime'].to_list(), (df['VWAP']+2.01*df['VWAP_DEV']).to_list(), 'r-', ms=3)
    axs.plot(df['Datetime'].to_list(), (df['VWAP']-2.01*df['VWAP_DEV']).to_list(), 'r-', ms=3)
    axs.plot(df['Datetime'].to_list(), (df['VWAP']+2.51*df['VWAP_DEV']).to_list(), 'r--', ms=3)
    axs.plot(df['Datetime'].to_list(), (df['VWAP']-2.51*df['VWAP_DEV']).to_list(), 'r--', ms=3)
    axs.plot(df['Datetime'].to_list(), (df['VWAP']+3.09*df['VWAP_DEV']).to_list(), 'r--', ms=3)
    axs.plot(df['Datetime'].to_list(), (df['VWAP']-3.09*df['VWAP_DEV']).to_list(), 'r--', ms=3)
    axs.plot(df['Datetime'].to_list(), (df['VWAP']+4.01*df['VWAP_DEV']).to_list(), 'r--', ms=3)
    axs.plot(df['Datetime'].to_list(), (df['VWAP']-4.01*df['VWAP_DEV']).to_list(), 'r--', ms=3)

    axs.xaxis.set_major_formatter(fmt)
    axs.grid()
    axs.set_title(title)
    axs.set_ylabel('Price')
    axs.set_xlabel('Time')
    plt.legend()
    plt.show()


def add_VWAP2df(df):
    # Add VWAP and STD to a dataframe
    # Generate daily VWAP, add it to the dataframe
    unique_date = list(set([df["Date"].iloc[i] for i,_ in enumerate(df["Date"].to_list())]))
    unique_date.sort()

    new_df = pd.DataFrame()
    for date in unique_date[1:3]:
        print(date, type(date))
        start_date = date
        end_date = date + datetime.timedelta(hours=23,minutes=59)
        
        # Select for a sub-dataframe to calculate the vwap of the day
        sub_df = df[(df['Datetime'] >= start_date) &(df['Datetime'] <end_date)]

        print("sub_df", sub_df)
        new_sub_df = cal_VWAP(sub_df)
        
        # Plot the daily chart to check if the VWAP range is reasonable
        plot_VWAP(new_sub_df,title=f"CLc1: {date.strftime('%m-%d-%Y')}")
        new_df = pd.concat([new_df, new_sub_df])
    return new_df
        
        
#vwapsum = iff(newSession, hl2*volume, vwapsum[1]+hl2*volume)
#volumesum = iff(newSession, volume, volumesum[1]+volume)
#v2sum = iff(newSession, volume*hl2*hl2, v2sum[1]+volume*hl2*hl2)
#myvwap = vwapsum/volumesum
#dev = sqrt(max(v2sum/volumesum - myvwap*myvwap, 0))


# New Signal format
class VWAPInversionStrategy():
    def __init__():
        pass
    
    def gen_data():
        return
    
    def run_cond(data_15min:pd.DataFrame,
                 last_data_15min:pd.DataFrame, 
                 last_data_1min:pd.DataFrame, 
                 N:float
                 ):
        # data_1min: 15 entry datagrame, matching data_15min
        # data_15min: single entry dataframe 
        
        # Input 15mins data, and 1 mind data
        # Input VWAP upper and lower Threshold
        VWAP_up = last_data_15min['VWAP'] + last_data_15min['VWAP_DEV'].iloc[0]*N
        VWAP_low = last_data_15min['VWAP'] - last_data_15min['VWAP_DEV'].iloc[0]*N
        
        # If 15mins data < VWAP upper Threshold
        # And next 15mins bar close at 70% above the previous bar
        # ->Sell direction
        cond_buy_list1= [len(last_data_1min[last_data_1min['Open']>VWAP_up])>0]
        cond_buy_list2= []
        
        # If 15mins data > VWAP upper Threshold
        # And next 15mins bar close at 70% below the previous bar
        # ->Sell direction
        cond_sell_list1= [len(last_data_1min[last_data_1min['Open']<VWAP_low])>0]
        cond_sell_list2= []

        return 
    
    def set_EES():
        
        entry_price = 0
        
        return 
    
    def apply_strategy():
        return
    
# Loop daily and find
def loop_signal():
    
    
    return 


def main():
    # Load Historical data
    #HISTORY_MINUTE_PKL = load_source_data_bt(list(DAILY_MINUTE_DATA_INDI_PKL.values()))
    HISTORY_MINUTE_PKL = load_source_data_bt([DAILY_MINUTE_DATA_INDI_PKL['CLc1']])

    # reindexing with time
    HISTORY_MINUTE_PKL['CLc1'] = reindex_dt(HISTORY_MINUTE_PKL['CLc1'])
    print(HISTORY_MINUTE_PKL['CLc1'])

    # Preprocess Resample
    # Turn historic data intpo 15 mins interval
    new_df = resample(HISTORY_MINUTE_PKL['CLc1'])
    
    # Select for only entries after 2021-1-1
    new_df = new_df[new_df['Datetime'] > datetime.datetime(2024,10,4)]
    print(new_df)
    # Calculate VWAP, save it in the dataframe as a new column.
    # Plot them if needed
    new_df = add_VWAP2df(new_df)
    
    print("new_df", new_df)
    
    # New Signal format
    # Loop daily and find

main()