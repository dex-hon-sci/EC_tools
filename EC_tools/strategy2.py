#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul  4 04:59:37 2024

@author: dexter
"""
import numpy as np
from scipy.interpolate import CubicSpline
from typing import Protocol

import EC_tools.math_func as mfunc

__author__="Dexter S.-H. Hon"

class Strategy(Protocol):
    """
    A Strategy is defined by given specific inputs related to forecasting or 
    past price data or other indicators that out put a specific instructions 
    (e.g., Buy/Sell/Neutral or something more complex) for a back-testing system 
    or a live trading alogirthm to execute.
    
    The trading instructions in question does not contain information about 
    the style of trading (e.g., one entry per day, or more), It is solely 
    informational on where you should buy/sell.
    
    """
    def __init__(self):
        self._buy_cond_list = [False]
        self._sell_cond_list = [False]
        self._buy_cond = False
        self._sell_cond = False
        self._neutral_cond = False
        self._direction = 'Neutral'
        
    @property
    def buy_cond(self):
        """
        The overall boolean value of the Buy condition

        """
        return all(self._buy_cond_list)
    
    @property
    def sell_cond(self):
        """
        The overall boolean value of the Sell condition

        """
        return all(self._sell_cond_list)
    
    @property
    def neutral_cond(self):
        """
        The overall boolean value of the Neutral condition

        """
        self._neutral_cond = not (self.buy_cond ^ self.sell_cond)
        return self._neutral_cond
    
    @property
    def direction(self):
        # make direction dictionary
        direction_dict = {"Buy": self.buy_cond, "Sell": self.sell_cond, 
                          "Neutral": self.neutral_cond}
        
        for direction_str in direction_dict:
            if direction_dict[direction_str]:
                direction = direction_str
                
        return direction

    
    def apply_strategy(self, history_data_lag5, apc_curve_lag5, open_price):
        
        data = self.gen_data_2(history_data_lag5, apc_curve_lag5)
        
        self.run_cond(data, open_price)
        
        EES = self.set_EES()
        
        return
    
class MRStrategyArgus(Strategy):
    """
    Mean-Reversion Strategy based on Argus Possibility Curves. 
    This class allows one to 
    
    """
    def __init__(self, curve_today, 
                 quant_list = np.arange(0.0025, 0.9975, 0.0025)):
        
        super().__init__()
        
        self._curve_today = curve_today
        self._quant_list = quant_list
        self._curve_today_spline = mfunc.generic_spline(self._quant_list, 
                                                        self._curve_today)
        
        self._sub_buy_cond_dict = dict()
        self._sub_sell_cond_dict = dict()
        self.strategy_name = 'argus_exact'

# =============================================================================
#     def gen_data(self, history_data_lag5, apc_curve_lag5):
#                               
#         """
#         A method that generate all the data needed for the strategy. The ouput
#         of this functions contain all the quantity that will be and can be used 
#         in creating variation of this strategy.
#         
#         """
#         
#         lag5_price = history_data_lag5['Settle']
#         
#         
#         # Find quants for the closing price for the past five days
#         lag5close_q = mfunc.find_quant(apc_curve_lag5.iloc[-5].to_numpy()[1:-1], 
#                                        self._quant_list, lag5_price.iloc[-5])
#         lag4close_q = mfunc.find_quant(apc_curve_lag5.iloc[-4].to_numpy()[1:-1], 
#                                        self._quant_list, lag5_price.iloc[-4])
#         lag3close_q = mfunc.find_quant(apc_curve_lag5.iloc[-3].to_numpy()[1:-1], 
#                                        self._quant_list, lag5_price.iloc[-3])
#         lag2close_q = mfunc.find_quant(apc_curve_lag5.iloc[-2].to_numpy()[1:-1], 
#                                        self._quant_list, lag5_price.iloc[-2])  
#         lag1close_q = mfunc.find_quant(apc_curve_lag5.iloc[-1].to_numpy()[1:-1], 
#                                        self._quant_list, lag5_price.iloc[-1]) 
#         
#         rollingaverage5q = np.average([lag1close_q, lag2close_q, 
#                                        lag3close_q, lag4close_q, 
#                                        lag5close_q])
#         
#         data0 = [lag1close_q, lag2close_q, lag3close_q, lag4close_q, lag5close_q, 
#                  rollingaverage5q]    
#         
#         data1 = {'lag1close_q': lag1close_q, 'lag2close_q': lag2close_q, 
#                 'lag3close_q': lag3close_q, 'lag4close_q': lag4close_q, 
#                 'lag5close_q': lag5close_q, 'rollingaverage5q': rollingaverage5q}
#         
#         return data0
# =============================================================================
    
    def gen_data(self, history_data_lag, apc_curve_lag, 
                            price_proxy = 'Settle', qunatile = [0.25,0.4,0.6,0.75]):
                              
        """
        A method that generate all the data needed for the strategy. The ouput
        of this functions contain all the quantity that will be and can be used 
        in creating variation of this strategy.
        
        """
        
        lag_price = history_data_lag[price_proxy]
        
        
        lag_list = [mfunc.find_quant(apc_curve_lag.iloc[i].to_numpy()[1:-1], 
                                     self._quant_list, lag_price.iloc[i]) for 
                                    i, _ in enumerate(apc_curve_lag)]
        # Note that the list goes like this [lag1q,lag2q,...]
        
        # calculate the rolling average
        rollingaverage_q = np.average(lag_list)
        

        strategy_info = {'lag_list': lag_list, 'rollingaverage': rollingaverage_q}
        
        qunatile_info = self._curve_today_spline(qunatile)
                #[float(self._curve_today_spline(0.25)), 
                # float(self._curve_today_spline(0.4)), 
                # float(self._curve_today_spline(0.6)), 
                # float(self._curve_today_spline(0.75))]

        
        return strategy_info, qunatile_info
        
    
    def run_cond(self, data, open_price, total_lag_days = 2, 
                                 apc_mid_Q = 0.5, 
                                 apc_trade_Qrange=(0.4,0.6), 
                                 apc_trade_Qmargin = (0.1,0.9),
                                 apc_trade_Qlimit=(0.05,0.95)):
    

        #lag2close_q = data['lag_list'][1]
        #lag1close_q = data['lag_list'][0]
        rollingaverage_q = data['rollingaverage']

        lag_close_q_list = [data['lag_list'][i] for i in range(total_lag_days)]
        mid_Q_list = [apc_mid_Q for i in range(total_lag_days)]
        
        # "BUY" condition
        # (1) create a list of Boolean value for evaluating if the last two 
        # consecutive days of closing price lower than the signal median
        cond_buy_list_1 = list(map(lambda x, y: x < y, lag_close_q_list, mid_Q_list))
        # (2) rolling 5 days average lower than the median apc 
        cond_buy_list_2 = list(map(lambda x, y: x < y, rollingaverage_q, apc_mid_Q))
        # (3) price at today's opening hour above the 0.1 quantile of today's apc
        cond_buy_list_3 = [(open_price >= self._curve_today_spline([
                                                    apc_trade_Qlimit[0]])[0])]
        
        # "SELL" condition
        # (1) Two consecutive days of closing price higher than the signal median
        cond_sell_list_1 = list(map(lambda x, y: x > y, lag_close_q_list, mid_Q_list))
        # (2) rolling 5 days average higher than the median apc 
        cond_sell_list_2 = list(map(lambda x, y: x > y, rollingaverage_q, apc_mid_Q))
        # (3) price at today's opening hour below the 0.9 quantile of today's apc
        cond_sell_list_3 = [(open_price <= self._curve_today_spline([
                                                    apc_trade_Qlimit[1]])[0])]
        
        
        self._sub_buy_cond_dict = {'NCONS': cond_buy_list_1,	
                             'NROLL': cond_buy_list_2,
                             'OP_WITHIN': cond_buy_list_3}
        self._sub_sell_cond_dict = {'NCONS': cond_sell_list_1,	
                             'NROLL': cond_sell_list_2,
                             'OP_WITHIN': cond_sell_list_3}
    
        
        return self.direction
        
    
    def set_EES(self, cond, buy_range=(0.4,0.6,0.1), 
                            sell_range =(0.6,0.4,0.9)):
        
        
        if self.direction == "Buy":
            # (A) Entry region at price < APC p=0.4 and 
            entry_price = float(self._curve_today(buy_range[0]))
            # (B) Exit price
            exit_price = float(self._curve_today(buy_range[1]))
            # (C) Stop loss at APC p=0.1
            stop_loss = float(self._curve_today(buy_range[2]))

            
        elif self.direction == "Sell":
            # (A) Entry region at price > APC p=0.6 and 
            entry_price = float(self._curve_today(sell_range[0]))
            # (B) Exit price
            exit_price = float(self._curve_today(sell_range[1]))
            # (C) Stop loss at APC p=0.9
            stop_loss = float(self._curve_today(sell_range[2]))
            
        elif self.direction == "Neutral":
            entry_price = "NA"
            exit_price = "NA"
            stop_loss = "NA"
        else:
            raise Exception(
                'Unaccepted input, condition needs to be either Buy, \
                    Sell, or Neutral.')
            
        return entry_price, exit_price, stop_loss
    
