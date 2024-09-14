#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 20 11:36:29 2024

@author: dexter
"""
import numpy as np
import pandas as pd
import EC_tools.math_func as mfunc

class GenHistoryStratData(object):
    """
    A class that contains a collection of method that generate data for 
    strategies base on history data
    
    """
    def __init__(self, history):
        self._history = history
        return
    
    def gen_lag_data(self, 
                     history_data_lag: pd.DataFrame, 
                     apc_curve_lag: pd.DataFrame, 
                     price_proxy: str = 'Settle', 
                     qunatile: list[float] = [0.25,0.4,0.6,0.75]) ->\
                     tuple[dict,list]: 
        """
        A method that generate all the data needed for the strategy. The ouput
        of this functions contain all the quantity that will be and can be used 
        in creating variation of this strategy.
        

        Parameters
        ----------
        history_data_lag : DataFrame
            The history data of the lag days.
        apc_curve_lag : DataFrame
            The APC curve of the lag days.
        price_proxy : str, optional
            The column name to call for price approximation. 
            It can be either "Open", "High", "Low", or "Settle".
            The default is 'Settle'.
        qunatile : list, optional
            1D list that contains the quantile desitred. 
            This function pass it into the APC of the day and calculate the 
            relevant price.
            The default is [0.25,0.4,0.6,0.75].

        Returns
        -------
        strategy_info : dict
            A dictionary containing two key-value pairs.
            'lag_list' is a list of quantiles of the lag days. The size of the 
            list depends on the input size of history_data_lag and apc_curve_lag.
            'rollingaverage' is the average of the quantiles in lag_list. It 
            contain a singular float value.
            
        qunatile_info : list
            A list of prices calculating using qunatile input into the APC
            of the date of interest.

        """
        # use the history data to call a column using either OHLC                      
        lag_price = history_data_lag[price_proxy]
        
        # Find the quantile number for the lag APC at the Lag Prices 
        lag_list = [mfunc.find_quant(apc_curve_lag.iloc[i].to_numpy()[1:-1], 
                                     self._quant_list, lag_price.iloc[i]) for 
                                    i in range(len(apc_curve_lag))]
        lag_list.reverse()
        # Note that the list goes like this [lag1q,lag2q,...]
        
        # calculate the rolling average
        rollingaverage_q = np.average(lag_list)
        
        # Storage
        strategy_info = {'lag_list': lag_list, 
                         'rollingaverage': rollingaverage_q}
        # The price of the quantile of interest, mostly for bookkeeping
        qunatile_info = list(self._curve_today_spline(qunatile))
        
        return strategy_info, qunatile_info

    def gen_lag_data_mode(self, 
                          history_data_lag: pd.DataFrame, 
                          apc_curve_lag: pd.DataFrame, 
                          price_proxy: str = 'Settle', 
                          quantile_delta: list = [-0.1, 0.0, +0.1])->\
                          tuple[dict,list]: 
        
        lag_price = history_data_lag[price_proxy]
        lag_list = [mfunc.find_quant(apc_curve_lag.iloc[i].to_numpy()[1:-1], 
                                     self._quant_list, lag_price.iloc[i]) for 
                                    i in range(len(apc_curve_lag))]
        lag_list.reverse()
        # Note that the list goes like this [lag1q,lag2q,...]
        # calculate the rolling average
        rollingaverage_q = np.average(lag_list)
        
        # turn the APC (cdf) to pdf in a list
        lag_pdf_list = [mfunc.cal_pdf(self._quant_list, 
                                      apc_curve_lag.iloc[i].to_numpy()[1:-1]) 
                                            for i in range(len(apc_curve_lag))]
        # Calculate the price of the mode in these apc
        mode_Q_list = [mfunc.find_pdf_quant(lag_pdf_list[i][0], lag_pdf_list[i][1])
                                        for i in range(len(apc_curve_lag))]
        mode_Q_list.reverse()
        
        # calculate the rolling average for the mode
        rollingaverage_mode_q = np.average(mode_Q_list)
        

        strategy_info = {'lag_list': lag_list, 
                         'rollingaverage': rollingaverage_q,
                         'mode_Q_list': mode_Q_list,
                         'rollingaverage_mode': rollingaverage_mode_q
                         }

        # Find the quantile in the CDF (NOT THE PDF! important) from the mode_price
        quantile = [quant + self._curve_today_reverse_spline(self.mode_price) 
                                                for quant in quantile_delta]

        qunatile_info = list(self._curve_today_spline(quantile))
 
        return strategy_info, qunatile_info 
