#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 17 23:30:24 2024

@author: dexter
"""
import pandas as pd 
import numpy as np
import EC_tools.utility as util
REF_SIGNAL ="/home/dexter/Euler_Capital_codes/EC_tools/results/20220101_20240628_signals_2.xlsx"
RESULT_SIGNAL = "/home/dexter/Euler_Capital_codes/EC_tools/results/argus_exact_signal_short_2_3cond.csv"

REF_PNL = "/home/dexter/Euler_Capital_codes/EC_tools/results/20220101_20240628_trades_2.xlsx"
RESULT_PNL = "/home/dexter/Euler_Capital_codes/EC_tools/results/argus_exact_PNL_short.csv"

df_ref_signal = pd.read_excel(REF_SIGNAL)
df_result_signal = pd.read_csv(RESULT_SIGNAL)

df_ref_PNL = pd.read_excel(REF_PNL)
df_result_PNL = pd.read_csv(RESULT_PNL)
print(df_ref_PNL['Entry_Datetime'], type(df_ref_PNL['Entry_Datetime'].iloc[0]))
df_ref_PNL['Entry_Datetime'] = [pd.to_datetime(df_ref_PNL['Entry_Datetime'].iloc[i]) for i in range(len(df_ref_PNL['Entry_Datetime']))]
print(df_ref_PNL['Entry_Datetime'], type(df_ref_PNL['Entry_Datetime'].iloc[0]))
print('REF',df_ref_PNL['Entry_Datetime'], type(df_ref_PNL['Entry_Datetime'].iloc[0]))

print(df_ref_PNL['Entry_Datetime'].iloc[1] - df_ref_PNL['Entry_Datetime'].iloc[0])

print('signal_ref_length:', len(df_ref_signal), 'signal_result_length:', len(df_result_signal))
print('PNL_ref_length:', len(df_ref_PNL), 'PNL_result_length:', len(df_result_PNL))
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
            result_val, ref_val= result_df[compare_col].iloc[i], None
        else:
            result_val, ref_val = result_df[compare_col].iloc[i], \
                                            temp_ref[compare_col].item()
        #print(pd.isna(result_val) , ref_val == None)
        if not pd.isna(result_val) and not pd.isna(ref_val):
            compare = compare_func(result_val, ref_val)
        else:
            print('NONE Error')
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
    print(x,y)

    if x>=y:
        delta = x - y
    elif x < y:
        delta = y-x
    print(delta)
    return delta

print('Signal')

A = find_difference(df_result_signal, df_ref_signal, 
                        (lambda x, y: x == y),
                        compare_col="Direction")

print('PNL')
#df_date_difference = A[A[4] == False]

# =============================================================================
# C = find_difference(df_result_PNL, df_ref_PNL, 
#                       date_compare,
#                       compare_col="Entry_Datetime", date_match_col = 'Entry_Date')
# =============================================================================

# =============================================================================
# D = find_difference(df_result_PNL, df_ref_PNL, 
#                        (lambda x, y: x - y),
#                        compare_col="Entry_Price", date_match_col = 'Entry_Date')
# =============================================================================


# 4 plots
#1) Entry time comparison
#2) Entry price comparison
#1) Exit time comparison
#2) Exit price comparison


def plot_difference_time():
    return 

def plot_difference_price():
    return