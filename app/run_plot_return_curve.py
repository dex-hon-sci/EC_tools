#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec  2 16:50:12 2024

@author: dexter
"""

import datetime as datetime

# import basic python packages
import pandas as pd
import numpy as np
from scipy import stats
from pathlib import Path

# common package import
import matplotlib.dates as mdates
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt

# import EC_tools
import EC_tools.utility as util

from crudeoil_future_const import APC_FILE_LOC, DATA_FILEPATH, DAILY_DATA_PKL, \
                                  make_path_list

# application import
from app.run_PNL_plot import extract_PNLplot_input


 
def make_daily_price_change_data(date_list, symbol='CLc1'):
    # A function that extract
    D = util.load_pkl(DAILY_DATA_PKL)[symbol]

    bucket = []
    for date in date_list:
        temp = D[D['Date']==date]
        diff = 100*abs(temp['Settle'].item() - temp['Open'].item())/temp['Open'].item()
        bucket.append(diff)
    return bucket


def plot_price_return_hist(x,y,**kwargs):
    default_kwargs = {'plot_title': '', 'ylabel': '', 'xlabel': '', 
                      'hist_size': 30, 'hist_ylim': [0,16], 
                      'scatter_ylim':[0,180]}
    kwargs = dict(default_kwargs,**kwargs)
    
    # make negative and postice lists
    positive = [ele for ele in x if ele > 0]
    negative = [ele for ele in x if ele < 0]
    
    diag_line = np.linspace(-4500,4500,10)
    plt.style.use('dark_background')

    # Create Price vs Return plot 
    fig, ax2 = plt.subplots()
    ax1 = ax2.twinx()

    ax1.vlines(0, 0, 16, lw=1)
    ax1.hlines(0,min(x)-2*np.std(x),max(x)+2*np.std(x), lw=1)
    
    ax1.set_title(kwargs['plot_title'])
    ax1.set_ylabel(kwargs['ylabel'])
    ax1.set_ylim(*kwargs['hist_ylim'])
    ax1.set_xlim(min(x)-2*np.std(x),max(x)+2*np.std(x))
    
    ax1.grid(True, ls='dashed',alpha=0.5,axis='both')

    # plot scatter plots
    ax1.scatter(x, y, c='w',s=1, alpha=0.3,zorder=9)

    # plot histogram for both positives and negatives
    ax2.hist(positive, kwargs['hist_size'], histtype='stepfilled', 
             facecolor='g', alpha=0.6)
    QQ = ax2.hist(negative, kwargs['hist_size'], histtype='stepfilled', 
                  facecolor='r', alpha=0.6)
    
    #print(QQ)

    ax2.set_xlabel(kwargs['xlabel'])

    ax2.tick_params(axis='y', labelcolor='#6dd8f2')
    ax2.set_ylabel("Count",color='#6dd8f2')
    
    ax2.set_ylim(*kwargs['scatter_ylim'])
    fig.tight_layout()

    plt.show()
    return

def run_main():
    #argusexact_cross_PS_PNL = "/home/dexter/Euler_Capital_codes/EC_tools/results/heatmap/PNL_argusexact_G40S10_.xlsx"
    argusexact_cross_PS_PNL = '/home/dexter/Euler_Capital_codes/EC_tools/results/heatmap2/20240813_argusexact_cross_P35S15_PNL_.xlsx'


    big_price_diff, big_trade_return = [], []

    symbols = ['CLc1', 'CLc2', 'HOc1', 'HOc2','RBc1','RBc2','QOc1','QOc2','QPc1','QPc2']
    for symbol in symbols:
        date_all, trade_return = extract_PNLplot_input(argusexact_cross_PS_PNL,
                                                       sheet_name=symbol,
                                                             #val_col = "Trade_Return")
                                                       val_col = 'scaled returns from trades')
        price_diff = make_daily_price_change_data(date_all,symbol=symbol)
        
        #D = util.load_pkl(DAILY_DATA_PKL)[symbol]
        #all_diff = abs(D['Settle']-D['Open'])/D['Open']
        
        print(symbol, len(trade_return),type(list(trade_return)))
        
        big_price_diff = big_price_diff + price_diff
        big_trade_return = big_trade_return + list(trade_return)
        #print(date_all_new, cumPNL_all_new)
        
        #print('positive', sum(positive), len(positive))
        #print('negative', sum(negative), len(negative))

    print(len(big_price_diff), len(big_trade_return))
    plot_price_return_hist(big_trade_return, big_price_diff, 
                           plot_title="Benchmark MR Returns (TP 40%, SL 10%)", 
                           ylabel = "Daily Price Changes [%]",
                           xlabel = "Scaled Returns per Trade [USD]")


    #argusexact_cross_PS_PNL = "/home/dexter/Euler_Capital_codes/EC_tools/results/heatmap/PNL_argusexact_G20S35_.xlsx"
    D = util.load_pkl(DAILY_DATA_PKL)['CLc1']
    all_diff = 100*abs(D['Settle']-D['Open'])/D['Open']
    
    plot_price_return_hist(D['Open'].to_list(), all_diff,
                           plot_title="", 
                           ylabel = "Price changes ",
                           xlabel = "Open Price [USD]",
                           hist_ylim = [0,16],
                           scatter_ylim = [0,50],
                           hist_size=100)

    
    
if __name__ == "__main__":
    run_main()