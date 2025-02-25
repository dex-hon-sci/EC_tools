#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan 26 00:42:13 2025

@author: dexter
"""
from itertools import islice
import datetime
import numpy as np
import pandas as pd
import openpyxl

import EC_tools.utility as util

#xl_filename = "/home/dexter/Euler_Capital_codes/EC_tools/results/heatmap/PNL_argusexact_G25S10_.xlsx"
#xl_filename = "/home/dexter/Euler_Capital_codes/EC_tools/results/EC_benchmark/20250210_argusexact_cross_P25S10_PNL_full_.xlsx"#EC_benchmark_prime.xlsx"
#xl_filename = "/home/dexter/Euler_Capital_codes/EC_tools/results/EC_benchmark/20250210_argusexact_cross_P25S10_PNL_.xlsx"#EC_benchmark_prime.xlsx"
#xl_filename = "/home/dexter/Euler_Capital_codes/EC_tools/results/EC_benchmark/20250210_argusexact_cross_P10S35_PNL_full_righttime_.xlsx"
#xl_filename = '/home/dexter/Euler_Capital_codes/EC_tools/results/consistency/live_trade_vs_backtest_newcode/live_trade_compare_pnl_.xlsx'
xl_filename = '/home/dexter/Euler_Capital_codes/EC_tools/results/heatmap2/20240813_argusexact_cross_P35S15_PNL_.xlsx'

wb_obj = openpyxl.load_workbook(xl_filename, keep_vba=True)

#symbol_list = wb_obj.sheetnames
symbol_list = ['Total']


def read_xl_file(xl_filename, sheet_name='Sheet1'):
    wb_obj = openpyxl.load_workbook(xl_filename, keep_vba=True)
    #sheet_obj = wb_obj.active
    ws = wb_obj[sheet_name]

    data = ws.values
    cols = next(data)[1:]
    data = list(data)
    idx = [r[0] for r in data]
    data = (islice(r, 1, None) for r in data)
    df = pd.DataFrame(data, columns=cols, index=idx)
    

    return df

def win_rate(df, col='scaled returns from trades'):
    win_trades = sum(
        1 for i in df[col].to_list() if i >= 0)
    lose_trades = sum(
        1 for i in df[col].to_list() if i < 0)

    return (win_trades/(win_trades+lose_trades))*100, '%', "Win Rate"
     
def profit_factor(df,col='scaled returns from trades'):
    win_trades_val = sum(i for i in df[col].to_list()
                         if i >= 0)
    lose_trades_val = sum(i for i in df[col].to_list()
                          if i < 0)
    print(win_trades_val, lose_trades_val)
    return abs(win_trades_val)/abs(lose_trades_val), '', 'Profit Factor'

def draw_down(df, date_col ='Entry_Date', 
              return_col='cumulative P&L from trades'):
    
    date_bucket, draw_down_bucket = [], []
    
    current_max = df[return_col].to_list()[0]
    for date, cum_return in zip(df[date_col].to_list(), 
                                df[return_col].to_list()):
        if cum_return > current_max:
            current_max = cum_return
            
        draw_down= 100*(cum_return - current_max)/current_max
        
        date_bucket.append(date)
        draw_down_bucket.append(draw_down)
    return date_bucket, draw_down_bucket

def group_by_date(df, date_col='Entry_Date',
                  return_col='scaled returns from trades'):

    temp_date = df[date_col].to_list()[0]
    temp_return = 0
    
    date_bucket, return_bucket = [], []

    for date, day_return in zip(df[date_col].to_list(), 
                                df[return_col].to_list()):
        if date != temp_date:
            temp_date = datetime.datetime.strptime(temp_date, '%Y-%m-%d')
            #print(temp_date,temp_return)
            date_bucket.append(temp_date)
            return_bucket.append(temp_return)
            #print(temp_date,temp_return)
            temp_date = date
            temp_return = day_return
        else:
            temp_return += day_return
        
    # add the last entries
    date_bucket.append(temp_date)
    return_bucket.append(temp_return)

    #print(date_bucket, return_bucket)
    return date_bucket, return_bucket

def sharpe_ratio(cum_returns,timescale):
    # risk-free rate
    RFR = 0.02
    
    #annual_return = ((cum_returns[-1]-cum_returns[0])/ cum_returns[0])**(1/3.7)
    #excess_return = np.diff(cum_returns)/ cum_returns[:-1]
    annual_return = ((np.log10(cum_returns[-1])-np.log10(cum_returns[0]))/ np.log10(cum_returns[0]))**(1/3.7)
    excess_return = np.diff(np.log10(cum_returns))/ np.log10(cum_returns[:-1])
    
    #excess_return = annual_return - np.repeat(0.04, len(annual_return))
    annual_std = np.std(excess_return)*np.sqrt(252)
    #252 trading days in a year
    
    print("annual_return", annual_return)
    print('annual_std', annual_std)
    print("excess_return", np.average(excess_return))#,excess_return)
    #return ((np.average(excess_return)-RFR)*252)/annual_std
    return (annual_return-RFR)/annual_std
#xl_filename = "/home/dexter/Euler_Capital_codes/EC_tools/results/beyondmarketopen2/"

for sym in symbol_list:
    
    df = read_xl_file(xl_filename, sheet_name=sym)
    
    date_bucket1, return_bucket = group_by_date(df)
    cum_return_bucket = np.cumsum(return_bucket)
    
    df_new = pd.DataFrame(data={'Date':date_bucket1, 'Return': cum_return_bucket})
    print(sym)
    print("Win_rate", win_rate(df))
    print("Profit Factor", profit_factor(df))
    #print('Total Profit', df['cumulative P&L from trades'].iloc[-1])
    print("Day(#), total return", len(date_bucket1), sum(return_bucket))
    
    a_ratio = sharpe_ratio(cum_return_bucket, 1/3.7)
    print("Sharpe Ratio", a_ratio)
    date_bucket2, drawdown_bucket = draw_down(df_new,date_col='Date', return_col='Return')
    print('==================')
    
        
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    
    plt.style.use('dark_background')
    fig = plt.figure(figsize=(14,6))
    gs = fig.add_gridspec(nrows=2, ncols = 1, height_ratios=[6, 2.5])
    fig.suptitle("")
    
    ax1 = fig.add_subplot(gs[0])
    ax2 = fig.add_subplot(gs[1], sharex=ax1)

    #ax1.bar(date_bucket1, return_bucket, color="g")
    ax1.plot(date_bucket1, cum_return_bucket, color="g")
    
    
    ax1.hlines(0,datetime.datetime(2020,11,22),
               datetime.datetime(2024,9,10), lw = 2.5,color='orange')
    ax2.plot(date_bucket2, drawdown_bucket,'-', c='b')
    
    fmt = mdates.DateFormatter('%y-%m-%d')
    #ax1.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    ax1.xaxis.set_major_formatter(fmt)
    ax2.xaxis.set_major_formatter(fmt)
    
    ax1.grid()
    ax2.grid()
    
    plt.show()
        
