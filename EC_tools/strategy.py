#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul  4 04:59:37 2024

@author: dexter
"""
import numpy as np
from scipy.interpolate import CubicSpline
from typing import Protocol
from enum import Enum, auto

import EC_tools.math_func as mfunc

__author__="Dexter S.-H. Hon"

class SignalStatus(Enum):
    BUY = "Buy" # When the position is added but not filled
    SELL = "Sell" # When the position is executed
    NEUTRAL = "Neutral" # When the position is cancelled


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
        self._buy_cond = False
        self._sell_cond = False
        self._neutral_cond = True
        
        self.cond_dict = {"Buy": [False], 
                          "Sell": [False]}
        # make the default value of a strategy 'Neutral'
        self._direction = SignalStatus.NEUTRAL 
        
    @property
    def buy_cond(self):
        """
        The overall boolean value of the Buy condition

        """
        self._buy_cond = all(self.cond_dict['Buy'])
        return self._buy_cond
    
    @property
    def sell_cond(self):
        """
        The overall boolean value of the Sell condition

        """
        self._sell_cond = all(self.cond_dict['Sell'])
        return self._sell_cond
    
    @property
    def neutral_cond(self):
        """
        The overall boolean value of the Neutral condition

        """
        self._neutral_cond = not (self.buy_cond ^ self.sell_cond)
        return self._neutral_cond
    
    @property
    def direction(self):
        
        if self.buy_cond == True:
            self._direction = SignalStatus.BUY
        
        if self.sell_cond == True:
                self._direction = SignalStatus.SELL

        if self.neutral_cond == True:
            self._direction = SignalStatus.NEUTRAL

        return self._direction
        
    
class MRStrategyArgus(Strategy):
    """
    Mean-Reversion Strategy based on Argus Possibility Curves. 
    This class allows us to ... 
    
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
        self.sub_cond_dict = {'Buy':[], 'Sell':[], 'Neutral': []}

        self.strategy_name = 'argus_exact'

    def flatten_sub_cond_dict(self):
        # a method that turn a sub_cond_dict into a cond_dict assuming the 
        # subgroups are only one layer deep.
        
        for key in self.sub_cond_dict:
            lis = self.sub_cond_dict[key]
            flatList = sum(lis, [])
            self.cond_dict[key] = flatList
         
    
    def gen_data(self, history_data_lag, apc_curve_lag, 
                            price_proxy = 'Settle', 
                            qunatile = [0.25,0.4,0.6,0.75]):
                              
        """
        A method that generate all the data needed for the strategy. The ouput
        of this functions contain all the quantity that will be and can be used 
        in creating variation of this strategy.
        
        """
        lag_price = history_data_lag[price_proxy]
        
        
        lag_list = [mfunc.find_quant(apc_curve_lag.iloc[i].to_numpy()[1:-1], 
                                     self._quant_list, lag_price.iloc[i]) for 
                                    i in range(len(apc_curve_lag))]
        lag_list.reverse()
        # Note that the list goes like this [lag1q,lag2q,...]
        
        # calculate the rolling average
        rollingaverage_q = np.average(lag_list)
        

        strategy_info = {'lag_list': lag_list, 
                         'rollingaverage': rollingaverage_q}
        
        qunatile_info = list(self._curve_today_spline(qunatile))
        
        return strategy_info, qunatile_info
        
    
    def run_cond(self, data, open_price, 
                                 total_lag_days = 2, 
                                 apc_mid_Q = 0.5, 
                                 apc_trade_Qrange=(0.4,0.6), 
                                 apc_trade_Qmargin = (0.1,0.9),
                                 apc_trade_Qlimit=(0.05,0.95)):
    

        rollingaverage_q = data['rollingaverage']

        lag_close_q_list = [data['lag_list'][i] for i in range(total_lag_days)]
        mid_Q_list = [apc_mid_Q for i in range(total_lag_days)]
        
        # "BUY" condition
        # (1) create a list of Boolean value for evaluating if the last two 
        # consecutive days of closing price lower than the signal median
        cond_buy_list_1 = list(map(lambda x, y: x < y, lag_close_q_list, mid_Q_list))
        # (2) rolling 5 days average lower than the median apc 
        cond_buy_list_2 = [(rollingaverage_q < apc_mid_Q)]
        # (3) price at today's opening hour above the 0.1 quantile of today's apc
        #cond_buy_list_3 = [(open_price >= self._curve_today_spline([
        #                                            apc_trade_Qlimit[0]])[0])]
        
        # "SELL" condition
        # (1) Two consecutive days of closing price higher than the signal median
        cond_sell_list_1 = list(map(lambda x, y: x > y, lag_close_q_list, mid_Q_list))
        # (2) rolling 5 days average higher than the median apc 
        cond_sell_list_2 = [(rollingaverage_q > apc_mid_Q)]
        # (3) price at today's opening hour below the 0.9 quantile of today's apc
        #cond_sell_list_3 = [(open_price <= self._curve_today_spline([
        #                                            apc_trade_Qlimit[1]])[0])]
        
        # save the condtion boolean value to the sub-condition dictionary
        self._sub_buy_cond_dict = {'NCONS': [cond_buy_list_1],	
                             'NROLL': [cond_buy_list_2]}
                             #'OP_WITHIN': [cond_buy_list_3]}
        self._sub_sell_cond_dict = {'NCONS': [cond_sell_list_1],	
                             'NROLL': [cond_sell_list_2]}
                             #'OP_WITHIN': [cond_sell_list_3]}
        
        # Store all sub-conditions into 
        self.sub_cond_dict = {'Buy':[sum(self._sub_buy_cond_dict[key],[]) 
                                for key in self._sub_buy_cond_dict], 
                         'Sell':[sum(self._sub_sell_cond_dict[key],[]) 
                                 for key in self._sub_buy_cond_dict]}
        
        # flatten the sub-conditoion list and sotre them in the condition list
        self.flatten_sub_cond_dict()

        # Create the condtion info for bookkeeping
        NCONS,	NROLL = len(self._sub_buy_cond_dict['NCONS'][0]), \
                                        len(data['lag_list'])
                                        
        # Find the Boolean value for each buy conditions subgroup
        sub_buy_1 = all(self._sub_buy_cond_dict['NCONS'][0])
        sub_buy_2 = all(self._sub_buy_cond_dict['NROLL'][0])
        # Find the Boolean value for each Sell conditions subgroup
        sub_sell_1 = all(self._sub_sell_cond_dict['NCONS'][0])
        sub_sell_2 = all(self._sub_sell_cond_dict['NROLL'][0])
                
        # Construct condtion dictionaray for each condition
        cond_dict_1 = {'Buy': sub_buy_1, 'Sell': sub_sell_1, 
                       'Neutral': not(sub_buy_1 ^ sub_sell_1)}
        cond_dict_2 = {'Buy': sub_buy_2, 'Sell': sub_sell_2, 
                       'Neutral': not(sub_buy_1 ^ sub_sell_1)}
        
        # Degine the name for the Buy/Sell action for each condition subgroups
        Signal_NCONS  = [key for key in cond_dict_1 if cond_dict_1[key] == True][0]
        Signal_NROLL  = [key for key in cond_dict_2 if cond_dict_2[key] == True][0]

        # Put the condition info in a list
        cond_info = [NCONS,	NROLL, Signal_NCONS, Signal_NROLL]
        
        return self.direction, cond_info


    def set_EES(self, cond, buy_range=([0.25,0.4],[0.6,0.75],0.05), 
                            sell_range =([0.6,0.75],[0.25,0.4],0.95)):

        if self.direction == SignalStatus.BUY:
            # (A) Entry region at price < APC p=0.4 and 
            entry_price = [float(self._curve_today_spline(buy_range[0][0])), 
                           float(self._curve_today_spline(buy_range[0][1]))]
            # (B) Exit price
            exit_price = [float(self._curve_today_spline(buy_range[1][0])), 
                          float(self._curve_today_spline(buy_range[1][1]))] 
            # (C) Stop loss at APC p=0.1
            stop_loss = float(self._curve_today_spline(buy_range[2]))

            
        elif self.direction == SignalStatus.SELL:
            # (A) Entry region at price > APC p=0.6 and 
            entry_price = [float(self._curve_today_spline(sell_range[0][0])), 
                           float(self._curve_today_spline(sell_range[0][1]))]
            # (B) Exit price
            exit_price = [float(self._curve_today_spline(sell_range[1][0])), 
                          float(self._curve_today_spline(sell_range[1][1]))]
            # (C) Stop loss at APC p=0.9
            stop_loss = float(self._curve_today_spline(sell_range[2]))
            
        elif self.direction == SignalStatus.NEUTRAL:
            entry_price = ["NA", "NA"]
            exit_price = ["NA", "NA"]
            stop_loss = "NA"
        else:
            raise Exception(
                'Unaccepted input, condition needs to be either Buy, \
                    Sell, or Neutral.')
            
        return entry_price, exit_price, stop_loss
    
    def apply_strategy(self, history_data_lag5, apc_curve_lag5, open_price, 
                       qunatile = [0.25,0.4,0.6,0.75],
                        total_lag_days = 2, 
                        apc_mid_Q = 0.5, 
                        #apc_trade_Qrange=(0.4,0.6), 
                        #apc_trade_Qmargin = (0.1,0.9),
                        #apc_trade_Qlimit=(0.05,0.95)
                       buy_range=([0.25,0.4],[0.6,0.75],0.05), 
                       sell_range =([0.6,0.75],[0.25,0.4],0.95)):
        
        strategy_info, quantile_info = self.gen_data(history_data_lag5, apc_curve_lag5,
                                                     qunatile = [0.25,0.4,0.6,0.75])
        
        direction, cond_info = self.run_cond(strategy_info, open_price,
                                             total_lag_days = total_lag_days, 
                                             apc_mid_Q = apc_mid_Q)
                                             
                                             #apc_trade_Qrange=apc_trade_Qrange, 
                                             #apc_trade_Qmargin = apc_trade_Qmargin,
                                             #apc_trade_Qlimit=apc_trade_Qlimit)
        
        entry_price, exit_price, stop_loss = self.set_EES(self.direction, 
                                                          buy_range=buy_range, 
                                                          sell_range=sell_range)

        if direction == SignalStatus.BUY:
            entry_price_val, exit_price_val = entry_price[1], exit_price[0]
        elif direction == SignalStatus.SELL:
            entry_price_val, exit_price_val = entry_price[0], exit_price[1]
        elif direction == SignalStatus.NEUTRAL:
            entry_price_val, exit_price_val = entry_price[0], exit_price[0]
            
        # Bookkeeping area
        EES = [entry_price[0], entry_price[1], 
               exit_price[0], exit_price[1], 
               stop_loss]
        EES_val = [entry_price_val, exit_price_val, stop_loss]
        
        # Turn strategy_info from dict to list
        strategy_info_list = strategy_info['lag_list'] + [strategy_info['rollingaverage']]
        
        # put all the data in a singular list. This is to be added in the 
        # data list in the loop
        #print(EES+ cond_info, strategy_info_list, quantile_info, [self.strategy_name])
        #print(type(EES+ cond_info), type(strategy_info_list), type(quantile_info), type([self.strategy_name]))
        
        data =  EES + cond_info + strategy_info_list + \
                quantile_info + EES_val + [self.strategy_name]
        
        return {'data': data, 'direction': direction.value}
    
#class MRStrategyArgus(Strategy):
