#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul  4 04:59:37 2024

@author: Dexter S.-H. Hon

The Strategy module contains the parent class for all strategy to be applied in 
signal generation. 

"""
import numpy as np
import pandas as pd

from typing import Protocol
from numpy.typing import NDArray

from enum import Enum, auto

import EC_tools.math_func as mfunc

__all__ = ["SignalStatus", "Strategy",
           "ArgusMRStrategy","ArgusMRStrategyMode",
           "ArgusMonthlyStrategy"]
__author__="Dexter S.-H. Hon"

APC_LENGTH = len(np.arange(0.0025, 0.9975, 0.0025))

class SignalStatus(Enum):
    """
    A simple class that contains the avaliable status for signals.
    
    """
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
    
    
class ArgusMRStrategy(Strategy):
    """
    Mean-Reversion Strategy based on Argus Possibility Curves. 
    This class allows us to ... 
    
    
    The Strategy condition is described in the run_cond method.
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

        self.strategy_name = 'argus_exact'

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
                 history_data_lag: list, 
                 apc_curve_lag: list, 
                 price_proxy: str = 'Settle', 
                 quantile: list = [0.25,0.4,0.6,0.75]):
        """
        A method that generate all the data needed for the strategy. The ouput
        of this functions contain all the quantity that will be and can be used 
        in creating variation of this strategy.
        

        Parameters
        ----------
        history_data_lag : list
            The history data of the lag days.
        apc_curve_lag : list
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
                              
        lag_price = history_data_lag[price_proxy]
        
        lag_list = [mfunc.find_quant(apc_curve_lag.iloc[i].to_numpy()[-1-APC_LENGTH:-1], 
                                     self._quant_list, lag_price.iloc[i]) for 
                                    i in range(len(apc_curve_lag))]
        lag_list.reverse()
        # Note that the list goes like this [lag1q,lag2q,...]
        
        # calculate the rolling average
        rollingaverage_q = np.average(lag_list)
        

        strategy_info = {'lag_list': lag_list, 
                         'rollingaverage': rollingaverage_q}
        
        qunatile_info = list(self._curve_today_spline(quantile))
        
        return strategy_info, qunatile_info
        
    
    def run_cond(self, data: dict, 
                 open_price: float, 
                 total_lag_days: int = 2, 
                 apc_mid_Q: float = 0.5): 
        """
        A method that run the condition elvaluation of this strategy.

        If the settlement price of the past two days is less (or more) than the 
        apc_mid_Q quantile in their respective days of APC, plus the rolling 
        average for the past five days settlement price qunatile being lower 
        (or higher) than the apc_mid_Q, we deem that day to be a "Buy" 
        (or "Sell") day.
        
        Parameters
        ----------
        data : dict
            strategy_info from gen_data.
        open_price : float
            The value of the open price.
        total_lag_days : int, optional
            The total number of lag days. The default is 2.
        apc_mid_Q : float, optional
            The middle quantile of an APC. The default is 0.5.
        apc_trade_Qrange : tuple, optional
            The trading quantile range. The default is (0.4,0.6).
        apc_trade_Qmargin : TYPE, optional
            The trading margin quantile range. The default is (0.1,0.9).
        apc_trade_Qlimit : TYPE, optional
            The limit range for trading. This is the stoploss quantile
            The default is (0.05,0.95).

        Returns
        -------
        self.direction
            The trading direction of the day.
        cond_info : list
            A list of condiions info for the user.
            For this strategy, the format is the following:
                [NCONS,	NROLL, Signal_NCONS, Signal_NROLL]
            Where NCONS is the number of lag days, NROLL is the number of 
            lag days used to calculate the rollingaverage, Signal_NCONS is 
            the trading signal using solely NCONS, and Signal_NROLL is the 
            trading signal using solely NROLL.

        """
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


    def set_EES(self, 
                buy_range: tuple = ([0.25,0.4],[0.6,0.75],0.05), 
                sell_range: tuple = ([0.6,0.75],[0.25,0.4],0.95)):
        """
        A method the set the Entry, Exit, Stop loss prices.
        This method read-in the direction attribute of the strategy and 
        decide which set of EES value to be set.
        
        Parameters
        ----------
        buy_range : tuple, optional
            A tuple that contain the desired quantile value range for buy action. 
            The format should be the following:
                ([lower_limit_entry, upper_limit_entry], 
                 [lower_limit_exit, upper_exit], stop_loss)
            The default is ([0.25,0.4],[0.6,0.75],0.05).
        sell_range : tuple, optional
            A tuple that contain the desired quantile value range for sell action. 
            The format should be the following:
                ([lower_limit_entry, upper_limit_entry], 
                 [lower_limit_exit, upper_exit], stop_loss)
            The default is ([0.6,0.75],[0.25,0.4],0.95).

        Raises
        ------
        Exception
            For invalid direction. It has to conform to the StrategyStatus
            Attributes.

        Returns
        -------
        entry_price : list
            A list contain the price caculated by the APC given the buy_range
            input.
        exit_price : list
            A list contain the price caculated by the APC given the sell_range
            input.
        stop_loss : float
            A price caculated by the APC given the stop_loss
            input.

        """

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
    
    def apply_strategy(self, 
                       history_data_lag: pd.DataFrame, 
                       apc_curve_lag: pd.DataFrame, 
                       open_price: float, 
                       quantile: list[float] = [0.25,0.4,0.6,0.75],
                       total_lag_days: int = 2, 
                       apc_mid_Q: float = 0.5, 
                       buy_range: tuple[list|tuple,float] = 
                                   ([0.25,0.4],[0.6,0.75],0.05), 
                       sell_range: tuple[list|tuple,float] = 
                                   ([0.6,0.75],[0.25,0.4],0.95)):
        """
        A method to apply the strategy.

        Parameters
        ----------
        history_data_lag : DataFrame
            The history data of the lag days.
        apc_curve_lag : DataFrame
            The APC curve of the lag days.
        open_price : float
            The opening price of the day.
        qunatile : list, optional
            A list of prices calculating using qunatile input into the APC
            of the date of interest. The default is [0.25,0.4,0.6,0.75].
        total_lag_days : int, optional
            The total number of lag days. The default is 2.
        apc_mid_Q : float, optional
            The middle quantile value. The default is 0.5.                   
        buy_range: tuple, optional
            A tuple that contain the desired quantile value range for buy action. 
            The default is ([0.25,0.4],[0.6,0.75],0.05).
        sell_range : tuple, optional
            A tuple that contain the desired quantile value range for sell action. 
            The default is ([0.6,0.75],[0.25,0.4],0.95).

        Returns
        -------
        dict
            A dictionary that contains the strategy data from the process.
            'data' contains EES value, cond_info, lag_list, rollingaverage,
            quantile_info, EES value (not range), and the strategy name

            'direction' contains the string of the trading direction (strategy
                        status).
        """
        
        strategy_info, quantile_info = self.gen_data(history_data_lag, apc_curve_lag,
                                                     quantile = quantile)
        
        direction, cond_info = self.run_cond(strategy_info, open_price,
                                             total_lag_days = total_lag_days, 
                                             apc_mid_Q = apc_mid_Q)
                                             
        
        entry_price, exit_price, stop_loss = self.set_EES(buy_range=buy_range, 
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
    

class ArgusMRStrategyMode(Strategy):
    
    def __init__(self, curve_today: NDArray, 
                         quant_list: NDArray = np.arange(0.0025, 0.9975, 0.0025)):
        
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
    
    def run_cond(self, data, open_price_quant, total_lag_days = 2):
        
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
        cond_buy_list_3 = [(open_price_quant >= 0.1)]
        
        # "SELL" condition
        # (1) Two consecutive days of closing price higher than the signal median
        cond_sell_list_1 = list(map(lambda x, y: x > y, lag_close_q_list, mode_Q_list))
        # (2) rolling 5 days average higher than the median apc 
        cond_sell_list_2 = [(rollingaverage_q > average_mode_Q)]
        # (3) price at today's opening hour below the 0.9 quantile of today's apc
        cond_sell_list_3 = [(open_price_quant <= 0.9)]
        
        # save the condtion boolean value to the sub-condition dictionary
        self._sub_buy_cond_dict = {'NCONS': [cond_buy_list_1],	
                             'NROLL': [cond_buy_list_2],
                             'OP_WITHIN': [cond_buy_list_3]}
        self._sub_sell_cond_dict = {'NCONS': [cond_sell_list_1],	
                             'NROLL': [cond_sell_list_2],
                             'OP_WITHIN': [cond_sell_list_3]}
                             
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
        
        if self.direction == SignalStatus.BUY:
            # (A) Entry region at price < APC p=0.4 and 
            entry_price = float(self._curve_today_spline(mode_quant+ 
                                                          buy_range[0]))
            # (B) Exit price
            exit_price = float(self._curve_today_spline(mode_quant+
                                                         buy_range[1]))
            # (C) Stop loss at APC p=0.1
            stop_loss = float(self._curve_today_spline(mode_quant+
                                                       buy_range[2]))

            
        elif self.direction == SignalStatus.SELL:
            # (A) Entry region at price > APC p=0.6 and 
            entry_price = float(self._curve_today_spline(mode_quant+
                                                          sell_range[0]))
            # (B) Exit price
            exit_price = float(self._curve_today_spline(mode_quant+
                                                         sell_range[1]))
            # (C) Stop loss at APC p=0.9
            stop_loss = float(self._curve_today_spline(mode_quant+
                                                       sell_range[2]))
            
        elif self.direction == SignalStatus.NEUTRAL:
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
                       open_price, 
                       quantile: list = [-0.1, 0.0, +0.1],
                       total_lag_days: int = 2, 
                       buy_range: tuple = (-0.1, 0.1, -0.45), 
                       sell_range: tuple = (0.1, -0.1, +0.45)):

        strategy_info, quantile_info = self.gen_data(history_data_lag, apc_curve_lag,
                                                     quantile_delta=quantile)
        
        open_price_quant = mfunc.find_quant(self._curve_today,
                                            self._quant_list, open_price)

        direction, cond_info = self.run_cond(strategy_info, open_price_quant,
                                             total_lag_days = total_lag_days)
                                             
        
        entry_price, exit_price, stop_loss = self.set_EES(buy_range=buy_range, 
                                                          sell_range=sell_range)

        if direction == SignalStatus.BUY:
            entry_price_val, exit_price_val = entry_price, exit_price
        elif direction == SignalStatus.SELL:
            entry_price_val, exit_price_val = entry_price, exit_price
        elif direction == SignalStatus.NEUTRAL:
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


class ArgusMRStrategy_22(Strategy):
    """
    Mean-Reversion Strategy based on Argus Possibility Curves. 
    This class allows us to ... 
    
    
    The Strategy condition is described in the run_cond method.
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

        self.strategy_name = 'argus_exact'

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
                 history_data_lag: list, 
                 apc_curve_lag: list, 
                 price_proxy: str = 'Settle', 
                 qunatile: list = [0.25,0.4,0.6,0.75]):
        """
        A method that generate all the data needed for the strategy. The ouput
        of this functions contain all the quantity that will be and can be used 
        in creating variation of this strategy.
        

        Parameters
        ----------
        history_data_lag : list
            The history data of the lag days.
        apc_curve_lag : list
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
                              
        lag_price = history_data_lag[price_proxy]
        
        lag_list = [mfunc.find_quant(apc_curve_lag.iloc[i].to_numpy()[-1-APC_LENGTH:-1], 
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
        
    
    def run_cond(self, data: dict, 
                 open_price: float, 
                 total_lag_days: int = 2, 
                 apc_mid_Q: float = 0.5): 
        """
        A method that run the condition elvaluation of this strategy.

        If the settlement price of the past two days is less (or more) than the 
        apc_mid_Q quantile in their respective days of APC, plus the rolling 
        average for the past five days settlement price qunatile being lower 
        (or higher) than the apc_mid_Q, we deem that day to be a "Buy" 
        (or "Sell") day.
        
        Parameters
        ----------
        data : dict
            strategy_info from gen_data.
        open_price : float
            The APC quantile value of the open price.
        total_lag_days : int, optional
            The total number of lag days. The default is 2.
        apc_mid_Q : float, optional
            The middle quantile of an APC. The default is 0.5.
        apc_trade_Qrange : tuple, optional
            The trading quantile range. The default is (0.4,0.6).
        apc_trade_Qmargin : TYPE, optional
            The trading margin quantile range. The default is (0.1,0.9).
        apc_trade_Qlimit : TYPE, optional
            The limit range for trading. This is the stoploss quantile
            The default is (0.05,0.95).

        Returns
        -------
        self.direction
            The trading direction of the day.
        cond_info : list
            A list of condiions info for the user.
            For this strategy, the format is the following:
                [NCONS,	NROLL, Signal_NCONS, Signal_NROLL]
            Where NCONS is the number of lag days, NROLL is the number of 
            lag days used to calculate the rollingaverage, Signal_NCONS is 
            the trading signal using solely NCONS, and Signal_NROLL is the 
            trading signal using solely NROLL.

        """
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
        cond_buy_list_3 = [(open_price >= apc_mid_Q)]
        
        # "SELL" condition
        # (1) Two consecutive days of closing price higher than the signal median
        cond_sell_list_1 = list(map(lambda x, y: x > y, lag_close_q_list, mid_Q_list))
        # (2) rolling 5 days average higher than the median apc 
        cond_sell_list_2 = [(rollingaverage_q > apc_mid_Q)]
        # (3) price at today's opening hour below the 0.9 quantile of today's apc
        cond_sell_list_3 = [(open_price <= apc_mid_Q)]
        
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


    def set_EES(self, 
                buy_range: tuple = ([0.25,0.4],[0.6,0.75],0.05), 
                sell_range: tuple = ([0.6,0.75],[0.25,0.4],0.95)):
        """
        A method the set the Entry, Exit, Stop loss prices.
        This method read-in the direction attribute of the strategy and 
        decide which set of EES value to be set.
        
        Parameters
        ----------
        buy_range : tuple, optional
            A tuple that contain the desired quantile value range for buy action. 
            The format should be the following:
                ([lower_limit_entry, upper_limit_entry], 
                 [lower_limit_exit, upper_exit], stop_loss)
            The default is ([0.25,0.4],[0.6,0.75],0.05).
        sell_range : tuple, optional
            A tuple that contain the desired quantile value range for sell action. 
            The format should be the following:
                ([lower_limit_entry, upper_limit_entry], 
                 [lower_limit_exit, upper_exit], stop_loss)
            The default is ([0.6,0.75],[0.25,0.4],0.95).

        Raises
        ------
        Exception
            For invalid direction. It has to conform to the StrategyStatus
            Attributes.

        Returns
        -------
        entry_price : list
            A list contain the price caculated by the APC given the buy_range
            input.
        exit_price : list
            A list contain the price caculated by the APC given the sell_range
            input.
        stop_loss : float
            A price caculated by the APC given the stop_loss
            input.

        """

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
    
    def apply_strategy(self, history_data_lag: list, 
                       apc_curve_lag: list, 
                       open_price: float, 
                       qunatile: list = [0.25,0.4,0.6,0.75],
                       total_lag_days: int = 2, 
                       apc_mid_Q: float = 0.5, 
                       buy_range: tuple = ([0.25,0.4],[0.6,0.75],0.05), 
                       sell_range: tuple = ([0.6,0.75],[0.25,0.4],0.95)):
        """
        A method to apply the strategy.

        Parameters
        ----------
        history_data_lag : list
            The history data of the lag days.
        apc_curve_lag : list
            The APC curve of the lag days.
        open_price : float
            The opening price of the day.
        qunatile : list, optional
            A list of prices calculating using qunatile input into the APC
            of the date of interest. The default is [0.25,0.4,0.6,0.75].
        total_lag_days : int, optional
            The total number of lag days. The default is 2.
        apc_mid_Q : float, optional
            The middle quantile value. The default is 0.5.                   
        buy_range: tuple, optional
            A tuple that contain the desired quantile value range for buy action. 
            The default is ([0.25,0.4],[0.6,0.75],0.05).
        sell_range : tuple, optional
            A tuple that contain the desired quantile value range for sell action. 
            The default is ([0.6,0.75],[0.25,0.4],0.95).

        Returns
        -------
        dict
            A dictionary that contains the strategy data from the process.
            'data' contains EES value, cond_info, lag_list, rollingaverage,
            quantile_info, EES value (not range), and the strategy name

            'direction' contains the string of the trading direction (strategy
                        status).
        """
        
        strategy_info, quantile_info = self.gen_data(history_data_lag, apc_curve_lag,
                                                     qunatile = qunatile)
        
        open_price_quant = mfunc.find_quant(self._curve_today,
                                            self._quant_list, open_price)
        
        direction, cond_info = self.run_cond(strategy_info, open_price_quant,
                                             total_lag_days = total_lag_days, 
                                             apc_mid_Q = apc_mid_Q)
                                             
        
        entry_price, exit_price, stop_loss = self.set_EES(buy_range=buy_range, 
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



class ArgusMonthlyStrategy(Strategy):
    def __init__(self, 
                 curve_monthly = np.arange(0.0025, 0.9975, 0.0025),
                 curve_today= np.arange(0.0025, 0.9975, 0.0025), 
                 quant_list = np.arange(0.0025, 0.9975, 0.0025)):
        
        super().__init__()
        self._curve_monthly = curve_monthly
        self._curve_today = curve_today
        self._quant_list = quant_list
        self._curve_monthly_spline = mfunc.generic_spline(self._quant_list, 
                                                        self._curve_monthly)
        self._curve_today_spline = mfunc.generic_spline(self._quant_list, 
                                                        self._curve_today)
        
        self._sub_buy_cond_dict = dict()
        self._sub_sell_cond_dict = dict()
        self.sub_cond_dict = {'Buy':[], 'Sell':[], 'Neutral': []}

        self.strategy_name = 'argus_monthly'
        
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
                 daily_cumavg: float, 
                 prev_cum_n: float,
                 history_data_lag: list, 
                 apc_curve_lag: list, 
                 price_proxy: str = 'Settle', 
                 quantile: list = [0.05,0.10,0.35,0.50,0.65,0.90,0.95]):
        
        
        lag_price = history_data_lag[price_proxy]
        
        lag_list = [mfunc.find_quant(apc_curve_lag.iloc[i].to_numpy()[-1-APC_LENGTH:-1], 
                                     self._quant_list, lag_price.iloc[i]) for 
                                    i in range(len(apc_curve_lag))]
        lag_list.reverse()
        # Note that the list goes like this [lag1q,lag2q,...]

        # calculate the rolling average
        rollingaverage_q = np.average(lag_list)
        

        strategy_info = {"daily_cumavg": daily_cumavg, 
                         "prev_cum_n": prev_cum_n,
                         'lag_list': lag_list, 
                         'rollingaverage': rollingaverage_q}
        
        quantile_info = list(self._curve_today_spline(quantile))
        
        return strategy_info, quantile_info
    
    def run_cond(self,
                 data: dict, 
                 total_lag_days: int = 2, 
                 apc_range_trigger_buy: list = [0.10, 0.35],
                 apc_range_trigger_sell: list = [0.65, 0.90]):
        
        lag1q = data['lag_list'][0]
        rollingaverage_q = data['rollingaverage']
        
        daily_cumavg = data["daily_cumavg"]
        prev_cum_n = data[ "prev_cum_n"]                 

        lag_close_q_list = [data['lag_list'][i] for i in range(total_lag_days)]
        #mid_Q_list = [apc_mid_Q for i in range(total_lag_days)]
        
        quant_price_entry_lower_buy = self._curve_monthly_spline(
                                        apc_range_trigger_buy[0])
        quant_price_entry_upper_buy = self._curve_monthly_spline(
                                        apc_range_trigger_buy[1])

        quant_price_entry_lower_sell = self._curve_monthly_spline(
                                        apc_range_trigger_sell[0])
        quant_price_entry_upper_sell = self._curve_monthly_spline(
                                        apc_range_trigger_sell[1])

        # "BUY" condition
        # (1) create a list of Boolean value for evaluating if the 
        # total_cum_avg is within the monthly APC: Q0.1 < total_cum_avg < Q0.35
        cond_buy_list_1 = list(map(lambda x, y, z: z < x < y, 
                                   [quant_price_entry_lower_buy], 
                                   [daily_cumavg], 
                                   [quant_price_entry_upper_buy]))
        
        # (2) The lag1q for the day before has to be lower than the entry lower bound
        # (2) rolling 5 days average lower than the daily apc entry upper bound
        cond_buy_list_2 = [(lag1q < 0.25)]
        cond_buy_list_3 = [(rollingaverage_q < 0.4)]
        
        # "SELL" condition
        # (1) create a list of Boolean value for evaluating if the 
        # total_cum_avg is within the monthly APC: Q0.65 < total_cum_avg < Q0.9
        cond_sell_list_1 = list(map(lambda x, y, z: z < x < y, 
                                    [quant_price_entry_lower_sell], 
                                    [daily_cumavg], 
                                    [quant_price_entry_upper_sell]))
        # (2) price at today's opening hour below the 0.9 quantile of today's apc
        # (2) rolling 5 days average higher than the daily apc entry upper bound
        cond_sell_list_2 = [(lag1q > 0.75)]
        cond_sell_list_3 = [(rollingaverage_q <= 0.6)]
        
        
        # save the condtion boolean value to the sub-condition dictionary
        self._sub_buy_cond_dict = {'NCUM_CONS': [cond_buy_list_1],
                                   'NCONS': [cond_buy_list_2],	
                                   'NROLL': [cond_buy_list_3]}
        self._sub_sell_cond_dict = {'NCUM_CONS': [cond_sell_list_1],
                                    'NCONS': [cond_sell_list_2],	
                                    'NROLL': [cond_sell_list_3]}
        
        # Store all sub-conditions into 
        self.sub_cond_dict = {'Buy':[sum(self._sub_buy_cond_dict[key],[]) 
                                for key in self._sub_buy_cond_dict], 
                              'Sell':[sum(self._sub_sell_cond_dict[key],[]) 
                                for key in self._sub_buy_cond_dict]}
        
        # flatten the sub-conditoion list and sotre them in the condition list
        self.flatten_sub_cond_dict()

        # Create the condtion info for bookkeeping
        NCUM_CONS, NCONS, NROLL = len(self._sub_buy_cond_dict['NCUM_CONS']), \
                                  len(self._sub_buy_cond_dict['NCONS'][0]), \
                                  len(data['lag_list'])
                                        
        # Find the Boolean value for each buy conditions subgroup
        sub_buy_1 = all(self._sub_buy_cond_dict['NCUM_CONS'][0])
        sub_buy_2 = all(self._sub_buy_cond_dict['NCONS'][0])
        sub_buy_3 = all(self._sub_buy_cond_dict['NROLL'][0])
        # Find the Boolean value for each Sell conditions subgroup
        sub_sell_1 = all(self._sub_sell_cond_dict['NCUM_CONS'][0])
        sub_sell_2 = all(self._sub_sell_cond_dict['NCONS'][0])
        sub_sell_3 = all(self._sub_sell_cond_dict['NROLL'][0])
                
        # Construct condtion dictionaray for each condition
        cond_dict_1 = {'Buy': sub_buy_1, 'Sell': sub_sell_1, 
                       'Neutral': not(sub_buy_1 ^ sub_sell_1)}
        cond_dict_2 = {'Buy': sub_buy_2, 'Sell': sub_sell_2, 
                       'Neutral': not(sub_buy_2 ^ sub_sell_2)}
        cond_dict_3 = {'Buy': sub_buy_3, 'Sell': sub_sell_3, 
                       'Neutral': not(sub_buy_3 ^ sub_sell_3)}
        
        # Degine the name for the Buy/Sell action for each condition subgroups
        Signal_NCUM_CONS  = [key for key in cond_dict_1 if cond_dict_1[key] == True][0]
        Signal_NCONS  = [key for key in cond_dict_2 if cond_dict_2[key] == True][0]
        Signal_NROLL  = [key for key in cond_dict_3 if cond_dict_3[key] == True][0]

        # Put the condition info in a list
        cond_info = [NCUM_CONS, NCONS,	NROLL, 
                     Signal_NCUM_CONS, Signal_NCONS, Signal_NROLL]
        
        return self.direction, cond_info
        
# =============================================================================
#         # "Entry condition" These information are for the backtests
#         check_entry_buy = (q0_10 < today_cum_avg < q0_35) # Buy
#         check_entry_sell = (q0_65 < today_cum_avg < q0_90) # Sell
#         # Exit condition
#         check_exit_buy = (q0_50 < today_cum_avg < q0_90) # Buy
#         check_exit_sell = (q0_10 < today_cum_avg < q0_50) # Sell
#         
#         # Stoploss
#         check_stoploss_buy = (today_cum_avg < q0_05)
#         check_stoploss_sell = (today_cum_avg > q0_95)
# =============================================================================
    
    def set_EES(self, 
                data: dict,                
                buy_range: tuple = ([0.10,0.35],[0.50,0.90],0.05), 
                sell_range: tuple = ([0.65,0.90],[0.10,0.50],0.95)):
        # buy_range = ([lower_bound_entry, upper_bound_entry], 
        #              [lower_bound_exit, upper_bound_exit], stoploss)
        
        prev_cum_avg = data["daily_cumavg"]
        prev_cum_n = data["prev_cum_n"]
        
        print("buy_range[0][0]", buy_range[0])
        # A list of quantile price for buy and sell range
        quant_price_entry_lower_buy = self._curve_monthly_spline(buy_range[0][0])
        quant_price_entry_upper_buy = self._curve_monthly_spline(buy_range[0][1])
        
        quant_price_exit_lower_buy = self._curve_monthly_spline(buy_range[1][0])
        quant_price_exit_upper_buy = self._curve_monthly_spline(buy_range[1][1])

        quant_price_entry_lower_sell = self._curve_monthly_spline(sell_range[0][0])
        quant_price_entry_upper_sell = self._curve_monthly_spline(sell_range[0][1])
        
        quant_price_exit_lower_sell = self._curve_monthly_spline(sell_range[1][0])
        quant_price_exit_upper_sell = self._curve_monthly_spline(sell_range[1][1])

        quant_price_stoploss_buy = self._curve_monthly_spline(buy_range[2])
        quant_price_stoploss_sell = self._curve_monthly_spline(sell_range[2])
        
        # The actual price target
        # "Buy" target entry range
        buy_target_lower_entry = quant_price_entry_lower_buy*(prev_cum_n + 1) - \
                                 prev_cum_avg*prev_cum_n
        buy_target_upper_entry = quant_price_entry_upper_buy*(prev_cum_n + 1) - \
                                 prev_cum_avg*prev_cum_n
        # "Buy" target exit range
        buy_target_lower_exit = quant_price_exit_lower_buy*(prev_cum_n + 1) - \
                                 prev_cum_avg*prev_cum_n
        buy_target_upper_exit = quant_price_exit_upper_buy*(prev_cum_n + 1) - \
                                 prev_cum_avg*prev_cum_n
        # "Buy" target stoploss 
        buy_stoploss_exit = quant_price_stoploss_buy*(prev_cum_n + 1) - \
                            prev_cum_avg * prev_cum_n
        # "Sell" target entry range
        sell_target_lower_entry = quant_price_entry_lower_sell*(prev_cum_n + 1) - \
                                  prev_cum_avg*prev_cum_n
        sell_target_upper_entry = quant_price_entry_upper_sell*(prev_cum_n + 1) - \
                                  prev_cum_avg*prev_cum_n
        
        # "Sell" target exit range
        sell_target_lower_exit = quant_price_exit_lower_sell*(prev_cum_n + 1) - \
                                  prev_cum_avg*prev_cum_n
        sell_target_upper_exit = quant_price_exit_upper_sell*(prev_cum_n + 1) - \
                                  prev_cum_avg*prev_cum_n
                                  
        # "Sell" target Stoploss           
        sell_stoploss_exit = quant_price_stoploss_sell*(prev_cum_n + 1) - \
                             prev_cum_avg * prev_cum_n
        
        
        if self.direction == SignalStatus.BUY:
            # (A) Entry region at price < APC p=0.4 and 
            entry_price = [buy_target_lower_entry, buy_target_upper_entry]
            # (B) Exit price
            exit_price = [buy_target_lower_exit, buy_target_upper_exit] 
            # (C) Stop loss at APC p=0.1
            stop_loss = buy_stoploss_exit

            
        elif self.direction == SignalStatus.SELL:
            # (A) Entry region at price > APC p=0.6 and 
            entry_price = [sell_target_lower_entry, sell_target_upper_entry]
            # (B) Exit price
            exit_price = [sell_target_lower_exit, sell_target_upper_exit]
            # (C) Stop loss at APC p=0.9
            stop_loss = sell_stoploss_exit
            
        elif self.direction == SignalStatus.NEUTRAL:
            entry_price = ["NA", "NA"]
            exit_price = ["NA", "NA"]
            stop_loss = "NA"
        else:
            raise Exception(
                'Unaccepted input, condition needs to be either Buy, \
                    Sell, or Neutral.')
            
        return entry_price, exit_price, stop_loss
    


        
    def apply_strategy(self, 
                       history_data_lag: list, 
                       apc_curve_lag: list, 
                       daily_cumavg: float, 
                       prev_cum_n: float,
                       quantile: list = [0.05,0.10,0.35,0.50,0.65,0.90,0.95],
                       total_lag_days: int = 1, 
                       buy_range: tuple = ([0.10,0.35],[0.50,0.90],0.05), 
                       sell_range: tuple = ([0.65,0.90],[0.10,0.50],0.95)):
        

        strategy_info, quantile_info = self.gen_data(daily_cumavg, 
                                                     prev_cum_n,
                                                     history_data_lag, 
                                                     apc_curve_lag,
                                                     quantile = quantile)
        
        #open_price_quant = mfunc.find_quant(self._curve_today,
        #                                    self._quant_list, open_price)
        
        direction, cond_info = self.run_cond(strategy_info,
                                             total_lag_days = total_lag_days)
                                             
        
        entry_price, exit_price, stop_loss = self.set_EES(strategy_info,
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



MR_STRATEGIES_0 = {"argus_exact": ArgusMRStrategy,
                   "argus_exact_mode": ArgusMRStrategyMode,
                   'argus_monthly': ArgusMonthlyStrategy}
