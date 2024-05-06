#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 23 23:44:17 2024

@author: dexter

"""
import pandas as pd
import numpy as np
from dataclasses import dataclass


from plotly.offline import iplot
from plotly.offline import plot, init_notebook_mode
import datetime as datetime

import matplotlib.dates as mdates
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt

import plotly.graph_objects as go

# import EC_tools
import EC_read as EC_read
import math_func as mfunc
import utility as util

color_dict_light_mode = {'data_col':'k','bg_col':'white', 'col':'g'}
color_dict_dark_mode = {'data_col':'white','bg_col':'k', 'col':'g'}

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

    return fig

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

    return fig

def plot_price(df):
    # plot a price chart with minute data
    # subplot 2 volume and price
    # time open high low settle 
    # volume


    fig = go.Figure(data=go.Ohlc(x=df['Time'], open =df['Open'],
                    high=df['High'],
                    low=df['Low'],
                    close=df['Settle']))
    fig.update(layout_xaxis_rangeslider_visible=False)
    fig.show(renderer="browser")
    return fig

@dataclass
class AxsesShade(object):
    # add axeses and shaded area
    def __init__(self):
        return None
    
@dataclass
class SubPlots(object):
    # add subplots
    def __init__(self):
        return None

class PlotPricing(object):
    # A clss that control the state of the pricing plots.
    
    # input other class objects here
    
    def __init__(self):
        self._pdf_mode = None
        self._add_APC_panel
        self._add_quant_lines = None
        self._add_EES_regions = None
        self._add_entry_exit_points = None
        self._add_bol_band = None
        return None
    
    def controller(object):
        # detemine whether the data is intraday minute data, seconds or days
        return None

    


def plot_price_BIG(x,y, events, pdf, 
                   quant_list, quant_price_list, direction="Neutral",
                   price_chart_title = "Date", 
                   open_hr = "0330", close_hr="1900",
                   events_lower_limit=70, events_upper_limit =78,
                   buy_time = "1201", buy_price =  86.05,
                   sell_time = "1900", sell_price = 85.70, 
                   bppt_x1 = [], bppt_y1 = [], 
                   bppt_x2 = [], bppt_y2 = [], 
                   bppt_x3 =[], bppt_y3 = []):
    """
    A function that plot the intraday minute pricing chart alongside the APC.

    Parameters
    ----------
    x : list
        The intraday minutes.
    y : list
        The price of intraday data.
    events : list
        The price of the APC.
    pdf : list
        The probability of the APC's pdf.
    quant_list : list
        A list of quantile name for text marking on the plot.
    quant_price_list : list
        The price of the horizontal lines corresponding to quant_list.
    direction : str
        Buy", "Sell", or "Neutral" signal.
    price_chart_title : str, optional
        The title of the plot. The default is "Date".
    open_hr : str, optional
        The opening hour of a trade day. The default is 0330 (03:30 at UK time).
    close_hr : str, optional
        The closing hour of a trade day. The default is 1900 (07:00 pm).
    events_lower_limit : TYPE, optional
        The lower bound in y-axis of the plot. The default is 70.
    events_upper_limit : TYPE, optional
        The upper bound in y-axis of the plot. The default is 78.

    Returns
    -------
    fig : <class 'matplotlib.figure.Figure'>
        The figure.

    """
    x_datetime = [datetime.datetime.combine(datetime.date.today(), t) for t in x]

    # Set the x-axis value based on datetime.time
    start_line = datetime.time(hour = 0, minute = 0)  
    end_line =  datetime.time(hour = 23, minute = 59)  
    open_hr = datetime.time(hour = int(open_hr[-4:-2]), minute = int(open_hr[-2:]))    
    close_hr = datetime.time(hour = int(close_hr[-4:-2]), minute = int(close_hr[-2:]))
    buy_time = datetime.time(hour = int(buy_time[-4:-2]), minute = int(buy_time[-2:]))    
    sell_time = datetime.time(hour = int(sell_time[-4:-2]), minute = int(sell_time[-2:]))
    EES_txt_start_time = datetime.time(hour = 20, minute = 50)
    
    start_line = datetime.datetime.combine(datetime.date.today(), start_line)
    end_line = datetime.datetime.combine(datetime.date.today(), end_line)
    open_hr = datetime.datetime.combine(datetime.date.today(), open_hr)
    close_hr = datetime.datetime.combine(datetime.date.today(), close_hr)
    buy_time = datetime.datetime.combine(datetime.date.today(), buy_time)  
    sell_time = datetime.datetime.combine(datetime.date.today(), sell_time)
    EES_txt_start_time = datetime.datetime.combine(datetime.date.today(), 
                                                   EES_txt_start_time)

    print(start_line, end_line, open_hr, close_hr, buy_time, sell_time)
    
    bppt_x1 = [datetime.datetime.combine(datetime.date.today(), t) for t in bppt_x1]
    bppt_x2 = [datetime.datetime.combine(datetime.date.today(), t) for t in bppt_x2]
    bppt_x3 = [datetime.datetime.combine(datetime.date.today(), t) for t in bppt_x3]

    # plotting area
    fig = plt.figure(figsize=(10,4))
    gs = fig.add_gridspec(nrows=1, ncols = 2, width_ratios = [4,1])

    ax1 = fig.add_subplot(gs[0])
    ax1.plot(x_datetime, y,'o--', ms=2, c='k')
    
    # crossover points set 1 
    ax1.plot(bppt_x1, bppt_y1,'o', ms=10, c='blue')
    ax1.plot(bppt_x2, bppt_y2,'o', ms=10, c='green')
    ax1.plot(bppt_x3, bppt_y3,'o', ms=10, c='red')
    
    # fill the closed trading hours with shade
    ax1.fill_between([start_line, open_hr], 0, 2000, color='grey', alpha=0.3)
    ax1.fill_between([close_hr, end_line], 0, 2000, color='grey', alpha=0.3)
    
    # the vertical lines that
    ax1.vlines(open_hr, 0, 2000, 'k')
    ax1.vlines(close_hr, 0, 2000, 'k')
    
    # set plot limits
    ax1.set_xlim([start_line, end_line])
    ax1.set_ylim([events_lower_limit, events_upper_limit])
    
    ax1.set_xlabel("Time (minutes)")
    ax1.set_ylabel("Price (USD)")
    ax1.set_title(price_chart_title)
    
    fmt = mdates.DateFormatter('%H:%M')
    ax1.xaxis.set_major_formatter(fmt)
    ax1.grid()
    

    # define the pixels of shift for the texts in both x and y axis
    txt_shift_x, txt_shift_y = np.std(pdf)/2, np.std(events)/20
    #define the shift in dates
    txt_shift_x_date = datetime.timedelta(hours = round(np.std(pdf)/2))

        
    # add quantile lines for both plots
    add_quant_lines(ax1, quant_list, quant_price_list, txt_shift_x_date, txt_shift_y, 
                        start_x = start_line, end_x = end_line, alpha = 0.5)

    
    if direction == "Buy":
        entry_price = quant_price_list[1]
        exit_price = quant_price_list[3]
        stop_loss = quant_price_list[0]
    elif direction == "Sell":
        entry_price = quant_price_list[3]
        exit_price = quant_price_list[1]
        stop_loss = quant_price_list[4]
    elif direction == "Neutral":
        entry_price = np.nan
        exit_price = np.nan
        stop_loss = np.nan
        
    # add the EES regions
    add_EES_region(ax1, entry_price, exit_price ,stop_loss, 
                   txt_shift_x_date, txt_shift_y, start_x = EES_txt_start_time,
                   end_x = end_line, direction = direction)
    
    # add the buying and selling points
    add_buysell_points(ax1, buy_time, buy_price, sell_time, sell_price)
    
    # add APC subplot
    add_pdf_panel(fig,  gs[1],  ax1, pdf, events, 
                  quant_list, quant_price_list, 
                  txt_shift_x, txt_shift_y)
    
    plt.show()
    
    return fig

def add_pdf_panel(fig, gs, sharey, pdf, events, quant_list, quant_price_list, 
                  txt_shift_x, txt_shift_y):

    ax_apc = fig.add_subplot(gs, sharey=sharey)
    ax_apc.plot(pdf, events, 'o', c='orange', ms =2)
    
    add_quant_lines(ax_apc, quant_list, quant_price_list, txt_shift_x, txt_shift_y, 
                        alpha = 0.5)

    ax_apc.set_xlim([-0.005, max(pdf)+ np.std(pdf)/4])
    ax_apc.set_title('APC')
    ax_apc.set_xlabel("Probability")
    ax_apc.invert_xaxis()
    ax_apc.grid()
    
# Strategy on off button and it changes all plots moving forwards

def add_quant_lines(ax, quant_list, quant_price_list, txt_shift_x, txt_shift_y, 
                    start_x = 0.0, end_x= 100, alpha = 0.5):
    """
    A function that add the quantile lines to a plot.

    Parameters
    ----------
    ax : <class 'matplotlib.axes._axes.Axes'>
        The figure.
    quant_list : list
        A list of quantile name for text marking on the plot.
    quant_price_list : list
        The price of the horizontal lines corresponding to quant_list.
    txt_shift_x : float
        The shift in x-axis for the text.
    txt_shift_y : float
        The shift in y-axis for the text.
    start_x: float, or datetime.time
        The starting position for the text in x-axis
    end_x: float, or datetime.time
        The ending position for the text in x-axis
    alpha : float, optional
        The transparency of the quantile line. The default is 0.5.

    """
    for quant, price in zip(quant_list, quant_price_list):
        ax.hlines(price, start_x, end_x, color='#C26F05', alpha = alpha)
        ax.text( start_x + txt_shift_x, price + txt_shift_y, quant, 
                 fontsize=8, color='#C26F05')
        
def add_EES_region(ax,entry_price, exit_price, stop_loss, 
                   txt_shift_x, txt_shift_y, start_x = 0.0, end_x = 2150,
                   direction="Neutral"):
    """
    A function that add the Entry, Exit, and Stop Loss regions to a plot.


    Parameters
    ----------
    ax : <class 'matplotlib.axes._axes.Axes'>
        The figure.
    entry_price : float
        entry_price.
    exit_price : float
        exit_price.
    stop_loss : float
        stop_loss.
    txt_shift_x : float
        The shift in x-axis for the text.
    txt_shift_y : float
        The shift in y-axis for the text.
    direction : str, optional
        "Buy", "Sell", or "Neutral" signal. The default is "Neutral".

    """

    start_line = datetime.time(hour = 0, minute = 0)  
    end_line =  datetime.time(hour = 23, minute = 59) 
    
    start_line = datetime.datetime.combine(datetime.date.today(), start_line)
    end_line = datetime.datetime.combine(datetime.date.today(), end_line)
    
    # dashed line is the entry line, solid line is the exit line
    # dashed red line is the stop loss
    
    if direction == "Buy":
        limit = -10000
    elif direction == "Sell":
        limit = 10000
    elif direction == "Neutral":
        limit = np.nan
    
    # The EES lines
    ax.hlines(entry_price, start_line, end_x, color='#18833D', ls="dashed", lw = 2)
    ax.hlines(exit_price, start_line, end_x, color='#18833D', ls="solid", lw = 2 )
    ax.hlines(stop_loss, start_line, end_x, color='#E5543D', ls = "dashed", lw = 2)
    
    # Green shade is the target region.
    ax.fill_between([start_line,end_line], entry_price, exit_price, color='green', 
                    alpha=0.3)
    # Red shade is the stop loss region. 
    ax.fill_between([start_line,end_line], stop_loss, limit, color='red', alpha=0.3)
    
    # The texts that indicate the regions
    ax.text(start_x + txt_shift_x, entry_price + txt_shift_y, "Entry Price", 
                  fontsize=8, color='#206829')
    ax.text(start_x + txt_shift_x, exit_price + txt_shift_y, "Exit Price", 
                  fontsize=8, color='#206829')
    ax.text(start_x + txt_shift_x, stop_loss + txt_shift_y, "Stop Loss", 
                  fontsize=8, color='#80271B')
    
def add_buysell_points(ax, entry_time, entry_price,exit_time, exit_price):
    
    # draw a line between entry and exit
    line_x, line_y = [entry_time,exit_time], [entry_price, exit_price]
    ax.plot(line_x, line_y, '--', color='blue')
    
    ax.plot(entry_time, entry_price, 'o', ms = 12, color='#206829', 
            markeredgecolor='k', alpha = 0.6)
    ax.plot(exit_time, exit_price, 'o', ms = 12, color='#206829', 
            markeredgecolor='k', alpha = 0.6)

    
def plot_candlestick_chart(prices,ax) -> None:

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
    

        
def plot_minute(filename_minute, signal_filename, price_approx = 'Open',
                date_interest = "2022-05-19", direction = "Buy",
                bppt_x1 =[], bppt_y1 = [], 
                bppt_x2 =[], bppt_y2 = [], 
                bppt_x3 =[], bppt_y3 = []):
    
    # read the reformatted minute history data
    history_data = EC_read.read_reformat_Portara_minute_data(filename_minute)
    
    #reformat the date of interest
    date_interest_year = int(date_interest[:4])
    date_interest_month = int(date_interest[5:7])
    date_interest_day = int(date_interest[-2:])
    
    #temporary solution here because to read the APC file I need to use string
    date_interest_dt = datetime.datetime(year = date_interest_year, 
                                      month = date_interest_month , 
                                      day = date_interest_day)
    
    # Get the history data on the date of interest
    interest = history_data[history_data['Date']  == date_interest_dt]
    
    # Change the time format from 0015 to 00:15 in string format
    #interest = util.convert_intmin_to_time(interest)
    
    x, y = interest['Time'], interest[price_approx]

    #read the APC file on the relevant date
    curve = EC_read.read_apc_data(signal_filename)
    curve = curve[curve['Forecast Period'] == date_interest]
    
    # Calculate the pdf from the cdf for plotting
    quant0 = np.arange(0.0025, 0.9975, 0.0025)
    even_spaced_prices, pdf = mfunc.cal_pdf(quant0, curve.to_numpy()[0][1:-1])
    
    #print("find_quant", mfunc.find_quant(curve.to_numpy()[0][1:-1], quant0, 97.9366))
    
    # Define the quantile list of interest based on a strategy
    # The lists are for marking the lines only. 
    quant_list=['q0.1','q0.4','q0.5','q0.6','q0.9']
    quant_price_list = [curve['0.1'], curve['0.4'], curve['0.5'], curve['0.6'], curve['0.9']]

    # Define the upper and lower bound of the pricing plot in the y-axis
    price_lower_limit = curve['0.05'].to_numpy()
    price_upper_limit = curve['0.95'].to_numpy()
    

    # Plot the pricing chart.
    plot_price_BIG(x,y, 
                   even_spaced_prices, pdf, 
                   quant_list, quant_price_list, 
                   direction,
                   price_chart_title =date_interest,
                   events_lower_limit= price_lower_limit,
                   events_upper_limit = price_upper_limit,
                   bppt_x1 = bppt_x1, bppt_y1 = bppt_y1, 
                   bppt_x2 =bppt_x2, bppt_y2 = bppt_y2, 
                   bppt_x3 =bppt_x3, bppt_y3 = bppt_y3)
    
    

    
if __name__ == "__main__":
    
    filename_daily = "../test_MS/data_zeroadjust_intradayportara_attempt1/Daily/CL.day"
    #################
    
    filename_minute = "../test_MS/data_zeroadjust_intradayportara_attempt1/intraday/1 Minute/CL.001"
    signal_filename = "APC_latest_CL.csv"
    #date_interest = "2022-05-19"
    #date_interest = "2024-04-03"
    date_interest = "2024-01-18"
    
    plot_minute(filename_minute, signal_filename, 
                date_interest = date_interest, direction="Sell")


