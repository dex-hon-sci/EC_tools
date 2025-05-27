#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 23 14:13:41 2025

@author: dexter
"""

import numpy as np
import pandas as pd

import EC_tools.utility.math_func as mfunc
from EC_tools.strategy import Strategy
from EC_tools.strategy.signal import SignalType
from EC_tools.base.read import find_crossover

APC_LENGTH = len(np.arange(0.0025, 0.9975, 0.0025))

argus_tailstrangle_format = ['Date', 'Price_Code', 'Direction', 'Commodity_name',
                            'Contract_Month','Timezone', 
                            'Valid_From_localtz_timestr', 'Valid_To_localtz_timestr', 
                            'CONS',	'Signal_CONS',	
                            'Q0.05', 'Q0.1','Q0.25', 'Q0.4', 'Q0.5', 
                            'Q0.6', 'Q0.75', 'Q0.9', 'Q0.95',
                            'Entry_Price', 'Exit_Price', 'StopLoss_Price',
                            'strategy_name']

class ArgusTailStrangleStrategy(Strategy):
    """
    """
    def __init__(self, 
                 curve_today= np.arange(0.0025, 0.9975, 0.0025), 
                 quant_list = np.arange(0.0025, 0.9975, 0.0025)):
        
        super().__init__()
        
        self._curve_today = curve_today
        self._quant_list = quant_list
        self._curve_today_spline = mfunc.generic_spline(self._quant_list, 
                                                        self._curve_today)
        
        self._sub_buy_cond_dict = dict()
        self._sub_sell_cond_dict = dict()
        self.sub_cond_dict = {'Buy':[], 'Sell':[], 'Neutral': []}

        self.strategy_name = 'argus_tailstrangle'
        
    def flatten_sub_cond_dict(self) -> None:
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
         
    
    def gen_data(self, 
                 historic_intraday_data: pd.DataFrame, 
                 price_proxy: str = 'Settle', 
                 quantile: list = [0.25,0.4,0.6,0.75])-> tuple[list|list]:
        
        price_data = historic_intraday_data[price_proxy].to_list()
        
        qunatile_info = list(self._curve_today_spline(quantile))
        
        return price_data, qunatile_info

    
    def run_cond(self, 
                 price_data: list[float], 
                 breakout_quant: dict[str|float] = \
                                 {'Buy': 0.95, 'Sell':0.05}): 
        #print(self._curve_today_spline(breakout_quant['Buy']))
        #print('length',len(price_data),self._curve_today_spline(
        #                                    breakout_quant['Buy']),
        #    type(self._curve_today_spline(float(breakout_quant['Buy']))),
        #    type(price_data))
        #print(breakout_quant['Buy'], breakout_quant['Sell'])
        
        threshold_low = self._curve_today_spline(float(breakout_quant['Sell']))
        threshold_high = self._curve_today_spline(float(breakout_quant['Buy']))
        
        #print(type(threshold_low), type(threshold_high), threshold_low, threshold_high)
        
        lower_breach_index = find_crossover(price_data, float(threshold_low))
        higher_breach_index = find_crossover(price_data, float(threshold_high))

        # Run conditions to determine direction
        cond_buy_list_1 = [(len(higher_breach_index['all'][0]) > 0)]
        cond_sell_list_1 = [(len(lower_breach_index['all'][0]) > 0)]
        
        print(len(higher_breach_index['all'][0]), 
              len(lower_breach_index['all'][0]))
        print(higher_breach_index, lower_breach_index)
        print(cond_buy_list_1, cond_sell_list_1)
        
        # save the condtion boolean value to the sub-condition dictionary
        self._sub_buy_cond_dict = {'CONS': [cond_buy_list_1]}
        self._sub_sell_cond_dict = {'CONS': [cond_sell_list_1]}
        
        # Store all sub-conditions 
        self.sub_cond_dict = {'Buy':[sum(self._sub_buy_cond_dict[key],[]) 
                                for key in self._sub_buy_cond_dict], 
                              'Sell':[sum(self._sub_sell_cond_dict[key],[]) 
                                 for key in self._sub_sell_cond_dict]}
        
        # flatten the sub-conditoion list and sotre them in the condition list
        self.flatten_sub_cond_dict()

        # Create the condtion info for bookkeeping
        CONS = len(self._sub_buy_cond_dict['CONS'][0])
                                        
        # Find the Boolean value for each buy conditions subgroup
        sub_buy_1 = all(self._sub_buy_cond_dict['CONS'][0])
        # Find the Boolean value for each Sell conditions subgroup
        sub_sell_1 = all(self._sub_sell_cond_dict['CONS'][0])
                
        sub_neutral_1 = all([True if not (sub_buy_1 or sub_sell_1) else False])
        # Construct condtion dictionaray for each condition
        cond_dict_1 = {'Buy': sub_buy_1, 'Sell': sub_sell_1, 
                       'Neutral':  sub_neutral_1}
        
        
        #print('cond_dict_1', cond_dict_1)
        # Degine the name for the Buy/Sell action for each condition subgroups
        Signal_BUYCONS  = ['Buy' if cond_dict_1['Buy'] == True else 'NA'][0]
        Signal_SELLCONS  = ['Sell' if cond_dict_1['Sell'] == True else 'NA'][0]
        Signal_NEUTRALCONS  = ['Neutral' if cond_dict_1['Neutral'] == True else 'NA'][0]

        if Signal_BUYCONS == 'Buy' and Signal_SELLCONS != 'Sell':
            Signal_CONS = Signal_BUYCONS
        elif Signal_BUYCONS != 'Buy' and Signal_SELLCONS == 'Sell':
            Signal_CONS = Signal_SELLCONS
        elif Signal_BUYCONS == 'Buy' and Signal_SELLCONS == 'Sell':
            Signal_CONS = 'Both'
        else:
            Signal_CONS = Signal_NEUTRALCONS
            
        # Put the condition info in a list
        cond_info = [CONS, Signal_CONS]
        print('Direction', self.direction)
        return self.direction, cond_info
    
    def set_EES(self, 
                buy_range: tuple = (0.95,1.0,0.9), 
                sell_range: tuple = (0.05,0.0,0.1)):
        # set EES prices
        match self.direction:
            case SignalType.BUY:
                # (A) Entry price
                entry_price = float(self._curve_today_spline(buy_range[0]))
                # (B) Exit price
                exit_price = float(self._curve_today_spline(buy_range[1]))
                # (C) Stop loss at APC p=0.1
                stop_loss = float(self._curve_today_spline(buy_range[2]))
                print("Buy Direction!")
                print("entry:",buy_range[0], entry_price)
                print("exit:",buy_range[1], exit_price)
                print("stop:",buy_range[2], stop_loss)
                
            case SignalType.SELL:
                # (A) Entry price
                entry_price = float(self._curve_today_spline(sell_range[0]))
                # (B) Exit price
                exit_price = float(self._curve_today_spline(sell_range[1]))
                # (C) Stop loss at APC p=0.9
                stop_loss = float(self._curve_today_spline(sell_range[2]))
                print("Sell Direction!")
                print("entry:",sell_range[0], entry_price)
                print("exit:",sell_range[1], exit_price)
                print("stop:",sell_range[2], stop_loss)
            
            case SignalType.NEUTRAL:
                entry_price = "NA"
                exit_price = "NA"
                stop_loss = "NA"
                print("Neutral Direction!")
                print("entry:",entry_price)
                print("exit:",exit_price)
                print("stop:",stop_loss)
            case _:
                raise Exception(
                'Unaccepted input, condition needs to be either Buy, \
                    Sell, or Neutral.')
            
        return entry_price, exit_price, stop_loss

    
    def apply_strategy(self, 
                       history_intraday: pd.DataFrame, 
                       buy_range: tuple[float] = (0.95,1.0,0.9), 
                       sell_range: tuple[float] = (0.05,0.0,0.1),
                       quantile: list[float] = [0.25,0.4,0.6,0.75],
                       breakout_quant: dict[str|float] = {'Buy':0.95, 'Sell':0.05}):
                    
        price_data, quantile_info = self.gen_data(history_intraday,
                                                  quantile = quantile)
        
        direction, cond_info = self.run_cond(price_data,
                                             breakout_quant = breakout_quant)
                                             
        
        entry_price, exit_price, stop_loss = self.set_EES(buy_range=buy_range, 
                                                          sell_range=sell_range)


        # Bookkeeping area
        EES = [entry_price, exit_price, stop_loss]
        EES_val = [entry_price, exit_price, stop_loss]
        
        
        # put all the data in a singular list. This is to be added in the 
        # data list in the loop
        #print(EES+ cond_info, strategy_info_list, quantile_info, [self.strategy_name])
        #print(type(EES+ cond_info), type(strategy_info_list), type(quantile_info), type([self.strategy_name]))
        
        data =  cond_info + quantile_info + EES_val + [self.strategy_name]
        
        return {'data': data, 'direction': direction.value}

