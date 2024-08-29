#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# import Python package
import pandas as pd
import numpy as np
import datetime as datetime

from typing import Protocol

# import from EC_tools
import EC_tools.read as read
from EC_tools.bookkeep import Bookkeep
import EC_tools.plot as plot
from EC_tools.portfolio import Portfolio
from crudeoil_future_const import OPEN_HR_DICT, CLOSE_HR_DICT, OIL_FUTURES_FEES
"""
Created on Thu Apr 18 18:22:17 2024

@author: dexter

The backtest module contains all the necessary functions and class to run 
backtesting on any strategy. At the moment, the module only contains methods 
that include static instructions.

Backtest Loop Type:
    This module contains a vareity of Loop type for users. 
    Pricing data can be too much to compute. Going through each ticks will be 
    wildly inefficient and redundant. To solve this problem, there are a 
    few Loop Types available in this module to make backtest faster
    
        (1) FullLoop
            Looping through every single data point. It contains the most 
            grandnuality and details but is also the slowest (by a large margin).
        (2) CrossoverLoop
            Looping over only the points of interest. Given a set of EES values.
            The loop only look at the time and price in which the price action
            breaches these threshold. This loop type contains the least details
            but is also the fastest.
        (3) RangeLoop
            Looping over a subset of data point given a boundary of intervals
    
Static Instruction Backtest:
    Functions in this module takes a precalculated Buy/Sell/Neutral
    signal with a predetermined target Entry, Exit, and Stop Loss (EES) level.
    The backtest loop utilise different trading method to search in the 
    pricing chart the appropriate time and price of EES and record 
    what trade was taken.
    
Backtest Methods on Singular Asset:
    loop_date
    
    loop_date_portfolio
    
Backtest Methods on Multiple Assets:
    There are several method that can be used to iterate through multiple assets.
    At the moment, there are three types:
        
List-based
    
Preload_list

Concurrent
 
"""
FILENAME_MINUTE =  "/home/dexter/Euler_Capital_codes/EC_tools/data/history_data/Minute/HO.001"
APC_FILENAME = "/home/dexter/Euler_Capital_codes/EC_tools/data/APC_latest/APC_latest_HOc1.csv"  

__all__ = ['prepare_signal_interest', 'extract_intraday_minute_data', 
           'plot_in_backtest', 'loop_date', 'loop_date_portfolio',
           'loop_portfolio_preloaded_list']
__author__="Dexter S.-H. Hon"

    

def prepare_signal_interest(filename_buysell_signals: str, 
                            direction: list[str] = ["Buy", "Sell"], 
                            trim: bool = False) -> pd.DataFrame:
    """
    A function that extract data from a signal table based on some directional 
    instruction.

    Parameters
    ----------
    filename_buysell_signals : str
        The file name of the directional data. It read the table as a dataframe.
    direction : list, str, optional
        The directional instruction. The default is ["Buy", "Sell"].
    trim : bool, optional
        Choose whether the result table contain only two clomns. 
        The default is False.

    Returns
    -------
    data : pandas dataframe
        The tuncated table with only the data of interest.

    """
    # read in direction data from the signal generation
    buysell_signals_data = pd.read_csv(filename_buysell_signals)    

    # The trim function reduce the number of columns to only 'Date' and 'direction'
    # This may cut down the computing and memory cost when dealing with large 
    # table.
    if trim == True:
        buysell_signals_data = buysell_signals_data[['Date', 'Direction']]
    elif trim == False:
        pass
    
    # Select for the signals in direction list.
    signal_data = []
    for i in direction:
        temp = buysell_signals_data[buysell_signals_data['Direction'] == i]
        signal_data.append(temp)
    # concatenate the list of signals
    signal_interest = pd.concat(signal_data, ignore_index=True)


    # make a column with Timestamp as its content
    signal_interest['Date'] =  [datetime.datetime(
                                                year = int(str(x)[0:4]), 
                                              month=int(str(x)[5:7]), 
                                              day = int(str(x)[8:])) 
                            for x in signal_interest['Date']]
    # sort the table by Date
    signal_interest.sort_values(by='Date', inplace=True)

    return signal_interest

def extract_intraday_minute_data(histroy_intraday_data: pd.DataFrame, 
                                 date_interest: str, 
                                 open_hr: str = '0330', 
                                 close_hr: str = '1900') -> pd.DataFrame:
    """
    A function that extract only the minute pricing data from a master file 
    given a single date of interest.

    Parameters
    ----------
    histrot_data_intraday : pandas dataframe
        The master file for minute data.
    date_interest : str
        In the format of '2020-02-02'.
    open_hr : str, optional
        Opening trading hour. The default is 300.
    close_hr : str, optional
        Closing trading hour. The default is 1900.

    Returns
    -------
    histroy_data_intraday : pandas dataframe
        A table isolated by the date of interest.

    """    
    # convert the string hour and minute input to datetime.time object
    
    if type(open_hr) == str:
        open_hr_str, open_min_str = open_hr[-4:-2], open_hr[-2:]
        open_hr =  datetime.time(hour = int(open_hr_str), minute = int(open_min_str))
    elif type(open_hr) == datetime.time:
        pass
    
    if type(close_hr) == str:
        close_hr_str, close_min_str = close_hr[-4:-2], close_hr[-2:]
        close_hr =  datetime.time(hour = int(close_hr_str), minute = int(close_min_str))
    elif type(close_hr) == datetime.time:
        pass

    
    # Given a date of interest, and read-in the intraday data.
    histroy_intraday_data = histroy_intraday_data[
                                histroy_intraday_data['Date']  == date_interest]
    
    # isolate the region of interest between the opening hour and the closing hour
    histroy_intraday_data = histroy_intraday_data[
                                            histroy_intraday_data['Time'] > open_hr]
    histroy_intraday_data = histroy_intraday_data[
                                            histroy_intraday_data['Time'] < close_hr]

    return histroy_intraday_data

def plot_in_backtest(date_interest: str | datetime.datetime, 
                     EES_dict:dict, 
                     direction: str, 
                     plot_or_not: bool = False) -> None:
    if plot_or_not == True:
        
        if isinstance(date_interest, datetime.datetime):
            date_interest_str = date_interest.strftime("%Y-%m-%d")
        elif type(date_interest)==str:
            date_interest_str = date_interest
            
            
        if len(EES_dict['entry']) > 0:    
            entry_times, entry_pts = list(zip(*EES_dict['entry']))
        else:
            entry_times, entry_pts = [], []
            
        if len(EES_dict['exit']) > 0:
            exit_times, exit_pts = list(zip(*EES_dict['exit']))
        else:
            exit_times, exit_pts = [], []
        
        if len(EES_dict['stop']) > 0:
            stop_times, stop_pts = list(zip(*EES_dict['stop']))
        else: 
            stop_times, stop_pts = [], []
        
        plot.plot_minute(FILENAME_MINUTE, APC_FILENAME, 
                         date_interest = date_interest_str, 
                         direction=direction,
                         bppt_x1=entry_times, bppt_y1=entry_pts,
                         bppt_x2=exit_times, bppt_y2=exit_pts,
                         bppt_x3=stop_times, bppt_y3=stop_pts)
        
    elif plot_or_not == False:
        pass

##############################################
class BacktestLoop(Protocol):
    pass

class LoopCrossPoints(BacktestLoop):
    
    def loop_date(trade_method, 
                  signal_table: pd.DataFrame, 
                  histroy_intraday_data: pd.DataFrame, 
                  strategy_name: str = 'argus_exact',
                  open_hr: str ='0330', close_hr: str='1930',
                  plot_or_not: bool = False, 
                  sort_by: str = 'Entry_Date') -> pd.DataFrame:
        """
        Fast looping method that generate simple CSV output file.
        This method isolate out the crossover points to find optimal EES 
        using onetradeperday. This loop is meant to be fast and only produce a 
        simple table, not a portfolio file.
        
        """
        symbol_list = signal_table['Price_Code']
        direction_list = signal_table['Direction'] 
        commodity_list = signal_table['Commodity_name']
        
        entry_price_list = signal_table['Entry_Price']
        exit_price_list = signal_table['Exit_Price']
        stoploss_price_list = signal_table['StopLoss_Price']

        date_interest_list = signal_table['Date']
        full_contract_symbol_list = signal_table['Contract_Month']

        get_obj_name_list = signal_table['Price_Code']
        strategy_name_list = signal_table['strategy_name']
        
            
        # make bucket 
        book = Bookkeep(bucket_type='backtest')
        dict_trade_PNL = book.make_bucket(keyword=strategy_name)
        
        trade_id = 0
        for date_interest, direction, commodity_name, \
            entry_price, exit_price, stoploss_price, \
            price_code, full_contract_symbol, \
            strategy_name in zip(date_interest_list,  \
                                 direction_list, commodity_list,
                                 entry_price_list, exit_price_list, stoploss_price_list,
                                 symbol_list,
                                 full_contract_symbol_list,
                                 strategy_name_list):
                                    
            if direction == 'Buy' or direction == 'Sell':
                target_entry = entry_price
                target_exit = exit_price
        
            else:
                target_entry, target_exit = 'NA', 'NA'
            
            # Define the date of interest by reading TimeStamp. 
            # We may want to remake all this and make Timestamp the universal 
            # parameter when dealing with time
            day = extract_intraday_minute_data(histroy_intraday_data, date_interest, 
                                         open_hr=open_hr, close_hr=close_hr)
            
            #print(day['Date'].iloc[0], direction, target_entry, target_exit, stop_exit)
            
            open_hr_dt, open_price = read.find_closest_price(day,
                                                             target_hr= open_hr,
                                                             direction='forward')
            close_hr_dt, close_price = read.find_closest_price(day,
                                                               target_hr= close_hr,
                                                               direction='backward')

            
            # make a dictionary for all the possible EES time and values
            EES_dict = read.find_minute_EES(day, target_entry, 
                                            target_exit, stoploss_price,
                                            open_hr=open_hr_dt, 
                                            close_hr=close_hr_dt, 
                                            direction = direction)

            # make the trade.
            trade_open, trade_close = trade_method(EES_dict)
            
            if trade_open != (np.nan, np.nan) and trade_close == (np.nan, np.nan):
                raise Exception('trade WTF {},{}'.format(trade_open, trade_close))
                
            entry_price, entry_datetime = trade_open[1], trade_open[0]
            exit_price, exit_datetime = trade_close[1], trade_close[0]
            
            
            # calculate statistics EES_dict
            if direction == "Buy": # for buy, we are longing
                return_trades = exit_price - entry_price
            elif direction == "Sell": # for sell, we are shorting
                return_trades = entry_price - exit_price

            # The risk and reward ratio is based on Abbe's old script but it should be the sharpe ratio
            risk_reward_ratio = abs(target_entry-stoploss_price)/\
                                abs(target_entry-target_exit)


            # put all the data in a singular list            
            data = [trade_id, direction, commodity_name,  price_code, 
                    full_contract_symbol, 
                    date_interest, entry_datetime, entry_price, 
                    date_interest, exit_datetime, exit_price, 
                    return_trades, risk_reward_ratio, strategy_name]

            # Storing the data    
            dict_trade_PNL = book.store_to_bucket_single(data)
                                        
            # plotting mid-backtest
            plot_in_backtest(date_interest, EES_dict, direction, 
                             plot_or_not=plot_or_not)
            
            trade_id = trade_id +1       

            #print('info', data)
            
        dict_trade_PNL = pd.DataFrame(dict_trade_PNL)
        #sort by date
        dict_trade_PNL = dict_trade_PNL.sort_values(by=sort_by)
             
        return dict_trade_PNL
        
    def loop_date_portfolio(portfo: Portfolio, 
                            trade_method, 
                            signal_table: pd.DataFrame, 
                            histroy_intraday_data: pd.DataFrame, 
                            strategy_name: str = 'argus_exact',
                            give_obj_name: str = "USD", 
                            get_obj_name: str = "CLc1", 
                            get_obj_quantity: int = 50,
                            open_hr: str = '0330', close_hr: str ='1930',
                            plot_or_not: bool = False):
        """
        Portfolio module method.
        
        
        """
        
        
        for date_interest, direction, target_entry, target_exit, \
            stop_exit, price_code in zip(signal_table['Date'], 
                                        signal_table['direction'], 
                                        signal_table['target entry'],
                                        signal_table['target exit'], 
                                        signal_table['stop exit'],
                                        signal_table['price code']):
                                            
            # Define the date of interest by reading TimeStamp. 
            # We may want to remake all this and make Timestamp the universal 
            # parameter when dealing with time
            day = extract_intraday_minute_data(histroy_intraday_data, date_interest, 
                                         open_hr=open_hr, close_hr=close_hr)
            
            print(day['Date'].iloc[0], direction, target_entry, target_exit, stop_exit)
            
            open_hr_dt, open_price = read.find_closest_price(day,
                                                               target_hr= open_hr,
                                                               direction='forward')
            
            print('open',open_hr_dt, open_price)
            
            close_hr_dt, close_price = read.find_closest_price(day,
                                                               target_hr= close_hr,
                                                               direction='backward')
            print('close', close_hr_dt, close_price)
        
            print('==================================')
            # The main Trade function here
            EES_dict, trade_open, trade_close, \
                pos_list, exec_pos_list = trade_method(portfo).run_trade(\
                                                day, give_obj_name, get_obj_name, 
                                                get_obj_quantity, target_entry, 
                                                target_exit, stop_exit, 
                                                open_hr=open_hr_dt, 
                                                close_hr=close_hr_dt, 
                                                direction = direction)
            print("----value----")
            print("value",portfo.total_value(date_interest))
            print('==================================')

                                        
            # plotting mid-backtest
            plot_in_backtest(date_interest, EES_dict, direction, 
                             plot_or_not=plot_or_not)
            
        return portfo
        

    def loop_portfolio_preloaded_list(portfo: Portfolio, 
                                      trade_method,
                                      signal_table: pd.DataFrame, 
                                      histroy_intraday_data_pkl, 
                                      give_obj_name: str = "USD", 
                                      get_obj_quantity: int = 1,
                                      plot_or_not: bool = False):
        """
        A method that utilise one portfolio to run multi-strategy
        
        """
        #symbol_list = list(histroy_intraday_data_pkl.keys())
        
        for i in range(len(signal_table)):
            item = signal_table.iloc[i]
                    
            symbol = item['Price_Code']
            direction = item['Direction'] 
            
            if direction == 'Buy':
                target_entry = item['Entry_Price']
                target_exit = item['Exit_Price'] 

            elif direction == 'Sell':
                target_entry = item['Entry_Price']
                target_exit = item['Exit_Price'] 

            else:
                target_entry, target_exit = 'NA', 'NA'
                
            stop_exit = item['StopLoss_Price'] 
            
            date_interest = item['Date']
            get_obj_name = item['Price_Code']

            open_hr = OPEN_HR_DICT[symbol]
            close_hr = CLOSE_HR_DICT[symbol]
                    
            histroy_intraday_data = histroy_intraday_data_pkl[symbol]

            
            day = extract_intraday_minute_data(histroy_intraday_data, date_interest, 
                                          open_hr=open_hr, close_hr=close_hr)
            
            open_hr_dt, open_price = read.find_closest_price(day,target_hr= open_hr,
                                                                direction='forward')
            
            
            close_hr_dt, close_price = read.find_closest_price(day,target_hr= close_hr,
                                                                direction='backward')
        
            #print('==================================')
            
            print(i, date_interest, direction, symbol)
            
            EES_dict, trade_open, trade_close, \
                pos_list, exec_pos_list = trade_method(portfo).run_trade(\
                                                day, give_obj_name, get_obj_name, 
                                                get_obj_quantity, target_entry, 
                                                target_exit, stop_exit, 
                                                open_hr=open_hr_dt, 
                                                close_hr=close_hr_dt, 
                                                direction = direction)
                    
            # plotting mid-backtest
            plot_in_backtest(date_interest, EES_dict, direction, 
                              plot_or_not=plot_or_not)
            
        return portfo

class LoopRange(BacktestLoop):
    pass

class LoopFull(BacktestLoop):
    pass 


def loop_date_full():
    """
    A method that loop through every single data points.
    It is slow but can be used to teste path dependent signals.
    
    """
    return 

###############################3

def loop_date(trade_method, 
              signal_table: pd.DataFrame, 
              histroy_intraday_data: pd.DataFrame, 
              strategy_name: str = 'argus_exact',
              open_hr: str ='0330', close_hr: str='1930',
              plot_or_not: bool = False, 
              sort_by: str = 'Entry_Date') -> pd.DataFrame:
    """
    Fast looping method that generate simple CSV output file.
    This method isolate out the crossover points to find optimal EES 
    using onetradeperday. This loop is meant to be fast and only produce a 
    simple table, not a portfolio file.
    
    """

    symbol_list = signal_table['Price_Code']
    direction_list = signal_table['Direction'] 
    commodity_list = signal_table['Commodity_name']
    
    entry_price_list = signal_table['Entry_Price']
    exit_price_list = signal_table['Exit_Price']
    stoploss_price_list = signal_table['StopLoss_Price']

    
    date_interest_list = signal_table['Date']
    full_contract_symbol_list = signal_table['Contract_Month']

    get_obj_name_list = signal_table['Price_Code']
    strategy_name_list = signal_table['strategy_name']
    
        
    # make bucket 
    book = Bookkeep(bucket_type='backtest')
    dict_trade_PNL = book.make_bucket(keyword=strategy_name)
    
    trade_id = 0
    for date_interest, direction, commodity_name, \
        entry_price, exit_price, stoploss_price, \
        price_code, full_contract_symbol, \
        strategy_name in zip(date_interest_list,  \
                             direction_list, commodity_list,
                             entry_price_list, exit_price_list, stoploss_price_list,
                             symbol_list,
                             full_contract_symbol_list,
                             strategy_name_list):
                                
        if direction == 'Buy':
            target_entry = entry_price
            target_exit = exit_price
    
        elif direction == 'Sell':
            target_entry = entry_price
            target_exit = exit_price
    
        else:
            target_entry, target_exit = 'NA', 'NA'
        
        # Define the date of interest by reading TimeStamp. 
        # We may want to remake all this and make Timestamp the universal 
        # parameter when dealing with time
        day = extract_intraday_minute_data(histroy_intraday_data, date_interest, 
                                     open_hr=open_hr, close_hr=close_hr)
        
        #print(day['Date'].iloc[0], direction, target_entry, target_exit, stop_exit)
        
        open_hr_dt, open_price = read.find_closest_price(day,
                                                           target_hr= open_hr,
                                                           direction='forward')
        
        #print('open',open_hr_dt, open_price)
        
        close_hr_dt, close_price = read.find_closest_price(day,
                                                           target_hr= close_hr,
                                                           direction='backward')
        #print('close', close_hr_dt, close_price)

        
        # make a dictionary for all the possible EES time and values
        EES_dict = read.find_minute_EES(day, 
                                        target_entry, target_exit, stoploss_price,
                                        open_hr=open_hr_dt, close_hr=close_hr_dt, 
                                        direction = direction)

        # make the trade.
        trade_open, trade_close = trade_method(EES_dict)
        
        if trade_open != (np.nan, np.nan) and trade_close == (np.nan, np.nan):
            raise Exception('trade WTF {},{}'.format(trade_open, trade_close))
       # print('trade', trade_open, trade_close)
            
        entry_price, entry_datetime = trade_open[1], trade_open[0]
        exit_price, exit_datetime = trade_close[1], trade_close[0]
        
        
        # calculate statistics EES_dict
        if direction == "Buy": # for buy, we are longing
            return_trades = exit_price - entry_price
        elif direction == "Sell": # for sell, we are shorting
            return_trades = entry_price - exit_price

        # The risk and reward ratio is based on Abbe's old script but it should be the sharpe ratio
        risk_reward_ratio = abs(target_entry-stoploss_price)/abs(target_entry-target_exit)


        # put all the data in a singular list       
        data = [trade_id, direction, commodity_name,  price_code, 
                full_contract_symbol, 
                date_interest, entry_datetime, entry_price, 
                date_interest, exit_datetime, exit_price, 
                return_trades, risk_reward_ratio, strategy_name]

        # Storing the data    
        dict_trade_PNL = book.store_to_bucket_single(data)
                                    
        # plotting mid-backtest
        plot_in_backtest(date_interest, EES_dict, direction, 
                         plot_or_not=plot_or_not)
        
        trade_id = trade_id +1       

        #print('info', data)
        
    dict_trade_PNL = pd.DataFrame(dict_trade_PNL)
    #sort by date
    dict_trade_PNL = dict_trade_PNL.sort_values(by=sort_by)
         
    return dict_trade_PNL
    
def loop_date_portfolio(portfo: type[Portfolio], 
                        trade_method, 
                        signal_table: pd.DataFrame, 
                        histroy_intraday_data: pd.DataFrame, 
                        strategy_name: str = 'argus_exact',
                        give_obj_name: str = "USD", 
                        get_obj_name: str = "CLc1", 
                        get_obj_quantity: int = 50,
                        open_hr: str = '0330', close_hr: str ='1930',
                        plot_or_not: bool = False):
    """
    Portfolio module method.
    
    
    """
    
    i=0
    for date_interest, direction, target_entry, target_exit, \
        stop_exit, price_code in zip(signal_table['Date'], 
                                    signal_table['direction'], 
                                    signal_table['target entry'],
                                    signal_table['target exit'], 
                                    signal_table['stop exit'],
                                    signal_table['price code']):
                                        
        # Define the date of interest by reading TimeStamp. 
        # We may want to remake all this and make Timestamp the universal 
        # parameter when dealing with time
        day = extract_intraday_minute_data(histroy_intraday_data, date_interest, 
                                     open_hr=open_hr, close_hr=close_hr)
        
        print(day['Date'].iloc[0], direction, target_entry, target_exit, stop_exit)
        
        open_hr_dt, open_price = read.find_closest_price(day,
                                                           target_hr= open_hr,
                                                           direction='forward')
        
        print('open',open_hr_dt, open_price)
        
        close_hr_dt, close_price = read.find_closest_price(day,
                                                           target_hr= close_hr,
                                                           direction='backward')
        print('close', close_hr_dt, close_price)
    
        print('==================================')
        # The main Trade function here
        EES_dict, trade_open, trade_close, \
        pos_list, exec_pos_list = trade_method(portfo).run_trade(\
                                                            day, give_obj_name, 
                                                            get_obj_name, 
                                                            get_obj_quantity, 
                                                            target_entry, 
                                                            target_exit, stop_exit, 
                                                            open_hr=open_hr_dt, 
                                                            close_hr=close_hr_dt, 
                                                            direction = direction,
                                                            fee=OIL_FUTURES_FEES[price_code],
                                                            open_time = open_hr_dt,
                                                            trade_id = i)
        print("----value----")
        print("value",portfo.total_value(date_interest))
        print('==================================')

        # plotting mid-backtest
        plot_in_backtest(date_interest, EES_dict, direction, 
                         plot_or_not=plot_or_not)
        i = i+1
        
    return portfo
    

def loop_portfolio_preloaded_list(portfo: Portfolio, 
                                  trade_method,
                                  signal_table: pd.DataFrame, 
                                  histroy_intraday_data_pkl, 
                                  give_obj_name: str = "USD", 
                                  get_obj_quantity: int = 1,
                                  plot_or_not: bool = False):
    """
    A method that utilise one portfolio to run multi-strategy
    
    """
    #symbol_list = list(histroy_intraday_data_pkl.keys())
    #tradebook = trade_method(portfo)
    
    for i in range(len(signal_table)):
        item = signal_table.iloc[i]
                
        symbol = item['Price_Code']
        direction = item['Direction'] 
        
        if direction == 'Buy':
            target_entry = item['Entry_Price']
            target_exit = item['Exit_Price'] 

        elif direction == 'Sell':
            target_entry = item['Entry_Price']
            target_exit = item['Exit_Price'] 

        else:
            target_entry, target_exit = 'NA', 'NA'
            
        stop_exit = item['StopLoss_Price'] 
        
        date_interest = item['Date']
        get_obj_name = item['Price_Code']

        open_hr = OPEN_HR_DICT[symbol]
        close_hr = CLOSE_HR_DICT[symbol]
                
        histroy_intraday_data = histroy_intraday_data_pkl[symbol]

        
        day = extract_intraday_minute_data(histroy_intraday_data, date_interest, 
                                           open_hr=open_hr, close_hr=close_hr)
        
        open_hr_dt, open_price = read.find_closest_price(day,target_hr= open_hr,
                                                         direction='forward')
        
        
        close_hr_dt, close_price = read.find_closest_price(day,target_hr= close_hr,
                                                           direction='backward')
            
        print(i, date_interest, direction, symbol)
        # The time to open all positions
        pos_open_dt = datetime.datetime.combine(date_interest.date(), open_hr_dt)
        
        EES_dict, trade_open, trade_close, \
        pos_list, exec_pos_list = trade_method(portfo).run_trade(\
                                                      day, give_obj_name, 
                                                      get_obj_name, 
                                                      get_obj_quantity, 
                                                      target_entry, 
                                                      target_exit, stop_exit, 
                                                      open_hr=open_hr_dt, 
                                                      close_hr=close_hr_dt, 
                                                      direction = direction,
                                                      fee=OIL_FUTURES_FEES[symbol],
                                                      open_time= pos_open_dt,
                                                      trade_id= i)
                
        # plotting mid-backtest
        plot_in_backtest(date_interest, EES_dict, direction, 
                          plot_or_not=plot_or_not)
        
    return portfo

# =============================================================================
# def loop_date_concurrent
# =============================================================================

if __name__ == "__main__":
    MASTER_SIGNAL_FILENAME = "/home/dexter/Euler_Capital_codes/EC_tools/results/benchmark_signal_full.csv"
    HISTORY_MINUTE_PKL_FILENAME ="/home/dexter/Euler_Capital_codes/EC_tools/data/pkl_vault/crudeoil_future_minute_full.pkl"

