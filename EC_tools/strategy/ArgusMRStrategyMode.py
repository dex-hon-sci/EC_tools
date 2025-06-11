#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 28 06:45:03 2025

@author: dexter
"""
import numpy as np

from EC_tools.utility import math_func as mfunc
from EC_tools.strategy import Strategy
from EC_tools.strategy.signal import SignalType
from crudeoil_future_const import APC_LENGTH

class ArgusMRStrategyMode(Strategy):
    
    def __init__(self, curve_today: np.ndarray, 
                 quant_list: np.ndarray = np.arange(0.0025, 0.9975, 0.0025)):
        
        super().__init__()
        
        self._curve_today = curve_today
        self._quant_list = quant_list
        self._curve_today_spline = mfunc.generic_spline(self._quant_list, 
                                                        self._curve_today,
                                                        method='cubic')
        self._curve_today_reverse_spline = mfunc.generic_spline(self._curve_today, 
                                                                self._quant_list, 
                                                                method='cubic')

        self._pdf_price, self._pdf = mfunc.cal_pdf(self._quant_list, 
                                                   self._curve_today)
        self._pdf_spline = mfunc.generic_spline(self._pdf_price, self._pdf)

        self._sub_buy_cond_dict = dict()
        self._sub_sell_cond_dict = dict()
        self.sub_cond_dict = {'Buy':[], 'Sell':[], 'Neutral': []}

        self.strategy_name = 'argus_exact_mode'
    
    @property
    def mode_price(self):

        return float(mfunc.find_pdf_val(self._pdf_price, self._pdf, func=max))
    
    def flatten_sub_cond_dict(self):
        """
        A method that turn a sub-condition-dictionary into a 
        condition-dictionary and pass it to the Strategy parent class.
        
        This function assume the sub_cond_dict is only one layer deep, i.e.
        a structure like this: {'Buy': [[...], [...], [...]], 'Sell':...}.
        
        Structure like this is not allowed:  
            {'Buy': [[...], [[...],[...]], [...]], 'Sell':...}.

        Returns
        -------
        None.

        """
        # a method that turn a sub_cond_dict into a cond_dict assuming the 
        # subgroups are only one layer deep.
        
        for key in self.sub_cond_dict:
            lis = self.sub_cond_dict[key]
            flatList = sum(lis, [])
            self.cond_dict[key] = flatList
    
    def gen_data(self, history_data_lag, apc_curve_lag, 
                            price_proxy = 'Settle', 
                            quantile_delta = [-0.1, 0.0, +0.1]):
        
        lag_price = history_data_lag[price_proxy]
        lag_list = [mfunc.find_quant(apc_curve_lag.iloc[i].to_numpy()[-1-APC_LENGTH:-1], 
                                     self._quant_list, lag_price.iloc[i]) for 
                                    i in range(len(apc_curve_lag))]
        lag_list.reverse()
        # Note that the list goes like this [lag1q,lag2q,...]
        # calculate the rolling average
        rollingaverage_q = np.average(lag_list)
        
        # turn the APC (cdf) to pdf in a list
        lag_pdf_list = [mfunc.cal_pdf(self._quant_list, 
                                      apc_curve_lag.iloc[i].to_numpy()[-1-APC_LENGTH:-1]) 
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
    
    def run_cond(self, data, #open_price_quant, 
                 total_lag_days = 2):
        
        rollingaverage_q = data['rollingaverage']
        lag_close_q_list = [data['lag_list'][i] for i in range(total_lag_days)]

        mode_Q_list = data['mode_Q_list']
        average_mode_Q = data['rollingaverage_mode']
        
        # "BUY" condition
        # (1) create a list of Boolean value for evaluating if the last two 
        # consecutive days of closing price lower than the signal median
        cond_buy_list_1 = list(map(lambda x, y: x < y, lag_close_q_list, mode_Q_list))
        # (2) rolling 5 days average lower than the median apc 
        cond_buy_list_2 = [(rollingaverage_q < average_mode_Q)]
        # (3) price at today's opening hour above the 0.1 quantile of today's apc
        #cond_buy_list_3 = [(open_price_quant >= 0.1)]
        
        # "SELL" condition
        # (1) Two consecutive days of closing price higher than the signal median
        cond_sell_list_1 = list(map(lambda x, y: x > y, lag_close_q_list, mode_Q_list))
        # (2) rolling 5 days average higher than the median apc 
        cond_sell_list_2 = [(rollingaverage_q > average_mode_Q)]
        # (3) price at today's opening hour below the 0.9 quantile of today's apc
        #cond_sell_list_3 = [(open_price_quant <= 0.9)]
        
        # save the condtion boolean value to the sub-condition dictionary
        self._sub_buy_cond_dict = {'NCONS': [cond_buy_list_1],	
                             'NROLL': [cond_buy_list_2],}
        #                     'OP_WITHIN': [cond_buy_list_3]}
        self._sub_sell_cond_dict = {'NCONS': [cond_sell_list_1],	
                             'NROLL': [cond_sell_list_2],}
        #                     'OP_WITHIN': [cond_sell_list_3]}
                             
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

    
    def set_EES(self, buy_range=(-0.1, 0.1, -0.45), 
                      sell_range =(0.1, -0.1, +0.45)):
        
        mode_quant = self._curve_today_reverse_spline(self.mode_price)
        
        if self.direction == SignalType.BUY:
            # (A) Entry region at price < APC p=0.4 and 
            entry_price = float(self._curve_today_spline(mode_quant+ 
                                                          buy_range[0]))
            # (B) Exit price
            exit_price = float(self._curve_today_spline(mode_quant+
                                                         buy_range[1]))
            # (C) Stop loss at APC p=0.1
            stop_loss = float(self._curve_today_spline(mode_quant+
                                                       buy_range[2]))

            
        elif self.direction == SignalType.SELL:
            # (A) Entry region at price > APC p=0.6 and 
            entry_price = float(self._curve_today_spline(mode_quant+
                                                          sell_range[0]))
            # (B) Exit price
            exit_price = float(self._curve_today_spline(mode_quant+
                                                         sell_range[1]))
            # (C) Stop loss at APC p=0.9
            stop_loss = float(self._curve_today_spline(mode_quant+
                                                       sell_range[2]))
            
        elif self.direction == SignalType.NEUTRAL:
            entry_price = "NA"
            exit_price = "NA"
            stop_loss = "NA"
        else:
            raise Exception(
                'Unaccepted input, condition needs to be either Buy, \
                    Sell, or Neutral.')
            
        return entry_price, exit_price, stop_loss
    
    def apply_strategy(self, 
                       history_data_lag, 
                       apc_curve_lag, 
                       #open_price, 
                       quantile: list = [-0.1, 0.0, +0.1],
                       total_lag_days: int = 2, 
                       buy_range: tuple = (-0.1, 0.1, -0.45), 
                       sell_range: tuple = (0.1, -0.1, +0.45)):

        strategy_info, quantile_info = self.gen_data(history_data_lag, apc_curve_lag,
                                                     quantile_delta=quantile)
        
        #open_price_quant = mfunc.find_quant(self._curve_today,
        #                                    self._quant_list, open_price)

        direction, cond_info = self.run_cond(strategy_info, #open_price_quant,
                                             total_lag_days = total_lag_days)
                                             
        
        entry_price, exit_price, stop_loss = self.set_EES(buy_range=buy_range, 
                                                          sell_range=sell_range)

        if direction == SignalType.BUY:
            entry_price_val, exit_price_val = entry_price, exit_price
        elif direction == SignalType.SELL:
            entry_price_val, exit_price_val = entry_price, exit_price
        elif direction == SignalType.NEUTRAL:
            entry_price_val, exit_price_val = entry_price, exit_price
            
        # Bookkeeping area
        EES = [entry_price, entry_price, 
               exit_price, exit_price, 
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
