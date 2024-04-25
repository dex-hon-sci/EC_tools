#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 23 23:44:17 2024

@author: dexter
"""
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import EC_read as EC_read
import math_func as mfunc

import numpy as np
from scipy.interpolate import CubicSpline, UnivariateSpline
import findiff as fd 


def plot_distribution(x,y):
    
    fig, ax = plt.subplots(figsize=(8,4))
    ax.plot(x, y,'o-', ms=2)
    ax.set(xlabel='quantile', ylabel='Price',
       title='')
    # reduce the number of ticks to 5
    ax.set_xticks(np.arange(min(x),max(x),(max(x)-min(x))*0.2))
    ax.grid()

    #fig.savefig("test.png")
    plt.show()

    return None

def plot_distribution_2(x,y,x1,y1):
    fig, ax = plt.subplots(figsize=(8,4))
    ax.plot(x, y,'o-', ms=2)
    ax.plot(x1, y1,'o-', ms=2)
    ax.set(xlabel='quantile', ylabel='Price',
       title='')

    ax.set_xticks(np.arange(0.0,1.0,(max(x)-min(x))*0.2))

    ax.grid()

    #fig.savefig("test.png")
    plt.show()

    return None

def plot_price(df):
    # plot a price chart with minute data
    # subplot 2 volume and price
    # time open high low settle 
    # volume
    fig = go.Figure(data=go.Ohlc(x=df['Date'],
                    open=df['Open'],
                    high=df['High'],
                    low=df['Low'],
                    close=df['Settle']))
    return fig

username, password = "dexter@eulercapital.com.au", "76tileArg56!"
start_date = "2024-03-12"
start_date_2 = "2024-01-01"

end_date = "2024-03-13"
categories = 'Argus Nymex WTI month 1, Daily'
keywords = "WTI"
symbol = "CL"

filename_daily = "../test_MS/data_zeroadjust_intradayportara_attempt1/Daily/CL.day"
filename_minute = "../test_MS/data_zeroadjust_intradayportara_attempt1/intraday/1 Minute/CL.001"

curve = EC_read.get_apc_from_server(username, password, start_date, end_date, 
                                    categories, keywords=keywords,symbol=symbol)
curve = curve[curve['Forecast Period'] == "2024-03-13"]


quant0 = np.arange(0.0025, 0.9975, 0.0025)
even_spaced_prices, pdf = mfunc.cal_pdf(quant0, curve.to_numpy()[0][1:-1])

#x1 = np.arange(0.0, 399, 1.0)
#even_spaced_prices = np.arange(np.min(curve.to_numpy()[0][1:-1]), 
#                               np.max(curve.to_numpy()[0][1:-1]), 0.005)
#plot_distribution(x0, curve.to_numpy()[0][1:-1])                  
#plot_distribution(even_spaced_prices, pdf)
           

x0 = np.asarray(curve.keys().to_numpy()[1:-1],float)

plot_distribution_2(x0, curve.to_numpy()[0][1:-1],
                    pdf, even_spaced_prices)

history_data_daily = EC_read.read_portara_daily_data(filename_daily,symbol,
                                                 start_date_2,end_date)
history_data_minute = EC_read.read_portara_minute_data(filename_minute,symbol, 
                                                  start_date_2, end_date,
                                                   start_filter_hour=30, 
                                                   end_filter_hour=331)
history_data = EC_read.merge_portara_data(history_data_daily, history_data_minute)

print(history_data.iloc[0])

portara_dat = history_data[history_data['Date only']==]

print(portara_dat)

#plot_price(portara_dat)
