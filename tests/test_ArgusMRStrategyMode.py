#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 25 11:29:51 2024

@author: dexter
"""

import datetime as datetime
import numpy as np

from EC_tools.strategy import MRStrategyArgus, SignalStatus, ArgusMRStrategyMode
import EC_tools.read as read
import EC_tools.math_func as mfunc
from crudeoil_future_const import CAT_LIST, KEYWORDS_LIST, SYMBOL_LIST, \
                                APC_FILE_LOC, HISTORY_DAILY_FILE_LOC,\
                                    HISTORY_MINTUE_FILE_LOC, TIMEZONE_DICT,\
                                        OPEN_HR_DICT, CLOSE_HR_DICT
                                        
from test_strategy import SingleRun

BUY_DATE_STR = "2021-03-02" #Buy date
SELL_DATE_STR = "2022-02-22" #Sell date
NEUTRAL_DATE_STR = "2021-01-27" #Neutral date

BuyTest = SingleRun(BUY_DATE_STR)
#SellTest = SingleRun(SELL_DATE_STR)
#NeutralTest =  SingleRun(NEUTRAL_DATE_STR)

def gen_data_Answer(Test):
    #Test = SingleRun(date)
    # Test the gen data function for Argus MR Strategy
    apc_curve_lag5, history_data_lag5 = read.extract_lag_data(Test.signal_data, 
                                                              Test.history_data_daily, 
                                                              Test.this_date)
    # Calculate the correct answer
    quant_list = np.arange(0.0025, 0.9975, 0.0025)
    qunatile_info_answer = mfunc.generic_spline(
        quant_list, Test.curve_this_date)([0.25,0.4,0.6,0.75])
    
    lag5 = mfunc.find_quant(apc_curve_lag5.iloc[0].to_numpy()[1:-1], 
                            quant_list, history_data_lag5['Settle'].iloc[0])
    lag4 = mfunc.find_quant(apc_curve_lag5.iloc[1].to_numpy()[1:-1], 
                            quant_list, history_data_lag5['Settle'].iloc[1])
    lag3 = mfunc.find_quant(apc_curve_lag5.iloc[2].to_numpy()[1:-1], 
                            quant_list, history_data_lag5['Settle'].iloc[2])
    lag2 = mfunc.find_quant(apc_curve_lag5.iloc[3].to_numpy()[1:-1], 
                            quant_list, history_data_lag5['Settle'].iloc[3])
    lag1 = mfunc.find_quant(apc_curve_lag5.iloc[4].to_numpy()[1:-1], 
                            quant_list, history_data_lag5['Settle'].iloc[4])
    
    rolling_avg_lag_answer = np.average([lag5,lag4,lag3,lag2,lag1])
    
    strategy_info_answer = [lag1,lag2,lag3,lag4,lag5]
    return qunatile_info_answer, strategy_info_answer, rolling_avg_lag_answer

def set_EES_Answer(Test, range_tuple = ([0.25,0.4], [0.6,0.75], 0.95)):
    #Test = SingleRun(date)

    quant_list = np.arange(0.0025, 0.9975, 0.0025)
    
    if isinstance(range_tuple[0][0], float) and isinstance(range_tuple[0][1], float):
        entry_price_answer = mfunc.generic_spline(quant_list, 
                                              Test.curve_this_date)(range_tuple[0])
    else:
        entry_price_answer = range_tuple[0]
        
    if isinstance(range_tuple[1][0], float) and isinstance(range_tuple[1][1], float):
        exit_price_answer = mfunc.generic_spline(quant_list, 
                                              Test.curve_this_date)(range_tuple[1])
    else:
        exit_price_answer = range_tuple[1]
        
    if isinstance(range_tuple[2], float):
        stop_loss_answer = mfunc.generic_spline(quant_list, 
                                      Test.curve_this_date)(range_tuple[2])
    else:
        stop_loss_answer = range_tuple[2]
        
    return entry_price_answer, exit_price_answer, stop_loss_answer


def make_Answer(date, range_tuple = ([0.25,0.4], [0.6,0.75], 0.95)):
    Test = SingleRun(date)

    answer_tuple = gen_data_Answer(Test)
    EES_answer_tuple = set_EES_Answer(Test, range_tuple =range_tuple)
    
    return {'answer_tuple': answer_tuple, 'EES_answer_tuple': EES_answer_tuple} 






def test_MRStrategyArgus_gen_data(Test)->None:
    # Test the gen data function for Argus MR Strategy
    apc_curve_lag5, history_data_lag5 = read.extract_lag_data(Test.signal_data, 
                                                              Test.history_data_daily, 
                                                              Test.this_date)
    # Run the programme.
    strategy_info, qunatile_info = \
        ArgusMRStrategyMode(Test.curve_this_date).gen_data(history_data_lag5, 
                                                            apc_curve_lag5)
    print(strategy_info, qunatile_info)
    
    
test_MRStrategyArgus_gen_data(BuyTest)

def test_MRStrategyArgus_rund_cond(Test, signal_status, cond_list)->None:
    pass

def test_MRStrategyArgus_set_EES(Test, EES_answer_tuple)->None:
    pass


