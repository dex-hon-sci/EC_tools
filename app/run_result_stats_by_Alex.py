#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 21 14:34:26 2025

@author: dexter
"""

import numpy as np

# prompt: read column names

#from google.colab import drive
import pandas as pd
import openpyxl

from itertools import islice


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

#drive.mount('/content/drive')

file_path = '/home/dexter/Euler_Capital_codes/EC_tools/results/heatmap2/20240813_argusexact_cross_P25S35_PNL_.xlsx'
col_interest = 'scaled returns from trades'
try:
    #df = pd.read_csv(file_path)
    df = read_xl_file(file_path, sheet_name='Total')

    #symbol_list = wb_obj.sheetnames
    #symbol_list = ['HOc1']

    
    
    print("CSV file read successfully!")

    # Get the column names
    column_names = df.columns.tolist()

except FileNotFoundError:
    print("File not found. Please check the file path.")

print(df.head())

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd

def plot_asset_cum_return():
    codes = df['Price_Code'].unique()
    df['Entry_Date'] = pd.to_datetime(df['Entry_Date'])
    
    for s in codes:
        new_df = df[df['Price_Code'] == s].copy()  # Create a copy of the slice
        # Calculate the cumulative sum of 'Trade_Return' using .loc
        new_df.loc[:, 'Cumulative_Trade_Return'] = new_df['Trade_Return'].cumsum()
        new_df['Running_Average'] = (
            new_df['Cumulative_Trade_Return'].rolling(window=30).mean()
        )
    
        # Plot the cumulative sum (rest of your plotting code remains the same)
        plt.figure(figsize=(12, 8))
        plt.plot(new_df['Entry_Date'], new_df['Cumulative_Trade_Return'], label = 'Cumulative Return')
        plt.plot(new_df['Entry_Date'], new_df['Running_Average'], label = 'Running Average', linewidth = 3)
    
        plt.xlabel('Time')
        plt.ylabel('Cumulative Trade Return')
        plt.title('Cumulative Trade Return Over Time: ' + s)
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator())
        plt.gcf().autofmt_xdate()
        plt.grid(True)
        plt.show()
        print()
    

from collections import Counter

def plot_entry_exit_time():
    filtered_df = df[df[col_interest] > 0]

    entry_times = pd.to_datetime(filtered_df['Entry_Datetime']).dt.strftime('%H').tolist()
    exit_times = pd.to_datetime(filtered_df['Exit_Datetime']).dt.strftime('%H').tolist()
    print(sorted(entry_times))

    entry_times_freq = Counter(entry_times)
    exit_times_freq = Counter(exit_times)
    entry_times_series = [entry_times_freq[str(i)] for i in sorted(entry_times_freq.keys())]
    exit_times_series = [exit_times_freq[str(i)] for i in sorted(exit_times_freq.keys())]
    
    # Plot the histogram with sorted x-axis ticks
    plt.figure(figsize=(12, 8))
    plt.bar(sorted(entry_times_freq.keys()), entry_times_series, label='Entry Times', alpha=0.8)
    plt.bar(sorted(exit_times_freq.keys()), exit_times_series, label='Exit Times', alpha=0.8)
    plt.xlabel('Time')
    plt.ylabel('Frequency')
    plt.title('Entry and Exit Times')
    plt.legend()
    plt.grid(True)
    plt.show()


def plot_hist_trade_return_bytime_before(before_hour):
    df['Exit_Datetime'] = pd.to_datetime(df['Exit_Datetime'])
    df['Entry_Datetime'] = pd.to_datetime(df['Entry_Datetime'])
    
    # Extract the hour from 'Exit_Datetime'
    df['Exit_Hour'] = df['Exit_Datetime'].dt.hour
    
    # Filter the DataFrame to select rows where 'Exit_Hour' is greater than or equal to 18
    filtered_df = df[df['Exit_Hour'] <= before_hour]
    #filtered_df = filtered_df[filtered_df[col_interest] <0]
    
    # Collect the 'Trade_Return_Fraction' values from the filtered DataFrame
    trade_return_fractions = filtered_df[col_interest].tolist()
    
    # Plot the histogram
    plt.figure(figsize=(12, 8))
    plt.hist(trade_return_fractions, bins=40)
    
    # Get current y-axis limits
    ymin, ymax = plt.ylim()
    
    # Adjust y-axis limits to include 0
    plt.ylim(min(ymin, -0.5), max(ymax, 0.5))  # Adjust -0.5 and 0.5 as needed
    
    plt.axvline(x=0, color='red', linewidth=2)  # Changed ayhline to axvline for vertical line
    plt.xlabel('Trade Return Fraction')
    plt.ylabel('Frequency')
    plt.title(f'Distribution of Trade Return before {before_hour}:00')
    plt.grid(True)
    plt.show()
    return trade_return_fractions

def plot_hist_trade_return_bytime_after(after_hour):
    df['Exit_Datetime'] = pd.to_datetime(df['Exit_Datetime'])
    df['Entry_Datetime'] = pd.to_datetime(df['Entry_Datetime'])
    
    # Extract the hour from 'Exit_Datetime'
    df['Exit_Hour'] = df['Exit_Datetime'].dt.hour
    
    # Filter the DataFrame to select rows where 'Exit_Hour' is greater than or equal to 18
    filtered_df = df[df['Exit_Hour'] >= after_hour]
    #filtered_df = filtered_df[filtered_df[col_interest] <0]

    # Collect the 'Trade_Return_Fraction' values from the filtered DataFrame
    trade_return_fractions = filtered_df[col_interest].tolist()

    ar = np.array(trade_return_fractions)
    print('Mean: ', round(np.mean(ar), 3))
    print('Deviation: ', round(np.std(ar), 3))
        
    # Collect the 'Trade_Return_Fraction' values from the filtered DataFrame
    trade_return_fractions = filtered_df[col_interest].tolist()
    
    # Plot the histogram
    plt.figure(figsize=(12, 8))
    plt.hist(trade_return_fractions, bins=30)
    
    # Get current y-axis limits
    ymin, ymax = plt.ylim()
    
    # Adjust y-axis limits to include 0
    plt.ylim(min(ymin, -0.5), max(ymax, 0.5))  # Adjust -0.5 and 0.5 as needed
    
    plt.axvline(x=0, color='red', linewidth=2)  # Changed ayhline to axvline for vertical line
    plt.xlabel('Trade Return Fraction')
    plt.ylabel('Frequency')
    plt.title(f'Distribution of Trade Return after {after_hour}:00')
    plt.grid(True)
    plt.show()
    return trade_return_fractions

def plot_hist_trade_return_bytime_between(low_bound,up_bound):
    df['Exit_Datetime'] = pd.to_datetime(df['Exit_Datetime'])
    df['Entry_Datetime'] = pd.to_datetime(df['Entry_Datetime'])
    
    # Extract the hour from 'Exit_Datetime'
    df['Exit_Hour'] = df['Exit_Datetime'].dt.hour
    
    # Filter the DataFrame to select rows where 'Exit_Hour' is greater than or equal to 18
    filtered_df = df[(df['Exit_Hour'] >= low_bound)&(df['Exit_Hour'] <= up_bound)]
    #filtered_df = filtered_df[filtered_df[col_interest] <0]
    
    # Collect the 'Trade_Return_Fraction' values from the filtered DataFrame
    trade_return_fractions = filtered_df[col_interest].tolist()
    
    # Plot the histogram
    plt.figure(figsize=(12, 8))
    plt.hist(trade_return_fractions, bins=40)
    
    # Get current y-axis limits
    ymin, ymax = plt.ylim()
    
    # Adjust y-axis limits to include 0
    plt.ylim(min(ymin, -0.5), max(ymax, 0.5))  # Adjust -0.5 and 0.5 as needed
    
    plt.axvline(x=0, color='red', linewidth=2)  # Changed ayhline to axvline for vertical line
    plt.xlabel('Trade Return Fraction')
    plt.ylabel('Frequency')
    plt.title(f'Distribution of Trade Return between {low_bound}:00 and {up_bound}:00')
    plt.grid(True)
    plt.show()
    return trade_return_fractions

def plot_entry_exit_mean_std_bytime():
    df['Exit_Datetime'] = pd.to_datetime(df['Exit_Datetime'])
    df['Entry_Datetime'] = pd.to_datetime(df['Entry_Datetime'])
    # Extract the hour from 'Exit_Datetime'
    df['Exit_Hour'] = df['Exit_Datetime'].dt.hour
    df['Entry_Hour'] = df['Entry_Datetime'].dt.hour
    
    
    x_tickslabel = [3+i for i in range(17)]

    
    print("length", len(df))

    filtered_df = df[df[col_interest] < 0]
    trade_return_fractions = filtered_df[col_interest].tolist()
    print(len(filtered_df), filtered_df)
    
    ar = np.array(trade_return_fractions)
    print('Mean: ', round(np.mean(ar), 3))
    print('Deviation: ', round(np.std(ar), 3))
    
    hours = list(range(3, 20))
    entry_to_return_mean = []
    entry_to_return_std = []
    exit_to_return_mean = []
    exit_to_return_std = []
    entry_to_return_box, exit_to_return_box = [],[]
    entry_to_return_mean_weight, exit_to_return_mean_weight = [], []
    
    three = [hour -2 for hour in hours]

    LENGTH = len(trade_return_fractions)

    entry_length, exit_length = 0,0
    for h in hours:
        filtered_df_2 = filtered_df[filtered_df['Entry_Hour'] == h]
        trade_return_fractions_2 = filtered_df_2[col_interest].tolist()
    
        print('entry', h, len(trade_return_fractions_2))
        entry_length += len(trade_return_fractions_2)
        
        # Check if the list is empty before calculating mean and std
        if trade_return_fractions_2:
            entry_to_return_mean.append(np.median(trade_return_fractions_2))
            entry_to_return_std.append(np.std(trade_return_fractions_2))
            entry_to_return_box.append(trade_return_fractions_2)
            entry_to_return_mean_weight.append(sum(trade_return_fractions_2))
        else:
            entry_to_return_mean.append(np.nan)  # Append NaN if list is empty
            entry_to_return_std.append(np.nan)
            entry_to_return_box.append(np.nan)
            entry_to_return_mean_weight.append(np.nan)

    for h in hours:
        filtered_df_3 = filtered_df[filtered_df['Exit_Hour'] == h]
        trade_return_fractions_3 = filtered_df_3[col_interest].tolist()
        print('exit', h, len(trade_return_fractions_3))
        exit_length += len(trade_return_fractions_3)

        # Check if the list is empty before calculating mean and std
        if trade_return_fractions_3:
            exit_to_return_mean.append(np.median(trade_return_fractions_3))
            exit_to_return_std.append(np.std(trade_return_fractions_3))
            
            exit_to_return_box.append(trade_return_fractions_3)
            exit_to_return_mean_weight.append(sum(trade_return_fractions_3))

        else:
            exit_to_return_mean.append(np.nan)  # Append NaN if list is empty
            exit_to_return_std.append(np.nan)
            exit_to_return_box.append(np.nan)
            exit_to_return_mean_weight.append(np.nan)

    #print(entry_to_return_box, exit_to_return_box)
    print(entry_length, exit_length)
    plt.figure(figsize=(12, 8))
    fig,ax = plt.subplots()

    ax.boxplot(entry_to_return_box, label='Entry',
                       medianprops={'color':'red'},
                       boxprops ={'facecolor':'green', 'alpha':0.5},
                       patch_artist=True,
                       tick_labels=x_tickslabel)  # will be used to label x-ticks
    
    
    ax.boxplot(exit_to_return_box, label='Exit',
                       medianprops={'color':'red'},
                       boxprops ={'facecolor':'blue','alpha':0.5},
                       patch_artist=True,
                       tick_labels= x_tickslabel)  # will be used to label x-ticks
    
    plt.plot(three, entry_to_return_mean, color='green', 
             marker='o',ms=2, label='Entry to Return Median')
    plt.plot(three, exit_to_return_mean, color='blue', 
             marker='o',ms=2, label='Exit to Return Median')

    plt.xlabel('Hour')
    plt.ylabel('Scaled Trade Return')
    plt.title('Scaled Trade Return Fraction vs. Entry/Exit Hour')
    plt.legend()
    plt.grid(True)
    plt.show()
    
    #plt.figure(figsize=(12, 8))
    fig,ax = plt.subplots()

    plt.plot(hours, entry_to_return_mean_weight, label='Entry to total Return', marker='o')
    plt.plot(hours, exit_to_return_mean_weight, label='Exit to total Return', marker='o')
    plt.axhline(y=0, color='green', linestyle='--', linewidth = 2)
    plt.xlabel('Hour')
    plt.ylabel('Total Trade Return')
    plt.title('Total Trade Return vs. Entry/Exit Hour')
    plt.legend()
    plt.grid(True)
    plt.show()

    #plt.figure(figsize=(12, 8))
    fig,ax = plt.subplots()

    plt.plot(hours, entry_to_return_std, label='Entry to Return Std', marker='o')
    plt.plot(hours, exit_to_return_std, label='Exit to Return Std', marker='o')
    plt.xlabel('Hour')
    plt.ylabel('Std Trade Return Fraction')
    plt.title('Std Trade Return Fraction vs. Entry/Exit Hour')
    plt.legend()
    plt.grid(True)
    plt.show()
    
#plot_entry_exit_time()
plot_entry_exit_mean_std_bytime()
# =============================================================================
# plot_hist_trade_return_bytime_between(11,12)
# plot_hist_trade_return_bytime_between(12,13)
# plot_hist_trade_return_bytime_between(13,14)
# plot_hist_trade_return_bytime_between(14,15)
# plot_hist_trade_return_bytime_between(15,16)
# plot_hist_trade_return_bytime_between(16,17)
# plot_hist_trade_return_bytime_between(17,18)
# plot_hist_trade_return_bytime_between(18,19)
# plot_hist_trade_return_bytime_between(19,20)
# 
# =============================================================================
# =============================================================================
# plot_hist_trade_return_bytime_before(12)
# plot_hist_trade_return_bytime_after(12)
# 
# plot_hist_trade_return_bytime_before(13)
# plot_hist_trade_return_bytime_after(13)
# 
# plot_hist_trade_return_bytime_before(14)
# plot_hist_trade_return_bytime_after(14)
# 
# plot_hist_trade_return_bytime_before(15)
# plot_hist_trade_return_bytime_after(15)
# 
# plot_hist_trade_return_bytime_before(16)
# plot_hist_trade_return_bytime_after(16)
# 
# plot_hist_trade_return_bytime_before(17)
# plot_hist_trade_return_bytime_after(17)
# 
# plot_hist_trade_return_bytime_before(18)
# plot_hist_trade_return_bytime_after(18)
# 
# plot_hist_trade_return_bytime_before(19)
# plot_hist_trade_return_bytime_after(19)
# =============================================================================
