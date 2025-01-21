#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 10 19:38:52 2024

@author: dexter

A quick application script to evaluate if a trading strategy is viable.

"""
# Python import
import sys
import os
import datetime
import random

sys.path.insert(0, '/home/dexter/Euler_Capital_codes/EC_tools/')

# Common Package import
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import pandas_market_calendars as mcal

# EC_tools import
import EC_tools.utility as util
import EC_tools.base.read as read

from crudeoil_future_const import DAILY_DATA_PKL, DAILY_MINUTE_DATA_PKL, \
                                  SIZE_DICT, round_turn_fees

# Setup all the trading dates and hours
MARKET_VD = mcal.get_calendar("NYSE").valid_days(start_date=datetime.datetime(2021,1,1), 
                                                 end_date=datetime.datetime(2024,10,4)).to_list()
TRADING_DATES = [ts.to_pydatetime().replace(tzinfo=None) for ts in MARKET_VD]
TRADING_MINUTES = [(datetime.datetime.combine(datetime.date.today(),
                                              datetime.time(0,0,0))+
                    datetime.timedelta(minutes=1*n)).time() 
                    for n in range(0,1440,1)] #1 minute interval

# Input files
DAY = util.load_pkl(DAILY_DATA_PKL)
MINUTE = util.load_pkl(DAILY_MINUTE_DATA_PKL)

def trade_bytime(df: pd.DataFrame, 
                 t1: datetime.time, 
                 delta_T: datetime.timedelta, 
                 time_proxy: str ='Time', 
                 price_proxy: str ='Open'): # tested

    last_time = TRADING_MINUTES[-1]
    # random trade, find the return between two time
    # t1 find the closest time
    t1 = datetime.datetime.combine(datetime.date.today(),t1)
    t1_str = datetime.datetime.strftime(t1,"%H%M")
    
    # get the time and price after a set time interval
    t2 = t1 + delta_T
    
    if t2.date() != t1.date(): # if it reaches the next day, reset it to the last entry
        #print("Beyond last minute", t2)
        t2 = datetime.datetime.combine(datetime.date.today(),last_time)
        #print("After Correction", t2)

    t2_str = datetime.datetime.strftime(t2,"%H%M")

    t1, price1 = read.find_closest_price_generic(df, t1_str, 
                                                 direction='forward', 
                                                 search_time=1000)
    #print('t1', t1)
    #print('price1', price1.item())
    t2, price2 = read.find_closest_price_generic(df, t2_str, 
                                                 direction='backward', 
                                                 search_time=1000)
   # print('t2', t2)
   # print('price2', price2.item())
    r = price2.item()-price1.item()
    print("rrr", r)
        
    return r

def gen_rand_sublist(n: int, parent_list: list = TRADING_DATES):
    # pick a list of trading days at random 
    # assume flat probability
    dates = random.sample(parent_list, n)
    dates.sort()
    return dates

def gen_duration_list(mu: float, sigma: float, n: int):
    
    # define the distribution
    dist = list(np.random.normal(mu, sigma, 1000))
    
    durations = random.sample(dist,n)
    delta_T_list = [datetime.timedelta(minutes=duration) for duration in durations]
    return delta_T_list

def assign_sign_to_list(input_list: list[float|int], PR: float): #tested
    # input_list postive rate
    
    coin_flip = lambda x: np.random.choice([abs(x), -1*abs(x)], p=[PR,1-PR]) 
    
    bucket = [coin_flip(ele) for ele in input_list]
    
    return bucket



def run_rand_trade_day(minute_data: dict, 
                       N_trades: int=3,     # Number of trades per day
                       N_days: int=20,     # Number of trades days
                       symbol: str ='CLc1'):
    # read in data
    df = minute_data[symbol]
    # randomising 
    # T_intervals
    mu, sigma = 5, 0.5
    #mu, sigma = 10, 2
    # Win Rate
    PR = 0.6
    
    # generate trading dates
    dates = gen_rand_sublist(N_days, parent_list = TRADING_DATES)
    i = 0
    date_bucket, N_trades_bucket, return_bucket = [], [], []
    PR_bucket, delta_T_bucket = [], []
    #print("dates",dates)
    for date in dates: # loop dates
        date_df = df[df["Date"]==date]
        #print(date,date_df)
        TRADING_MINUTES_DAY = date_df['Time'].to_list()
        
        #print("TRADING_MINUTES_DAY", i, TRADING_MINUTES_DAY)
        print("N_trades", N_trades)
        #print(random.sample(TRADING_MINUTES_DAY, N_trades))
        
        # generate the starting time for opening a position for that date
        open_pos_times = gen_rand_sublist(N_trades, parent_list = TRADING_MINUTES_DAY)
        delta_T_list = gen_duration_list(mu, sigma, N_trades)
        
        
        #print("DOD",date, open_pos_times, delta_T_list)
       
        # loop through them to find
        return_list = [trade_bytime(date_df, t,delta_T) for t, delta_T in 
                       zip(open_pos_times, delta_T_list)]
        #print("return_list", return_list)
        return_list = assign_sign_to_list(return_list,PR)
        #print("return_list_after", return_list)
        i = i+1         
        # sum up the return of the day
        
        date_bucket.append(date)
        return_bucket.append(sum(return_list))
        N_trades_bucket.append(N_trades)
        PR_bucket.append(PR)
        delta_T_bucket.append(np.average(delta_T_list))
    # plot
    return date_bucket, N_trades_bucket, return_bucket, PR_bucket, delta_T_bucket

def plot_N_R(x_labels,y_data,ax,**kwargs):

    #ax.plot(x, y,'o', c='w', ms=3,alpha=0.6)
    bplot = ax.boxplot(y_data,
                       medianprops={'color':'red'},
                       patch_artist=True,  # fill with color
                       tick_labels=x_labels)  # will be used to label x-ticks
    
    
    line_x = np.arange(0,50,1)
    line_y = line_x*kwargs['fee']
    line_y2 = line_x*30
    
    ax.fill_between(line_x, line_y, np.repeat(-4000,len(line_x)), color='r', alpha=0.4)
    ax.fill_between(line_x, line_y2, line_y, color='#e37a46', alpha=0.4)
    ax.fill_between(line_x, np.repeat(+4000,len(line_x)), line_y2, color='g', alpha=0.4)
    
    ax.plot(line_x, line_y, c='w',ls='solid', label = 'Round Trip Fee= USD 15')
    ax.plot(line_x, line_y2, c='w',ls='dashed', label = 'Round Trip Fee= USD 30')

    ax.hlines(-4,45,0,ls="dashed",lw=2)
    ax.set_title(kwargs['plot_title'])
    ax.set_xlabel(kwargs['xlabel'])
    ax.set_ylabel(kwargs['ylabel'])
    
    ax.set_ylim(-2000,4000)
    ax.set_xlim(0,32)
    ax.grid(ls='dashed',alpha=0.5)
     
    
def plot_prob(x: list[float], ax, **kwargs):
    
    ax.hist(x, kwargs['bin_size'], histtype='stepfilled', facecolor='g',
               alpha=0.6)
    ax.vlines(np.median(x),0, 10)
    
    ax.set_title(kwargs['plot_title'])
    ax.set_xlabel(kwargs['xlabel'])
    ax.set_ylabel(kwargs['ylabel'])
    
    ax.yaxis.set_label_position("right")
    ax.yaxis.tick_right()


def plot_box(x_labels,y_data, N_trade_list, WR_list, delta_T_list):
    #N_trade_list = np.arange(10,50,1)
    #WR_list = np.arange(10,50,1)
    #delta_T_list = np.arange(10,50,1)
    
    plt.style.use('dark_background')

    fig = plt.figure(figsize=(24,12))
    gs = GridSpec(3,5)
    ax1 = fig.add_subplot(gs[0:3,0:3])
    ax2 = fig.add_subplot(gs[0,3:])
    ax3 = fig.add_subplot(gs[1,3:])
    ax4 = fig.add_subplot(gs[2,3:])
    
    plot_N_R(x_labels,y_data, ax1,
             plot_title = "40 trading days, 60% Win Rate",
             xlabel="Number of Trades Per Day",
             ylabel='Return Per Trades [USD]',
             fee = round_turn_fees['CLc1'])
    
    plot_prob(N_trade_list, ax2,
              bin_size = int(len(N_trade_list)/10),
              plot_title = "",
              xlabel = "Number of Trade Per Day",
              ylabel= "Count")
    plot_prob(WR_list, ax3,
              bin_size = int(len(WR_list)/10),
              plot_title = "",
              xlabel = "Win Rate",
              ylabel= "Count")
    plot_prob(delta_T_list, ax4,
              bin_size = int(len(delta_T_list)/10),
              plot_title = "",
              xlabel = "Position Duration Delta T [Seconds]",
              ylabel= "Count")
    ax1.legend(loc='upper left')
    fig.tight_layout()

    plt.show()

    


if __name__ == "__main__":
    
        
    N_trades_list = list(np.arange(1,30,1))

    master_date_bucket, master_N_trades_bucket, master_return_bucket = [],[],[]
    master_PR_bucket, master_delta_T_bucket = [],[]
    for N in N_trades_list:
        print('N',N)
        date_bucket, N_trades_bucket, return_bucket, \
                          PR_bucket, delta_T_bucket = run_rand_trade_day(MINUTE, 
                                                                         N_trades=N, 
                                                                         N_days=40)
        
        master_date_bucket.append(date_bucket)
        master_N_trades_bucket.append(N_trades_bucket)
        master_return_bucket.append(list(np.array(return_bucket)*SIZE_DICT['CLc1']))
        master_PR_bucket.append(PR_bucket)
        
        delta_T_bucket = [ele.seconds for ele in delta_T_bucket]
        
        master_delta_T_bucket.append(delta_T_bucket)
        
        
    print(master_date_bucket, master_N_trades_bucket, master_return_bucket,
          master_PR_bucket, master_delta_T_bucket)

    plt.style.use('dark_background')
    
    fig,ax = plt.subplots()
    
    plot_N_R(N_trades_list, 
             master_return_bucket,
             ax,
             plot_title = "40 trading days, 60% Win Rate",
             xlabel="Number of Trades Per Day",
             ylabel='Return Per Trades [USD]',
             fee = round_turn_fees['CLc1'])
    
    plt.legend(loc='upper left')
    plt.show()
    
    master_N_trades_bucket_flat = [item for row in master_N_trades_bucket for item in row]
    master_PR_bucket_flat = [item for row in master_PR_bucket for item in row]
    master_delta_T_bucket_flat =  [item for row in master_delta_T_bucket for item in row]
    
    #plot box plot on different iteration 
    plot_box(N_trades_list,
             master_return_bucket,
             master_N_trades_bucket_flat, 
             master_PR_bucket_flat,
             master_delta_T_bucket_flat)