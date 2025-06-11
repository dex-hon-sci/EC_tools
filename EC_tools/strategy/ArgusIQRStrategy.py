#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 13 12:29:38 2025

@author: dexter
"""
import sys
sys.path.insert(0, "/home/dexter/Euler_Capital_codes/EC_tools")
# python import
from typing import Protocol
from enum import Enum, auto
from dataclasses import dataclass, field
import datetime

import numpy as np
import pandas as pd

import EC_tools.utility as util
import EC_tools.utility.math_func as mfunc
from EC_tools.strategy import Strategy, APC_LENGTH
from EC_tools.strategy.signal import SignalType
from ext_codes.ArgusPossibilityCurves2 import ArgusPossibilityCurves
from crudeoil_future_const import DAILY_APC_PKL

import os
from dotenv import load_dotenv 


argus_IQRSKW_format = ['Date', 'Price_Code', 'Direction', 'Commodity_name',
                        'Contract_Month','Timezone', 
                        'Valid_From_localtz_timestr', 'Valid_To_localtz_timestr', 
                        'CONS',	'Signal_CONS',	
                        'Q0.05', 'Q0.1','Q0.25', 'Q0.4', 'Q0.5', 
                        'Q0.6', 'Q0.75', 'Q0.9', 'Q0.95',
                        'Entry_Price', 'Exit_Price', 'StopLoss_Price',
                        'strategy_name']
#extract_lag_data
def gen_apc_stat(apc_curve_data:pd.DataFrame):
    # operate on the dataframe, use this before the signal generation loop
    apc_curve_data_c = apc_curve_data.copy()
    
    ### Stat 1: IQR (inter-quartile range)    
    apc_curve_data_c["IQR"] = apc_curve_data_c["0.75"]-apc_curve_data_c["0.25"]
    
    ### Stat 2 : Central skewness
    apc_curve_data_c["CRT_SKW"] = (apc_curve_data_c["0.25"]+apc_curve_data_c["0.75"]-2*apc_curve_data_c["0.5"]) / (apc_curve_data_c["0.75"] - apc_curve_data_c["0.25"])
    
    ### Stat 3: Tail skewness
    apc_curve_data_c["Tail_SKW"] = (apc_curve_data_c["0.0025"]+apc_curve_data_c["0.9975"]-2*apc_curve_data_c["0.5"]) / (apc_curve_data_c["0.9975"] - apc_curve_data_c["0.0025"])
    
    ### Stat 4: Downside tail risk
    apc_curve_data_c["Downside_Tail_Risk"] = apc_curve_data_c["0.5"]-apc_curve_data_c["0.0025"]
    
    ### Stat 5: Upside tail risk
    apc_curve_data_c["Upside_Tail_Risk"] = apc_curve_data_c["0.9975"]-apc_curve_data_c["0.5"]      
    
    apc_curve_data_c = apc_curve_data_c[['PUBLICATION_DATE', 'PERIOD', 'CATEGORY', 
                                         'CONTINUOUS_FORWARD','TIMESTAMP', 
                                         'PRICE_UNIT', 'symbol', 'IQR', 'CRT_SKW',
                                         'Tail_SKW', 'Downside_Tail_Risk', 
                                         'Upside_Tail_Risk']]
    return apc_curve_data_c

def cal_apc_stat(apc_spline):
    # Calculate line by line the stat of the APC
    apc_stat_data = dict()
    ### Stat 1: IQR (inter-quartile range)    
    apc_stat_data["IQR"] = apc_spline(0.75)-apc_spline(0.25)
    
    ### Stat 2 : Central skewness
    apc_stat_data["CRT_SKW"] = (apc_spline(0.25)+apc_spline(0.75)-2*apc_spline(0.5)) / (apc_spline(0.75) - apc_spline(0.25))
    
    ### Stat 3: Tail skewness
    apc_stat_data["Tail_SKW"] = (apc_spline(0.0025)+apc_spline(0.9975)-2*apc_spline(0.5)) / (apc_spline(0.9975) - apc_spline(0.0025))
    
    ### Stat 4: Downside tail risk
    apc_stat_data["Downside_Tail_Risk"] = apc_spline(0.5)-apc_spline(0.0025)
    
    ### Stat 5: Upside tail risk
    apc_stat_data["Upside_Tail_Risk"] = apc_spline(0.9975)-apc_spline(0.5)      

    return apc_stat_data
    


load_dotenv()
ARGUS_USR = os.environ.get("ARGUS_USRX")
ARGUS_PW = os.environ.get("ARGUS_PWX")

    
def pull_ArgusIQR_signals(start_date, end_date, categories):
    apc = ArgusPossibilityCurves(username=ARGUS_USR, password=ARGUS_PW)
    apc.authenticate()

    #set update_from_remote to false if you don't want to check for new metadata
    apc.getMetadataCSV(filepath="argus_latest_meta.csv", 
                       force_update_from_remote=True)

    apc_data = apc.getPossibilityCurves(start_date=start_date, 
                                        end_date=end_date, 
                                        categories=categories)
    
    data_with_trading_signals = apc.calculate_trading_signals(data=apc_data, 
                                                              IQR_window=10, 
                                                              Skew_window=12)

    print(data_with_trading_signals[['PERIOD', 'CATEGORY', 'CONTINUOUS_FORWARD', 
                                     'TIMESTAMP', 'PRICE_UNIT', 'IQR', 
                                     'Central Skewness', 'Tail Skewness',
                                     'Downside Tail Risk', 'Upside Tail Risk', 
                                     'IQR Moving Average',
                                     'Central Skewness Moving Average', 
                                     'Signal IQR', 'Signal IQR-Skewness']])
    return data_with_trading_signals

def pull_ArgusOBOS(start_date: datetime.date, 
                   end_date: datetime.date, 
                   obos):
    # Pull the OBOS level values from Argus, migrate this to run_update_db
    apc = ArgusPossibilityCurves(username=ARGUS_USR, password=ARGUS_PW)
    apc.authenticate()

    #set update_from_remote to false if you don't want to check for new metadata
    apc.getMetadataCSV(filepath="argus_latest_meta.csv", 
                       force_update_from_remote=True)

    ava_obos = apc.get_available_obos()
    print(ava_obos, len(ava_obos))
    obos_data = apc.getOBOS(start_date, end_date, obos)
    print("obos_data", obos_data)
    return obos_data

class ArgusIQRStrategy(Strategy):
    
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

        self.strategy_name = 'argus_IQR_SKW'

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
                 apc_stat_data: pd.DataFrame, 
                 Window_IQR: int =10,
                 Window_SKW: int = 10,
                 quantile: list = [0.25,0.4,0.6,0.75]):
        
        IQR_MA = apc_stat_data['IQR_MA']
        CRT_SKW_MA = apc_stat_data['CRT_SKW_MA']
        #IQR_MA = apc_stat_data[:, 'IQR'].rolling(window=Window_IQR).mean()
        #CRT_SKW_MA = apc_stat_data.loc[:, 'CRT_SKW'].rolling(window=Window_SKW).mean()

        strategy_info = {'IQR_MA': float(IQR_MA),
                         'CRT_SKW_MA': float(CRT_SKW_MA), 
                         'Window_IQR': Window_IQR, # Window size for IQR
                         'Window_SKW': Window_SKW, # Window size for SKW
                         'stat': [float(apc_stat_data['IQR']), 
                                  float(apc_stat_data['CRT_SKW']), 
                                  float(apc_stat_data['TAIL_SKW']), 
                                  float(apc_stat_data['Down_tail_risk']), 
                                  float(apc_stat_data['Up_tail_risk'])]}
        
        qunatile_info = list(self._curve_today_spline(quantile))
        
        return strategy_info, qunatile_info 
    
    def run_cond(self, data: dict): 
        
        # Run conditions
        IQR_MA, CRT_SKW_MA = data['IQR_MA'], data['CRT_SKW_MA']        
        #Window_IQR, Window_SKW = data['Window_IQR'], data['Window_SKW']
        IQR, CRT_SKW = data['stat'][0], data['stat'][1]
        
        #If IQR > IQR_moving_average (widen Range)
        # AND Central_Skewness < Central_Skewness_moving_average (skew below MA)
        # -> Sell
        cond_sell_list_1 = [(IQR > IQR_MA)]
        cond_sell_list_2 = [(CRT_SKW < CRT_SKW_MA)]
        
        #If IQR < IQR_moving_average  (narrowed range)
        # AND Central_Skewness > Central_Skewness_moving_average (skew above MA)
        # -> Buy       
        cond_buy_list_1 = [(IQR < IQR_MA)]
        cond_buy_list_2 = [(CRT_SKW > CRT_SKW_MA)]
        
        # save the condtion boolean value to the sub-condition dictionary
        self._sub_buy_cond_dict = {'IQR_CON': [cond_buy_list_1],	
                                   'CRT_SKW_CON': [cond_buy_list_2]}
        self._sub_sell_cond_dict = {'IQR_CON': [cond_sell_list_1],	
                                    'CRT_SKW_CON': [cond_sell_list_2]}
        
        # Store all sub-conditions into 
        self.sub_cond_dict = {'Buy':[sum(self._sub_buy_cond_dict[key],[]) 
                                for key in self._sub_buy_cond_dict], 
                             'Sell':[sum(self._sub_sell_cond_dict[key],[]) 
                                for key in self._sub_buy_cond_dict]}
        
        self.flatten_sub_cond_dict()

        # Create the condtion info for bookkeeping
        IQR_CON,	 CRT_SKW_CON = len(self._sub_buy_cond_dict['IQR_CON'][0]), \
                               len(self._sub_buy_cond_dict['CRT_SKW_CON'][0])
                                        
        # Find the Boolean value for each buy conditions subgroup
        sub_buy_1 = all(self._sub_buy_cond_dict['IQR_CON'][0])
        sub_buy_2 = all(self._sub_buy_cond_dict['CRT_SKW_CON'][0])
        # Find the Boolean value for each Sell conditions subgroup
        sub_sell_1 = all(self._sub_sell_cond_dict['IQR_CON'][0])
        sub_sell_2 = all(self._sub_sell_cond_dict['CRT_SKW_CON'][0])
                
        # Construct condtion dictionaray for each condition
        cond_dict_1 = {'Buy': sub_buy_1, 'Sell': sub_sell_1, 
                       'Neutral': not(sub_buy_1 ^ sub_sell_1)}
        cond_dict_2 = {'Buy': sub_buy_2, 'Sell': sub_sell_2, 
                       'Neutral': not(sub_buy_1 ^ sub_sell_1)}
        
        # Degine the name for the Buy/Sell action for each condition subgroups
        Signal_IQR  = [key for key in cond_dict_1 if cond_dict_1[key] == True][0]
        Signal_SKW  = [key for key in cond_dict_2 if cond_dict_2[key] == True][0]

        # Put the condition info in a list
        cond_info = [IQR_CON, CRT_SKW_CON, Signal_IQR, Signal_SKW]
        
        return self.direction, cond_info

    
    def set_EES(self, 
                OB: float, OS: float,
                buy_range: tuple = (0.4,0.6,0.05), 
                sell_range: tuple = (0.6,0.4,0.95)):
        #if self.direction :
            
        match self.direction:
            case SignalType.BUY:
                entry_price = OB
                exit_price = OS
                stop_loss = self._curve_today_spline(buy_range[2])
            case SignalType.SELL:
                entry_price = OS
                exit_price = OB
                stop_loss = self._curve_today_spline(sell_range[2])

            case SignalType.NEUTRAL:
                entry_price = 'NA'
                exit_price = 'NA'
                stop_loss = 'NA'
            case _:
                raise Exception('Not matching any signal types')
        #entry_price, exit_price, stop_loss = 0, 0,0 
        return entry_price, exit_price, stop_loss

    
    def apply_strategy(self, 
                       apc_stat_data: pd.DataFrame, 
                       apc_curve_data: pd.DataFrame,          
                       OB: float, 
                       OS: float,
                       buy_range: tuple[list|tuple,float] = 
                                   ([0.25,0.4],[0.6,0.75],0.05), 
                       sell_range: tuple[list|tuple,float] = 
                                   ([0.6,0.75],[0.25,0.4],0.95),
                       #quantile: list[float] = [0.25,0.4,0.6,0.75],
                       Window_IQR: int = 38,
                       Window_SKW: int = 22):

        strategy_info, quantile_info = self.gen_data(apc_stat_data, 
                                                Window_IQR = Window_IQR, 
                                                Window_SKW = Window_SKW,
                                                quantile = [0.25,0.4,0.6,0.75])
        
        direction, cond_info = self.run_cond(strategy_info)
        
        entry_price, exit_price, stop_loss = self.set_EES(OB,OS,
                                                          buy_range=buy_range, 
                                                          sell_range=sell_range)

        # Bookkeeping area
        EES_val = [entry_price, exit_price, stop_loss]
        
        # Turn strategy_info from dict to list
        strategy_info_list = strategy_info['lag_list'] + [strategy_info['rollingaverage']]
        
        # put all the data in a singular list. This is to be added in the 
        # data list in the loop
        #print(EES+ cond_info, strategy_info_list, quantile_info, [self.strategy_name])
        #print(type(EES+ cond_info), type(strategy_info_list), type(quantile_info), type([self.strategy_name]))
        
        data =  cond_info + strategy_info_list + \
                quantile_info + EES_val + [self.strategy_name]
        
        return {'data': data, 'direction': direction.value}
    
if __name__ == "__main__":
# =============================================================================
#     import datetime as datetime
#     start_date = datetime.date(2025, 3, 25)
#     end_date = datetime.date(2025, 3, 27)
# 
#     categories = [ASSET_ARGUS_DICT['CLc1']['categories']]
#     data = pull_ArgusIQR_signals(start_date, end_date, categories)
#     
#     print(data)
# =============================================================================
    APC = util.load_pkl(DAILY_APC_PKL)
    start_date = datetime.date(2025, 5, 25)
    end_date = datetime.date(2025, 5, 26)

    apc_curve_data_c = gen_apc_stat(APC['CLc1'])
    #data = pull_ArgusIQR_signals(start_date,end_date,
    #                      ['Argus Nymex WTI month 1, Daily'])
    
    #print(data)
    #pull OBOS levels for target entry and exit
    data = pull_ArgusOBOS(start_date,end_date,
                          ['Argus ICE gasoil month 1'])
    print(type(data), data.iloc[0])