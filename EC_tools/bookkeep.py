#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May  9 23:28:28 2024

@author: dexter

Bookkeeping module
"""

__all__ = ['Bookkeep']

__author__="Dexter S.-H. Hon"

# tested
class Bookkeep(object):
    
    signal_columns = ['APC forecast period', 'APC Contract Symbol']
    
    # usemaxofpdf_insteadof_medianpdf
    A = ["Q0.1","Q0.4","Q0.5","Q0.6","Q0.9"]
    
    B = ["Q0.1", "Qmax-0.1", "Qmax","Qmax+0.1","Q0.9"]

    #use_OB_OS_levels_for_lag_conditions
    C = ["Close price lag 1", "Close price lag 2", "OB level 1 lag 1", 
     "OB level 1 lag 2", "OS level 1 lag 1", "OS level 1 lag 2", 
     "OB level 3", "OS level 3", "Price 3:30 UK time"]

    D = ['Quant close lag 1', 'Quant close lag 2', 'mean Quant close n = 5',
     'Quant 3:30 UK time']

    # abs(entry_region_exit_region_range[0]) > 0
    E = ['target entry lower', 'target entry upper']

    F = ['target entry']

    # abs(entry_region_exit_region_range[1]) > 0:
    G = ['target entry lower', 'target entry upper']

    H = ['target exit']

    End = ['stop exit', 'direction', 'price code', 'strategy_id']
    
    
    benchmark_PNL = ['Price Code', 'predicted signal','date',
                     'return from trades', 'entry price','entry datetime',
                     'exit price', 'exit datetime', 'risk/reward value ratio']
    
    argus_exact_format = ['Date', 'Price_Code', 'Direction', 'Commodity_name',
                        'Contract_Month','Timezone', 
                        'Valid_From_localtz_timestr', 'Valid_To_localtz_timestr', 
                        'Target_Lower_Entry_Price', 'Target_Upper_Entry_Price',
                        'Target_Lower_Exit_Price', 'Target_Upper_Exit_Price',
                        'Stop_Exit_Price',
                        'NCONS',	'NROLL', 'Signal_NCONS', 'Signal_NROLL',	
                        'Quant_Close_Price_Lag_1', 'Quant_Close_Price_Lag_2',	
                        'Quant_Close_Price_Lag_3', 'Quant_Close_Price_Lag_4',	
                        'Quant_Close_Price_Lag_5', 'Quant_Close_Price_Lag_1_rm_5',	
                        'Q0.25', 'Q0.4', 'Q0.6', 'Q0.75', 
                        'Entry_Price', 'Exit_Price', 'StopLoss_Price',
                        'strategy_name']
    
    argus_exact_amb_format = ['Date', 'Price_Code', 'Direction', 'Commodity_name',
                        'Contract_Month','Timezone', 
                        'Valid_From_localtz_timestr', 'Valid_To_localtz_timestr', 
                        'Target_Lower_Entry_Price', 'Target_Upper_Entry_Price',
                        'Target_Lower_Exit_Price', 'Target_Upper_Exit_Price',
                        'Stop_Exit_Price',
                        'NCONS',	'NROLL', 'Signal_NCONS', 'Signal_NROLL',	
                        'Quant_Close_Price_Lag_1', 'Quant_Close_Price_Lag_2',	
                        'Quant_Close_Price_Lag_3', 'Quant_Close_Price_Lag_4',	
                        'Quant_Close_Price_Lag_5', 'Quant_Close_Price_Lag_1_rm_5',	
                        'Q0.25', 'Q0.4', 'Q0.6', 'Q0.75', 
                        'Entry_Price', 'Exit_Price', 'StopLoss_Price',
                        'strategy_name']
    
    argus_exact_mode_format = ['Date', 'Price_Code', 'Direction', 'Commodity_name',
                        'Contract_Month','Timezone', 
                        'Valid_From_localtz_timestr', 'Valid_To_localtz_timestr', 
                        'Target_Lower_Entry_Price', 'Target_Upper_Entry_Price',
                        'Target_Lower_Exit_Price', 'Target_Upper_Exit_Price',
                        'Stop_Exit_Price',
                        'NCONS',	'NROLL', 'Signal_NCONS', 'Signal_NROLL',	
                        'Quant_Close_Price_Lag_1', 'Quant_Close_Price_Lag_2',	
                        'Quant_Close_Price_Lag_3', 'Quant_Close_Price_Lag_4',	
                        'Quant_Close_Price_Lag_5', 'Quant_Close_Price_Lag_1_rm_5',	
                        'Q0.25', 'Q_mode-0.1', 'Q_mode+0.1', 'Q0.75', 
                        'Entry_Price', 'Exit_Price', 'StopLoss_Price',
                        'strategy_name']

    argus_PNL = ['Trade_Id', 'Direction', 'Commodity', 'Price_Code', 
                 'Contract_Month',
                 'Entry_Date',	'Entry_Datetime', 'Entry_Price',
                 'Exit_Date','Exit_Datetime','Exit_Price',
                 'Return_Trades', 'Risk_Reward_Ratio', 'strategy_name']
    
    STRATEGY_SIGNAL_COL_DICT = {
            "benchmark": signal_columns + A + D + F + H + End, 
            "mode": signal_columns + B + D + F + H + End, 
            "argus_exact": argus_exact_format,
            "argus_exact_amb": argus_exact_amb_format,
            "argus_exact_mode": argus_exact_mode_format
                   }
    
    BACKTEST_PNL_COL_DICT = {
            "benchmark": benchmark_PNL,
            "mode": benchmark_PNL,
            "argus_exact": argus_PNL,
            "argus_exact_amb": argus_PNL,
            "argus_exact_mode": argus_PNL

                    }
    
    def __init__(self, bucket_type = 'backtest'):
        self.bucket =  dict() # the main bucket for book-keeping.
        
        # choose which column dictionary to be called.
        if bucket_type =='mr_signals':
            self.bucket_dict = self.STRATEGY_SIGNAL_COL_DICT
        elif bucket_type =='backtest':
            self.bucket_dict = self.BACKTEST_PNL_COL_DICT

    def make_bucket(self, keyword='benchmark'):
        # simple method to make a bucket given some keywords
        bucket_keys = self.bucket_dict[keyword]
        for i in bucket_keys:
            self.bucket[i] = []
            
        return self.bucket 
    
    def store_to_bucket_single(self, data):
        """
        A simple function to store data in a bucket one entry at a time. 

        ParametersCurrent date and timeSaturday July 13, 2024 06:32:52 (AEST) Canberra, Australia (GMT +1000)

        ----------
        data : list
            A list of data to put into the bucket.

        Returns
        -------
        bucket: dict
            A filled bucket with data

        """
        # Storing the data for single entry. Please use this in a loop   
        for i, key in enumerate(self.bucket):
            self.bucket[key].append(data[i])   

        return self.bucket
    
    def store_to_bucket(self, data):
        return self.bucket