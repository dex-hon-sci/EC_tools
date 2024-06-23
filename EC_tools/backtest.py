#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 18 18:22:17 2024

@author: dexter
"""
# import Python package
import pandas as pd
import numpy as np
import datetime as datetime

# import from EC_tools
import EC_tools.read as read
import EC_tools.utility as util
from EC_tools.bookkeep import Bookkeep
from EC_tools.trade import  trade_choice_simple, OneTradePerDay
import EC_tools.plot as plot
from EC_tools.portfolio import Asset, Portfolio

FILENAME_MINUTE = "/home/dexter/Euler_Capital_codes/test_MS/data_zeroadjust_intradayportara_attempt1/intraday/1 Minute/HO.001"
FILENSME_BUYSELL_SIGNALS = "/home/dexter/Euler_Capital_codes/EC_tools/results/benchmark_signals/benchmark_signal_HOc1_full.csv"
SIGNAL_FILENAME = "/home/dexter/Euler_Capital_codes/EC_tools/data/benchmark_signal_test.csv"   

APC_FILENAME = "/home/dexter/Euler_Capital_codes/EC_tools/data/APC_latest/APC_latest_HOc1.csv"  

# tested
def prepare_signal_interest(filename_buysell_signals, 
                            direction=["Buy", "Sell"], trim = False):
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
        buysell_signals_data = buysell_signals_data[['APC forecast period', 
                                                     'direction']]
    elif trim == False:
        pass
    
    # Select for the signals in direction list.
    signal_data = []
    for i in direction:
        temp = buysell_signals_data[buysell_signals_data['direction'] == i]
        signal_data.append(temp)
    
    # concatenate the list of signals
    signal_interest = pd.concat(signal_data, ignore_index=True)

    # make a column with Timestamp as its content
    #signal_interest['Date'] = pd.to_datetime(signal_interest["APC forecast period"], 
    #                              format='%Y-%m-%d')
    #print(signal_interest['APC forecast period'], signal_interest['APC forecast period'].iloc[0])
    #print(signal_interest['APC forecast period'].iloc[0][0:4], 
    #      signal_interest['APC forecast period'].iloc[0][5:7],
    #      signal_interest['APC forecast period'].iloc[0][8:])
    signal_interest['Date'] =  [datetime.datetime(
                                                year = int(str(x)[0:4]), 
                                              month=int(str(x)[5:7]), 
                                              day = int(str(x)[8:])) 
                            for x in signal_interest['APC forecast period']]
    # sort the table by Date
    signal_interest.sort_values(by='Date', inplace=True)

    return signal_interest

#tested
def extract_intraday_minute_data(histrot_intraday_data, date_interest, 
                                 open_hr='0330', close_hr='1900'):
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
    print('open_hr', open_hr)
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
    histrot_intraday_data = histrot_intraday_data[
                                histrot_intraday_data['Date']  == date_interest]
    
    # isolate the region of interest between the opening hour and the closing hour
    histrot_intraday_data = histrot_intraday_data[
                                            histrot_intraday_data['Time'] > open_hr]
    histrot_intraday_data = histrot_intraday_data[
                                            histrot_intraday_data['Time'] < close_hr]

    return histrot_intraday_data

# tested
def plot_in_backtest(date_interest, EES_dict, direction, plot_or_not=False):
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
                        date_interest = date_interest_str, direction=direction,
                          bppt_x1=entry_times, bppt_y1=entry_pts,
                          bppt_x2=exit_times, bppt_y2=exit_pts,
                          bppt_x3=stop_times, bppt_y3=stop_pts)
        
    elif plot_or_not == False:
        pass


def loop_date_full():
    """
    A method that loop through every single data points.
    It is slow but can be used to teste path dependent signals.
    
    """
    return 

def loop_date(signal_table, histroy_intraday_data, open_hr='0330', 
              close_hr='1930',
              plot_or_not = False):
    """
    Fast looping method that generate simple CSV output file.
    This method isolate out the crossover points to find optimal EES 
    using onetradeperday.    
    
    """
    
    # make bucket 
    book = Bookkeep(bucket_type='backtest')
    dict_trade_PNL = book.make_bucket(keyword='benchmark')
    
    for date_interest, direction, target_entry, target_exit, stop_exit, price_code in zip(
            signal_table['Date'], 
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

        
        # make a dictionary for all the possible EES time and values
        EES_dict = read.find_minute_EES(day, target_entry, target_exit, stop_exit,
                          open_hr=open_hr_dt, close_hr=close_hr_dt, 
                          direction = direction)

        # make the trade.
        trade_open, trade_close = trade_choice_simple(EES_dict)

        entry_price, exit_price = trade_open[1], trade_close[1]
        entry_datetime= trade_open[0]
        exit_datetime = trade_close[0]
        
        # calculate statistics EES_dict
        if direction == "Buy": # for buy, we are longing
            return_trades = exit_price - entry_price
        elif direction == "Sell": # for sell, we are shorting
            return_trades = entry_price - exit_price

        # The risk and reward ratio is based on Abbe's old script but it should be the sharpe ratio
        risk_reward_ratio = abs(target_entry-stop_exit)/abs(target_entry-target_exit)


        # put all the data in a singular list
        data = [price_code, direction, date_interest,
                return_trades, entry_price,  entry_datetime,
                    exit_price, exit_datetime, risk_reward_ratio]
        
        # Storing the data    
        dict_trade_PNL = book.store_to_bucket_single(data)
                                    
        # plotting mid-backtest
        plot_in_backtest(date_interest, EES_dict, direction, 
                         plot_or_not=plot_or_not)

        print('info', data)
        
    dict_trade_PNL = pd.DataFrame(dict_trade_PNL)
    
    #sort by date
    dict_trade_PNL = dict_trade_PNL.sort_values(by='date')
         
    return dict_trade_PNL
    
def loop_date_portfolio(portfo, signal_table, histroy_intraday_data, 
                        give_obj_name = "USD", get_obj_name = "CLc1", 
                        get_obj_quantity = 50,
                        open_hr='0330', close_hr='1930',
                        plot_or_not = False):
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
            pos_list, exec_pos_list = OneTradePerDay(portfo).run_trade(\
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
    

def loop_date_portfolio_multi_strategy():
    """
    A method that utilise one portfolio to run multi-strategy
    
    """

    
    return 

@util.time_it #@util.save_csv('benchmark_PNL_CLc1_full.csv')
def run_backtest():
    # master function that runs the backtest itself.
    # The current method only allows one singular direction signal perday. and a set of constant EES

    
    # read the reformatted minute history data
    history_data = read.read_reformat_Portara_minute_data(FILENAME_MINUTE)
    
    # Find the date for trading, only "Buy" or "Sell" date are taken.
    trade_date_table = prepare_signal_interest(FILENSME_BUYSELL_SIGNALS, trim = False)
        
    # loop through the date and set the EES prices for each trading day   
    dict_trade_PNL = loop_date(trade_date_table, history_data, open_hr='0330', 
                  close_hr='2000', plot_or_not = False)    

    return dict_trade_PNL

@util.time_it
@util.pickle_save('portfolio_HOc1_test.pkl')
def run_backtest_portfolio():
    # master function that runs the backtest itself.
    # The current method only allows one singular direction signal perday. and a set of constant EES

    
    # read the reformatted minute history data
    history_data = read.read_reformat_Portara_minute_data(FILENAME_MINUTE)

    # Find the date for trading, only "Buy" or "Sell" date are taken.
    trade_date_table = prepare_signal_interest(FILENSME_BUYSELL_SIGNALS, trim = False)
    
    start_date = datetime.datetime(2021,1,1)
    end_date = datetime.datetime(2023,12,30)
    # Select for the date interval for investigation
    history_data = history_data[(history_data['Date'] > start_date) & 
                                (history_data['Date'] < end_date)]
    
    trade_date_table = trade_date_table[(trade_date_table['Date'] > start_date) & 
                                        (trade_date_table['Date'] < end_date)]
    
    # Initialise Portfolio
    P1 = Portfolio()
    USD_initial = Asset("USD", 10_300_000, "dollars", "Cash") # initial fund
    P1.add(USD_initial,datetime=datetime.datetime(2020,12,31))
    
    # loop through the date and set the EES prices for each trading day   
    P1 = loop_date_portfolio(P1, trade_date_table, history_data,
                                            give_obj_name = "USD", get_obj_name = "HOc1",
                                            get_obj_quantity = 10,
                                            open_hr='1300', close_hr='1828', 
                                            plot_or_not = False)    
    print('master_table', P1.master_table)

    return P1

def run_backtest_portfolio_multistrategy(): 
    # Initialise Portfolio
    P1 = Portfolio()
    USD_initial = Asset("USD", 10_300_000, "dollars", "Cash") # initial fund
    P1.add(USD_initial,datetime=datetime.datetime(2020,12,31))
    
    # a list of input files
    P1.loop_date_portfolio_multi_strategy()
    return 

## WIP area ###

class LoopDate(object):
    def __init__(self):
        return 

if __name__ == "__main__":
    
    #run_backtest()
    run_backtest_portfolio()