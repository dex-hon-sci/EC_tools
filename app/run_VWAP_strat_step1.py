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
    # Add Datetime column into the dataframe
    date_series = [ele.date() for ele in df['Date'].to_list()]
    time_series = df['Time'].to_list()
    datetime_series = [datetime.datetime.combine(date,time) 
                       for date, time in zip(date_series, time_series)]
    
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

def plot_VWAP(df, title='', 
              upmakersx=[],upmakersy=[],
              downmakersx=[],downmakersy=[]):
    fig, axs = plt.subplots(1, 1, figsize=(10, 4), layout='constrained')
    fmt = mdates.DateFormatter("%H:%M:%S")

    axs.plot(df['Datetime'].to_list(), df['Open'].to_list(), 'o-', 
             color='r',ms=1,lw=1)
    axs.plot(df['Datetime'].to_list(), df['Settle'].to_list(), 'o-', 
             color='b',ms=1,lw=1)
    axs.plot(df['Datetime'].to_list(), df['High'].to_list(), '-')
    axs.plot(df['Datetime'].to_list(), df['Low'].to_list(), '-')
    axs.fill_between(df['Datetime'].to_list(), df['Low'].to_list(), 
                     df['High'].to_list(), color='g',alpha=0.3)
    
    axs.plot(df['Datetime'].to_list(), df['VWAP'].to_list(), 'o-', 
             color= 'grey', ms=3)
    axs.plot(df['Datetime'].to_list(), (df['VWAP']+1.28*df['VWAP_DEV']).to_list(), 
             '-', lw=1,color="#c5486a")
    axs.plot(df['Datetime'].to_list(), (df['VWAP']-1.28*df['VWAP_DEV']).to_list(), 
             '-', lw=1, color="#c5486a")
    axs.plot(df['Datetime'].to_list(), (df['VWAP']+2.01*df['VWAP_DEV']).to_list(), 
             '-', lw=1, color="#c5486a")
    axs.plot(df['Datetime'].to_list(), (df['VWAP']-2.01*df['VWAP_DEV']).to_list(), 
             '-', lw=1,color="#c5486a")
    axs.plot(df['Datetime'].to_list(), (df['VWAP']+2.51*df['VWAP_DEV']).to_list(), 
             '--', lw=1,color="#c5486a")
    axs.plot(df['Datetime'].to_list(), (df['VWAP']-2.51*df['VWAP_DEV']).to_list(), 
             '--', lw=1, color="#c5486a")
    axs.plot(df['Datetime'].to_list(), (df['VWAP']+3.09*df['VWAP_DEV']).to_list(), 
             '--', lw=1,color="#c5486a")
    axs.plot(df['Datetime'].to_list(), (df['VWAP']-3.09*df['VWAP_DEV']).to_list(), 
             '--', lw=1, color="#c5486a")
    axs.plot(df['Datetime'].to_list(), (df['VWAP']+4.01*df['VWAP_DEV']).to_list(), 
             '--', lw=1, color="#c5486a")
    axs.plot(df['Datetime'].to_list(), (df['VWAP']-4.01*df['VWAP_DEV']).to_list(), 
             '--', lw=1,color="#c5486a")


    axs.plot(upmakersx, upmakersy,'+',color="green", ms=8)
    axs.plot(downmakersx, downmakersy,'_',color="green",ms=8)
    
    axs.xaxis.set_major_formatter(fmt)
    axs.grid()
    axs.set_title(title)
    axs.set_ylabel('Price')
    axs.set_xlabel('Time')
    plt.legend()
    plt.show()


def add_VWAP2df(df:pd.DataFrame, 
                unique_date:list[datetime.datetime], 
                open_hr: str, close_hr:str)->pd.DataFrame:
    # Add VWAP and STD to a dataframe
    # Generate daily VWAP, add it to the dataframe
    #unique_date = list(set([df["Date"].iloc[i] for i,_ in enumerate(df["Date"].to_list())]))
    #unique_date.sort()

    new_df = pd.DataFrame()
    for date in unique_date:
        print(date, type(date))
        start_date = date + datetime.timedelta(hours = int(open_hr[0:2]),
                                               minutes = int(open_hr[2:4]))
        end_date = date + datetime.timedelta(hours = int(close_hr[0:2]),
                                             minutes = int(close_hr[2:4]))
        
        # Select for a sub-dataframe to calculate the vwap of the day
        sub_df = df[(df['Datetime'] >= start_date) &(df['Datetime'] <end_date)]

        print("sub_df", sub_df)
        new_sub_df = cal_VWAP(sub_df)
        
        # Plot the daily chart to check if the VWAP range is reasonable
        new_df = pd.concat([new_df, new_sub_df])
    return new_df
        
        
#vwapsum = iff(newSession, hl2*volume, vwapsum[1]+hl2*volume)
#volumesum = iff(newSession, volume, volumesum[1]+volume)
#v2sum = iff(newSession, volume*hl2*hl2, v2sum[1]+volume*hl2*hl2)
#myvwap = vwapsum/volumesum
#dev = sqrt(max(v2sum/volumesum - myvwap*myvwap, 0))

from EC_tools.strategy_2 import Strategy
from EC_tools.strategy_2.signal import Signal, SignalType, SignalSide, SignalStatus
#from EC_tools.strategy.signal import SignalType, Signal, SignalSide
from EC_tools.order.cqg_enums import OrderSide, OrderType
from EC_tools.order.cqg_order import CQGOrder

# New Signal format
class VWAPInversionStrategy(Strategy):
    def __init__(self, 
                 asset_name: str, qty: int,
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
        self.asset_name = asset_name
        self.qty = qty
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
        
        ##print("up_bool", up_bool)
        #print("low_bool", low_bool)
        # Exclude the bars that hit both high and low threshold. Dud signals.
        up_bool_exclude = [(ele_up and not ele_low) for ele_up, ele_low in zip(up_bool, low_bool)]
        low_bool_exclude = [(ele_low and not ele_up) for ele_up, ele_low in zip(up_bool, low_bool)]
        
        # The index of upbreach and downbreach
        upbreach_indices = np.arange(len(self._aggmin_data))[up_bool_exclude]
        downbreach_indices = np.arange(len(self._aggmin_data))[low_bool_exclude]
        print("upbreach_indices2", upbreach_indices)
        print("downbreach_indices2", downbreach_indices)

        return upbreach_indices, downbreach_indices
    
    def make_signals(self, 
                     upbreach_indices:np.array, 
                     downbreach_indices: np.array,
                     barclose_threshold_factor: float = 0.75) -> list[dict]:
        
        
        asset_name = self.asset_name
        QTY = self.qty
        signals_dt, signals = [], []
        signal_df = pd.DataFrame()

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
            if cond_sell_list1[0]:
                direction = SignalType.SELL  
            else:
                direction = SignalType.NEUTRAL
            
            ## for Sell signal, next 2 entry Sell
            # Define the price and time parameters
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

            # Make SELL Signal
            if direction == SignalType.SELL:
                # Target-Entry Order
                action_TEO_SHORT = CQGOrder(asset_name,
                                            OrderSide.SIDE_SELL,
                                            OrderType.ORDER_TYPE_MKT,
                                            QTY, open_=True, close_=False,
                                            kwargs={'MKT_time': TE_time})
                # Target-Exit Order
                action_TPO_SHORT = CQGOrder(asset_name,
                                            OrderSide.SIDE_BUY,
                                            OrderType.ORDER_TYPE_LMT,
                                            QTY,  open_=False, close_=True,
                                            kwargs={'LMT_price': TP_price})                 
                # Stop-Loss Order
                action_SLO_SHORT = CQGOrder(asset_name,
                                            OrderSide.SIDE_BUY,
                                            OrderType.ORDER_TYPE_LMT,
                                            QTY,  open_=False, close_=True,
                                            kwargs={'LMT_price': SL_price})
                # Market-Close Order
                action_MCO_SHORT = CQGOrder(asset_name,
                                            OrderSide.SIDE_BUY,
                                            OrderType.ORDER_TYPE_MKT,
                                            QTY,  open_=False, close_=True,
                                            kwargs={'MKT_time': CO_time})
                # For MKT order, use convert2BTorder function and input MKT_price there
                # Action list
                actions = [action_TEO_SHORT, action_TPO_SHORT, 
                           action_SLO_SHORT, action_MCO_SHORT]
                
                S = Signal(SignalType.SELL, # Signal type
                           SignalSide.SELL, # Signal Side
                           SignalStatus.ACTIVE, # Signal status
                           TE_time, # start_time
                           CO_time, # end_time
                           actions) # Orders
                print('===============')
                print("SELL Signal:", TE_time, TE_price, upbreach_index, upbreach_index+2)
                signals.append(S)
                signals_dt.append(TE_time)
                siganl_row = {"signal_datetime": [TE_time], 
                              "signal":[S]}
                signal_df = pd.concat([signal_df, pd.DataFrame(siganl_row)])

                
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
            if cond_sell_list1[0]:
                direction = SignalType.BUY   
            else:
                direction =SignalType.NEUTRAL
            
            ## for Sell signal, next 2 entry Sell
            # Define the price and time parameters
            # Target Entry time and price 
            TE_time = self._aggmin_data['Datetime'].iloc[downbreach_index+2] 
            TE_price = self._aggmin_data['Open'].iloc[downbreach_index+2]
            # Target Entry time and price 
            TP_price = self._aggmin_data['Open'].iloc[downbreach_index+2] - \
                      bar_width*self._TP_multiplier
            # Stop-Loss time and price 
            SL_price = self._aggmin_data['Open'].iloc[downbreach_index+2] + \
                       bar_width*self._SL_multiplier
            # Close Order time
            CO_time = self._aggmin_data['Datetime'].iloc[downbreach_index+2+self._segment_barmulitplier]

            # Make BUY signal
            if direction == SignalType.BUY:
                # Target-Entry Order
                action_TEO_LONG = CQGOrder(asset_name,
                                           OrderSide.SIDE_BUY,
                                           OrderType.ORDER_TYPE_MKT,
                                           QTY, open_=True, close_=False,
                                           kwargs={'MKT_time': TE_time})
                # Target-Exit Order
                action_TPO_LONG = CQGOrder(asset_name,
                                            OrderSide.SIDE_SELL,
                                            OrderType.ORDER_TYPE_LMT,
                                            QTY,  open_=False, close_=True,
                                            kwargs={'LMT_price': TP_price})                 
                # Stop-Loss Order
                action_SLO_LONG = CQGOrder(asset_name,
                                            OrderSide.SIDE_SELL,
                                            OrderType.ORDER_TYPE_LMT,
                                            QTY,  open_=False, close_=True,
                                            kwargs={'LMT_price': SL_price})
                # Market-Close Order
                action_MCO_LONG = CQGOrder(asset_name,
                                            OrderSide.SIDE_SELL,
                                            OrderType.ORDER_TYPE_MKT,
                                            QTY,  open_=False, close_=True,
                                            kwargs={'MKT_time': CO_time})
                # For MKT order, use convert2BTorder function and input MKT_price there
                # Action list
                actions = [action_TEO_LONG, action_TPO_LONG, 
                           action_SLO_LONG, action_MCO_LONG]
                
                S = Signal(SignalType.BUY, # Signal type
                           SignalSide.BUY, # Signal Side
                           SignalStatus.ACTIVE, # Signal status
                           TE_time, # start_time
                           CO_time, # end_time
                           actions) # Orders
                print('===============')
                print("BUY Signal:", TE_time, TE_price, downbreach_index, downbreach_index+2)
                signals.append(S)
                signals_dt.append(TE_time)
                siganl_row = {"signal_datetime": [TE_time], 
                              "signal":[S]}
                signal_df = pd.concat([signal_df, pd.DataFrame(siganl_row)])
                
        signal_df = signal_df.sort_values(by=["signal_datetime"], 
                                          ascending=True)
        return signal_df
    
    def plot_check(self, upbreach_indices, downbreach_indices):
        mkup_y = [self._aggmin_data['High'].iloc[i] for i in upbreach_indices]
        mkup_x = [self._aggmin_data['Datetime'].iloc[i] for i in upbreach_indices]
        mkdown_y = [self._aggmin_data['Low'].iloc[i] for i in downbreach_indices]
        mkdown_x = [self._aggmin_data['Datetime'].iloc[i] for i in downbreach_indices]
        
        date = self._aggmin_data['Datetime'].iloc[0]
        
        plot_VWAP(self._aggmin_data, 
                  title=f"{self.asset_name}: {date.strftime('%Y-%m-%d')}",
                  upmakersx=mkup_x, upmakersy=mkup_y,
                  downmakersx=mkdown_x, downmakersy=mkdown_y)

    def apply_strategy(self):
        
        # generate a pair of upbreach and downbreach indices
        # This shorten the loop by vectorising the intraday data.
        upbreach_indices, downbreach_indices = self.gen_data()
        print("up", upbreach_indices, len(upbreach_indices),
              "down", downbreach_indices, len(downbreach_indices))
        
        self.plot_check(upbreach_indices, downbreach_indices)

        #direction, cond_info = self.run_cond(upbreach_indices, downbreach_indices)
        signal_df = self.make_signals(upbreach_indices, downbreach_indices)
        
        return signal_df 

    
# =============================================================================
# (strategy: type[Strategy], 
#                 book: type[Bookkeep], 
#                 signal_data: pd.DataFrame, 
#                 history_data: pd.DataFrame, 
#                 start_date: datetime.datetime, 
#                 end_date: datetime.datetime,
#                 buy_range: tuple = ([0.25,0.4],[0.6,0.75],0.05), 
#                 sell_range: tuple = ([0.6,0.75],[0.25,0.4],0.95), 
# 
# =============================================================================

# Loop daily and find
def loop_signal(df: pd.DataFrame, 
                unique_date: list[datetime.datetime], 
                asset_name: str, qty: int,
                **kwargs):
    
    master_signal_df = pd.DataFrame()
    
    for date in unique_date:
        #self._N_sigma = N_sigma # mulitplying factor for sigma
        #self._TP_multiplier = TP_multiplier
        #self._SL_multiplier = SL_multiplier
        #self._segment_barmulitplier = segment_barmulitplier

        signal_df = VWAPInversionStrategy(asset_name, qty, 
                                          df, 
                                          kwargs['N_sigma'],
                                          TP_multiplier = kwargs['TP_multiplier'],
                                          SL_multiplier = kwargs['SL_multiplier'],
                                          segment_barmulitplier = \
                                          kwargs['segment_barmulitplier']).apply_strategy()

        master_signal_df = pd.concat([master_signal_df, signal_df])
        
    master_signal_df = master_signal_df.sort_value(by=["signal_datetime"], 
                                                   ascending=True)
    return master_signal_df

from crudeoil_future_const import WRONG_OPEN_HR_DICT, CLOSE_HR_DICT, TIMEZONE_DICT,TEST_FILE_LOC

DEFAULT_KWARGS= {#'history_daily_list': list(HISTORY_DAILY_FILE_LOC.values()),
                 #'history_minute_list': list(HISTORY_MINTUE_FILE_LOC.values()),
                 #'history_daily_pkl': DAILY_DATA_PKL,
                 'open_hr_dict': WRONG_OPEN_HR_DICT, 
                 'close_hr_dict': CLOSE_HR_DICT, 
                 'timezone_dict': TIMEZONE_DICT,
                 'save_filenames_loc':TEST_FILE_LOC,
                 'quantile': [0.05,0.1,0.25,0.4,0.5,0.6,0.75,0.9,0.95],
                 'master_signal_filename': "master_signal.csv",
                 'save_or_not': False,
                 'merge_or_not': True,
                 'contract_symbol_condse': False,
                 'loop_symbol': None,
                 'open_hr': '', 
                 'close_hr': '',
                 'asset_name':'', 
                 'Timezone': "",
                 'qty':1,
                 'N_sigma':2,
                 'TP_multiplier':2, 
                 'SL_multiplier':1,
                 'segment_barmulitplier':4,
                 'time_interval':'15Min'}

# =============================================================================
# (strategy: type[Strategy], 
# #filename_list: list[str], 
# signal_pkl: dict, 
# history_daily_pkl: dict, 
# start_date: str, end_date: str,
# buy_range: tuple[float] = ([0.2,0.25],[0.75,0.8],0.1),
# sell_range: tuple[float] = ([0.75,0.8],[0.2,0.25],0.9),
#  **kwargs) -> pd.DataFrame:
# =============================================================================


def run_gen_signals(#strategy: Strategy, 
                       daily_minute_data_pkl: dict[pd.DataFrame], 
                       start_date: datetime.datetime, 
                       end_date: datetime.datetime, 
                       **kwargs):
    
    default_kwargs = DEFAULT_KWARGS
    kwargs = dict(default_kwargs,**kwargs)

    master_dict, symbol_list = dict(), ['CLc1']

    for symbol in symbol_list:
        # Load Historical data
        HISTORY_MINUTE_PKL = load_source_data_bt([daily_minute_data_pkl[symbol]])

        # reindexing with time
        HISTORY_MINUTE_PKL[symbol] = reindex_dt(HISTORY_MINUTE_PKL[symbol])
        print(HISTORY_MINUTE_PKL[symbol])

        # Preprocess Resample
        # Turn historic data intpo 15 mins interval (default)
        new_df = resample(HISTORY_MINUTE_PKL[symbol], 
                          time_interval=kwargs['time_interval'])
        
        # Select for the range of dates
        new_df = new_df[(new_df['Datetime'] >= start_date) & 
                        (new_df['Datetime'] <= end_date)]

        # Define unique trading date for the script to loop through
        unique_date = list(set([new_df["Date"].iloc[i] 
                           for i,_ in enumerate(new_df["Date"].to_list())]))[1:]
        unique_date.sort()
        
        ####Make Features (Can turn this into another changable function later)
        open_hr, close_hr = kwargs['open_hr_dict'][symbol], kwargs['close_hr_dict'][symbol]
        
        # Calculate VWAP, save it in the dataframe as a new column.
        new_df = add_VWAP2df(new_df, unique_date, open_hr, close_hr)

        asset_name = symbol
        QTY =1 
        print("new_df",new_df)
        print("unique_date",unique_date)
        print("asset_name", asset_name)
        print("QTY", QTY)
        filename = kwargs['save_filenames_loc'][symbol]
        @util.pickle_save("{}".format(filename), save_or_not=kwargs['save_or_not'])
        def run_gen_MR_indi():
            master_signal_df = loop_signal(new_df, 
                                           unique_date, 
                                           asset_name, QTY, 
                                           **kwargs)
            return master_signal_df
        
        master_dict[symbol] = run_gen_MR_indi()


# =============================================================================
# strategy: type[Strategy], 
#                         start_date: str, end_date: str,
#                         buy_range: tuple[float] = (0.4,0.6,0.1), 
#                         sell_range: tuple[float] = (0.6,0.4,0.9),
#                         runtype: str = 'list', 
#                         **kwargs) -> None:
    
# =============================================================================
#             # The strategy will be ran in loop_signal decorator
#             master_signal_dict = loop_signal(df: pd.DataFrame, 
#                             unique_date: list[datetime.datetime], 
#                             asset_name: str, qty: int
#             return master_signal_dict
#         
# 
#         master_dict[symbol] = run_gen_MR_indi()
# 
#     return master_dict
# 
# =============================================================================
# =============================================================================

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
    signal_df = VWAPInversionStrategy(new_df,2).apply_strategy()
    print(signal_df)
    
    
#main()
start_date = datetime.datetime(2024,10,4)
end_date = datetime.datetime(2024,10,8)
run_gen_signals(DAILY_MINUTE_DATA_INDI_PKL, start_date, end_date )