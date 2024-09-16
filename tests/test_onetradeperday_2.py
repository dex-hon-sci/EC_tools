#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 29 16:50:39 2024

@author: dexter


"""

import datetime as datetime

from EC_tools.portfolio import Portfolio
from EC_tools.position import PositionStatus
from EC_tools.trade import OneTradePerDay_2
from EC_tools.backtest import extract_intraday_minute_data, \
                              prepare_signal_interest, plot_in_backtest
from crudeoil_future_const import DATA_FILEPATH, RESULT_FILEPATH
import EC_tools.read as read


FILENAME_MINUTE = DATA_FILEPATH +"/history_data/Minute/CL.001"
FILENSME_BUYSELL_SIGNALS = RESULT_FILEPATH + "/argus_exact_signal/argus_exact_signal_CLc1_full.csv"
#SIGNAL_FILENAME = DATA_FILEPATH + "/APC_latest/APC_latest_CLc1.csv"   
def read_CSVfiles():
    histroy_intraday_data = read.read_reformat_Portara_minute_data(FILENAME_MINUTE)
    signal_table = prepare_signal_interest(FILENSME_BUYSELL_SIGNALS, trim = False)
    return histroy_intraday_data, signal_table

# Read the input files once
histroy_intraday_data, signal_table = read_CSVfiles()

def setup_trade_test(date_interest, open_hr, close_hr, direction, 
                     histroy_intraday_data, signal_table, add_extra_asset = False):
    P1 = Portfolio()

    # Use one day to test if the trade logic works
    USD_initial = {'name':"USD", 'quantity': 10_000_000, 'unit':"dollars", 
                   'asset_type':"Cash", 'misc':{}} # initial fund

    P1.add(USD_initial, datetime= datetime.datetime(2020,12,30))
    
    if add_extra_asset:
        CL_extra = {'name':"CLc1", 'quantity': 25, 'unit':"contracts", 
                    'asset_type':"Future", 'misc':{}} # extra asset to test auto_unload
        P1.add(CL_extra, datetime= datetime.datetime(2020,12,31))
    
    #histroy_intraday_data = read.read_reformat_Portara_minute_data(FILENAME_MINUTE)
    #signal_table = prepare_signal_interest(FILENSME_BUYSELL_SIGNALS, trim = False)
    
    
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

#setup_tuple = setup_trade_test

def onetradeperday(date_interest, direction, 
                   close_exit_or_not: bool = True,
                   auto_unload_all: bool = False,
                   add_extra_asset: bool = False):
    # Setting up the trade itself. First load the parameters
    give_obj_name = "USD"
    get_obj_name = "CLc1"
    open_hr, close_hr = '0330', '2000'
    

    # set up the test
    P1, day, target_entry, target_exit, \
    stop_exit, open_hr_dt, close_hr_dt = setup_trade_test(date_interest, 
                                                          open_hr, close_hr,
                                                          direction,
                                                          histroy_intraday_data, 
                                                          signal_table,
                                                          add_extra_asset = add_extra_asset)
            
    open_hr_dt, open_price = read.find_closest_price(day,
                                                     target_hr= open_hr,
                                                     direction='forward')
    
    
    close_hr_dt, close_price = read.find_closest_price(day,
                                                       target_hr= close_hr,
                                                       direction='backward')

    EES_dict = read.find_minute_EES(day, 
                                    target_entry, target_exit, stop_exit,
                                    open_hr=open_hr_dt, close_hr=close_hr_dt, 
                                    direction = direction)
    #print(EES_dict)
    print('1')
    #print('day', day, read.find_crossover(day['Open'].to_numpy(), stop_exit))
    #print(target_entry, target_exit, stop_exit)
    
    T = OneTradePerDay_2(P1)
    T.close_exit_or_not = close_exit_or_not
    T.auto_unload_all = auto_unload_all
    
    # this is the main function to be tested
    trade_open, trade_close, pos_dict, exec_pos_dict = \
                                            T.run_trade(EES_dict,  
                                                        give_obj_name, 
                                                        get_obj_name, 
                                                        50, 
                                                        target_entry, 
                                                        target_exit, 
                                                        stop_exit, 
                                                        open_hr=open_hr_dt, 
                                                        close_hr=close_hr_dt,
                                                        direction = direction)
                                          
    #print(EES_dict, trade_open, trade_close)
    print('2')

    
    plot_in_backtest(date_interest, get_obj_name,
                     EES_dict, direction, plot_or_not=False)

    return P1, day, target_entry, target_exit, \
           stop_exit, open_hr_dt, close_hr_dt, EES_dict, trade_open, \
           trade_close, pos_dict, exec_pos_dict
            
#%%
# Test dates inputs
date_interest_no_entry_buy = "2023-12-29" # no entry test case (Buy) Done
date_interest_normal_exit_buy = "2021-04-01" #  normal exit case (Buy) Done
date_interest_stop_loss_buy = "2021-08-04" # stop loss test case (Buy) Done
date_interest_close_exit_buy = "2022-11-18" #  sell at close case (Buy) Done

date_interest_no_entry_sell = "2023-04-13" # no entry test case (Sell) Done
date_interest_normal_exit_sell = "2023-05-24" #  normal exit case (Sell) 
date_interest_stop_loss_sell = "2021-04-14" # stop loss test case (Sell) Done
date_interest_close_exit_sell = "2022-10-27" #  sell at close case (Sell) Done
############################################################################
# Test area
############################################################################
# test Buy case, 1) no trade, normal exit, stop loss, close case
# test Sell case, 1) no trade, normal exit, stop loss, close case

def test_onetradeperday_buy_noentry() -> None:   
    give_obj_name = "USD"
    
    P1, day, \
    target_entry, target_exit, stop_exit, \
    open_hr_dt, close_hr_dt, \
    EES_dict, trade_open, trade_close, \
    pos_dict, exec_pos_dict = onetradeperday(date_interest_no_entry_buy,'Buy')

    assert pos_dict['entry_pos'].status == PositionStatus.VOID
    assert pos_dict['exit_pos'].status == PositionStatus.VOID
    assert pos_dict['stop_pos'].status == PositionStatus.VOID
    assert pos_dict['close_pos'].status == PositionStatus.VOID
    assert exec_pos_dict['opening_pos'] == None
    assert exec_pos_dict['closing_pos'] == None

    USD_amount = P1.master_table[P1.master_table['name'] == give_obj_name\
                                 ]['quantity'].iloc[0]
        
    print(P1.pool)
    assert USD_amount == 10000000
    assert len(P1.pool) == 1
    

def test_onetradeperday_buy_normalexit()->None:
    # Setting up the trade itself. First load the parameters
    give_obj_name = "USD"
    get_obj_name = "CLc1"
    
    P1, day, \
    target_entry, target_exit, stop_exit, \
    open_hr_dt, close_hr_dt, \
    EES_dict, trade_open, trade_close, \
    pos_dict, exec_pos_dict = onetradeperday(date_interest_normal_exit_buy,'Buy')

    assert pos_dict['entry_pos'].status == PositionStatus.FILLED
    assert pos_dict['exit_pos'].status == PositionStatus.FILLED
    assert pos_dict['stop_pos'].status == PositionStatus.VOID
    assert pos_dict['close_pos'].status == PositionStatus.VOID
    assert exec_pos_dict['opening_pos'].status == PositionStatus.FILLED
    assert exec_pos_dict['closing_pos'].status == PositionStatus.FILLED
    
    USD_amount = P1.master_table[P1.master_table['name'] == give_obj_name\
                                 ]['quantity'].iloc[0]
    CL_amount = P1.master_table[P1.master_table['name'] == get_obj_name\
                                ]['quantity'].iloc[0]

    assert USD_amount > 10000000
    assert CL_amount < 1
    assert len(P1.pool) == 6 #Initial fund + 4 Four exchanges + Fee = 6 entries
    print(USD_amount, P1.pool)
    
def test_onetradeperday_buy_stoploss() -> None:   
    give_obj_name = "USD"
    get_obj_name = "CLc1"
    
    P1, day, \
    target_entry, target_exit, stop_exit, \
    open_hr_dt, close_hr_dt, \
    EES_dict, trade_open, trade_close, \
    pos_dict, exec_pos_dict = onetradeperday(date_interest_stop_loss_buy,'Buy')

    print("target_entry, target_exit", target_entry, target_exit)
    assert pos_dict['entry_pos'].status == PositionStatus.FILLED
    assert pos_dict['exit_pos'].status == PositionStatus.VOID
    assert pos_dict['stop_pos'].status == PositionStatus.FILLED
    assert pos_dict['close_pos'].status == PositionStatus.VOID
    assert exec_pos_dict['opening_pos'].status == PositionStatus.FILLED
    assert exec_pos_dict['closing_pos'].status == PositionStatus.FILLED
    USD_amount = P1.master_table[P1.master_table['name'] == give_obj_name\
                                 ]['quantity'].iloc[0]
    CL_amount = P1.master_table[P1.master_table['name'] == get_obj_name\
                                ]['quantity'].iloc[0]
        
    assert USD_amount < 10000000
    assert CL_amount < 1
    assert len(P1.pool) == 6
    
def test_onetradeperday_buy_closeexit() -> None:   
    give_obj_name = "USD"
    get_obj_name = "CLc1"
    
    P1, day, \
    target_entry, target_exit, stop_exit, \
    open_hr_dt, close_hr_dt, \
    EES_dict, trade_open, trade_close, \
    pos_dict, exec_pos_dict = onetradeperday(date_interest_close_exit_buy,'Buy')
    
    print("target_entry, target_exit", target_entry, target_exit)
    print("pos_dict", pos_dict)
    assert pos_dict['entry_pos'].status == PositionStatus.FILLED
    assert pos_dict['exit_pos'].status == PositionStatus.VOID
    assert pos_dict['stop_pos'].status == PositionStatus.VOID
    assert pos_dict['close_pos'].status == PositionStatus.FILLED
    assert exec_pos_dict['opening_pos'].status == PositionStatus.FILLED
    assert exec_pos_dict['closing_pos'].status == PositionStatus.FILLED

    CL_amount = P1.master_table[P1.master_table['name'] == get_obj_name\
                                ]['quantity'].iloc[0]
        
    assert CL_amount < 1
    assert len(P1.pool) == 6
  
test_onetradeperday_buy_noentry() 
#test_onetradeperday_buy_normalexit()
#test_onetradeperday_buy_stoploss()
############################################################################
#Sell side test
def test_onetradeperday_sell_noentry() -> None:   
    give_obj_name = "USD"
    
    P1, day, \
    target_entry, target_exit, stop_exit, \
    open_hr_dt, close_hr_dt, \
    EES_dict, trade_open, trade_close, \
    pos_dict, exec_pos_dict = onetradeperday(date_interest_no_entry_sell,'Sell')

    assert pos_dict['entry_pos'].status == PositionStatus.VOID
    assert pos_dict['exit_pos'].status == PositionStatus.VOID
    assert pos_dict['stop_pos'].status == PositionStatus.VOID
    assert pos_dict['close_pos'].status == PositionStatus.VOID
    assert exec_pos_dict['opening_pos'] == None
    assert exec_pos_dict['closing_pos'] == None

    USD_amount = P1.master_table[P1.master_table['name'] == give_obj_name\
                                 ]['quantity'].iloc[0]
        
    #print(P1.pool)
    assert USD_amount == 10000000
    assert len(P1.pool) == 1

def test_onetradeperday_sell_normalexit()->None:
    # Setting up the trade itself. First load the parameters
    give_obj_name = "USD"
    get_obj_name = "CLc1"
    
    P1, day, \
    target_entry, target_exit, stop_exit, \
    open_hr_dt, close_hr_dt, \
    EES_dict, trade_open, trade_close, \
    pos_dict, exec_pos_dict = onetradeperday(date_interest_normal_exit_sell,'Sell')

    assert pos_dict['entry_pos'].status == PositionStatus.FILLED
    assert pos_dict['exit_pos'].status == PositionStatus.FILLED
    assert pos_dict['stop_pos'].status == PositionStatus.VOID
    assert pos_dict['close_pos'].status == PositionStatus.VOID
    assert exec_pos_dict['opening_pos'].status == PositionStatus.FILLED
    assert exec_pos_dict['closing_pos'].status == PositionStatus.FILLED

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
    
    P1, day, \
    target_entry, target_exit, stop_exit, \
    open_hr_dt, close_hr_dt, \
    EES_dict, trade_open, trade_close, \
    pos_dict, exec_pos_dict = onetradeperday(date_interest_stop_loss_sell,'Sell')


    assert pos_dict['entry_pos'].status == PositionStatus.FILLED
    assert pos_dict['exit_pos'].status == PositionStatus.VOID
    assert pos_dict['stop_pos'].status == PositionStatus.FILLED
    assert pos_dict['close_pos'].status == PositionStatus.VOID
    assert exec_pos_dict['opening_pos'].status == PositionStatus.FILLED
    assert exec_pos_dict['closing_pos'].status == PositionStatus.FILLED

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
    
    P1, day, \
    target_entry, target_exit, stop_exit, \
    open_hr_dt, close_hr_dt, \
    EES_dict, trade_open, trade_close, \
    pos_dict, exec_pos_dict = onetradeperday(date_interest_close_exit_sell,'Sell')
    
    assert pos_dict['entry_pos'].status == PositionStatus.FILLED
    assert pos_dict['exit_pos'].status == PositionStatus.VOID
    assert pos_dict['stop_pos'].status == PositionStatus.VOID
    assert pos_dict['close_pos'].status == PositionStatus.FILLED
    assert exec_pos_dict['opening_pos'].status == PositionStatus.FILLED
    assert exec_pos_dict['closing_pos'].status == PositionStatus.FILLED

    CL_amount = P1.master_table[P1.master_table['name'] == get_obj_name\
                                ]['quantity'].iloc[0]
    debt_amount = P1.master_table[P1.master_table['misc'] == {'debt'}\
                                   ]['quantity'].iloc[0]     
    #print(P1.master_table)

    assert CL_amount < 1e-5
    assert len(P1.pool) == 8
    
# =============================================================================
# ### close_exit not allowed
# First three scenario should have the same results
# =============================================================================
# BUY Directions
def test_onetradeperday_buy_noentry_nocloseexit() -> None:   

    give_obj_name = "USD"
    
    P1, day, \
    target_entry, target_exit, stop_exit, \
    open_hr_dt, close_hr_dt, \
    EES_dict, trade_open, trade_close, \
    pos_dict, exec_pos_dict = onetradeperday(date_interest_no_entry_buy,'Buy',
                                             close_exit_or_not = False)

    assert pos_dict['entry_pos'].status == PositionStatus.VOID
    assert pos_dict['exit_pos'].status == PositionStatus.VOID
    assert pos_dict['stop_pos'].status == PositionStatus.VOID
    assert list(pos_dict.keys()) == ['entry_pos', 'exit_pos', 'stop_pos']
    assert exec_pos_dict['opening_pos'] == None
    assert exec_pos_dict['closing_pos'] == None

    USD_amount = P1.master_table[P1.master_table['name'] == give_obj_name\
                                 ]['quantity'].iloc[0]
        
    print(P1.pool)
    assert USD_amount == 10000000
    assert len(P1.pool) == 1
    

def test_onetradeperday_buy_normalexit_nocloseexit()->None:
    # Setting up the trade itself. First load the parameters
    give_obj_name = "USD"
    get_obj_name = "CLc1"
    
    P1, day, \
    target_entry, target_exit, stop_exit, \
    open_hr_dt, close_hr_dt, \
    EES_dict, trade_open, trade_close, \
    pos_dict, exec_pos_dict = onetradeperday(date_interest_normal_exit_buy,'Buy',
                                             close_exit_or_not = False)

    assert pos_dict['entry_pos'].status == PositionStatus.FILLED
    assert pos_dict['exit_pos'].status == PositionStatus.FILLED
    assert pos_dict['stop_pos'].status == PositionStatus.VOID
    assert list(pos_dict.keys()) == ['entry_pos', 'exit_pos', 'stop_pos']
    assert exec_pos_dict['opening_pos'].status == PositionStatus.FILLED
    assert exec_pos_dict['closing_pos'].status == PositionStatus.FILLED
    
    USD_amount = P1.master_table[P1.master_table['name'] == give_obj_name\
                                 ]['quantity'].iloc[0]
    CL_amount = P1.master_table[P1.master_table['name'] == get_obj_name\
                                ]['quantity'].iloc[0]

    assert USD_amount > 10000000
    assert CL_amount < 1
    assert len(P1.pool) == 6 #Initial fund + 4 Four exchanges + Fee = 6 entries
    print(USD_amount, P1.pool)
    
def test_onetradeperday_buy_stoploss_nocloseexit() -> None:   
    give_obj_name = "USD"
    get_obj_name = "CLc1"
    
    P1, day, \
    target_entry, target_exit, stop_exit, \
    open_hr_dt, close_hr_dt, \
    EES_dict, trade_open, trade_close, \
    pos_dict, exec_pos_dict = onetradeperday(date_interest_stop_loss_buy,'Buy',
                                             close_exit_or_not = False)

    print("target_entry, target_exit", target_entry, target_exit)
    assert pos_dict['entry_pos'].status == PositionStatus.FILLED
    assert pos_dict['exit_pos'].status == PositionStatus.VOID
    assert pos_dict['stop_pos'].status == PositionStatus.FILLED
    assert list(pos_dict.keys()) == ['entry_pos', 'exit_pos', 'stop_pos']
    assert exec_pos_dict['opening_pos'].status == PositionStatus.FILLED
    assert exec_pos_dict['closing_pos'].status == PositionStatus.FILLED
    
    USD_amount = P1.master_table[P1.master_table['name'] == give_obj_name\
                                 ]['quantity'].iloc[0]
    CL_amount = P1.master_table[P1.master_table['name'] == get_obj_name\
                                ]['quantity'].iloc[0]
        
    assert USD_amount < 10000000
    assert CL_amount < 1
    assert len(P1.pool) == 6
    
def test_onetradeperday_buy_closeexit_nocloseexit() -> None:   
    give_obj_name = "USD"
    get_obj_name = "CLc1"
    
    P1, day, \
    target_entry, target_exit, stop_exit, \
    open_hr_dt, close_hr_dt, \
    EES_dict, trade_open, trade_close, \
    pos_dict, exec_pos_dict = onetradeperday(date_interest_close_exit_buy,'Buy',
                                             close_exit_or_not = False)
    
    print("target_entry, target_exit", target_entry, target_exit)
    print("pos_dict", pos_dict)
    assert pos_dict['entry_pos'].status == PositionStatus.FILLED
    assert pos_dict['exit_pos'].status == PositionStatus.VOID
    assert pos_dict['stop_pos'].status == PositionStatus.VOID
    assert list(pos_dict.keys()) == ['entry_pos', 'exit_pos', 'stop_pos']
    assert exec_pos_dict['opening_pos'].status == PositionStatus.FILLED
    assert exec_pos_dict['closing_pos'] == None
    assert list(exec_pos_dict.keys()) == ['opening_pos', 'closing_pos']

    CL_amount = P1.master_table[P1.master_table['name'] == get_obj_name\
                                ]['quantity'].iloc[0]
        
    assert CL_amount == 50
    assert len(P1.pool) == 3

# =============================================================================
# # SELL direction
# =============================================================================
def test_onetradeperday_sell_noentry_nocloseexit() -> None:   
    give_obj_name = "USD"
    
    P1, day, \
    target_entry, target_exit, stop_exit, \
    open_hr_dt, close_hr_dt, \
    EES_dict, trade_open, trade_close, \
    pos_dict, exec_pos_dict = onetradeperday(date_interest_no_entry_sell,'Sell',
                                             close_exit_or_not = False)

    assert pos_dict['entry_pos'].status == PositionStatus.VOID
    assert pos_dict['exit_pos'].status == PositionStatus.VOID
    assert pos_dict['stop_pos'].status == PositionStatus.VOID
    assert list(pos_dict.keys()) == ['entry_pos', 'exit_pos', 'stop_pos']
    assert exec_pos_dict['opening_pos'] == None
    assert exec_pos_dict['closing_pos'] == None

    USD_amount = P1.master_table[P1.master_table['name'] == give_obj_name\
                                 ]['quantity'].iloc[0]
        
    #print(P1.pool)
    assert USD_amount == 10000000
    assert len(P1.pool) == 1

def test_onetradeperday_sell_normalexit_nocloseexit()->None:
    # Setting up the trade itself. First load the parameters
    give_obj_name = "USD"
    get_obj_name = "CLc1"
    
    P1, day, \
    target_entry, target_exit, stop_exit, \
    open_hr_dt, close_hr_dt, \
    EES_dict, trade_open, trade_close, \
    pos_dict, exec_pos_dict = onetradeperday(date_interest_normal_exit_sell,'Sell',
                                             close_exit_or_not = False)

    assert pos_dict['entry_pos'].status == PositionStatus.FILLED
    assert pos_dict['exit_pos'].status == PositionStatus.FILLED
    assert pos_dict['stop_pos'].status == PositionStatus.VOID
    assert list(pos_dict.keys()) == ['entry_pos', 'exit_pos', 'stop_pos']
    assert exec_pos_dict['opening_pos'].status == PositionStatus.FILLED
    assert exec_pos_dict['closing_pos'].status == PositionStatus.FILLED

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
    assert debt_amount < 1e-5
    assert CL_amount < 1e-5

def test_onetradeperday_sell_stoploss_nocloseexit() -> None:   
    give_obj_name = "USD"
    get_obj_name = "CLc1"
    
    P1, day, \
    target_entry, target_exit, stop_exit, \
    open_hr_dt, close_hr_dt, \
    EES_dict, trade_open, trade_close, \
    pos_dict, exec_pos_dict = onetradeperday(date_interest_stop_loss_sell,'Sell',
                                             close_exit_or_not = False)


    assert pos_dict['entry_pos'].status == PositionStatus.FILLED
    assert pos_dict['exit_pos'].status == PositionStatus.VOID
    assert pos_dict['stop_pos'].status == PositionStatus.FILLED
    assert list(pos_dict.keys()) == ['entry_pos', 'exit_pos', 'stop_pos']
    assert exec_pos_dict['opening_pos'].status == PositionStatus.FILLED
    assert exec_pos_dict['closing_pos'].status == PositionStatus.FILLED

    USD_amount = P1.master_table[P1.master_table['name'] == give_obj_name\
                                 ]['quantity'].iloc[0]
    CL_amount = P1.master_table[P1.master_table['name'] == get_obj_name\
                                ]['quantity'].iloc[0]
    debt_amount = P1.master_table[P1.master_table['misc'] == {'debt'}\
                                    ]['quantity'].iloc[0]
    #print(P1.pool, CL_amount)
    #print(P1.master_table)
    assert USD_amount < 10000000
    assert len(P1.pool) == 8
    assert debt_amount < 1e-5
    assert CL_amount < 1e-5
    
def test_onetradeperday_sell_closeexit_nocloseexit() -> None:   
    give_obj_name = "USD"
    get_obj_name = "CLc1"
    
    P1, day, \
    target_entry, target_exit, stop_exit, \
    open_hr_dt, close_hr_dt, \
    EES_dict, trade_open, trade_close, \
    pos_dict, exec_pos_dict = onetradeperday(date_interest_close_exit_sell,'Sell',
                                             close_exit_or_not = False)
    
    assert pos_dict['entry_pos'].status == PositionStatus.FILLED
    assert pos_dict['exit_pos'].status == PositionStatus.VOID
    assert pos_dict['stop_pos'].status == PositionStatus.VOID
    assert list(pos_dict.keys()) == ['entry_pos', 'exit_pos', 'stop_pos']
    assert exec_pos_dict['opening_pos'].status == PositionStatus.FILLED
    assert exec_pos_dict['closing_pos'] == None
    assert list(exec_pos_dict.keys()) == ['opening_pos', 'closing_pos']


    CL_amount = P1.master_table[P1.master_table['name'] == get_obj_name\
                                ]['quantity'].iloc[0]
    debt_amount = P1.master_table[P1.master_table['misc'] == {'debt'}\
                                   ]['quantity'].iloc[0]     
    print("P1.pool", P1.pool, P1.master_table)
    assert CL_amount < 1e-5
    assert len(P1.pool) == 5
    assert debt_amount == -50
    
# =============================================================================
# ### test auto upload all 
# In the setup, we added an extra 25 contracts of CLc1 to the Portfolio
# with auto_unload_all turned on, it should sell/buy-back all 75 contracts
# =============================================================================
# =============================================================================
# # BUY Directions
# =============================================================================
def test_onetradeperday_buy_noentry_autounload() -> None:   

    give_obj_name = "USD"
    
    P1, day, \
    target_entry, target_exit, stop_exit, \
    open_hr_dt, close_hr_dt, \
    EES_dict, trade_open, trade_close, \
    pos_dict, exec_pos_dict = onetradeperday(date_interest_no_entry_buy,'Buy',
                                             add_extra_asset= True,
                                             auto_unload_all= True)

    assert pos_dict['entry_pos'].status == PositionStatus.VOID
    assert pos_dict['exit_pos'].status == PositionStatus.VOID
    assert pos_dict['stop_pos'].status == PositionStatus.VOID
    assert pos_dict['close_pos'].status == PositionStatus.VOID
    assert exec_pos_dict['opening_pos'] == None
    assert exec_pos_dict['closing_pos'] == None

    USD_amount = P1.master_table[P1.master_table['name'] == give_obj_name\
                                 ]['quantity'].iloc[0]
        
    print(P1.pool)
    assert USD_amount == 10000000
    assert len(P1.pool) == 2
    

def test_onetradeperday_buy_normalexit_autounload() -> None:
    # Setting up the trade itself. First load the parameters
    give_obj_name = "USD"
    get_obj_name = "CLc1"
    
    P1, day, \
    target_entry, target_exit, stop_exit, \
    open_hr_dt, close_hr_dt, \
    EES_dict, trade_open, trade_close, \
    pos_dict, exec_pos_dict = onetradeperday(date_interest_normal_exit_buy,'Buy',
                                             close_exit_or_not=True,
                                             add_extra_asset= True,
                                             auto_unload_all= True)
    print('pos_dict', pos_dict)
    print("exec_pos_dict['closing_pos']", exec_pos_dict['closing_pos'])
    
    assert pos_dict['entry_pos'].status == PositionStatus.FILLED
    assert pos_dict['exit_pos'].status == PositionStatus.FILLED
    assert pos_dict['stop_pos'].status == PositionStatus.VOID
    assert pos_dict['close_pos'].status == PositionStatus.VOID
    assert exec_pos_dict['opening_pos'].status == PositionStatus.FILLED
    assert exec_pos_dict['closing_pos'].status == PositionStatus.FILLED
    
    USD_amount = P1.master_table[P1.master_table['name'] == give_obj_name\
                                 ]['quantity'].iloc[0]
    CL_amount = P1.master_table[P1.master_table['name'] == get_obj_name\
                                ]['quantity'].iloc[0]

    print(USD_amount, P1.pool, P1.master_table)
    print(len(P1.pool))
    assert exec_pos_dict['closing_pos'].get_obj['quantity'] == 50
    assert USD_amount > 10000000 + 25*pos_dict['entry_pos']._price*1000
    assert CL_amount < 1
    assert len(P1.pool) == 10 #Initial fund (2) + 4 Four exchanges + Fee + 2 extra + Fee = 10 entries
    

def test_onetradeperday_buy_stoploss_autounload() -> None:   
    give_obj_name = "USD"
    get_obj_name = "CLc1"
    
    P1, day, \
    target_entry, target_exit, stop_exit, \
    open_hr_dt, close_hr_dt, \
    EES_dict, trade_open, trade_close, \
    pos_dict, exec_pos_dict = onetradeperday(date_interest_stop_loss_buy,'Buy',
                                             add_extra_asset= True,
                                             auto_unload_all= True)

    print("target_entry, target_exit", target_entry, target_exit)
    assert pos_dict['entry_pos'].status == PositionStatus.FILLED
    assert pos_dict['exit_pos'].status == PositionStatus.VOID
    assert pos_dict['stop_pos'].status == PositionStatus.FILLED
    assert pos_dict['close_pos'].status == PositionStatus.VOID
    assert exec_pos_dict['opening_pos'].status == PositionStatus.FILLED
    assert exec_pos_dict['closing_pos'].status == PositionStatus.FILLED
    
    USD_amount = P1.master_table[P1.master_table['name'] == give_obj_name\
                                 ]['quantity'].iloc[0]
    CL_amount = P1.master_table[P1.master_table['name'] == get_obj_name\
                                ]['quantity'].iloc[0]
    print(USD_amount, P1.pool, P1.master_table)
    assert USD_amount < 10000000 + 25*pos_dict['entry_pos']._price*1000
    assert CL_amount < 1
    assert len(P1.pool) == 10
    

def test_onetradeperday_buy_closeexit_autounload() -> None:   
    give_obj_name = "USD"
    get_obj_name = "CLc1"
    
    P1, day, \
    target_entry, target_exit, stop_exit, \
    open_hr_dt, close_hr_dt, \
    EES_dict, trade_open, trade_close, \
    pos_dict, exec_pos_dict = onetradeperday(date_interest_close_exit_buy,'Buy',
                                             add_extra_asset= True,
                                             auto_unload_all= True)
    
    print("target_entry, target_exit", target_entry, target_exit)
    print("pos_dict", pos_dict)
    assert pos_dict['entry_pos'].status == PositionStatus.FILLED
    assert pos_dict['exit_pos'].status == PositionStatus.VOID
    assert pos_dict['stop_pos'].status == PositionStatus.VOID
    assert pos_dict['close_pos'].status == PositionStatus.FILLED
    assert exec_pos_dict['opening_pos'].status == PositionStatus.FILLED
    assert exec_pos_dict['closing_pos'].status == PositionStatus.FILLED
    assert list(exec_pos_dict.keys()) == ['opening_pos', 'closing_pos']

    CL_amount = P1.master_table[P1.master_table['name'] == get_obj_name\
                                ]['quantity'].iloc[0]
        
    assert CL_amount < 1e-5
    assert len(P1.pool) == 10
    
#test_onetradeperday_buy_noentry_autounload()    
#test_onetradeperday_buy_normalexit_autounload()
#test_onetradeperday_buy_stoploss_autounload()
#test_onetradeperday_buy_closeexit_autounload()

# =============================================================================
# # SELL Directions
# =============================================================================
def test_onetradeperday_sell_noentry_autounload() -> None:   
    give_obj_name = "USD"
    
    P1, day, \
    target_entry, target_exit, stop_exit, \
    open_hr_dt, close_hr_dt, \
    EES_dict, trade_open, trade_close, \
    pos_dict, exec_pos_dict = onetradeperday(date_interest_no_entry_sell,'Sell',
                                             add_extra_asset= True,
                                             auto_unload_all= True)

    assert pos_dict['entry_pos'].status == PositionStatus.VOID
    assert pos_dict['exit_pos'].status == PositionStatus.VOID
    assert pos_dict['stop_pos'].status == PositionStatus.VOID
    assert pos_dict['close_pos'].status == PositionStatus.VOID
    assert exec_pos_dict['opening_pos'] == None
    assert exec_pos_dict['closing_pos'] == None

    USD_amount = P1.master_table[P1.master_table['name'] == give_obj_name\
                                 ]['quantity'].iloc[0]
        
    #print(P1.pool)
    assert USD_amount == 10000000
    assert len(P1.pool) == 2

def test_onetradeperday_sell_normalexit_autounload()->None:
    # Setting up the trade itself. First load the parameters
    give_obj_name = "USD"
    get_obj_name = "CLc1"
    
    P1, day, \
    target_entry, target_exit, stop_exit, \
    open_hr_dt, close_hr_dt, \
    EES_dict, trade_open, trade_close, \
    pos_dict, exec_pos_dict = onetradeperday(date_interest_normal_exit_sell,'Sell',
                                             add_extra_asset= True,
                                             auto_unload_all= True)

    assert pos_dict['entry_pos'].status == PositionStatus.FILLED
    assert pos_dict['exit_pos'].status == PositionStatus.FILLED
    assert pos_dict['stop_pos'].status == PositionStatus.VOID
    assert pos_dict['close_pos'].status == PositionStatus.VOID
    assert exec_pos_dict['opening_pos'].status == PositionStatus.FILLED
    assert exec_pos_dict['closing_pos'].status == PositionStatus.FILLED

    USD_amount = P1.master_table[P1.master_table['name'] == give_obj_name\
                                 ]['quantity'].iloc[0]
    CL_amount = P1.master_table[P1.master_table['name'] == get_obj_name\
                                ]['quantity'].iloc[0]
    debt_amount = P1.master_table[P1.master_table['misc'] == {'debt'}\
                                ]['quantity'].iloc[0]
        
    print("exec_pos_dict", exec_pos_dict)
    print(exec_pos_dict['closing_pos'].get_obj['quantity'])
    print("P1.pool",P1.pool)
    print("P1.master_table", P1.master_table)
    # =============================================================================
    for PP in P1.position_pool:
        print(PP)
    # =============================================================================

    assert USD_amount > 10000000
    assert len(P1.pool) == 11 # 2 initial Fund + 6 action in Short + Fee + 2 extra execution
    assert debt_amount < 1e-5
    assert CL_amount < 1e-5
    assert exec_pos_dict['closing_pos'].get_obj['quantity'] ==50


def test_onetradeperday_sell_stoploss_autounload() -> None:   
    give_obj_name = "USD"
    get_obj_name = "CLc1"
    
    P1, day, \
    target_entry, target_exit, stop_exit, \
    open_hr_dt, close_hr_dt, \
    EES_dict, trade_open, trade_close, \
    pos_dict, exec_pos_dict = onetradeperday(date_interest_stop_loss_sell,'Sell',
                                             add_extra_asset= True,
                                             auto_unload_all= True)


    assert pos_dict['entry_pos'].status == PositionStatus.FILLED
    assert pos_dict['exit_pos'].status == PositionStatus.VOID
    assert pos_dict['stop_pos'].status == PositionStatus.FILLED
    assert pos_dict['close_pos'].status == PositionStatus.VOID
    assert exec_pos_dict['opening_pos'].status == PositionStatus.FILLED
    assert exec_pos_dict['closing_pos'].status == PositionStatus.FILLED

    USD_amount = P1.master_table[P1.master_table['name'] == give_obj_name\
                                 ]['quantity'].iloc[0]
    CL_amount = P1.master_table[P1.master_table['name'] == get_obj_name\
                                ]['quantity'].iloc[0]
    debt_amount = P1.master_table[P1.master_table['misc'] == {'debt'}\
                                    ]['quantity'].iloc[0]
    #print(P1.pool, CL_amount)
    #print(P1.master_table)
    assert USD_amount < 10000000 + 25*pos_dict['entry_pos']._price*1000
    assert len(P1.pool) == 11
    assert debt_amount < 1e-5
    assert CL_amount < 1e-5
    
def test_onetradeperday_sell_closeexit_autounload() -> None:   
    give_obj_name = "USD"
    get_obj_name = "CLc1"
    
    P1, day, \
    target_entry, target_exit, stop_exit, \
    open_hr_dt, close_hr_dt, \
    EES_dict, trade_open, trade_close, \
    pos_dict, exec_pos_dict = onetradeperday(date_interest_close_exit_sell,'Sell',
                                             add_extra_asset= True,
                                             auto_unload_all= True)
    
    assert pos_dict['entry_pos'].status == PositionStatus.FILLED
    assert pos_dict['exit_pos'].status == PositionStatus.VOID
    assert pos_dict['stop_pos'].status == PositionStatus.VOID
    assert pos_dict['close_pos'].status == PositionStatus.FILLED
    assert exec_pos_dict['opening_pos'].status == PositionStatus.FILLED
    assert exec_pos_dict['closing_pos'].status == PositionStatus.FILLED
    assert list(exec_pos_dict.keys()) == ['opening_pos', 'closing_pos']


    CL_amount = P1.master_table[P1.master_table['name'] == get_obj_name\
                                ]['quantity'].iloc[0]
    debt_amount = P1.master_table[P1.master_table['misc'] == {'debt'}\
                                   ]['quantity'].iloc[0]     
    print("P1.pool", P1.pool, P1.master_table)
    assert CL_amount < 1e-5
    assert len(P1.pool) == 11
    assert debt_amount< 1e-5
    
test_onetradeperday_sell_closeexit_autounload()