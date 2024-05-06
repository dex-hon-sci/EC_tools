#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 18 18:22:17 2024

@author: dexter
"""
import pandas as pd
import numpy as np
import datetime as datetime

import EC_read as EC_read
import EC_plot as EC_plot
import EC_strategy as EC_strategy
import utility as util

# Spit out the document for overall PNL analysis

# tested
def find_crossover(input_array, threshold):
    # a function that make a list of cross over point's indices given a particular threshold
    
    threshold = np.repeat(threshold, len(input_array))
    
    # The difference between the input value and the threshold number
    # Positive values mean the input is higher than threshold
    # Negative values mean the input is lower than threshold
    delta = input_array - threshold
    
    # This is an array 1 unit in the past
    #delta_lag = np.concatenate([delta, np.array([np.nan])])[1:]
    delta_lag = np.concatenate([np.array([np.nan]), delta])[:-1]
    
    # IF delta[i] > delta_lag[i], then the price rise above threshold
    # Because all elements are either +1, -1 or 0, the larger value has to be +1.
    # np.sign(delta) = +1, while np.sign(delta_lag) = -1 means yesterday the value 
    # is lower than threshold and today's value is higher than the threshold-> rise above
    indices_rise_above  = np.where(np.sign(delta) > np.sign(delta_lag))
    
    # IF delta[i] < delta_lag[i], then the price drop below threshold
    indices_drop_below = np.where(np.sign(delta) < np.sign(delta_lag))

    #print('rise', indices_rise_above)
    #print('drop', indices_drop_below)
    
    # Produce a dic of indicies for below and above
    return {'rise': indices_rise_above, 
            'drop': indices_drop_below}


class BackTest(object):
    def __init__(self):
        self._instruction = None
        
    def make_report(object):
        
        return None
        
    
    
    
# tested
def prepare_signal_interest(filename_buysell_signals, direction=["Buy", "Sell"], trim = False):
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
        #print('temp', temp)
        signal_data.append(temp)
    
    # concatenate the list of signals
    signal_interest = pd.concat(signal_data, ignore_index=True)

    # make a column with Timestamp as its content
    signal_interest['Date'] = pd.to_datetime(signal_interest["APC forecast period"], 
                                  format='%Y-%m-%d')
                                  
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
    # convert the string hour and minute input to datetime.time objecy
    open_hr_str, open_min_str = open_hr[-4:-2], open_hr[-2:]
    close_hr_str, close_min_str = close_hr[-4:-2], close_hr[-2:]

    open_hr =  datetime.time(hour = int(open_hr_str), minute = int(open_min_str))
    close_hr =  datetime.time(hour = int(close_hr_str), minute = int(close_min_str))

    
    # Given a date of interest, and read-in the intraday data.
    histrot_intraday_data = histrot_intraday_data[
                                histrot_intraday_data['Date']  == date_interest]
    
    # isolate the region of interest between the opening hour and the closing hour
    histrot_intraday_data = histrot_intraday_data[
                                            histrot_intraday_data['Time'] > open_hr]
    histrot_intraday_data = histrot_intraday_data[
                                            histrot_intraday_data['Time'] < close_hr]

    return histrot_intraday_data



def loop_date(signal_table, histroy_intraday_data, open_hr='0330', 
              close_hr='1930',
              plot_or_not = False):
    
    # make bucket
    profits_losses_bucket = {
    'Price Code': [],
    'predicted signal': [],
    'date': [],
    'return from trades': [],
    'entry price': [],
    'entry datetime': [],
    'exit price': [],
    'exit datetime': [],
    'risk/reward value ratio': [],
    }
   
    #trade_date_table is the signal table
    

    print('signal_table',signal_table)
    
    
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
        
        # make a dictionary for all the possible EES time and values
        EES_dict = set_minute_EES(day, target_entry, target_exit, stop_exit,
                          open_hr=open_hr, close_hr=close_hr, direction = direction)
        
        # make the trade.
        #trade_open, trade_close = trade_choice(EES_dict)
        trade_open, trade_close = None, None
        # WIP
        entry_price, exit_price = None, None
        #entry_price, exit_price = trade_open[1], trade_close[1]
        entry_datetime= None
        exit_datetime = None
        
        # calculate statistics
        #return_trades = (exit_price - entry_price)/ entry_price
        return_trades = None
        risk_reward_ratio = None
        
        # store stuff into buckets
        # WIP

        #make bucket for storage
        bucket = profits_losses_bucket
        
        # put all the data in a singular list
        data = [price_code, direction, date_interest,
                return_trades, entry_price,  entry_datetime,
                    exit_price, exit_datetime, risk_reward_ratio]
        
        # Storing the data    
        dict_trade_PNL = EC_strategy.MRStrategy.\
                                        store_to_bucket_single(bucket, data)
                                        
        # =================Plotting Secrions ===============
        if plot_or_not == True:
            
            filename_minute = "../test_MS/data_zeroadjust_intradayportara_attempt1/intraday/1 Minute/CL.001"
            signal_filename = "APC_latest_CL.csv"   
            
            date_interest_str=date_interest.strftime("%Y-%m-%d")
            
            entry_times, entry_pts = EES_dict['entry_times'], EES_dict['entry_pts']
            exit_times, exit_pts = EES_dict['exit_times'], EES_dict['exit_pts']
            stop_times, stop_pts = EES_dict['stop_times'], EES_dict['stop_pts']
            
            EC_plot.plot_minute(filename_minute, signal_filename, 
                            date_interest = date_interest_str, direction=direction,
                              bppt_x1=entry_times, bppt_y1=entry_pts,
                              bppt_x2=exit_times, bppt_y2=exit_pts,
                              bppt_x3=stop_times, bppt_y3=stop_pts)
            
        elif plot_or_not == False:
            pass
        # ===================================================
        
    dict_trade_PNL = pd.DataFrame(dict_trade_PNL)
    
    print('dict_trade_PNL', dict_trade_PNL)
    #sort by date
    dict_trade_PNL = dict_trade_PNL.sort_values(by='Date')
    
        
    return EES_dict
    
def set_minute_EES(histroy_data_intraday, 
                      target_entry, target_exit, stop_exit
                      ,open_hr="0330", close_hr="1930", 
                      price_approx = 'Open', direction = 'Neutral',
                      close_trade_hr='1925'):
    
    # define subsample. turn the pandas series into a numpy array
    price_list = histroy_data_intraday[price_approx].to_numpy()
    time_list = histroy_data_intraday['Time'].to_numpy()
    
    # Find the crossover indices
    entry_pt_dict = find_crossover(price_list, target_entry)
    exit_pt_dict = find_crossover(price_list, target_exit)
    stop_pt_dict = find_crossover(price_list, stop_exit)
    
    
    if direction == "Neutral":
        print("Neutral")
        # for 'Neutral' action, all info are empty
        entry_pts = []
        entry_times = []
            
        exit_pts = []
        exit_times = []
        
        stop_pts = []
        stop_times = []
    
    elif direction == "Buy":
        print("Buy")
        # for 'Buy' action EES sequence is drop,rise,drop
        entry_pts = price_list[entry_pt_dict['drop'][0]]
        entry_times = time_list[entry_pt_dict['drop'][0]]
            
        exit_pts = price_list[exit_pt_dict['rise'][0]]
        exit_times = time_list[exit_pt_dict['rise'][0]]
        
        stop_pts = price_list[stop_pt_dict['drop'][0]]
        stop_times = time_list[stop_pt_dict['drop'][0]]
            
    elif direction == "Sell":
        print("Sell")
        # for 'Sell' action EES sequence is rise,drop,rise
        entry_pts = price_list[entry_pt_dict['rise'][0]]
        entry_times = time_list[entry_pt_dict['rise'][0]]
            
        exit_pts = price_list[exit_pt_dict['drop'][0]]
        exit_times = time_list[exit_pt_dict['drop'][0]]
        
        stop_pts = price_list[stop_pt_dict['rise'][0]]
        stop_times = time_list[stop_pt_dict['rise'][0]]
    else:
        raise ValueError('Direction has to be either Buy, Sell, or Neutral.')
    
    # Define the closing time and closing price. Here we choose 19:25 for final trade
    close_time = datetime.time(int(close_trade_hr[:2]),int(close_trade_hr[2:]))
    close_pt = price_list[np.where(time_list==close_time)[0]][0]
    
    print(close_time, close_pt)
    # storage
# =============================================================================
#     EES_dict = {'entry_times': entry_times,
#                 'entry_pts': entry_pts,
#                 'exit_times': exit_times,
#                 'exit_pts': exit_pts,
#                 'stop_times': stop_times,
#                 'stop_pts': stop_pts,
#                 'close_time': close_time,
#                 'close_pt': close_pt
#                 }
# =============================================================================

    EES_dict = {'entry': list(zip(entry_times,entry_pts)),
                'exit': list(zip(exit_times,exit_pts)),
                'close': [close_time, close_pt]
                }
    print('EES_dict', EES_dict)

    # Spit out a Dict of data
    return EES_dict

def trade_choice(EES_dict):
    # a function that control which price to buy and sell
    # Trading choice should be a class on its own. This is just a prototype.
    # I need a whole module of classes related to trade. to operate on portfolio and so on
    
    # if entry list = None, no trade that day
    # else, choose position x or a list of positions
    
    
    if len(EES_dict['entry']) == 0:
        pass
    else:
        # choose the entry point
        trade_open = EES_dict['entry'][0]
        
    #trade_close = EES_dict['exit'][0]
    
    if len(EES_dict['exit']) == 0:
        trade_close = EES_dict['close']
    else:
        # choose the exit point

        trade_close = EES_dict['exit'][0]
    
    
    buy_moment = None
    sell_moment = None
    print("REESS", EES_dict['entry'],EES_dict['exit'])
    #print('trade_open, trade_close', trade_open, trade_close)
    # output: trade_open_time, trade_open_price, trade_close_time, trade_close_price 
   # return trade_open, trade_close

# =============================================================================
# 
# def analysis_cross_percentage():
#     # A function that calculate the percentage of points that crosses over to 
#     # the different regions.
#     return None
# =============================================================================
    

@util.time_it
def run_backtest():
    # master function that runs the backtest itself.
    
    filename_minute = "../test_MS/data_zeroadjust_intradayportara_attempt1/intraday/1 Minute/CL.001"
    filename_buysell_signals = "./benchmark_signal_test.csv"
    
    # read the reformatted minute history data
    history_data = EC_read.read_reformat_Portara_minute_data(filename_minute)
    
    # Find the date for trading
    trade_date_table = prepare_signal_interest(filename_buysell_signals, trim = False)
        
    # loop through the date and set the EES prices for each trading day   
    loop_date(trade_date_table, history_data, plot_or_not = False)    

    # The current method only allows one singular direction signal perday. and a set of constant EES
    

    return None


def run_backtest_list():
    return None



if __name__ == "__main__":
    run_backtest()