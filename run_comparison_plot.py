#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 17 23:30:24 2024

@author: dexter
"""
import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import MultipleLocator

import datetime as datetime
import EC_tools.utility as util

REF_SIGNAL ="/home/dexter/Euler_Capital_codes/EC_tools/results/20220101_20240628_signals_2.xlsx"
RESULT_SIGNAL = "/home/dexter/Euler_Capital_codes/EC_tools/results/argus_exact_signal_short_2_3cond.csv"

REF_PNL = "/home/dexter/Euler_Capital_codes/EC_tools/results/20220101_20240628_trades_2.xlsx"
RESULT_PNL = "/home/dexter/Euler_Capital_codes/EC_tools/results/argus_exact_PNL_short.csv"

df_ref_signal = pd.read_excel(REF_SIGNAL)
df_result_signal = pd.read_csv(RESULT_SIGNAL)

df_ref_PNL = pd.read_excel(REF_PNL)
df_result_PNL = pd.read_csv(RESULT_PNL)

# =============================================================================
# print(df_ref_PNL['Entry_Datetime'], type(df_ref_PNL['Entry_Datetime'].iloc[0]))
# df_ref_PNL['Entry_Datetime'] = [pd.to_datetime(df_ref_PNL['Entry_Datetime'].iloc[i]) for i in range(len(df_ref_PNL['Entry_Datetime']))]
# print(df_ref_PNL['Entry_Datetime'], type(df_ref_PNL['Entry_Datetime'].iloc[0]))
# print('REF',df_ref_PNL['Entry_Datetime'], type(df_ref_PNL['Entry_Datetime'].iloc[0]))
# 
# print(df_ref_PNL['Entry_Datetime'].iloc[1] - df_ref_PNL['Entry_Datetime'].iloc[0])
# 
print('signal_ref_length:', len(df_ref_signal), 'signal_result_length:', len(df_result_signal))
print('PNL_ref_length:', len(df_ref_PNL), 'PNL_result_length:', len(df_result_PNL))
# 
# =============================================================================
#print(df_ref_PNL, df_result_PNL)

#print(df_ref_PNL['Entry_Datetime'].iloc[1000], df_result_PNL['Entry_Datetime'].iloc[1000])
#signal_ref_length: 6322 signal_result_length: 6228
#PNL_ref_length: 1833 PNL_result_length: 2486

#@util.save_csv("/home/dexter/Euler_Capital_codes/EC_tools/results/entrydate_diff.csv")
def find_difference(result_df, ref_df, compare_func, compare_col = 'Direction',
                    date_match_col = 'Date', sym_match_col = 'Price_Code',
                    compare_result_col = 'Same'):
    
    #result_df has to be shorter than ref_def
    bucket = []
    i = 0
    #print(len(result_df))
    while i < len(result_df):
        #print(i)
        date_interest = result_df[date_match_col].iloc[i]
        symbol = result_df[sym_match_col].iloc[i]
        
        temp_ref = ref_df[(ref_df[date_match_col] == date_interest)&
                                 (ref_df[sym_match_col]==symbol)]
        
        #print(i,date_interest, symbol, "length:",len(temp_ref))

        if len(temp_ref) != 1:
            if result_df[compare_col].iloc[i] == np.nan:
               print(date_interest, symbol, result_df[compare_col].iloc[i], temp_ref)
            result_val, ref_val= result_df[compare_col].iloc[i], None
        else:
            result_val, ref_val = result_df[compare_col].iloc[i], \
                                            temp_ref[compare_col].item()
        #print(pd.isna(result_val) , ref_val == None)
        if not pd.isna(result_val) and not pd.isna(ref_val):
            compare = compare_func(result_val, ref_val)
        else:
            compare = None
        #print(result_val, ref_val)

        data = [date_interest, symbol, result_val, ref_val, compare]

        bucket.append(data)
        i = i +1
        
    df_bucket = pd.DataFrame(bucket,columns=[date_match_col, sym_match_col, 
                                             compare_col+'_result', 
                                             compare_col+'_ref', 
                                             compare_result_col])
    return df_bucket


def date_compare(x,y):
    x, y = pd.to_datetime(x), pd.to_datetime(y)
# =============================================================================
#     if x>=y:
#         delta = x - y
#     elif x < y:
#         delta = y-x
# =============================================================================
    delta = y-x
    return delta.total_seconds()/60

print('Signal')

direction_diff = find_difference(df_result_signal, df_ref_signal, 
                        (lambda x, y: x == y),
                        compare_col="Direction")
print('Total mislagined signals', len(direction_diff[direction_diff['Same']==False]))

print('PNL')
#df_date_difference = A[A[4] == False]

entry_dt_diff = find_difference(df_result_PNL, df_ref_PNL, 
                       date_compare,
                       compare_col="Entry_Datetime", date_match_col = 'Entry_Date')

entry_price_diff = find_difference(df_result_PNL, df_ref_PNL, 
                        (lambda x, y: x / y),
                        compare_col="Entry_Price", date_match_col = 'Entry_Date')

exit_dt_diff = find_difference(df_result_PNL, df_ref_PNL, 
                       date_compare,
                       compare_col="Exit_Datetime", date_match_col = 'Exit_Date')

exit_price_diff = find_difference(df_result_PNL, df_ref_PNL, 
                        (lambda x, y: x / y),
                        compare_col="Exit_Price", date_match_col = 'Exit_Date')


entry_dt_diff.to_csv("/home/dexter/Euler_Capital_codes/EC_tools/results/entry_dt_diff.csv", index=False)
entry_price_diff.to_csv("/home/dexter/Euler_Capital_codes/EC_tools/results/entry_price_diff.csv", index=False)
exit_dt_diff.to_csv("/home/dexter/Euler_Capital_codes/EC_tools/results/exit_dt_diff.csv", index=False)
exit_price_diff.to_csv("/home/dexter/Euler_Capital_codes/EC_tools/results/exit_price_diff.csv", index=False)

# 4 plots
#1) Entry time comparison
#2) Entry price comparison
#1) Exit time comparison
#2) Exit price comparison
symbol_list = ['CLc1', 'CLc2', 'HOc1', 'HOc2', 'RBc1', 'RBc2', 
               'QOc1', 'QOc2', 'QPc1', 'QPc2']
col_list = ['#62A0E1', '#62A0E1','#EB634E', '#EB634E','#E99938', '#E99938',
            '#5CDE93','#5CDE93','#6ABBC6','#6ABBC6']
marker_list = ['o', '*', 'o', '*','o', '*','o', '*','o', '*']

def plot_difference(dt_diff, match_date_col = 'Entry_Date',
                         price_chart_title = 'Entry_datetime difference',
                         ylabel="$Result - Ref $",
                         y_bound = (-60,60), ylim = [-600,600]):
    plt.style.use('dark_background')
    
    spacing = 105 # This can be your user specified spacing. 
    minorLocator = MultipleLocator(spacing)

    #fig = plt.figure(figsize=(10,4))
    fig, ax = plt.subplots(figsize=(10,8))
    
    for sym, col, marker in zip(symbol_list, col_list, marker_list):
        temp = dt_diff[dt_diff['Price_Code'] == sym]
        
        x_dt, y = np.asarray(temp[match_date_col], dtype='datetime64[s]'), \
                    temp['Same'].to_numpy()
        
        ax.scatter(x_dt, y, marker = marker, c = col, label = sym)

    #print(min(x_dt), max(x_dt), type(x_dt[0]))
    ax.set_xlabel(match_date_col)
    ax.set_ylabel(ylabel)
    ax.set_title(price_chart_title)
    
        
    x_format = '%y-%m-%d'
    fmt = mdates.DateFormatter(x_format)
    ax.xaxis.set_major_formatter(fmt)
    
    ax.yaxis.set_minor_locator(minorLocator)
    ax.xaxis.set_minor_locator(minorLocator)
    ax.tick_params(axis='x', labelrotation=90)

    ax.grid()
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
   # upper_timedelta_limit= pd.Timedelta(days = 1)
   # lower_timedelta_limit= pd.Timedelta(days = -1)
    
    ax.hlines(y_bound[0],np.datetime64('2022-01-01T00:00:00'),
              np.datetime64('2024-06-20T00:00:00'), 
              color = 'red', lw=2, ls='dashed')
    ax.hlines(y_bound[1],np.datetime64('2022-01-01T00:00:00'),
              np.datetime64('2024-06-20T00:00:00'), 
              color = 'red', lw=2, ls='dashed')
    ax.set_xlim([np.datetime64('2022-01-01T00:00:00'),
                 np.datetime64('2024-06-20T00:00:00')])
    ax.set_ylim(ylim)

    #ax.yaxis.set_major_formatter(fmt_y)
    plt.show()

    return 

def plot_all(entry_dt_diff, exit_dt_diff,entry_price_diff,exit_price_diff):
    plot_difference(entry_dt_diff, match_date_col = 'Entry_Date', 
                         ylabel ="Result - Ref (Minutes)",
                         price_chart_title = 'Entry_datetime difference')
    plot_difference(entry_price_diff, match_date_col = 'Entry_Date', 
                         ylabel = 'Result/Ref',
                         y_bound = (-1,1), ylim = [0.95,1.05],
                         price_chart_title = 'Entry_Price difference')
    
    plot_difference(exit_dt_diff, match_date_col = 'Exit_Date', 
                         ylabel ="Result - Ref (Minutes)",
                         price_chart_title = 'Exit_datetime difference')
    plot_difference(exit_price_diff, match_date_col = 'Exit_Date', 
                         ylabel = 'Result/Ref',
                         y_bound = (-1,1), ylim = [0.95,1.05],
                         price_chart_title = 'Exit_Price difference')
    
if __name__ == "__main__":
    
    B  = entry_dt_diff[(entry_dt_diff['Same']<70) & (entry_dt_diff['Same']>-70)], 
    B1 =  entry_dt_diff[entry_dt_diff['Same']>70 & (entry_dt_diff['Same']<-70)] 
    
    C = exit_dt_diff[(entry_dt_diff['Same']<70)&(entry_dt_diff['Same']>-70)]
    C1 = exit_dt_diff[(entry_dt_diff['Same']>70)&(entry_dt_diff['Same']<-70)]
    
    D = entry_price_diff[(entry_price_diff['Same']<1.4) & (entry_price_diff['Same']>-1.4)]
    D1 =  entry_dt_diff[(entry_dt_diff['Same']>1.4)&(entry_price_diff['Same']<-1.4)] 
    
    print(len(B), len(B1), len(C), len(C1))
    #plot_difference_time(B)

    plot_all(entry_dt_diff, exit_dt_diff,entry_price_diff,exit_price_diff)