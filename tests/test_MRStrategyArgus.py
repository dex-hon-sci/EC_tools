#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jul 14 05:03:16 2024

@author: dexter

"""
import datetime as datetime
import numpy as np
import pytest

from EC_tools.strategy import MRStrategyArgus, SignalStatus
import EC_tools.read as read
import EC_tools.math_func as mfunc
import EC_tools.utility as util
from crudeoil_future_const import CAT_LIST, KEYWORDS_LIST, SYMBOL_LIST, \
                                APC_FILE_LOC, HISTORY_DAILY_FILE_LOC,\
                                    HISTORY_MINTUE_FILE_LOC, TIMEZONE_DICT,\
                                        OPEN_HR_DICT, CLOSE_HR_DICT
                                        
SIGNAL = "/home/dexter/Euler_Capital_codes/EC_tools/data/APC_latest/APC_latest_CLc1.csv"
HISTORY_DAILY = "/home/dexter/Euler_Capital_codes/EC_tools/data/history_data/Day/CL.day"
HISTORY_MINUTE = "/home/dexter/Euler_Capital_codes/EC_tools/data/history_data/Minute/CL.001"

BUY_DATE_STR = "2021-03-02" #Buy date
SELL_DATE_STR = "2022-02-22" #Sell date
NEUTRAL_DATE_STR = "2021-01-27" #Neutral date

class SingleRun():
    @util.time_it
    def __init__(self, date_str, 
                 signal_filename = SIGNAL, 
                 filename_daily = HISTORY_DAILY, 
                 filename_minute= HISTORY_MINUTE,
                 symbol= 'CLc1'):
        
        self.this_date = datetime.datetime.strptime(date_str, '%Y-%m-%d')
        # The reading part takes the longest time: 13 seconds. The loop itself takes 
        # input 1, APC. Load the master table in memory and test multple strategies   
        self.signal_data =  read.read_reformat_APC_data(signal_filename)
        
        # input 2, Portara history file.
        # start_date2 is a temporary solution 
        self.history_data_daily = read.read_reformat_Portara_daily_data(filename_daily)
        self.history_data_minute = read.read_reformat_Portara_minute_data(filename_minute)
        
        # Add a symbol column
        self.history_data_daily['symbol'] = [symbol for i in range(len(self.history_data_daily))]
        self.history_data_minute['symbol'] = [symbol for i in range(len(self.history_data_minute))]
        
        # Find the opening price at 03:30 UK time. If not found, 
        #loop through the next 30 minutes to find the opening price
        self.price_330 = read.find_open_price(self.history_data_daily, self.history_data_minute)
        self.open_price = self.price_330[
            self.price_330['Date']==self.this_date]['Open Price'].item()

        # Find the APC on this date
        self.curve_this_date = self.signal_data[(
                                self.signal_data['Forecast Period']==self.this_date)]\
                                        .to_numpy()[0][1:-1]

        self.direction = SignalStatus.NEUTRAL

def gen_data_Answer(date):
    Test = SingleRun(date)
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

def set_EES_Answer(date, range_tuple = ([0.25,0.4], [0.6,0.75], 0.95)):
    Test = SingleRun(date)

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


@pytest.mark.parametrize("date, answer_tuple", 
                         [(BUY_DATE_STR, gen_data_Answer(BUY_DATE_STR)), 
                          (SELL_DATE_STR, gen_data_Answer(SELL_DATE_STR)),
                          (NEUTRAL_DATE_STR, gen_data_Answer(NEUTRAL_DATE_STR))]) 
def test_MRStrategyArgus_gen_data(date, answer_tuple)->None:
    Test = SingleRun(date)
    # Test the gen data function for Argus MR Strategy
    apc_curve_lag5, history_data_lag5 = read.extract_lag_data(Test.signal_data, 
                                                              Test.history_data_daily, 
                                                              Test.this_date)
    # Run the programme.
    strategy_info, qunatile_info = \
        MRStrategyArgus(Test.curve_this_date).gen_data(history_data_lag5, 
                                                            apc_curve_lag5)
    
    # Calculate the correct answer
    qunatile_info_answer = answer_tuple[0]
    strategy_info_answer = answer_tuple[1]
    rolling_avg_lag_answer = answer_tuple[2]
    
    assert all(qunatile_info[i] == qunatile_info_answer[i] for i,_ in enumerate(qunatile_info))
    assert all(strategy_info['lag_list'][i] == strategy_info_answer[i] for i, _ in enumerate(strategy_info))
    assert (strategy_info['rollingaverage'] - rolling_avg_lag_answer) < 1e-8

@pytest.mark.parametrize("date, signal_status, cond_list", 
                         [(BUY_DATE_STR, SignalStatus.BUY, [2 , 5, 'Buy', 'Buy']), 
                          (SELL_DATE_STR, SignalStatus.SELL, [2 , 5, 'Sell', 'Sell']), 
                          (NEUTRAL_DATE_STR, SignalStatus.NEUTRAL, [2, 5,'Neutral', 'Buy'])])
def test_MRStrategyArgus_rund_cond(date, signal_status, cond_list)->None:
    Test = SingleRun(date)
    # Test the gen data function for Argus MR Strategy
    apc_curve_lag5, history_data_lag5 = read.extract_lag_data(Test.signal_data, 
                                                              Test.history_data_daily, 
                                                              Test.this_date)
    # Run the programme.
    strategy_info, qunatile_info = \
        MRStrategyArgus(Test.curve_this_date).gen_data(history_data_lag5, 
                                                       apc_curve_lag5)
    
    MR = MRStrategyArgus(Test.curve_this_date)
    
    direction, cond_info = MR.run_cond(
                                strategy_info, Test.open_price, 
                                total_lag_days = 2, 
                                 apc_mid_Q = 0.5, 
                                 apc_trade_Qrange=(0.4,0.6), 
                                 apc_trade_Qmargin = (0.1,0.9),
                                 apc_trade_Qlimit=(0.05,0.95))
    
    assert direction == signal_status
    assert all(cond_info[i] == cond_list[i] for i,_ in enumerate(cond_list))


@pytest.mark.parametrize("date, EES_answer_tuple", 
                         [(BUY_DATE_STR, set_EES_Answer(BUY_DATE_STR, 
                                    range_tuple=([0.25,0.4], [0.6,0.75], 0.05))), 
                          (SELL_DATE_STR, set_EES_Answer(SELL_DATE_STR,
                                    range_tuple=([0.6,0.75], [0.25,0.4], 0.95))),
                          (NEUTRAL_DATE_STR, set_EES_Answer(NEUTRAL_DATE_STR,
                                    range_tuple=(['NA','NA'], ['NA','NA'], 'NA')))]) 
def test_MRStrategyArgus_set_EES(date, EES_answer_tuple)->None:
    Test = SingleRun(date)

    apc_curve_lag5, history_data_lag5 = read.extract_lag_data(Test.signal_data, 
                                                              Test.history_data_daily, 
                                                              Test.this_date)
    MR = MRStrategyArgus(Test.curve_this_date)

    # Run the programme.
    strategy_info, qunatile_info = MR.gen_data(history_data_lag5, 
                                                       apc_curve_lag5)
        
    direction, cond_info = MR.run_cond(strategy_info, Test.open_price)
    
    entry_price, exit_price, stop_loss = MR.set_EES(
                                buy_range=([0.25,0.4],[0.6,0.75],0.05), 
                            sell_range =([0.6,0.75],[0.25,0.4],0.95))
    
    #Correct answers
    entry_price_answer = EES_answer_tuple[0]
    exit_price_answer = EES_answer_tuple[1]
    stop_loss_answer = EES_answer_tuple[2]
    
    #print(entry_price, exit_price, stop_loss)
    assert all(entry_price[i] == entry_price_answer[i] for i,_ in enumerate(entry_price))
    assert all(exit_price[i] == exit_price_answer[i] for i,_ in enumerate(exit_price))
    assert stop_loss == stop_loss_answer
    
