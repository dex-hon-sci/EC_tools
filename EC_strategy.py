#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr  5 03:19:59 2024

@author: dexter

This is a list of strategy that can be implemented in other scripts.
"""
import numpy as np
import math_func as mfunc
from scipy.interpolate import CubicSpline, UnivariateSpline

# round trip fee 15 dollars
__author__="Dexter S.-H. Hon"

class MRStrategy(object):
    
    def __init__(self):
        self._buy_cond_list = []
        self._sell_cond_list = []
        return None
    
    def set_buy_cond(self):
        return None
    
    def make_signal_bucket(strategy_name="benchmark"):
        # a function that make data bucket for a particular strategy
        
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
    
        End = ['stop exit', 'direction', 'price code']
    
        
        # a dictionary for column combination
        strategy_dict = {
            "benchmark": signal_columns + A + D + F + H + End, 
            "mode": signal_columns + B + D + F + H + End 
                   }
   
        # Define the empty bucket keys
        bucket_keys = strategy_dict[strategy_name]
        
        dict_futures_quant_signals = dict()
        for i in bucket_keys:
            dict_futures_quant_signals[i] = []
            
        return dict_futures_quant_signals
   

    def store_to_bucket_single(bucket, data):
        """
        A simple function to store data in a bucket. This function should be 
        used in adjacent to make_signal_bucket.

        Parameters
        ----------
        bucket : dict
            An empty dictionary with column names.
        data : list
            A list of data to put into the bucket.

        Returns
        -------
        bucket: dict
            A filled bucket with data

        """
        # Storing the data    
        for i, key in enumerate(bucket):
            bucket[key].append(data[i])   

        return bucket

    def argus_benchmark_strategy(price_330, history_data_lag5, apc_curve_lag5,
                                     curve_today):
        """
        This function takes in one single day worth of data and 
        produce a string of "Buy/Sell" signal.
    
        The benchmark mean reversion strategy from Argus media. This is our 
        baseline MR strategy. It generate a "Buy/Sell" signal base on the followiing:
        
            IF (1) Two consecutive days of closing price lower than the signal median
                (2) rolling 5 days average lower than the median apc 
                (3) price at today's opening hour above the 0.1 quantile of today's apc
            Then,
                produce "Buy" signal.
            
            IF (1) Two consecutive days of closing price higher than the signal median
                (2) rolling 5 days average higher than the median apc 
                (3) price at today's opening hour below the 0.9 quantile of today's apc
            Then,
                 produce "Sell" signal.
    
        Note that the neutral signal is given by a xnor gate. It means that if 
        both Buy_cond and Sell_cond are the same, Neutral_cond return True.

        Parameters
        ----------
        price_330 : float
            The starting price of the day.
        history_data_lag5 : pandas dataframe table
            The last 5 days of historical data.
        apc_curve_lag5 : pandas dataframe table
            The last 5 days of APC data.
        curve_today : 1D pandas dataframe
            The APC curve of the date of interest.

        Returns
        -------
        direction : str
            "Buy/Sell" signal.
            
        """
        # strategy cal_history -> direction, gen_data -> data, set_price -> EES
        
        # inputs
        quant_330UKtime = price_330
        lag5_price = history_data_lag5['Settle']
    
        # define the lag 2 days settlement prices
        history_data_lag2_close = lag5_price.iloc[-2]
        history_data_lag1_close = lag5_price.iloc[-1]
        
        # The APC two days (lag2) before this date
        signal_data_lag2_median =  apc_curve_lag5.iloc[-2]['0.5'] 
        # The APC one day1 (lag1) before this date
        signal_data_lag1_median =  apc_curve_lag5.iloc[-1]['0.5']

        # Reminder: pulling directly from a list is a factor of 3 faster than   
        # doing spline everytime
        
        # calculate the 5 days average for closing price
        rollinglagq5day = np.average(lag5_price)         
                
        # calculate the median of the apc for the last five days
        median_apc_5days = np.median([apc_curve_lag5.iloc[-5]['0.5'],
                                      apc_curve_lag5.iloc[-4]['0.5'],
                                      apc_curve_lag5.iloc[-3]['0.5'],
                                      apc_curve_lag5.iloc[-2]['0.5'],
                                      apc_curve_lag5.iloc[-1]['0.5']])

        # "BUY" condition
        # (1) Two consecutive days of closing price lower than the signal median
        cond1_buy = (history_data_lag2_close < signal_data_lag2_median)
        cond2_buy = (history_data_lag1_close < signal_data_lag1_median)
        # (2) rolling 5 days average lower than the median apc 
        cond3_buy = rollinglagq5day < median_apc_5days
        # (3) price at today's opening hour above the 0.1 quantile of today's apc
        cond4_buy = quant_330UKtime >= curve_today['0.1']
    
        # "SELL" condition
        # (1) Two consecutive days of closing price higher than the signal median
        cond1_sell = (history_data_lag2_close > signal_data_lag2_median)
        cond2_sell = (history_data_lag1_close > signal_data_lag1_median)    
        # (2) rolling 5 days average higher than the median apc 
        cond3_sell = rollinglagq5day > median_apc_5days
        # (3) price at today's opening hour below the 0.9 quantile of today's apc
        cond4_sell = quant_330UKtime <= curve_today['0.9']
        
        print("===================This is in the package")  
        print("cond1_buy", cond1_buy, history_data_lag2_close, signal_data_lag2_median)
        print("cond2_buy", cond2_buy, history_data_lag1_close, signal_data_lag1_median)
        print("cond3_buy", cond3_buy, rollinglagq5day,  median_apc_5days)
        print("cond4_buy", cond4_buy, quant_330UKtime, curve_today['0.1'])
        print("====================")
        print("cond1_sell", cond1_sell, history_data_lag2_close, signal_data_lag2_median)
        print("cond2_sell", cond2_sell, history_data_lag1_close, signal_data_lag1_median)
        print("cond3_sell", cond3_sell, rollinglagq5day,  median_apc_5days)
        print("cond4_sell", cond4_sell, quant_330UKtime, curve_today['0.1'])
        print("======================")
        
        
        # Find the boolean value of strategy conditions
        Buy_cond = cond1_buy and cond2_buy and cond3_buy and cond4_buy
        Sell_cond =  cond1_sell and cond2_sell and cond3_sell and cond4_sell
        
        Neutral_cond = not (Buy_cond ^ Sell_cond) #xnor gate
    
        # make direction dictionary
        direction_dict = {"Buy": Buy_cond, "Sell": Sell_cond, "Neutral": Neutral_cond}
        
        for i in direction_dict:
            if direction_dict[i] == True:
                direction = i
        
        return direction

    def argus_benchmark_mode(price_330, history_data_lag5, apc_curve_lag5,
                                     curve_today):
        # inputs
        quant_330UKtime = price_330
        lag5_price = history_data_lag5['Settle']
        
        # Match the date just to be sure
        # To be added
    
        # define the lag 2 days settlement prices
        history_data_lag2_close = lag5_price.iloc[-2]
        history_data_lag1_close = lag5_price.iloc[-1]
        
        ########################################################################
        #Find the mode of the curve and find the quantile
        # make the apc lag list into pdf form
        quant0 = np.arange(0.0025, 0.9975, 0.0025)

        for i in range(len(apc_curve_lag5)):
            # price, probability
            spaced_events, pdf_lag = mfunc.cal_pdf(quant0, apc_curve_lag5[i].to_numpy()[1:-1])
        
        #[ ["date", price0.01 ...., contract code],[...],...   ]
        # [{}]
        
        # get the one with max probability

        # get the wanted quantiles

        #pdf_lag1, even_spaced_prices_lag1, spline_apc_lag1 = get_APC_spline_for_APC_pdf(lag_apc_data[0].to_numpy()[0][1:end_prices])
        events_spaced, pdf_lag = mfunc.cal_pdf(quant0, curve_today.to_numpy()[1:-1])
        
        #spline_apc_lag1 = CubicSpline(curve_today.to_numpy()[1:-1], 
        #                 np.arange(0.0025, 0.9975, 0.0025))
        
        #price_max_prob_lag1 = even_spaced_prices_lag1[np.argmin(abs(pdf_lag1-np.max(pdf_lag1)))]
        #q_price_max_prob_lag1 = spline_apc_lag1(price_max_prob_lag1)        
        #######################################################################
        
        
        # The APC two days (lag2) before this date
        signal_data_lag2_mode =  max(apc_curve_lag5.iloc[-2][1:-1])
        # The APC one day1 (lag1) before this date
        signal_data_lag1_mode =  max(apc_curve_lag5.iloc[-1][1:-1])

        # Find the quantile of the mode of the lag2days apc    
        lag1q = mfunc.find_quant(apc_curve_lag5.iloc[-2][1:-1], quant0, signal_data_lag2_mode)
        lag2q = mfunc.find_quant(apc_curve_lag5.iloc[-1][1:-1], quant0, signal_data_lag1_mode)

        print("lag1q, lag2q", lag1q, lag2q)
        # Reminder: pulling directly from a list is a factor of 3 faster than doing 
        # spline everytime
            
        # calculate the 5 days average for closing price
        rollinglagq5day = np.average(lag5_price)         
                    
        # calculate the median of the apc for the last five days
        mode_apc_5days = np.median([max(apc_curve_lag5.iloc[-5][1:-1]),
                                          max(apc_curve_lag5.iloc[-4][1:-1]),
                                          max(apc_curve_lag5.iloc[-3][1:-1]),
                                          max(apc_curve_lag5.iloc[-2][1:-1]),
                                          max(apc_curve_lag5.iloc[-1][1:-1])])
        
        # "BUY" condition
        # (1) Two consecutive days of closing price lower than the signal median
        cond1_buy = (history_data_lag2_close < signal_data_lag2_mode)
        cond2_buy = (history_data_lag1_close < signal_data_lag1_mode)
        # (2) rolling 5 days average lower than the median apc 
        cond3_buy = rollinglagq5day < mode_apc_5days
        # (3) price at today's opening hour above the 0.1 quantile of today's apc
        cond4_buy = quant_330UKtime >= curve_today['0.1']
        
        # "SELL" condition
        # (1) Two consecutive days of closing price higher than the signal median
        cond1_sell = (history_data_lag2_close > signal_data_lag2_mode)
        cond2_sell = (history_data_lag1_close > signal_data_lag1_mode)    
        # (2) rolling 5 days average higher than the median apc 
        cond3_sell = rollinglagq5day > mode_apc_5days
        # (3) price at today's opening hour below the 0.9 quantile of today's apc
        cond4_sell = quant_330UKtime <= curve_today['0.9']   
        
        print("===================This is in the package")  
        print("cond1_buy", cond1_buy, history_data_lag2_close, signal_data_lag2_mode)
        print("cond2_buy", cond2_buy, history_data_lag1_close, signal_data_lag1_mode)
        print("cond3_buy", cond3_buy, rollinglagq5day,  mode_apc_5days)
        print("cond4_buy", cond4_buy, quant_330UKtime, curve_today['0.1'])
        print("====================")
        print("cond1_sell", cond1_sell, history_data_lag2_close, signal_data_lag2_mode)
        print("cond2_sell", cond2_sell, history_data_lag1_close, signal_data_lag1_mode)
        print("cond3_sell", cond3_sell, rollinglagq5day,  mode_apc_5days)
        print("cond4_sell", cond4_sell, quant_330UKtime, curve_today['0.1'])
        print("======================")

        # Find the boolean value of strategy conditions
        Buy_cond = cond1_buy and cond2_buy and cond3_buy and cond4_buy
        Sell_cond =  cond1_sell and cond2_sell and cond3_sell and cond4_sell
        
        Neutral_cond = not (Buy_cond ^ Sell_cond) # xnor gate
    
        # make direction dictionary
        direction_dict = {"Buy": Buy_cond, "Sell": Sell_cond, "Neutral": Neutral_cond}
        
        for i in direction_dict:
            if direction_dict[i] == True:
                direction = i
                
        return direction
    
    def gen_strategy_data(history_data_lag5, apc_curve_lag5, curve_today,
                          strategy_name="benchmark"):
        """
        A simple function to generate the relevant data from a given strategy 
        for backtesting.

        Parameters
        ----------
        history_data_lag5 : pandas dataframe table
            The last 5 days of historical data.
        apc_curve_lag5 : pandas dataframe table
            The last 5 days of APC data.
        curve_today : 1D pandas dataframe
            The APC curve of the date of interest.
        strategy_name : str, optional
            The relevant strategy name. The default is "benchmark".

        Returns
        -------
        data0 : list
            A list of relevant data.

        """
        quant0 = np.arange(0.0025, 0.9975, 0.0025)
        q_minus, q_plus = 0.4,0.6
        
        if strategy_name == "benchmark":
            quantiles_forwantedprices = [0.1, 0.4, 0.5, 0.6, 0.9] 
        elif strategy_name == "mode":
            quantiles_forwantedprices = [0.1, q_minus, 0.5, q_plus, 0.9] 

        # Here it get the probabilty at different x axis            
        wanted_quantiles = mfunc.generic_spline(
            quant0, curve_today.to_numpy()[1:-1])(quantiles_forwantedprices)
        
        history_data_lag2_close = history_data_lag5["Settle"].iloc[-2]
        history_data_lag1_close = history_data_lag5["Settle"].iloc[-1]   
        
        lag2q = mfunc.find_quant(curve_today[1:-1], quant0, history_data_lag2_close)  
        lag1q = mfunc.find_quant(curve_today[1:-1], quant0, history_data_lag1_close) 
        
        rollinglagq5day = np.average(history_data_lag5["Settle"].to_numpy())
        
        roll5q = mfunc.find_quant(curve_today[1:-1], quant0, rollinglagq5day) 
        
        data0 = [
            wanted_quantiles[0],
            wanted_quantiles[1],
            wanted_quantiles[2],
            wanted_quantiles[3],
            wanted_quantiles[4],
            lag1q, lag2q, roll5q
            ]            
        
        return data0
    
    def set_EES_APC(cond, curve_today, buy_cond=(0.4,0.6,0.1), 
                            sell_cond =(0.6,0.4,0.9)):
        """
        A generic method to set the entry, exit, and stop loss (ESS) prices 
        base on an APC. 
        
        Parameters
        ----------
        cond : str
            Only accept "Buy", "Sell", or "Neutral".
        curve_today : 1D pandas dataframe
            The APC for one single day.
        buy_cond : 3 elements tuple, optional
            The quantile for extracting the price of the APC for a "Buy" signal. 
            This has to be a 3-element tuple: 
                (entry quant, exit quant, stop loss quant)
                The default is (0.4,0.6,0.1).
        sell_cond : 3 elements tuple, optional
            The quantile for extracting the price of the APC for a "Buy" signal. 
            This has to be a 3-element tuple: 
                (entry quant, exit quant, stop loss quant)
                The default is (0.6,0.4,0.9).

        Returns
        -------
        entry_price : float
            entry_price.
        exit_price : float
            exit_price.
        stop_loss : float
            stop_loss.

        """
        quant0 = np.arange(0.0025, 0.9975, 0.0025)
        curve_today = CubicSpline(quant0, curve_today.to_numpy()[1:-1])
        
        if cond == "Buy":
            # (A) Entry region at price < APC p=0.4 and 
            entry_price = curve_today(buy_cond[0])
            # (B) Exit price
            exit_price = curve_today(buy_cond[1])
            # (C) Stop loss at APC p=0.1
            stop_loss = curve_today(buy_cond[2])

            
        elif cond == "Sell":
            # (A) Entry region at price > APC p=0.6 and 
            entry_price = curve_today(sell_cond[0])
            # (B) Exit price
            exit_price = curve_today(sell_cond[1])
            # (C) Stop loss at APC p=0.9
            stop_loss = curve_today(sell_cond[2])
            
        elif cond == "Neutral":
            # (A) Entry region at price > APC p=0.6 and 
            entry_price = "NA"
            # (B) Exit price
            exit_price = "NA"
            # (C) Stop loss at APC p=0.9
            stop_loss = "NA"
        else:
            raise Exception(
                'Unaccepted input, condition needs to be either Buy, \
                    Sell, or Neutral.')
            
        return entry_price, exit_price, stop_loss
    
