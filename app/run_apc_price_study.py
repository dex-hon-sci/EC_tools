#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug  7 19:30:06 2024

@author: dexter
"""
import datetime as datetime

from crudeoil_future_const import APC_FILE_LOC, DATA_FILEPATH, SYMBOL_LIST, \
                                  MONTHLY_APC_PKL, SYMBOL_LIST_SHORT
import EC_tools.utility as util
from run_PNL_plot import twopanel_plot


#APC_PKL_FILENAME = DATA_FILEPATH + '/pkl_vault/crudeoil_future_APC_full.pkl' 
APC_PKL_FILENAME = MONTHLY_APC_PKL
APC_quantile_label_list = ['0.1','0.4','0.5','0.6','0.9']

apc_pkl = util.load_pkl(APC_PKL_FILENAME)

HISTORY_DAY_PKL_FILENAME = DATA_FILEPATH + '/pkl_vault/crudeoil_future_daily_full.pkl' 
history_pkl = util.load_pkl(HISTORY_DAY_PKL_FILENAME)

def pre_select_apc(apc_pkl):
    """
    A function that preselect a subset of the APC file.
    It returns a reduced version of the apc. The methid is mainly for selecting
    for the monthly APC with a given

    """
    temp = dict()
    for key in apc_pkl:
        df = apc_pkl[key] 
        df = df[df['CONTINUOUS_FORWARD'] == 1]
        temp[key] = df
    
    apc_pkl = temp
        
    return apc_pkl

apc_pkl = pre_select_apc(apc_pkl)
print(apc_pkl)

#####

def make_apc_asset_dict(symbol, APC_quantile_label_list):
    """
    Make a dictionary of a single asset that contain the quantile price 
    information.
    """
    master_dict = dict()
    for num in APC_quantile_label_list:
        quantile_list = [apc_pkl[symbol].iloc[i][num] 
                         for i in range(len(apc_pkl[symbol]))]
        master_dict[num] = quantile_list
        
    return master_dict


def make_apc_dict(symbol_list):
    """
    A function that make a dictionary of assets, each in itself is a dicrtionary 
    containing the quantile price information
    """
    master_dict = dict()
    for symbol in symbol_list:
       asset_dict = make_apc_asset_dict(symbol, APC_quantile_label_list)
       master_dict[symbol] = asset_dict
    return master_dict

import numpy as np

def find_delta(apc_interest, history_interest, symbol):
    """
    Find the price difference in between two different list.

    Parameters
    ----------
    apc_interest : TYPE
        DESCRIPTION.
    history_interest : TYPE
        DESCRIPTION.
    symbol : TYPE
        DESCRIPTION.

    Returns
    -------
    delta_list : TYPE
        DESCRIPTION.

    """
    # Daily settlement price list
    history_interest_close_list = history_interest['Settle'].to_list()

    apc_date = [apc_interest['PERIOD'].iloc[i]
                    for i in range(len(apc_interest))]
        
    delta_list = list()
    for i in range(len(history_interest_close_list)):
        delta = (history_interest_close_list[i] - 
                         apc_interest.iloc[i]['0.5']) / apc_interest.iloc[i]['0.5']
        delta_list.append(delta)

        if history_interest['Date'].to_list()[i] != apc_date[i]:
            print('mismatch date', history_interest['Date'].to_list()[i], apc_date[i])
            pass
        
    N = len(delta_list)
    rms = np.sqrt((1/N)*sum(np.array(delta_list)**2))
    print(symbol, 'Root mean square error:', rms)
    return delta_list




#apc_dict = make_apc_dict(SYMBOL_LIST)
apc_dict = make_apc_dict(SYMBOL_LIST_SHORT)


def plot_all_apc_price(symbol_list, col_list, start_date, end_date):


    for i, symbol in enumerate(symbol_list):
        # make the date list for this asset
        apc_interest = apc_pkl[symbol][(apc_pkl[symbol]['PERIOD'] >= start_date) & 
                                       (apc_pkl[symbol]['PERIOD'] <= end_date)]
        
        
        apc_date = [apc_interest['PERIOD'].iloc[i]
                    for i in range(len(apc_interest))]
        
        
        
        # Truncate the historical data to a period of interest
        history_interest = history_pkl[symbol][(history_pkl[symbol]['Date'] >= start_date) &
                                               (history_pkl[symbol]['Date'] <= end_date)]
        

        # Make a list of apc quant data
        apc_quant_list = [apc_interest[num] for num in APC_quantile_label_list]
        

        
        #delta_list = find_delta(apc_interest, history_interest, symbol)
        delta_list = [0 for i in range(len(history_interest['Date'].to_list()))]

        
        # plot the cumulative plot 
        twopanel_plot(history_interest['Date'].to_list(), 
                    history_interest['Settle'].to_list(),
                    delta_list, 
                    upper_plot_ylabel = 'Price (USD)', 
                    lower_plot_ylabel = r'$\rm \Delta (price - q0.5) / q0.5$',
                    xlabel = 'Date', plot_title = "{}~Price".format(symbol),
                    line_color = col_list[i], label=symbol,
                    sub_x_list= [apc_date, apc_date, apc_date, apc_date, apc_date],
                    sub_y1_list= apc_quant_list,
                    sub_label_list = APC_quantile_label_list,
                    sub_col_list = ['w', 'w', 'w', 'w', 'w'], 
                    sub_line_list = ['dashed', 'solid', 'dotted', 'solid', 'dashed'])
        
def plot_all_apc_price_OHLC(symbol_list, col_list, start_date, end_date):


    for i, symbol in enumerate(symbol_list):
        # make the date list for this asset
        apc_interest = apc_pkl[symbol][(apc_pkl[symbol]['PERIOD'] >= start_date) & 
                                       (apc_pkl[symbol]['PERIOD'] <= end_date)]
        
        
        apc_date = [apc_interest['PERIOD'].iloc[i]
                    for i in range(len(apc_interest))]
        
        
        
        # Truncate the historical data to a period of interest
        history_interest = history_pkl[symbol][(history_pkl[symbol]['Date'] >= start_date) &
                                               (history_pkl[symbol]['Date'] <= end_date)]
        

        # Make a list of apc quant data
        apc_quant_list = [apc_interest[num] for num in APC_quantile_label_list]
        
        open_list = history_interest['Open'].to_list()
        high_list = history_interest['High'].to_list()
        low_list = history_interest['Low'].to_list()
        close_list = history_interest['Settle'].to_list()
        
        # plot the cumulative plot 
        twopanel_plot(history_interest['Date'].to_list(), 
                    history_interest['Settle'].to_list(),
                    history_interest['Volume'].to_list(),
                    upper_plot_ylabel = 'Price (USD)', 
                    lower_plot_ylabel = r'$\rm Volume$',
                    xlabel = 'Date', plot_title = "{}~Price".format(symbol),
                    line_color = 'k', label=symbol,
                    sub_x_list= [apc_date, apc_date, apc_date, apc_date, apc_date] +\
                                [apc_date, apc_date, apc_date, apc_date],
                    sub_y1_list= apc_quant_list + \
                                    [open_list, high_list, low_list, close_list],
                    sub_label_list = APC_quantile_label_list+['Open','High','Low','Close'],
                    sub_col_list = ['w', 'w', 'w', 'w', 'w'] + [col_list[i]]*4, 
                    sub_line_list = ['dashed', 'solid', 'dotted', 'solid', 'dashed'] +\
                                    ['solid', 'dotted', 'dotted', 'solid'],
                    alpha = 0.2)

        
if __name__=='__main__':
    #COL_LIST = ['#62A0E1', '#62A0E1', '#EB634E', '#EB634E', 
    #            '#E99938', '#E99938','#5CDE93', '#5CDE93', 
    #            '#6ABBC6', '#6ABBC6']
    COL_LIST = ['#62A0E1', '#EB634E',  
                '#E99938','#5CDE93', 
                '#6ABBC6']
    
    start_date = datetime.datetime.strptime("2021-01-11", '%Y-%m-%d')
    end_date = datetime.datetime.strptime('2024-06-17', '%Y-%m-%d')

        
    #plot_all_apc_price(SYMBOL_LIST, COL_LIST, start_date, end_date)    
    plot_all_apc_price(SYMBOL_LIST_SHORT, COL_LIST, start_date, end_date)    

    #plot_all_apc_price_OHLC(SYMBOL_LIST, COL_LIST, start_date, end_date)