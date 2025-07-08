#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 20 11:36:29 2024

@author: dexter

This module contains simple fucntions that generate dervied quantity from a 
base data set.

For example, time, prices, and volume are base data set (Independent variables).
VWAP, BollingerBand, and etc. are the derived quantity, 
hence features (Dependent varaiables).
"""
import datetime
import numpy as np
import pandas as pd
import EC_tools.math_func as mfunc


def resample(df: pd.DataFrame, time_interval = "15Min") -> pd.DataFrame:
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

def cal_VWAP(df:pd.DataFrame) -> pd.DataFrame:
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

# =============================================================================
# def add_VWAP2df(df: pd.DataFrame, 
#                 unique_date: list[datetime.datetime]) -> pd.DataFrame:
#     # Add VWAP and STD to a dataframe
#     # Generate daily VWAP, add it to the dataframe
#     #unique_date = list(set([df["Date"].iloc[i] for i,_ in enumerate(df["Date"].to_list())]))
#     #unique_date.sort()
# 
#     new_df = pd.DataFrame()
#     for date in unique_date[1:2]:
#         print(date, type(date))
#         start_date = date + datetime.timedelta(hours=3,minutes=30)
#         end_date = date + datetime.timedelta(hours=22,minutes=0)
#         
#         # Select for a sub-dataframe to calculate the vwap of the day
#         sub_df = df[(df['Datetime'] >= start_date) &(df['Datetime'] <end_date)]
# 
#         print("sub_df", sub_df)
#         new_sub_df = cal_VWAP(sub_df)
#         
#         # Plot the daily chart to check if the VWAP range is reasonable
#         new_df = pd.concat([new_df, new_sub_df])
#     return new_df
# =============================================================================
        
def add_VWAP2df(df:pd.DataFrame, 
                unique_date:list[datetime.datetime], 
                open_hr: str, close_hr:str)->pd.DataFrame:
    # Add VWAP and STD to a dataframe
    # Generate daily VWAP, add it to the dataframe
    #unique_date = list(set([df["Date"].iloc[i] for i,_ in enumerate(df["Date"].to_list())]))
    #unique_date.sort()

    new_df = pd.DataFrame()
    for date in unique_date:
        print(date, type(date))
        
        delta = datetime.timedelta(minutes=60*3)
        start_date = date + datetime.timedelta(hours = int(open_hr[0:2]),
                                               minutes = int(open_hr[2:4]))
        end_date = date + datetime.timedelta(hours = int(close_hr[0:2]),
                                             minutes = int(close_hr[2:4])) +delta
        
        # Select for a sub-dataframe to calculate the vwap of the day
        sub_df = df[(df['Datetime'] >= start_date) &(df['Datetime'] <=end_date)]

        print("sub_df", sub_df)
        new_sub_df = cal_VWAP(sub_df)
        
        # Plot the daily chart to check if the VWAP range is reasonable
        new_df = pd.concat([new_df, new_sub_df])
    return new_df

def add_ATR(df: pd.DataFrame,
            period:int=14):
    df['high_low'] = df['High'] - df['Low']
    df['high_prev_close'] = abs(df['High'] - df['Settle'].shift(1))
    df['low_prev_close'] = abs(df['Low'] - df['Settle'].shift(1))
    df['True_Range'] = df[['high_low', 'high_prev_close', 'low_prev_close']].max(axis=1)

    # Calculate ATR using Exponential Moving Average (EMA) of True Range
    # The standard ATR calculation uses a modified EMA where the smoothing factor
    # is 1/period for the first ATR value, and then (previous_ATR * (period - 1) + current_TR) / period
    # for subsequent values. Pandas ewm with adjust=False approximates this.
    df['ATR'] = df['True_Range'].ewm(span=period, adjust=False).mean()

    # Clean up intermediate columns
    df = df.drop(columns=['high_low', 'high_prev_close', 
                          'low_prev_close', 'True_Range'])
    return df


def reindex_dt(df:pd.DataFrame):
    # Add Datetime column into the dataframe
    date_series = [ele.date() for ele in df['Date'].to_list()]
    time_series = df['Time'].to_list()
    datetime_series = [datetime.datetime.combine(date,time) 
                       for date, time in zip(date_series, time_series)]
    
    df['Datetime'] = datetime_series
    df = df.set_index('Datetime')
    df['Datetime'] = df.index

    #df.reset_index(inplace=True)

    return df

