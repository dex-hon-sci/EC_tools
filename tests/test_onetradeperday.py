#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 29 16:50:39 2024

@author: dexter
"""

# make a Portfolio

from EC_tools.portfolio import Asset, Portfolio
from EC_tools.position import Position, ExecutePosition, PositionStatus
from EC_tools.trade import Trade, OneTradePerDay
from EC_tools.backtest import extract_intraday_minute_data, \
                            prepare_signal_interest, plot_in_backtest
from crudeoil_future_const import DATA_FILEPATH, RESULT_FILEPATH
import EC_tools.read as read



FILENAME_MINUTE = DATA_FILEPATH +"/history_data/Minute/CL.001"
FILENSME_BUYSELL_SIGNALS = RESULT_FILEPATH + "/argus_exact_signal/argus_exact_signal_CLc1_full.csv"
SIGNAL_FILENAME = DATA_FILEPATH + "/APC_latest/APC_latest_CLc1.csv"   

def setup_trade_test(date_interest, open_hr, close_hr, direction):
        
    # Use one day to test if the trade logic works
    P1 = Portfolio()
    USD_initial = {'name':"USD", 'quantity': 10_000_000, 'unit':"dollars", 
                   'asset_type':"Cash", 'misc':{}} # initial fund
    P1.add(USD_initial)
    
    histroy_intraday_data = read.read_reformat_Portara_minute_data(FILENAME_MINUTE)
    signal_table = prepare_signal_interest(FILENSME_BUYSELL_SIGNALS, trim = False)
    
    
    day = extract_intraday_minute_data(histroy_intraday_data, date_interest, 
                                       open_hr=open_hr, close_hr=close_hr)
    signal_table = signal_table[signal_table['Date'] == date_interest] 
    
    #print(signal_table.iloc[0])
    
    target_entry, target_exit, stop_exit = float(signal_table['Entry_Price'].iloc[0]), \
                                           float(signal_table['Exit_Price'].iloc[0]), \
                                           float(signal_table['StopLoss_Price'].iloc[0])
    
    print(day['Date'].iloc[0], direction, target_entry, target_exit, stop_exit)
    
    open_hr_dt, open_price = read.find_closest_price(day,
                                                       target_hr= open_hr,
                                                       direction='forward')
    
    print('open',open_hr_dt, open_price)
    
    close_hr_dt, close_price = read.find_closest_price(day,
                                                       target_hr= close_hr,
                                                       direction='backward')
    print('close', close_hr_dt, close_price)
     
    
    #print(P1.master_table)
    return P1, day, target_entry, target_exit, \
           stop_exit, open_hr_dt, close_hr_dt



def onetradeperday(date_interest, direction):
    # Setting up the trade itself. First load the parameters
    give_obj_name = "USD"
    get_obj_name = "CLc1"
    open_hr, close_hr = '0330', '2000'
    

    # set up the test
    P1, day, target_entry, target_exit, \
        stop_exit, open_hr_dt, close_hr_dt = setup_trade_test(date_interest, \
                                                              open_hr, close_hr,\
                                                              direction)
            
    open_hr_dt, open_price = read.find_closest_price(day,
                                                     target_hr= open_hr,
                                                     direction='forward')
    
    
    close_hr_dt, close_price = read.find_closest_price(day,
                                                       target_hr= close_hr,
                                                       direction='backward')

    print('1')
    #print('day', day, read.find_crossover(day['Open'].to_numpy(), stop_exit))
    #print(target_entry, target_exit, stop_exit)
    # this is the main function to be tested
    EES_dict, trade_open, trade_close, pos_list, exec_pos_list = \
        OneTradePerDay(P1).run_trade(day, 
                                     give_obj_name, get_obj_name, 
                                     50, target_entry, 
                                     target_exit, stop_exit, 
                                     open_hr=open_hr_dt, 
                                     close_hr=close_hr_dt,
                                     direction = direction)
                                          
    #print(EES_dict, trade_open, trade_close)
    print('2')

    
    plot_in_backtest(date_interest, EES_dict, direction, plot_or_not=False)

    return P1, day, target_entry, target_exit, \
        stop_exit, open_hr_dt, close_hr_dt, EES_dict, trade_open, \
            trade_close, pos_list, exec_pos_list
            
#%%
############################################################################
# Test area
############################################################################
# test Buy case, 1) no trade, normal exit, stop loss, close case
# test Sell case, 1) no trade, normal exit, stop loss, close case

date_interest_no_entry_buy = "2023-12-29" # no entry test case (Buy) Done
date_interest_close_exit_buy = "2024-04-30" #  sell at close case (Buy) Done
date_interest_stop_loss_buy = "2021-08-04" # stop loss test case (Buy) Done
date_interest_normal_exit_buy = "2021-04-01" #  normal exit case (Buy) Done

    
def test_onetradeperday_buy_noentry() -> None:   
    give_obj_name = "USD"
    
    P1, day, target_entry, target_exit, \
    stop_exit, open_hr_dt, close_hr_dt, EES_dict, trade_open, \
    trade_close, pos_list, exec_pos_list = onetradeperday(date_interest_no_entry_buy,
                                                          'Buy')

    assert pos_list[0].status == PositionStatus.VOID
    assert pos_list[1].status == PositionStatus.VOID
    assert pos_list[2].status == PositionStatus.VOID
    assert pos_list[3].status == PositionStatus.VOID
    assert exec_pos_list[0] == None
    assert exec_pos_list[1] == None

    USD_amount = P1.master_table[P1.master_table['name'] == give_obj_name\
                                 ]['quantity'].iloc[0]
        
    print(P1.pool)
    assert USD_amount == 10000000
    assert len(P1.pool) == 1
    

def test_onetradeperday_buy_normalexit()->None:
    # Setting up the trade itself. First load the parameters
    give_obj_name = "USD"
    get_obj_name = "CLc1"
    
    P1, day, target_entry, target_exit, \
        stop_exit, open_hr_dt, close_hr_dt, EES_dict, trade_open, \
            trade_close, pos_list, exec_pos_list = onetradeperday(
                                                date_interest_normal_exit_buy,
                                                        'Buy')

    assert pos_list[0].status == PositionStatus.FILLED
    assert pos_list[1].status == PositionStatus.FILLED
    assert pos_list[2].status == PositionStatus.VOID
    assert pos_list[3].status == PositionStatus.VOID
    assert exec_pos_list[0].status == PositionStatus.FILLED
    assert exec_pos_list[1].status == PositionStatus.FILLED

    USD_amount = P1.master_table[P1.master_table['name'] == give_obj_name\
                                 ]['quantity'].iloc[0]
    CL_amount = P1.master_table[P1.master_table['name'] == get_obj_name\
                                ]['quantity'].iloc[0]
        
    print(P1.pool)
    print(P1.master_table)
    assert USD_amount > 10000000
    assert CL_amount < 1
    assert len(P1.pool) == 6 #Initial fund + 4 Four exchanges + Fee = 6 entries
    
def test_onetradeperday_buy_stoploss() -> None:   
    give_obj_name = "USD"
    get_obj_name = "CLc1"
    
    P1, day, target_entry, target_exit, \
        stop_exit, open_hr_dt, close_hr_dt, EES_dict, trade_open, \
            trade_close, pos_list, exec_pos_list = onetradeperday(
                                                date_interest_stop_loss_buy,
                                                        'Buy')
    print(pos_list[0].status, pos_list[1].status, 
          pos_list[2].status, pos_list[3].status)

    print(exec_pos_list[0].status, exec_pos_list[1].status)
    
    assert pos_list[0].status == PositionStatus.FILLED
    assert pos_list[1].status == PositionStatus.VOID
    assert pos_list[2].status == PositionStatus.FILLED
    assert pos_list[3].status == PositionStatus.VOID
    assert exec_pos_list[0].status == PositionStatus.FILLED
    assert exec_pos_list[1].status == PositionStatus.FILLED

    USD_amount = P1.master_table[P1.master_table['name'] == give_obj_name\
                                 ]['quantity'].iloc[0]
    CL_amount = P1.master_table[P1.master_table['name'] == get_obj_name\
                                ]['quantity'].iloc[0]
        
    assert USD_amount < 10000000
    assert CL_amount < 1
    assert len(P1.pool) == 6
    
#test_onetradeperday_buy_noentry() 
test_onetradeperday_buy_normalexit()
test_onetradeperday_buy_stoploss()

def test_onetradeperday_buy_closeexit() -> None:   
    give_obj_name = "USD"
    get_obj_name = "CLc1"
    
    P1, day, target_entry, target_exit, \
        stop_exit, open_hr_dt, close_hr_dt, EES_dict, trade_open, \
            trade_close, pos_list, exec_pos_list = onetradeperday(
                                                date_interest_close_exit_buy,
                                                        'Buy')
            
    assert pos_list[0].status == PositionStatus.FILLED
    #assert pos_list[1].status == PositionStatus.VOID
    assert pos_list[2].status == PositionStatus.VOID
    #assert pos_list[3].status == PositionStatus.FILLED
    assert exec_pos_list[0].status == PositionStatus.FILLED
    assert exec_pos_list[1].status == PositionStatus.FILLED

    CL_amount = P1.master_table[P1.master_table['name'] == get_obj_name\
                                ]['quantity'].iloc[0]
        
    assert CL_amount < 1
    assert len(P1.pool) == 6

############################################################################
#Sell side test

date_interest_no_entry_sell = "2023-04-13" # no entry test case (Sell) Done
date_interest_normal_exit_sell = "2023-05-24" #  normal exit case (Sell) 
date_interest_stop_loss_sell = "2021-04-14" # stop loss test case (Sell) Done
date_interest_close_exit_sell = "2022-10-27" #  sell at close case (Sell) Done

def test_onetradeperday_sell_noentry() -> None:   
    give_obj_name = "USD"
    
    P1, day, target_entry, target_exit, \
        stop_exit, open_hr_dt, close_hr_dt, EES_dict, trade_open, \
            trade_close, pos_list, exec_pos_list = onetradeperday(
                                                date_interest_no_entry_sell,
                                                        'Sell')

    assert pos_list[0].status == PositionStatus.VOID
    assert pos_list[1].status == PositionStatus.VOID
    assert pos_list[2].status == PositionStatus.VOID
    assert pos_list[3].status == PositionStatus.VOID
    assert exec_pos_list[0] == None
    assert exec_pos_list[1] == None

    USD_amount = P1.master_table[P1.master_table['name'] == give_obj_name\
                                 ]['quantity'].iloc[0]
        
    #print(P1.pool)
    assert USD_amount == 10000000
    assert len(P1.pool) == 1

def test_onetradeperday_sell_normalexit()->None:
    # Setting up the trade itself. First load the parameters
    give_obj_name = "USD"
    get_obj_name = "CLc1"
    
    P1, day, target_entry, target_exit, \
        stop_exit, open_hr_dt, close_hr_dt, EES_dict, trade_open, \
            trade_close, pos_list, exec_pos_list = onetradeperday(
                                                date_interest_normal_exit_sell,
                                                        'Sell')

    assert pos_list[0].status == PositionStatus.FILLED
    assert pos_list[1].status == PositionStatus.FILLED
    assert pos_list[2].status == PositionStatus.VOID
    assert pos_list[3].status == PositionStatus.VOID
    assert exec_pos_list[0].status == PositionStatus.FILLED
    assert exec_pos_list[1].status == PositionStatus.FILLED

    USD_amount = P1.master_table[P1.master_table['name'] == give_obj_name\
                                 ]['quantity'].iloc[0]
    CL_amount = P1.master_table[P1.master_table['name'] == get_obj_name\
                                ]['quantity'].iloc[0]
    debt_amount = P1.master_table[P1.master_table['misc'] == {'debt'}\
                                ]['quantity'].iloc[0]
    #print(P1.pool)
    #print(P1.master_table)
#    print(P1.log)
    #print(debt_amount)
    assert USD_amount > 10000000
    assert len(P1.pool) == 8
   # assert debt_amount == 0
    
#test_onetradeperday_sell_normalexit()   

def test_onetradeperday_sell_stoploss() -> None:   
    give_obj_name = "USD"
    get_obj_name = "CLc1"
    
    P1, day, target_entry, target_exit, \
        stop_exit, open_hr_dt, close_hr_dt, EES_dict, trade_open, \
            trade_close, pos_list, exec_pos_list = onetradeperday(
                                                date_interest_stop_loss_sell,
                                                        'Sell')


    assert pos_list[0].status == PositionStatus.FILLED
    assert pos_list[1].status == PositionStatus.VOID
    assert pos_list[2].status == PositionStatus.FILLED
    assert pos_list[3].status == PositionStatus.VOID
    assert exec_pos_list[0].status == PositionStatus.FILLED
    assert exec_pos_list[1].status == PositionStatus.FILLED

    USD_amount = P1.master_table[P1.master_table['name'] == give_obj_name\
                                 ]['quantity'].iloc[0]
    CL_amount = P1.master_table[P1.master_table['name'] == get_obj_name\
                                ]['quantity'].iloc[0]
    debt_amount = P1.master_table[P1.master_table['misc'] == {'debt'}\
                                    ]['quantity'].iloc[0]
    #print(P1.pool, CL_amount)
    #print(P1.master_table)
    assert USD_amount < 10000000
    assert CL_amount < 1e-5
    assert len(P1.pool) == 8
    
def test_onetradeperday_sell_closeexit() -> None:   
    give_obj_name = "USD"
    get_obj_name = "CLc1"
    
    P1, day, target_entry, target_exit, \
        stop_exit, open_hr_dt, close_hr_dt, EES_dict, trade_open, \
            trade_close, pos_list, exec_pos_list = onetradeperday(
                                                date_interest_close_exit_sell,
                                                        'Sell')
    assert pos_list[0].status == PositionStatus.FILLED
    assert pos_list[1].status == PositionStatus.VOID
    assert pos_list[2].status == PositionStatus.VOID
    assert pos_list[3].status == PositionStatus.FILLED
    assert exec_pos_list[0].status == PositionStatus.FILLED
    assert exec_pos_list[1].status == PositionStatus.FILLED

    CL_amount = P1.master_table[P1.master_table['name'] == get_obj_name\
                                ]['quantity'].iloc[0]
    debt_amount = P1.master_table[P1.master_table['misc'] == {'debt'}\
                                   ]['quantity'].iloc[0]     
    #print(P1.master_table)

    assert CL_amount < 1e-5
    assert len(P1.pool) == 8