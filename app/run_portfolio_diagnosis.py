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
from crudeoil_future_const import RESULT_FILEPATH
#xl_filename = "/home/dexter/Euler_Capital_codes/EC_tools/results/heatmap/PNL_argusexact_G25S10_.xlsx"
#xl_filename = "/home/dexter/Euler_Capital_codes/EC_tools/results/EC_benchmark/20250210_argusexact_cross_P25S10_PNL_full_.xlsx"#EC_benchmark_prime.xlsx"
#xl_filename = "/home/dexter/Euler_Capital_codes/EC_tools/results/EC_benchmark/20250210_argusexact_cross_P25S10_PNL_.xlsx"#EC_benchmark_prime.xlsx"
#xl_filename = "/home/dexter/Euler_Capital_codes/EC_tools/results/EC_benchmark/20250210_argusexact_cross_P10S35_PNL_full_righttime_.xlsx"
#xl_filename = '/home/dexter/Euler_Capital_codes/EC_tools/results/consistency/live_trade_vs_backtest_newcode/live_trade_compare_pnl_Jan13Feb18_.xlsx'
#xl_filename = '/home/dexter/Euler_Capital_codes/EC_tools/results/heatmap2/20240813_argusexact_cross_P25S20_PNL_.xlsx'
#xl_filename = '/home/dexter/Euler_Capital_codes/EC_tools/results/consistency/live_trade_vs_backtest_newcode/live_trade_compare_pnl_TP25SL40_normalopen_.xlsx'

#xl_filename = RESULT_FILEPATH + '/MR_lag_roll/0330_entry/MR_2lag_5roll/20240814_argusexact_cross_P25S35_0330_entry_PNL_full_.xlsx'
#xl_filename = RESULT_FILEPATH +'/heatmap3_buyQ50sellQ50/20240813_argusexact_cross_P15S45_PNL_.xlsx'
#xl_filename = RESULT_FILEPATH +'/heatmap2/20240813_argusexact_cross_P35S25_PNL_.xlsx'
#xl_filename = RESULT_FILEPATH + '/test_results/test_master_pnl_8_SLB_.xlsx'
#xl_filename = RESULT_FILEPATH +'/strong_MR_signal/20240814_argusexact_cross_P25S35_0330_entry_PNL_full_.xlsx'
#xl_filename = RESULT_FILEPATH +'/strong_MR_signal/1lag5roll/20240814_argustrend_cross_P40S20_0330_entry_PNL_full_.xlsx'
#xl_filename = RESULT_FILEPATH +'/MR_signal_study/SLD4/test_master_pnl_SLD4_.xlsx'
#xl_filename = RESULT_FILEPATH +'/ArgusTailStrangle/20240814_argutailstrangle_cross_TE20SL10_0330_entry_PNL_full_.xlsx'
#xl_filename = RESULT_FILEPATH +'/ArgusTailStrangle/20240814_argutailstrangle_cross_TE45SL35_0330_entry_PNL_full_.xlsx'
xl_filename = RESULT_FILEPATH +'/ArgusIQRSKW/20240814_argusIQRSKW_cross_WIQR22WSKW10_TETPOBOSSL45_0330_entry_PNL_full_.xlsx'

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
    
    print(df)
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
            
        draw_down= np.log(cum_return/current_max)
        
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

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from itertools import cycle

def plot_multipanels(filenames:list[str], labels: list[str],
                     sym:str, plot_type ='trade_return'):
    cycol = cycle('bgrcmk')    # define colour scheme
    prev_plot = None
    
    x_lower_limit = datetime.datetime(2025,1,11)
    x_upper_limit = datetime.datetime(2025,2,28)
    
    x_delta = datetime.timedelta(days=15)    
    
    plt.style.use('dark_background')
    fig = plt.figure(figsize=(12,10))
    gs = fig.add_gridspec(nrows=len(filenames), 
                          ncols = 1, height_ratios=[2, 2,2,2])

    for i, xl_filename in enumerate(filenames):
        # Read data
        df = read_xl_file(xl_filename, sheet_name=sym)
        date_bucket, return_bucket = group_by_date(df)
        cum_return_bucket = np.cumsum(return_bucket)
        
        df_new = pd.DataFrame(data={'Date':date_bucket, 
                                    'Return': cum_return_bucket})
        # setup plot
        ax = fig.add_subplot(gs[i], sharex=prev_plot)
        
        if plot_type == 'trade_return':
            y_upper_limit = max(return_bucket) + np.std(return_bucket)
            y_lower_limit = min(return_bucket) - np.std(return_bucket)
            
            max_y = max(return_bucket)
            current_col = next(cycol)

            ax.bar(date_bucket, return_bucket, color=current_col)
        elif plot_type == 'cum_return':
            y_upper_limit = max(cum_return_bucket) + np.std(cum_return_bucket)
            y_lower_limit = min(cum_return_bucket) - np.std(cum_return_bucket)
            max_y = max(cum_return_bucket)

            current_col = next(cycol)
            
            ax.plot(date_bucket, cum_return_bucket, color=current_col)

        prev_plot = ax
        
        ax.hlines(0,x_lower_limit, x_upper_limit, lw = 2,color='orange')
        ax.text(x_upper_limit-x_delta, max_y,
                labels[i],  color = current_col, fontsize=15)
        
        fmt = mdates.DateFormatter('%y-%m-%d')
        #ax1.legend(loc='center left', bbox_to_anchor=(1, 0.5))
        ax.xaxis.set_major_formatter(fmt)
        ax.set_ylim(y_lower_limit, y_upper_limit)
        ax.grid()
        
    plt.suptitle(r"Cumulative Return Comparison", fontsize=15)

    plt.show()
    
    return

def livetrading_vs_backtest_plot(date_bucket, return_bucket,
                                 dates=[],datas=[], labels=[],
                                 mode='trade_return'):
    cycol = cycle('crb')    # define colour scheme

    x_lower_limit = datetime.datetime(2025,1,11)
    x_upper_limit = datetime.datetime(2025,2,28)

    y_upper_limit = max(return_bucket) + np.std(return_bucket)
    y_lower_limit = min(return_bucket) - np.std(return_bucket)

    
    plt.style.use('dark_background')
    fig = plt.figure(figsize=(12,2.5))
    gs = fig.add_gridspec(nrows=1,
                          ncols = 1, height_ratios=[2])
    
    ax = fig.add_subplot(gs[0])
    
    for date, data, label in zip(dates,datas, labels):
        if mode =='trade_return':
            ax.bar(date, data, color=next(cycol),label=label)
        elif mode == 'cum_return':
            cum_return = np.cumsum(data)
            ax.plot(date, cum_return, color=next(cycol),label=label, 
                    drawstyle='steps-mid')

    if mode =='trade_return':
        ax.bar(date_bucket, return_bucket, 
                lw =4, edgecolor='w', color='None',label='Live-Trades')
    elif  mode == 'cum_return':
        cum_return = np.cumsum(return_bucket)
        ax.plot(date_bucket, cum_return, 'w',label='Live-Trades', lw =3,
                drawstyle='steps-mid')

            #drawstyle='steps-mid')
    ax.hlines(0,x_lower_limit, x_upper_limit, lw = 2,color='orange')
    

    fmt = mdates.DateFormatter('%y-%m-%d')
    #ax1.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    ax.xaxis.set_major_formatter(fmt)
    ax.set_ylim(y_lower_limit, y_upper_limit)
    ax.grid()
    plt.legend(loc='upper right')
    plt.title("Live vs Backtest Results (Cumulative Returns)")
    plt.show()

    return

if __name__ == "__main__":
    filepath = '/consistency/live_trade_vs_backtest_newcode/'
    TP25SL35 = RESULT_FILEPATH + filepath + 'live_trade_compare_pnl_TP25SL35_.xlsx'
    TP25SL35_normalopen = RESULT_FILEPATH + filepath + 'live_trade_compare_pnl_TP25SL35_normalopen_.xlsx'
    TP25SL10 = RESULT_FILEPATH + filepath + 'live_trade_compare_pnl_TP25SL10_.xlsx'
    TP25SL10_normalopen = RESULT_FILEPATH + filepath + 'live_trade_compare_pnl_TP25SL10_normalopen_.xlsx'




    if False:
        live_xl_filename = RESULT_FILEPATH + '/trading_operation/live_record.xlsx'
        syms = ['CLc1', 'CLc2', 'HOc1', 'HOc2',
                'RBc1','RBc2','QOc1','QOc2','QPc1','QPc2']
        
        LIVE_DATA = read_xl_file(live_xl_filename, sheet_name='Sheet1')
        TP25SL35 = read_xl_file(TP25SL35,sheet_name='Total')
        TP25SL10 = read_xl_file(TP25SL10,sheet_name='Total')
        TP25SL10_normalopen = read_xl_file(TP25SL10_normalopen,
                                           sheet_name='Total')
        
# =============================================================================
#         
#         TP25SL35_select = TP25SL35[(TP25SL35['Entry_Date']>='2025-02-19')]
#         TP25SL10_select = TP25SL10[(TP25SL10['Entry_Date']<'2025-02-19')&
#                                    (TP25SL10['Entry_Date']>='2025-01-16')]
#         TP25SL10_no_select = TP25SL10_normalopen[(TP25SL10_normalopen['Entry_Date']
#                                                    <'2025-01-16')]
#         
#         date_bucket_TP25SL35, return_bucket_TP25SL35 = group_by_date(TP25SL35_select)
#         date_bucket_TP25SL10, return_bucket_TP25SL10 = group_by_date(TP25SL10_select)
#         date_bucket_TP25SL10_no, return_bucket_TP25SL10_no = group_by_date(TP25SL10_no_select)
# 
# =============================================================================
        date_bucket_TP25SL35, return_bucket_TP25SL35 = group_by_date(TP25SL35)
        date_bucket_TP25SL10, return_bucket_TP25SL10 = group_by_date(TP25SL10)
        date_bucket_TP25SL10_no, return_bucket_TP25SL10_no = group_by_date(TP25SL10_normalopen)
        
        date_bucket = LIVE_DATA['Date'].to_numpy()
        return_bucket = [sum(LIVE_DATA[syms].iloc[i].to_list()) for i in range(len(LIVE_DATA))]
        
        return_bucket_float = [float(ele) for ele in return_bucket]
        cum_return_bucket = np.cumsum(return_bucket_float)
        
        print(date_bucket, return_bucket)
        livetrading_vs_backtest_plot(date_bucket,return_bucket,
                                     dates=[date_bucket_TP25SL10_no,
                                            date_bucket_TP25SL10, 
                                            date_bucket_TP25SL35],
                                     datas=[return_bucket_TP25SL10_no,
                                            return_bucket_TP25SL10, 
                                            return_bucket_TP25SL35],
                                     labels=['TP25SL10_NormalOpen',
                                             'TP25SL10','TP25SL35'],
                                     mode='cum_return')
    
    
    if False:
        # Compare live trades and backtest, plot 4 panels 
        filepath = '/consistency/live_trade_vs_backtest_newcode/'
        TP25SL35 = RESULT_FILEPATH + filepath + 'live_trade_compare_pnl_TP25SL35_.xlsx'
        TP25SL35_normalopen = RESULT_FILEPATH + filepath + 'live_trade_compare_pnl_TP25SL35_normalopen_.xlsx'
        TP25SL10 = RESULT_FILEPATH + filepath + 'live_trade_compare_pnl_TP25SL10_.xlsx'
        TP25SL10_normalopen = RESULT_FILEPATH + filepath + 'live_trade_compare_pnl_TP25SL10_normalopen_.xlsx'

        FILENAMES = [TP25SL35, TP25SL35_normalopen, 
                     TP25SL10, TP25SL10_normalopen]
    
        LABELS = ["TP25SL35 (3:30 UTC open)", 'TP25SL35 (NormalOpen)',
                  "TP25SL10  (3:30 UTC open)", "TP25SL10 (NormalOpen)"]
        plot_multipanels(FILENAMES, LABELS, sym='Total',plot_type="cum_return")
    
    if True:
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
        
