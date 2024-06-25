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
    
    STRATEGY_SIGNAL_COL_DICT = {
            "benchmark": signal_columns + A + D + F + H + End, 
            "mode": signal_columns + B + D + F + H + End 
                   }
    
    BACKTEST_PNL_COL_DICT = {
            "benchmark": benchmark_PNL,
            "mode": benchmark_PNL
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

        Parameters
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