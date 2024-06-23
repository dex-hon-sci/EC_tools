#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr  5 03:19:59 2024

@author: dexter

This is a list of strategy that can be implemented in other scripts.
"""
import numpy as np
from scipy.interpolate import CubicSpline
from typing import Protocol

import EC_tools.math_func as mfunc

# round trip fee 15 dollars
__author__="Dexter S.-H. Hon"

class Strategy(Protocol):
# make protocol class
# condition array all([cond_1,cond_2]) == True then Buy
    def __init__(self):
        self._buy_cond_list = []
        self._sell_cond_list = []
        self._direction = None
        return None

    def set_EES():

        return
    
    def gen_strategy_data():
        return 
    
    # strategy cal_history -> direction, gen_data -> data, set_price -> EES

class MRStrategy(object):
    """
    Mean-Reversion Strategy. 
    
    """
    def __init__(self):
        self._buy_cond_list = []
        self._sell_cond_list = []
        self._buy_cond = False
        self._sell_cond = False
        self._direction = 'Neutral'
    
    # make a list of lambda functions for the multiple conditions 
    # make a set of numbers for different EES (or EES range) 
    # also make them into a list or data frame to allow multiple EES in the same day.
    
    @property
    def buy_cond(self):
        if all(self._buy_cond_list) == True:
            self._buy_cond = True
        return self._buy_cond
    
    @property
    def sell_cond(self):
        if all(self._sell_cond_list) == True:
            self._sell_cond = True
        return self._sell_cond
    
    @property
    def neutral_cond(self):
        neutral_cond = not (self._buy_cond ^ self._sell_cond)
        return neutral_cond
    
    @property
    def direction(self):
        # make direction dictionary
        direction_dict = {"Buy": self.buy_cond, "Sell": self.sell_cond, 
                          "Neutral": self.neutral_cond}
        
        for direction_str in direction_dict:
            if direction_dict[direction_str]:
                self._direction = direction_str
                
        return self._direction

    def argus_benchmark_strategy(self, open_price, history_data_lag5, apc_curve_lag5,
                                     curve_today, apc_mid_Q = 0.5, 
                                     apc_trade_Qrange=(0.4,0.6), 
                                     apc_trade_Qlimit=(0.1,0.9)):
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
        curve_today : dataframe
            The APC curve of the date of interest.

        Returns
        -------
        direction : str
            "Buy/Sell" signal.
            
        """
        
        # inputs
        lag5_price = history_data_lag5['Settle']
        
        # spline the APCs
        quant_list = np.array(list(map(float, apc_curve_lag5.columns.values[1:-1])))
        apc_curve_lag5_spline = [mfunc.generic_spline(quant_list, 
                                    apc_curve_lag5.iloc[i][1:-1].to_numpy()) 
                                  for i in range(len(apc_curve_lag5))]
        
        curve_today_spline = mfunc.generic_spline(quant_list, 
                                    curve_today.iloc[0][1:-1].to_numpy())
        
        # define the lag 2 days settlement prices
        history_data_lag2_close = lag5_price.iloc[-2]
        history_data_lag1_close = lag5_price.iloc[-1]
        
        # The APC two days (lag2) before this date
        signal_data_lag2_median =  apc_curve_lag5_spline[-2]([apc_mid_Q])[0]
        # The APC one day1 (lag1) before this date
        signal_data_lag1_median =  apc_curve_lag5_spline[-1]([apc_mid_Q])[0]
        
        # Reminder: pulling directly from a list is a factor of 3 faster than   
        # doing spline everytime. But doing spline is more flexible
        
        # calculate the 5 days average for closing price
        rollinglagq5day = np.average(lag5_price)         
        median_apc_5days = np.median([spline([apc_mid_Q])[0] for spline in apc_curve_lag5_spline])

        # "BUY" condition
        # (1) Two consecutive days of closing price lower than the signal median
        cond1_buy = (history_data_lag2_close < signal_data_lag2_median)
        cond2_buy = (history_data_lag1_close < signal_data_lag1_median)
        # (2) rolling 5 days average lower than the median apc 
        cond3_buy = rollinglagq5day < median_apc_5days
        # (3) price at today's opening hour above the 0.1 quantile of today's apc
        cond4_buy = open_price >= curve_today_spline([apc_trade_Qlimit[0]])[0] #float(curve_today['0.1'].iloc[0])
    
        # "SELL" condition
        # (1) Two consecutive days of closing price higher than the signal median
        cond1_sell = (history_data_lag2_close > signal_data_lag2_median)
        cond2_sell = (history_data_lag1_close > signal_data_lag1_median)    
        # (2) rolling 5 days average higher than the median apc 
        cond3_sell = rollinglagq5day > median_apc_5days
        # (3) price at today's opening hour below the 0.9 quantile of today's apc
        cond4_sell = open_price <= curve_today_spline([apc_trade_Qlimit[1]])[0] #float(curve_today['0.9'].iloc[0])
        
        self._buy_cond_list = [cond1_buy, cond2_buy, cond3_buy, cond4_buy]
        self._sell_cond_list = [cond1_sell, cond2_sell, cond3_sell, cond4_sell]

        return self.direction

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

        #print("lag1q, lag2q", lag1q, lag2q)
        
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
            quant0, curve_today)(quantiles_forwantedprices)
        
        history_data_lag2_close = history_data_lag5["Settle"].iloc[-2]
        history_data_lag1_close = history_data_lag5["Settle"].iloc[-1]   
        
        lag2q = mfunc.find_quant(curve_today, quant0, history_data_lag2_close)  
        lag1q = mfunc.find_quant(curve_today, quant0, history_data_lag1_close) 
        
        rollinglagq5day = np.average(history_data_lag5["Settle"].to_numpy())
        
        roll5q = mfunc.find_quant(curve_today, quant0, rollinglagq5day) 
        
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
        base on a cumulative probability distribution. 
        
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
        curve_today = CubicSpline(quant0, curve_today)
        
        if cond == "Buy":
            # (A) Entry region at price < APC p=0.4 and 
            entry_price = float(curve_today(buy_cond[0]))
            # (B) Exit price
            exit_price = float(curve_today(buy_cond[1]))
            # (C) Stop loss at APC p=0.1
            stop_loss = float(curve_today(buy_cond[2]))

            
        elif cond == "Sell":
            # (A) Entry region at price > APC p=0.6 and 
            entry_price = float(curve_today(sell_cond[0]))
            # (B) Exit price
            exit_price = float(curve_today(sell_cond[1]))
            # (C) Stop loss at APC p=0.9
            stop_loss = float(curve_today(sell_cond[2]))
            
        elif cond == "Neutral":
            entry_price = "NA"
            exit_price = "NA"
            stop_loss = "NA"
        else:
            raise Exception(
                'Unaccepted input, condition needs to be either Buy, \
                    Sell, or Neutral.')
            
        return entry_price, exit_price, stop_loss
    
    
MR_STRATEGIES = {'benchmark': MRStrategy.argus_benchmark_strategy,
                      'mode': MRStrategy.argus_benchmark_mode}




def apply_strategy(strategy_name:str):
     return MR_STRATEGIES[strategy_name]