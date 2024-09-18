#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 25 11:29:51 2024

@author: dexter
"""

import datetime as datetime
import numpy as np
import pytest


from EC_tools.strategy import ArgusMRStrategy, SignalStatus, ArgusMRStrategyMode
import EC_tools.read as read
import EC_tools.math_func as mfunc
from crudeoil_future_const import CAT_LIST, KEYWORDS_LIST, SYMBOL_LIST, \
                                  APC_FILE_LOC, HISTORY_DAILY_FILE_LOC,\
                                  HISTORY_MINTUE_FILE_LOC, TIMEZONE_DICT,\
                                  OPEN_HR_DICT, CLOSE_HR_DICT,APC_LENGTH
                                        
from tests.test_strategy import SingleRun

BUY_DATE_STR = "2021-03-02" #Buy date
SELL_DATE_STR = "2022-02-22" #Sell date
NEUTRAL_DATE_STR = "2021-01-27" #Neutral date


def gen_data_Answer(Test):
    # The lag quantiles and rollingaverage
    # Test the gen data function for Argus MR Strategy
    apc_curve_lag5, history_data_lag5 = read.extract_lag_data(Test.signal_data, 
                                                              Test.history_data_daily, 
                                                              Test.this_date)
    # Calculate the correct answer
    quant_list = np.arange(0.0025, 0.9975, 0.0025)
    
    lag5 = mfunc.find_quant(apc_curve_lag5.iloc[0].to_numpy()[-1-APC_LENGTH:-1], 
                            quant_list, history_data_lag5['Settle'].iloc[0])
    lag4 = mfunc.find_quant(apc_curve_lag5.iloc[1].to_numpy()[-1-APC_LENGTH:-1], 
                            quant_list, history_data_lag5['Settle'].iloc[1])
    lag3 = mfunc.find_quant(apc_curve_lag5.iloc[2].to_numpy()[-1-APC_LENGTH:-1], 
                            quant_list, history_data_lag5['Settle'].iloc[2])
    lag2 = mfunc.find_quant(apc_curve_lag5.iloc[3].to_numpy()[-1-APC_LENGTH:-1], 
                            quant_list, history_data_lag5['Settle'].iloc[3])
    lag1 = mfunc.find_quant(apc_curve_lag5.iloc[4].to_numpy()[-1-APC_LENGTH:-1], 
                            quant_list, history_data_lag5['Settle'].iloc[4])
    
    rolling_avg_lag_answer = np.average([lag5,lag4,lag3,lag2,lag1])
    
    strategy_info_answer = [lag1,lag2,lag3,lag4,lag5]
    
    # The answers for the quantile of the mode
    # Find the pdf from cdf
    lag5_pdf = mfunc.cal_pdf(quant_list, apc_curve_lag5.iloc[0].to_numpy()[-1-APC_LENGTH:-1]) 
    lag4_pdf = mfunc.cal_pdf(quant_list, apc_curve_lag5.iloc[1].to_numpy()[-1-APC_LENGTH:-1]) 
    lag3_pdf = mfunc.cal_pdf(quant_list, apc_curve_lag5.iloc[2].to_numpy()[-1-APC_LENGTH:-1]) 
    lag2_pdf = mfunc.cal_pdf(quant_list, apc_curve_lag5.iloc[3].to_numpy()[-1-APC_LENGTH:-1]) 
    lag1_pdf = mfunc.cal_pdf(quant_list, apc_curve_lag5.iloc[4].to_numpy()[-1-APC_LENGTH:-1]) 
    
    # Calculate the price of the mode in these apc
    mode_Q_lag5 = mfunc.find_pdf_quant(lag5_pdf[0], lag5_pdf[1], func=max)
    mode_Q_lag4 = mfunc.find_pdf_quant(lag4_pdf[0], lag4_pdf[1], func=max)
    mode_Q_lag3 = mfunc.find_pdf_quant(lag3_pdf[0], lag3_pdf[1], func=max)
    mode_Q_lag2 = mfunc.find_pdf_quant(lag2_pdf[0], lag2_pdf[1], func=max)
    mode_Q_lag1 = mfunc.find_pdf_quant(lag1_pdf[0], lag1_pdf[1], func=max)
    
    mode_Q_list_answer = [mode_Q_lag1, mode_Q_lag2, mode_Q_lag3, mode_Q_lag4, mode_Q_lag5]
    rolling_avg_mode_Q_answer = np.average(mode_Q_list_answer)
    
    # Define quantile_info answer
    # calculate the pdf for the date of interest
    pdf_this_date = mfunc.cal_pdf(quant_list, Test.curve_this_date)
    mode_value = mfunc.find_pdf_val(pdf_this_date[0],pdf_this_date[1],func=max)
    
    # make a reverse spine for the CDF!!!! NOT THE PDF. VERY IMPORTANT
    curve_today_reverse_spline = mfunc.generic_spline(Test.curve_this_date, 
                                                                quant_list, 
                                                                method='cubic')
    
    mode_quant =  float(curve_today_reverse_spline(mode_value))
    
    #print("mode_quant", mode_quant, [mode_quant-0.1, mode_quant, mode_quant+0.1])
    
    qunatile_info_answer = mfunc.generic_spline(
        quant_list, Test.curve_this_date)([mode_quant-0.1, mode_quant, mode_quant+0.1])
    
    return qunatile_info_answer, strategy_info_answer, rolling_avg_lag_answer, \
                                    mode_Q_list_answer, rolling_avg_mode_Q_answer

def set_EES_Answer(Test, range_tuple = (-0.1, 0.1, -0.45)):
    
    
#buy_range=(-0.1, 0.1, -0.45),   sell_range =(0.1, -0.1, +0.45)
    quant_list = np.arange(0.0025, 0.9975, 0.0025)

    # calculate the pdf for the date of interest
    pdf_this_date = mfunc.cal_pdf(quant_list, Test.curve_this_date)
    mode_value = mfunc.find_pdf_val(pdf_this_date[0],pdf_this_date[1],func=max)
    
    # make a reverse spine for the CDF!!!! NOT THE PDF. VERY IMPORTANT
    curve_today_reverse_spline = mfunc.generic_spline(Test.curve_this_date, 
                                                                quant_list, 
                                                                method='cubic')
    
    mode_quant =  float(curve_today_reverse_spline(mode_value))
    
    
    if isinstance(range_tuple[0], float):
        entry_price_answer = mfunc.generic_spline(quant_list, Test.curve_this_date)(
                                                    mode_quant+range_tuple[0])
    else:
        entry_price_answer = range_tuple[0] # For Neutral condition
        
    if isinstance(range_tuple[1], float):
        exit_price_answer = mfunc.generic_spline(quant_list, Test.curve_this_date)(
                                                    mode_quant+range_tuple[1])
    else:
        exit_price_answer = range_tuple[1]
        
    if isinstance(range_tuple[2], float):
        stop_loss_answer = mfunc.generic_spline(quant_list, Test.curve_this_date)(
                                                    mode_quant+range_tuple[2])
    else:
        stop_loss_answer = range_tuple[2]
        
    return entry_price_answer, exit_price_answer, stop_loss_answer


def make_Answer(date, range_tuple= (-0.1, 0.1, -0.45)):
    Test = SingleRun(date)

    answer_tuple = gen_data_Answer(Test)
    EES_answer_tuple = set_EES_Answer(Test, range_tuple =range_tuple)
    
    return {'answer_tuple': answer_tuple, 'EES_answer_tuple': EES_answer_tuple} 


BuyAnswer = make_Answer(BUY_DATE_STR, range_tuple= (-0.1, 0.1, -0.45))
SellAnswer = make_Answer(SELL_DATE_STR,  range_tuple =(0.1, -0.1, +0.45))
NeutralAnswer = make_Answer(NEUTRAL_DATE_STR, range_tuple= ('NA', 'NA', 'NA'))

BuyTest = SingleRun(BUY_DATE_STR)
SellTest = SingleRun(SELL_DATE_STR)
NeutralTest =  SingleRun(NEUTRAL_DATE_STR)

@pytest.mark.parametrize("Test, answer_tuple", 
                         [(BuyTest, BuyAnswer['answer_tuple']), 
                          (SellTest, SellAnswer['answer_tuple']),
                          (NeutralTest, NeutralAnswer['answer_tuple'])]) 
def test_MRStrategyArgus_gen_data(Test, answer_tuple)->None:
    # Test the gen data function for Argus MR Strategy
    apc_curve_lag5, history_data_lag5 = read.extract_lag_data(Test.signal_data, 
                                                              Test.history_data_daily, 
                                                              Test.this_date)
    # Run the programme.
    strategy_info, qunatile_info = \
        ArgusMRStrategyMode(Test.curve_this_date).gen_data(history_data_lag5, 
                                                            apc_curve_lag5)
    #print(strategy_info, qunatile_info)
    
    # Calculate the correct answer
    qunatile_info_answer = answer_tuple[0]
    strategy_info_answer = answer_tuple[1]
    rolling_avg_lag_answer = answer_tuple[2]
    mode_Q_list_answer = answer_tuple[3]
    rolling_avg_mode_Q_answer = answer_tuple[4]
    #print(qunatile_info_answer,qunatile_info )
    assert all(qunatile_info[i] == qunatile_info_answer[i] for i,_ 
                                               in enumerate(qunatile_info))
    assert all(strategy_info['lag_list'][i] == strategy_info_answer[i] for i, _ 
                                               in enumerate(strategy_info))
    assert (strategy_info['rollingaverage'] - rolling_avg_lag_answer) < 1e-8
    assert all(strategy_info['mode_Q_list'][i] == mode_Q_list_answer[i] for i, _ 
                                           in enumerate(mode_Q_list_answer))
    assert (strategy_info['rollingaverage_mode'] - rolling_avg_mode_Q_answer) <\
                                                                            1e-8

@pytest.mark.parametrize("Test, signal_status, cond_list", 
                         [(BuyTest, SignalStatus.BUY, [2 , 5, 'Buy', 'Buy']), 
                          (SellTest, SignalStatus.SELL, [2 , 5, 'Sell', 'Sell']), 
                          (NeutralTest, SignalStatus.NEUTRAL, [2, 5,'Neutral', 'Buy'])])
def test_MRStrategyArgus_rund_cond(Test, signal_status, cond_list)->None:
    # Test the gen data function for Argus MR Strategy
    apc_curve_lag5, history_data_lag5 = read.extract_lag_data(Test.signal_data, 
                                                              Test.history_data_daily, 
                                                              Test.this_date)
    # Run the programme.
    strategy_info, qunatile_info = \
        ArgusMRStrategyMode(Test.curve_this_date).gen_data(history_data_lag5, 
                                                       apc_curve_lag5)
    
    MR = MRStrategyArgus(Test.curve_this_date)
    direction, cond_info = MR.run_cond(strategy_info, Test.open_price, 
                                           total_lag_days = 2)
    
    assert direction == signal_status
    assert all(cond_info[i] == cond_list[i] for i,_ in enumerate(cond_list))

@pytest.mark.parametrize("Test, EES_answer_tuple", 
                         [(BuyTest, BuyAnswer['EES_answer_tuple']), 
                          (SellTest, SellAnswer['EES_answer_tuple'] ),
                          (NeutralTest, NeutralAnswer['EES_answer_tuple'])]) 
def test_MRStrategyArgus_set_EES(Test, EES_answer_tuple)->None:
    apc_curve_lag5, history_data_lag5 = read.extract_lag_data(Test.signal_data, 
                                                              Test.history_data_daily, 
                                                              Test.this_date)
    MR = ArgusMRStrategyMode(Test.curve_this_date)

    # Run the programme.
    strategy_info, qunatile_info = MR.gen_data(history_data_lag5, 
                                                       apc_curve_lag5)
        
    direction, cond_info = MR.run_cond(strategy_info, Test.open_price)
    
    entry_price, exit_price, stop_loss = MR.set_EES(
                                buy_range=(-0.1, 0.1, -0.45), 
                            sell_range =(0.1, -0.1, +0.45))
    
    #Correct answers
    entry_price_answer = EES_answer_tuple[0]
    exit_price_answer = EES_answer_tuple[1]
    stop_loss_answer = EES_answer_tuple[2]
    
    
    print(entry_price, entry_price_answer)
    #print(entry_price, exit_price, stop_loss)
    assert entry_price == entry_price_answer 
    assert exit_price == exit_price_answer 
    assert stop_loss == stop_loss_answer

test_MRStrategyArgus_gen_data(BuyTest, BuyAnswer['answer_tuple'])
test_MRStrategyArgus_set_EES(BuyTest,BuyAnswer['EES_answer_tuple'])
test_MRStrategyArgus_rund_cond(BuyTest, SignalStatus.BUY, [2 , 5, 'Buy', 'Buy'])