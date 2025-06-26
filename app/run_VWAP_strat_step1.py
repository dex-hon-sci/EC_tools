#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 24 17:31:37 2025

@author: dexter
"""
import sys
sys.path.insert(0, "/home/dexter/Euler_Capital_codes/EC_tools")
import datetime
import pandas as pd
import numpy as np

import EC_tools.utility as util
from crudeoil_future_const import DAILY_MINUTE_DATA_INDI_PKL

def load_source_data_bt(filenames_loc: list) -> dict:
    master_dict = {}
    for filename in filenames_loc:
        temp_dict = util.load_pkl(filename)
        master_dict = dict(master_dict, **temp_dict)
        
    return master_dict

def reindex_dt(df:pd.DataFrame):
    date_series = [ele.date() for ele in df['Date'].to_list()]
    time_series = df['Time'].to_list()
    datetime_series = [datetime.datetime.combine(date,time) for date, time in zip(date_series, time_series)]
    
    df['Datetime'] = datetime_series
    df = df.set_index('Datetime')
    #df.reset_index(inplace=True)

    return df

def resample(df: pd.DataFrame, time_interval = "15Min"):
    ohlc_dict = {'Date':'first',
                 #'Time': '',
                'Open': 'first',
                'High': 'max',
                'Low': 'min',
                'Settle': 'last',
                'Volume': 'sum'  # Include if volume data is present
                }

    new_df = df.resample(time_interval).apply(ohlc_dict)
    new_df['Datetime'] = new_df.index

    return new_df


def cal_VWAP(df:pd.DataFrame):
    # high + low + close
    TPrice = (df['High'] + df['Low'] + df['Settle'])/3
    TPVolume_cumsum = (TPrice*df['Volume']).cumsum() #vwapsum
    TP2Volume_cumsum = (TPrice*TPrice*df['Volume']).cumsum() #v2sum
    volume_cumsum = df['Volume'].cumsum()
    
    # Calculate the VWAP value
    vwap = TPVolume_cumsum/volume_cumsum
    # Calculate the std of the vwap
    dev = np.sqrt((TP2Volume_cumsum/volume_cumsum-vwap*vwap))
    print('vwap',vwap, 'dev',dev)
    df['VWAP'] = vwap
    df['VWAP_DEV'] = dev
    return df

import matplotlib.dates as mdates
import matplotlib.pyplot as plt

def plot_VWAP(df, title=''):
    fig, axs = plt.subplots(1, 1, figsize=(10, 4), layout='constrained')
    fmt = mdates.DateFormatter("%H:%M:%S")

    axs.plot(df['Datetime'].to_list(), df['Open'].to_list(), 'o-')
    axs.plot(df['Datetime'].to_list(), df['VWAP'].to_list(), 'o-', color= 'grey', ms=3)
    axs.plot(df['Datetime'].to_list(), (df['VWAP']+1.28*df['VWAP_DEV']).to_list(), 'r-', ms=3)
    axs.plot(df['Datetime'].to_list(), (df['VWAP']-1.28*df['VWAP_DEV']).to_list(), 'r-', ms=3)
    axs.plot(df['Datetime'].to_list(), (df['VWAP']+2.01*df['VWAP_DEV']).to_list(), 'r-', ms=3)
    axs.plot(df['Datetime'].to_list(), (df['VWAP']-2.01*df['VWAP_DEV']).to_list(), 'r-', ms=3)
    axs.plot(df['Datetime'].to_list(), (df['VWAP']+2.51*df['VWAP_DEV']).to_list(), 'r--', ms=3)
    axs.plot(df['Datetime'].to_list(), (df['VWAP']-2.51*df['VWAP_DEV']).to_list(), 'r--', ms=3)
    axs.plot(df['Datetime'].to_list(), (df['VWAP']+3.09*df['VWAP_DEV']).to_list(), 'r--', ms=3)
    axs.plot(df['Datetime'].to_list(), (df['VWAP']-3.09*df['VWAP_DEV']).to_list(), 'r--', ms=3)
    axs.plot(df['Datetime'].to_list(), (df['VWAP']+4.01*df['VWAP_DEV']).to_list(), 'r--', ms=3)
    axs.plot(df['Datetime'].to_list(), (df['VWAP']-4.01*df['VWAP_DEV']).to_list(), 'r--', ms=3)

    axs.xaxis.set_major_formatter(fmt)
    axs.grid()
    axs.set_title(title)
    axs.set_ylabel('Price')
    axs.set_xlabel('Time')
    plt.legend()
    plt.show()


def add_VWAP2df(df, unique_date):
    # Add VWAP and STD to a dataframe
    # Generate daily VWAP, add it to the dataframe
    #unique_date = list(set([df["Date"].iloc[i] for i,_ in enumerate(df["Date"].to_list())]))
    #unique_date.sort()

    new_df = pd.DataFrame()
    for date in unique_date[1:2]:
        print(date, type(date))
        start_date = date + datetime.timedelta(hours=3,minutes=30)
        end_date = date + datetime.timedelta(hours=22,minutes=0)
        
        # Select for a sub-dataframe to calculate the vwap of the day
        sub_df = df[(df['Datetime'] >= start_date) &(df['Datetime'] <end_date)]

        print("sub_df", sub_df)
        new_sub_df = cal_VWAP(sub_df)
        
        # Plot the daily chart to check if the VWAP range is reasonable
        plot_VWAP(new_sub_df,title=f"CLc1: {date.strftime('%Y-%m-%d')}")
        new_df = pd.concat([new_df, new_sub_df])
    return new_df
        
        
#vwapsum = iff(newSession, hl2*volume, vwapsum[1]+hl2*volume)
#volumesum = iff(newSession, volume, volumesum[1]+volume)
#v2sum = iff(newSession, volume*hl2*hl2, v2sum[1]+volume*hl2*hl2)
#myvwap = vwapsum/volumesum
#dev = sqrt(max(v2sum/volumesum - myvwap*myvwap, 0))

from EC_tools.strategy import Strategy
from EC_tools.strategy.signal import SignalType, Signal

# New Signal format
class VWAPInversionStrategy(Strategy):
    def __init__(self, 
                 aggmin_data:pd.DataFrame, 
                 N_sigma:float,
                 TP_multiplier: float|int = 2,
                 SL_multiplier: float|int = 1,
                 segment_barmulitplier: float|int = 4):
        # One active trade at a time
        
        # We have to monitor three rows of data
        # 1) Initial 15 mins for VWAP condition (Signal)
        # 2) Confirmation Second 15mins for 70% inversion (signal)
        # 3) Next four 15mins for trading (This one we do it in backtest)
        super().__init__()

        self._aggmin_data = aggmin_data #aggegrated minute data (Any mins chuck)
        self._N_sigma = N_sigma # mulitplying factor for sigma
        self._TP_multiplier = TP_multiplier
        self._SL_multiplier = SL_multiplier
        self._segment_barmulitplier = segment_barmulitplier
        
        # Calculate the ranges for the VWAP Inversion
        self.VWAP_up = self._aggmin_data['VWAP'] + self._aggmin_data['VWAP_DEV']*self._N_sigma
        self.VWAP_low = self._aggmin_data['VWAP'] - self._aggmin_data['VWAP_DEV']*self._N_sigma
            
        self._sub_buy_cond_dict = dict()
        self._sub_sell_cond_dict = dict()
        self.sub_cond_dict = {'Buy':[], 'Sell':[], 'Neutral': []}
        
        self.strategy_name = 'VWAP_Inversion'

    
    def gen_data(self) -> tuple[np.array]:
        # Find the time(index) where one of the 15min OHLC is higher/lower
        # than the threshold
        # The boolean value for price going above the upper VWAP threshold
        #up_bool_open = np.sign(self._aggmin_data['Open'] - self.VWAP_up) > 0
        up_bool_high = np.sign(self._aggmin_data['High'] - self.VWAP_up) > 0
        up_bool_low = np.sign(self._aggmin_data['Low'] - self.VWAP_up) > 0
        #up_bool_close = np.sign(self._aggmin_data['Settle'] - self.VWAP_up) > 0
        
        # If any of these are true, it means 
        #up_bool = (up_bool_open or up_bool_high or up_bool_low or up_bool_close)
        up_bool = [(bool1 or bool2) for bool1,bool2 in zip(up_bool_high, up_bool_low)]
        
        # The boolean value for price going below the lower VWAP threshold
        #low_bool_open = np.sign(self._aggmin_data['Open'] - self.VWAP_low) < 0
        low_bool_high = np.sign(self._aggmin_data['High'] - self.VWAP_low) < 0 
        low_bool_low = np.sign(self._aggmin_data['Low'] - self.VWAP_low) < 0
        #low_bool_close = np.sign(self._aggmin_data['Settle'] - self.VWAP_low) <0
        
        #print("up_bool_high", up_bool_high, "up_bool_low", up_bool_low)
        #print("low_bool_high", low_bool_high,"low_bool_low", low_bool_low)
        
        # If any of these are true, it means the bar has hit the threshold in this minute
        # XOR condition, if 
        #low_bool = (low_bool_open or low_bool_high or low_bool_low or low_bool_close)
        low_bool = [(bool1 or bool2) for bool1,bool2 in zip(low_bool_high, low_bool_low)]
        #print("up_bool", up_bool)
        #print("low_bool", low_bool)

        upbreach_indices = np.arange(len(self._aggmin_data))[up_bool]
        downbreach_indices = np.arange(len(self._aggmin_data))[low_bool]
        #print("upbreach_indices", upbreach_indices)
        #print("downbreach_indices", downbreach_indices)
        return upbreach_indices, downbreach_indices
    
    def run_cond(self, 
                 upbreach_indices:np.array, 
                 downbreach_indices: np.array,
                 barclose_threshold_factor: float = 0.75) -> list[dict]:
        # Loop through the day based on the upbreach_indices and downbreach_indices

        for upbreach_index in upbreach_indices:
            # If 15mins data < VWAP upper Threshold
            # And next 15mins bar close at 70% above the previous bar
            # -> Sell direction
            #cond_buy_list1= [len(last_data_1min[last_data_1min['Open']>VWAP_up])>0]
            bar_width = self._aggmin_data['High'].iloc[upbreach_index] - \
                        self._aggmin_data['Low'].iloc[upbreach_index] 
            barclose_threshold = self._aggmin_data['High'].iloc[upbreach_index] - \
                                 bar_width* barclose_threshold_factor
            
            second_settle = self._aggmin_data['Settle'].iloc[upbreach_index+1]
            # IF the close of the next bar is lower than the limit
            cond_sell_list1= [(second_settle < barclose_threshold)]
            
            # Assign direction
            direction = SignalType.SELL if cond_sell_list1[0] else SignalType.NEUTRAL
            
            if direction == SignalType.SELL:
                
                #for Sell signal, next 2 entry Sell
                # Target Entry time and price 
                TE_time = self._aggmin_data['Datetime'].iloc[upbreach_index+2] 
                TE_price = self._aggmin_data['Open'].iloc[upbreach_index+2]
                # Target Entry time and price 
                TP_price = self._aggmin_data['Open'].iloc[upbreach_index+2] - \
                          bar_width*self._TP_multiplier
                # Stop-Loss time and price 
                SL_price = self._aggmin_data['Open'].iloc[upbreach_index+2] + \
                           bar_width*self._SL_multiplier
                # Close Order time
                CO_time = self._aggmin_data['Datetime'].iloc[upbreach_index+2+self._segment_barmulitplier]
                
                signal_dict = {"direction": direction, 
                               'TE_ordertype': "MKT", # for MKT, entry search for time, for LMT or STP, search for price
                               "TE_time": TE_time,
                               "TE_price": TE_price,
                               "segment_starttime": self._aggmin_data['Datetime'].iloc[upbreach_index+2],
                               "segment_endtime": self._aggmin_data['Datetime'].iloc[upbreach_index+2+self._segment_barmulitplier],
                               "TP_ordertype": "LMT",
                               "TP_price": TP_price,
                               "TP_ordertype": "STP",
                               "SL_price": SL_price
                               }
                print(signal_dict)
                
                
                Signal()
                
                action1 = {"order_side": direction,
                           "order_type": "MKT",
                           "time": TE_time,
                           "price": TE_price, 
                           }
                
                action2 = {"order_side": SignalType.BUY,
                           "order_type": "LMT",
                           "price": TP_price, 
                           }
                
                action3 = {"order_side": SignalType.BUY,
                           "order_type": "STP",
                           "price": SL_price, 
                           }
                action4 = {"order_side": SignalType.BUY,
                           "order_type": "STP",
                           "price": SL_price}
                
        for downbreach_index in downbreach_indices:
            # If 15mins data > VWAP upper Threshold
            # And next 15mins bar close at 70% below the previous bar
            # ->Sell direction
            #cond_sell_list1= [len(last_data_1min[last_data_1min['Open']<VWAP_low])>0]
            bar_width = self._aggmin_data['High'].iloc[downbreach_index] - \
                        self._aggmin_data['Low'].iloc[downbreach_index] 
            barclose_threshold = self._aggmin_data['Low'].iloc[downbreach_index] + \
                                 bar_width* barclose_threshold_factor
                                 
            second_settle = self._aggmin_data['Settle'].iloc[downbreach_index+1]

            # IF the close of the next bar is higher than the limit
            cond_buy_list1= [second_settle > barclose_threshold]
            
            # Assign direction
            direction = SignalType.BUY if cond_sell_list1[0] else SignalType.NEUTRAL
            
            
            if direction == SignalType.BUY:
                pass

         
    
    def set_EES(self):
        # Duration (default = 4 bars)
        # set EES prices
        match self.direction:
            case SignalType.BUY:
                # (A) Entry price
                entry_price = float(0)
                # (B) Exit price
                exit_price = float(0)
                # (C) Stop loss at APC p=0.1
                stop_loss = float(0)
                print("Buy Direction!")

                
            case SignalType.SELL:
                # (A) Entry price
                entry_price = float(0)
                # (B) Exit price
                exit_price = float(1)
                # (C) Stop loss at APC p=0.9
                stop_loss = float(2)
                print("Sell Direction!")

            
            case SignalType.NEUTRAL:
                entry_price = "NA"
                exit_price = "NA"
                stop_loss = "NA"
                print("Neutral Direction!")
            case _:
                raise Exception(
                'Unaccepted input, condition needs to be either Buy, \
                    Sell, or Neutral.')
            
        return entry_price, exit_price, stop_loss
    
    def apply_strategy(self):
        
        # generate a pair of upbreach and downbreach indices
        # This shorten the loop by vectorising the intraday data.
        upbreach_indices, downbreach_indices = self.gen_data()
        print("up", upbreach_indices, len(upbreach_indices),
              "down", downbreach_indices, len(downbreach_indices))
        #
        #direction, cond_info = self.run_cond(upbreach_indices, downbreach_indices)
        self.run_cond(upbreach_indices, downbreach_indices)
        
        #entry_price, exit_price, stop_loss = self.set_EES()


        # Bookkeeping area
        #EES = [entry_price, exit_price, stop_loss]
        #EES_val = [entry_price, exit_price, stop_loss]
        
        
        # put all the data in a singular list. This is to be added in the 
        # data list in the loop
        
        #data =  cond_info + quantile_info + EES_val + [self.strategy_name]
        
        return #{'data': data, 'direction': direction.value}

    
# Loop daily and find
def loop_signal():
    for i in range(10):
        
        VWAPInversionStrategy(new_df,1.2).apply_strategy()

        pass
    
    return 


def main():
    
    # Load Historical data
    #HISTORY_MINUTE_PKL = load_source_data_bt(list(DAILY_MINUTE_DATA_INDI_PKL.values()))
    HISTORY_MINUTE_PKL = load_source_data_bt([DAILY_MINUTE_DATA_INDI_PKL['CLc1']])

    # reindexing with time
    HISTORY_MINUTE_PKL['CLc1'] = reindex_dt(HISTORY_MINUTE_PKL['CLc1'])
    print(HISTORY_MINUTE_PKL['CLc1'])

    # Preprocess Resample
    # Turn historic data intpo 15 mins interval
    new_df = resample(HISTORY_MINUTE_PKL['CLc1'])
    
    # Select for only entries after 2021-1-1
    new_df = new_df[new_df['Datetime'] > datetime.datetime(2024,10,4)]
    print(new_df)
    
    # Define unique trading date for the script to loop through
    unique_date = list(set([new_df["Date"].iloc[i] 
                       for i,_ in enumerate(new_df["Date"].to_list())]))
    unique_date.sort()
    
    # Calculate VWAP, save it in the dataframe as a new column.
    # Plot them if needed
    new_df = add_VWAP2df(new_df, unique_date)
    
    print("new_df", new_df, len(new_df))
    
    # New Signal format
    # Loop daily and find
    VWAPInversionStrategy(new_df,1.2).apply_strategy()

main()