#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 23 23:44:17 2024

@author: dexter
"""
import pandas as pd
import numpy as np
from plotly.offline import iplot
from plotly.offline import plot, init_notebook_mode

import matplotlib.gridspec as gridspec

import matplotlib.pyplot as plt
import plotly.graph_objects as go

import EC_read as EC_read
import math_func as mfunc

color_dict_light_mode = {}
color_dict_dark_mode = {}

class PlotPricing(object):
    
    def __init__(self):
        self._color_mode = None
        return None

def plot_distribution(x,y, color = 'k', title = "",
                      xlabel = 'quantile', ylabel = 'Price'):
    
    fig, ax = plt.subplots(figsize=(8,4))
    ax.plot(x, y,'o--', ms=1, c= color)
    ax.set(xlabel = xlabel, ylabel = ylabel,
       title=title)
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
    import plotly.io as pio


    fig = go.Figure(data=go.Ohlc(x=df['Time'], open =df['Open'],
                    high=df['High'],
                    low=df['Low'],
                    close=df['Settle']))
    fig.update(layout_xaxis_rangeslider_visible=False)
    fig.show(renderer="browser")
    #iplot(fig)
    return fig

def plot_price_BIG(x,y,events, pdf, 
                   quant_list, quant_price_list, 
                   price_chart_title = "Date", 
                   open_hr = 300, close_hr=2000):
    
    fig = plt.figure(figsize=(10,4))
    gs = fig.add_gridspec(nrows=1, ncols = 2, width_ratios = [4,1])

    ax1 = fig.add_subplot(gs[0])
    #plot_candlestick_chart(price,ax1)

    ax1.plot(x, y,'o--', ms=2, c='k')

    
    # fill the closed trading hours with shade
    ax1.fill_between([0,open_hr], 0, 2000, color='grey', alpha=0.3)
    ax1.fill_between([close_hr,2500], 0, 2000, color='grey', alpha=0.3)
    
    # the vertical lines that
    ax1.vlines(open_hr, 0, 2000, 'k')
    ax1.vlines(close_hr, 0, 2000, 'k')
    
    ax1.set_xlim([-10, 2400])
    ax1.set_ylim([min(events), max(events)])
    
    ax1.set_xlabel("Time (minutes)")
    ax1.set_ylabel("Price (USD)")
    ax1.set_title(price_chart_title)
    ax1.grid()

    ax2 = fig.add_subplot(gs[1], sharey=ax1)
    ax2.plot(pdf, events, 'o', c='orange', ms =2)
    
    quant_list = ['q0.1','q0.4','q0.5','q0.6','q0.9']
    
    for quant, price in zip(quant_list, quant_price_list):
        ax1.hlines(price, 0, 2500.0, color='#C26F05')
        ax1.text( 0.0 + np.std(pdf)/2, price+ np.std(events)/200, quant, 
                 fontsize=8, color='#C26F05')

        ax2.hlines(price, 0, 2500.0, color='#C26F05')
        ax2.text( 0.0 + np.std(pdf)/2, price+ np.std(events)/200, quant, 
                 fontsize=8, color='#C26F05')
    
    ax2.set_xlim([0, max(pdf)+ np.std(pdf)/4])

    ax2.set_title('APC')
    ax2.set_xlabel("Probability")
    ax2.invert_xaxis()
    ax2.grid()

    plt.show()
    
    return fig

# make a class for plotting minute data
# Strategy on off button and it changes all plots moving forwards

def add_quant_lines(ax, quant_list, quant_price_list, txt_x, txt_y, alpha = 0.5):
    
    txt_x, txt_y = 0.0 + np.std(pdf)/2, price+ np.std(events)/200

    for quant, price in zip(quant_list, quant_price_list):
        print(quant, price)
        ax.hlines(price, 0, 1.0, color='#C26F05', alpha = alpha)
        ax.text(txt_x, txt_y, quant, 
                 fontsize=8, color='#C26F05')
        
def add_EES_region():
    # add Entry, Exit, Stop Loss regions
    for quant, price in zip(quant_list, quant_price_list):
        print(quant, price)
        ax.hlines(price, 0, 1.0, color='#C26F05')
        ax.text(txt_x, txt_y, quant, 
                 fontsize=8, color='#C26F05')
        
    return None
    
def plot_candlestick_chart(prices,ax):

    # "up" dataframe will store the stock_prices  
    # when the closing stock price is greater than or equal to the opening stock prices 
    up = prices[prices.Settle >= prices.Open] 
  
    # "down" dataframe will store the stock_prices 
    # when the closing stock price is lesser than the opening stock prices 
    down = prices[prices.Settle < prices.Open] 
  
    # When the stock prices have decreased, then it 
    # will be represented by blue color candlestick 
    col1 = 'red'
  
    # When the stock prices have increased, then it  
    # will be represented by green color candlestick 
    col2 = 'green'
  
    # Setting width of candlestick elements 
    width = 2
    width2 = .5
  
    # Plotting up prices of the stock 
    ax.bar(up.index, up.Settle-up.Open, width, bottom=up.Open, color=col1) 
    ax.bar(up.index, up.High-up.Settle, width2, bottom=up.Settle, color=col1) 
    ax.bar(up.index, up.Low-up.Open, width2, bottom=up.Open, color=col1) 
  
    # Plotting down prices of the stock 
    ax.bar(down.index, down.Settle-down.Open, width, bottom=down.Open, color=col2) 
    ax.bar(down.index, down.High-down.Open, width2, bottom=down.Open, color=col2) 
    ax.bar(down.index, down.Low-down.Settle, width2, bottom=down.Settle, color=col2) 
    

username, password = "dexter@eulercapital.com.au", "76tileArg56!"
start_date = "2024-03-12"
start_date_2 = "2024-01-01"

end_date = "2024-03-13"
categories = 'Argus Nymex WTI month 1, Daily'
keywords = "WTI"
symbol = "CL"

filename_daily = "../test_MS/data_zeroadjust_intradayportara_attempt1/Daily/CL.day"
filename_minute = "../test_MS/data_zeroadjust_intradayportara_attempt1/intraday/1 Minute/CL.001"

##curve = EC_read.get_apc_from_server(username, password, start_date, end_date, 
##                                    categories, keywords=keywords,symbol=symbol)

##
##x0 = np.asarray(curve.keys().to_numpy()[1:-1],float)
##
##plot_distribution_2(x0, curve.to_numpy()[0][1:-1],
##                    pdf, even_spaced_prices)


#x1 = np.arange(0.0, 399, 1.0)
#even_spaced_prices = np.arange(np.min(curve.to_numpy()[0][1:-1]), 
#                               np.max(curve.to_numpy()[0][1:-1]), 0.005)
#plot_distribution(x0, curve.to_numpy()[0][1:-1])                  
#plot_distribution(even_spaced_prices, pdf)
           

def plot_minute(filename):
    #date_interest = "2022-05-11"
    
    # read the reformatted minute history data
    history_data = read_reformat_Portara_minute_data(filename)
    
    date_interest = "2022-05-19"
    
    interest = history_data[history_data['Date']  == date_interest]
    
    print(interest['Open'])
    
    x = interest['Time']
    y = interest['Settle']
    ######################################################
    curve = EC_read.read_apc_data("APC_latest_CL.csv")

    curve = curve[curve['Forecast Period'] == date_interest]
    quant0 = np.arange(0.0025, 0.9975, 0.0025)
    even_spaced_prices, pdf = mfunc.cal_pdf(quant0, curve.to_numpy()[0][1:-1])
    
    print("find_quant", mfunc.find_quant(curve.to_numpy()[0][1:-1], quant0, 97.9366))
    
    quant_list=['q0.1','q0.4','q0.5','q0.6','q0.9']
    quant_price_list = [curve['0.1'], curve['0.4'], curve['0.5'], curve['0.6'], curve['0.9']]
    print("curve curve",quant_price_list)

    price = interest.set_index('Time')


    plot_price_BIG(x,y, even_spaced_prices, pdf, quant_list, quant_price_list, 
                   price_chart_title=date_interest,price=None)
    
    

    
def read_reformat_Portara_minute_data(filename):
    history_data =  pd.read_csv(filename)
    history_data.columns = ['Date', 'Time', 'Open', 'High', 'Low', 
                            'Settle', 'Volume', 'Contract Code']
    history_data['Date'] = [str(x)[0:4] + '-' + str(x)[4:6] + '-' + str(x)[6:] 
                            for x in history_data['Date']]
    return history_data
    
plot_minute(filename_minute)


