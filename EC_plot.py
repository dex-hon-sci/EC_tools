#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 23 23:44:17 2024

@author: dexter
"""
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import EC_read as EC_read

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
    #ax.set_xticks(np.arange(0.0,1.0,(max(x)-min(x))*0.2))
    #ax.set_xticks(ax.get_xticks()[::len(ax.get_xticks())//10])
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

    #ax.set_xticks(np.arange(min(x),max(x),(max(x)-min(x))*0.2))
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
    return None


def cal_APC_pdf(apc_prices):
    #cdf
    even_spaced_prices = np.arange(np.min(apc_prices), np.max(apc_prices), 0.005)
    
    print(len(even_spaced_prices))
    
    spline_apc_rev = UnivariateSpline(apc_prices, np.arange(0.0025, 0.9975, 0.0025), s = 0)
    quantiles_even_prices = spline_apc_rev(even_spaced_prices)

    dq = even_spaced_prices[1]-even_spaced_prices[0]
    deriv = fd.FinDiff(0, dq, 1)
    pdf = deriv(quantiles_even_prices)
    
    print(len(pdf))
    
    spline_pdf = UnivariateSpline(even_spaced_prices, pdf,  s = 0.0015)
    pdf = spline_pdf(even_spaced_prices)
    
    print(len(pdf))
    return even_spaced_prices, pdf

def cal_APC_pdf_2(apc_prices):
    #cdf
    x = np.arange(0.0025, 0.9975, 0.0025)
    print(len(x))
    
    spline_apc = UnivariateSpline(x, apc_prices, s = 0)
    
    quantiles_even_prices = spline_apc(x)
    print(quantiles_even_prices)
    
    dq = x[1]-x[0]
    deriv = fd.FinDiff(0, dq, 1)
    pdf = deriv(quantiles_even_prices)
        
    #spline_pdf = UnivariateSpline(x, pdf,  s = 0.0015)
    #pdf = spline_pdf(x)
    
    print(len(pdf))
    return pdf

username, password = "dexter@eulercapital.com.au", "76tileArg56!"
start_date = "2024-03-12"
end_date = "2024-03-13"
categories = 'Argus Nymex WTI month 1, Daily'
keywords = "WTI"
symbol = "CL"

filename_daily = "../test_MS/data_zeroadjust_intradayportara_attempt1/Daily/CL.day"


curve = EC_read.get_apc_from_server(username, password, start_date, end_date, 
                                    categories, keywords=keywords,symbol=symbol)
curve = curve[curve['Forecast Period'] == "2024-03-13"]

x1 = np.arange(0.0, 399, 1.0)

even_spaced_prices, pdf = cal_APC_pdf(curve.to_numpy()[0][1:-1])

print(pdf)

even_spaced_prices = np.arange(np.min(curve.to_numpy()[0][1:-1]), 
                               np.max(curve.to_numpy()[0][1:-1]), 0.005)

x0 = np.asarray(curve.keys().to_numpy()[1:-1],float)
print(type(x0[0]))

plot_distribution(x0, curve.to_numpy()[0][1:-1])
                  
plot_distribution(even_spaced_prices, pdf)
           

plot_distribution_2(x0, curve.to_numpy()[0][1:-1],
                    pdf, even_spaced_prices)