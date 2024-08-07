#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug  7 19:30:06 2024

@author: dexter
"""
import datetime as datetime

from crudeoil_future_const import APC_FILE_LOC, DATA_FILEPATH, SYMBOL_LIST
import EC_tools.utility as util
from run_PNL_plot import cumPNL_plot


APC_PKL_FILENAME = DATA_FILEPATH + '/pkl_vault/crudeoil_future_APC_full.pkl' 
APC_quantile_label_list = ['0.1','0.4','0.5','0.6','0.9']

apc_pkl = util.load_pkl(APC_PKL_FILENAME)
apc_date = [apc_pkl['CLc1'].iloc[i]['Forecast Period'] for i in range(len(apc_pkl['CLc1']))]


HISTORY_DAY_PKL_FILENAME = DATA_FILEPATH + '/pkl_vault/crudeoil_future_daily_full.pkl' 
history_pkl = util.load_pkl(HISTORY_DAY_PKL_FILENAME)

print(len(history_pkl['CLc1']['Date'].to_list()), 
      len(history_pkl['CLc1']['Settle'].to_list()),
      len(history_pkl['CLc1']['Volume'].to_list()))
# =============================================================================
# CLc1_01 = [apc_pkl['CLc1'].iloc[i]['0.1'] for i in range(len(apc_pkl['CLc1']))]
# #print(apc_date, CLc1_01)
# 
# 
# CLc1_apc_list = [[apc_pkl['CLc1'].iloc[i][num] for i in range(len(apc_pkl['CLc1']))] for num in APC_quantile_label_list]
#     
#     
# =============================================================================
def make_apc_asset_dict(symbol, APC_quantile_label_list):
    
    master_dict = dict()
    for num in APC_quantile_label_list:
        quantile_list = [apc_pkl[symbol].iloc[i][num] 
                         for i in range(len(apc_pkl['CLc1']))]
        master_dict[num] = quantile_list
        
    return master_dict


def make_apc_dict(symbol_list):
    master_dict = dict()
    for symbol in symbol_list:
       asset_dict = make_apc_asset_dict(symbol, APC_quantile_label_list)
       master_dict[symbol] = asset_dict
    return master_dict

start_date = datetime.datetime.strptime("2021-01-11", '%Y-%m-%d')
end_date = datetime.datetime.strptime('2024-06-17', '%Y-%m-%d')

apc_dict = make_apc_dict(SYMBOL_LIST)


def plot_all_apc_price():
    col_list = ['#62A0E1', '#62A0E1', '#EB634E', '#EB634E', 
                '#E99938', '#E99938','#5CDE93', '#5CDE93', 
                '#6ABBC6', '#6ABBC6']

    for i, symbol in enumerate(SYMBOL_LIST):
        
        history_interest = history_pkl[symbol][(history_pkl[symbol]['Date'] >= start_date) &
                                               (history_pkl[symbol]['Date'] <= end_date)]
        cumPNL_plot(history_interest['Date'].to_list(), 
                    history_interest['Settle'].to_list(),
                    history_interest['Volume'].to_list(),               
                    line_color = col_list[i], label=symbol,
                    sub_date_list= [apc_date, apc_date, apc_date, apc_date, apc_date],
                    sub_data_list= [apc_dict[symbol][num] for num in APC_quantile_label_list],
                    sub_label_list = APC_quantile_label_list,
                    sub_col_list = ['w', 'w', 'w', 'w', 'w'], 
                    sub_line_list = ['dashed', 'solid', 'dotted', 'solid', 'dashed'])
        
        
plot_all_apc_price()