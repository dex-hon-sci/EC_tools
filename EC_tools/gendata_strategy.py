#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 20 11:36:29 2024

@author: dexter
"""
import numpy as np
import EC_tools.math_func as mfunc

class GenLagHistoryData():
    def __init

    def gen_data(self, history_data_lag, apc_curve_lag, 
                            price_proxy = 'Settle', 
                            quantile_delta = [-0.1, 0.0, +0.1]):
        
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