#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr  5 03:19:59 2024

@author: dexter

This is a list of strategy that can be implemented in other scripts.
"""
import numpy as np

class MeanReversionStrategy():
    
    def make_signal_bucket():
        # a function that make data bucket for a particular strategy

        signal_columns = ['APC forecast period', 'APC Contract Symbol']
        
        # usemaxofpdf_insteadof_medianpdf
        A = ["Q0.1","Q0.4","Q0.5","Q0.6","Q0.9"]
        
        B = ["Q0.1", "Qmax-0.1", "Qmax","Qmax+0.1","Q0.9"]
        
        # use_OB_OS_levels_for_lag_conditions
        C = ["Close price lag 1", "Close price lag 2", "OB level 1 lag 1", 
             "OB level 1 lag 2", "OS level 1 lag 1", "OS level 1 lag 2", 
             "OB level 3", "OS level 3", "Price 3:30 UK time"]
        
        D = ['Quant close lag 1', 'Quant close lag 2', 'mean Quant close n = 5',
             'Quant 3:30 UK time']
        
        # abs(entry_region_exit_region_range[0]) > 0
        E = ['target entry lower', 'target entry upper']
        
        F = ['target entry']
        
        # abs(entry_region_exit_region_range[1]) > 0:
        G= ['target entry lower', 'target entry upper']

        H = ['target exit']
        
        End = ['stop exit', 'direction', 'price code']
        
        # Base form of column, benchmark
        # Old + A + D + F + H + end
        
        I1 = signal_columns + A + D + F + H + End
        
        #I1 = ['APC forecast period', 'APC Contract Symbol', "Q0.1", "Qmax-0.1", 
        #     "Qmax","Qmax+0.1","Q0.9", 'Quant close lag 1', 'Quant close lag 2', 
        #     'mean Quant close n = 5', 'Quant 3:30 UK time', 'target entry', 
        #     'target exit', 'stop exit', 'direction', 'price code']
        
        dictionary_futures_contracts_quantiles_for_signals = dict()

        for i in I1:
            dictionary_futures_contracts_quantiles_for_signals[i] = []
        
        return dictionary_futures_contracts_quantiles_for_signals
    

    #@loop_signal
    def argus_benchmark_strategy(price_330, history_data_lag5, apc_curve_lag5,
                                 curve_today):
        """
        The benchmark mean reversion strategy

        Parameters
        ----------
        price_330 : float
            DESCRIPTION.

        Returns
        -------
        dict
            A dictionary.

        """
        # inputs
        quant_330UKtime = price_330
        lag5_price = history_data_lag5['Settle']
        # Match the date just to be sure
        
        
        history_data_lag2_close = lag5_price[-2]
        history_data_lag1_close = lag5_price[-1]
        
        # The APC two days (lag2) before this date
        signal_data_lag2_median =  apc_curve_lag5[-2]['0.5'] 
        # The APC one day1 (lag1) before this date
        signal_data_lag1_median =  apc_curve_lag5[-1]['0.5']

        
        # pulling directly from a list is a factor of 3 faster than doing spline everytime
        
        # calculate the 5 days average for closing price
        rollinglagq5day = np.average(lag5_price)         
        
        # calculate the median of the apc for the last five days
        median_apc_5days = np.median([apc_curve_lag5[-5]['0.5'],
                                      apc_curve_lag5[-4]['0.5'],
                                      apc_curve_lag5[-3]['0.5'],
                                      apc_curve_lag5[-2]['0.5'],
                                      apc_curve_lag5[-1]['0.5']])

        # "BUY" condition
        # (1) Two consecutive days of closing price lower than the signal median
        cond1_buy = (history_data_lag2_close < signal_data_lag2_median)
        cond2_buy = (history_data_lag1_close < signal_data_lag1_median)
        # (2) rolling 5 days average lower than the media apc 
        cond3_buy = rollinglagq5day < median_apc_5days
        # (3) price at today's opening hour above the 0.1 quantile of today's apc
        cond4_buy = quant_330UKtime >= curve_today['0.1']
        
        # "SELL" condition
        # (1) Two consecutive days of closing price higher than the signal median
        cond1_sell = (history_data_lag2_close > signal_data_lag2_median)
        cond2_sell = (history_data_lag1_close < signal_data_lag1_median)    
        # (2) rolling 5 days average higher than the media apc 
        cond3_sell = rollinglagq5day > median_apc_5days
        # (3) price at today's opening hour below the 0.9 quantile of today's apc
        cond4_sell = quant_330UKtime <= curve_today['0.9']
        
        # Find the boolean value of strategy conditions
        Buy_cond = cond1_buy and cond2_buy and cond3_buy and cond4_buy
        Sell_cond =  cond1_sell and cond2_sell and cond3_sell and cond4_sell
        Neutral_cond = not (Buy_cond and Sell_cond)
        
        # make direction dictionary
        direction_dict = {"Buy": Buy_cond, "Sell": Sell_cond, "Neutral": Neutral_cond}
        
        for i in direction_dict:
            if direction_dict[i] == True:
                direction = i
        
        return direction
    
    def set_entry_price(cond, curve_today,buy_cond=(0.4,0.1) , sell_cond =(0.6,0.9)):
        
        if cond=="Buy":
            # (A) Entry region at price < APC p=0.4 and 
            entry_price = curve_today['0.4']
            # (B) Stop loss at APC p=0.1
            stop_loss = curve_today['0.1']
        elif cond=="Sell":
            # (A) Entry region at price > APC p=0.6 and 
            entry_price = curve_today['0.6']
            # (B) Stop loss at APC p=0.9
            stop_loss = curve_today['0.9']
        elif cond == "Neutral":
            # (A) Entry region at price > APC p=0.6 and 
            entry_price = "NA"
            # (B) Stop loss at APC p=0.9
            stop_loss = "NA"
        return {entry_price, stop_loss}
    
    def modified_benchmark():
        return None