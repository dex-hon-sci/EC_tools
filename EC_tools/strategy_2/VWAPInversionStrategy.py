#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul  1 13:51:48 2025

@author: dexter

Each Strategy module contain the Strategy class and a loop_signal function
"""
import datetime
import pandas as pd
import numpy as np
from EC_tools.strategy_2 import Strategy
from EC_tools.strategy_2.signal import Signal, SignalType, SignalSide, SignalStatus
#from EC_tools.strategy.signal import SignalType, Signal, SignalSide
from EC_tools.order.cqg_enums import OrderSide, OrderType
from EC_tools.order.cqg_order import CQGOrder

import matplotlib.dates as mdates
import matplotlib.pyplot as plt


def plot_VWAP(df, title='', 
              upmakersx=[],upmakersy=[],
              downmakersx=[],downmakersy=[]):
    plt.style.use('dark_background')

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
    
    date_str = df['Datetime'].to_list()[0].strftime('%Y-%m-%d')

    axs.plot(upmakersx, upmakersy,'+',color="green", ms=15)
    axs.plot(downmakersx, downmakersy,'_',color="green",ms=15)
    
    axs.xaxis.set_major_formatter(fmt)
    axs.grid()
    axs.set_title(title)
    axs.set_ylabel('Price')
    axs.set_xlabel('Time')
    plt.legend()
    #plt.show()
    plt.savefig(f"/home/dexter/Euler_Capital_codes/EC_tools/results/VWAP_Inversion/plots/VWAP_{date_str}.png", dpi=150)

# New Signal format
class VWAPInversionStrategy(Strategy):
    def __init__(self, 
                 asset_name: str, qty: int,
                 aggmin_data: pd.DataFrame, 
                 aggmin_data_out: pd.DataFrame, 
                 N_sigma:float,
                 TP_multiplier: float|int = 2,
                 SL_multiplier: float|int = 2,
                 segment_barmulitplier: float|int = 4,
                 reversal_factor_long: float = 0.75,
                 reversal_factor_short: float = 0.25,
                 startsignal_index: int = 1): 
        #startsignal_index is the index number after detecting a breach (15mins step)
        # One active trade at a time
        
        # We have to monitor three rows of data
        # 1) Initial 15 mins for VWAP condition (Signal)
        # 2) Confirmation Second 15mins for 70% inversion (signal)
        # 3) Next four 15mins for trading (This one we do it in backtest)
        super().__init__()
        self.asset_name = asset_name
        self.qty = qty
        self._aggmin_data = aggmin_data #aggegrated minute data (Any mins chuck)
        self._aggmin_data_out = aggmin_data_out #aggegrated minute data (Any mins chuck)
        
        self._N_sigma = N_sigma # mulitplying factor for sigma
        self._TP_multiplier = TP_multiplier
        self._SL_multiplier = SL_multiplier
        self._segment_barmulitplier = segment_barmulitplier
        self.reversal_factor_long = reversal_factor_long
        self.reversal_factor_short = reversal_factor_short
        self.startsignal_index = startsignal_index
        
        # Calculate the ranges for the VWAP Inversion
        self.VWAP_up = self._aggmin_data['VWAP'] + self._aggmin_data['VWAP_DEV']*self._N_sigma
        self.VWAP_low = self._aggmin_data['VWAP'] - self._aggmin_data['VWAP_DEV']*self._N_sigma
        self.VWAP_up_out = self._aggmin_data_out['VWAP'] + self._aggmin_data_out['VWAP_DEV']*self._N_sigma
        self.VWAP_low_out = self._aggmin_data_out['VWAP'] - self._aggmin_data_out['VWAP_DEV']*self._N_sigma
            
        self._sub_buy_cond_dict = dict()
        self._sub_sell_cond_dict = dict()
        self.sub_cond_dict = {'Buy':[], 'Sell':[], 'Neutral': []}
        
        self.strategy_name = 'VWAP_Inversion'

    
    def gen_data(self) -> tuple[np.array]:
        # Find the time(index) where one of the 15min OHLC is higher/lower
        # than the threshold
        
        # ======Pine Script reference=====
        # barRange = high - low
        #bullRev = close >= (low + 0.75 * barRange)
        #bearRev = close <= (low + 0.25 * barRange)
        #longCondition = (low <= D1 or low <= D2 or low <= D3)
        #shortCondition = (high >= U1 or high >= U2 or high >= U3)

        #revBullConfirmed = longCondition and bullRev
        #revBearConfirmed = shortCondition and bearRev

        # ================For Short===========================================
        # The boolean value for price going above the upper VWAP threshold
        up_bool_open = np.sign(self._aggmin_data['Open'] - self.VWAP_up) > 0
        up_bool_low = np.sign(self._aggmin_data['Low'] - self.VWAP_up) > 0
        
        # the high of the breach bar being above than the VWAP threshold
        up_bool_high = np.sign(self._aggmin_data['High'] - self.VWAP_up) > 0
        # Define barRange using the breach bar
        bar_range_short = self._aggmin_data['High'] - self._aggmin_data['Low']
        
        # Direction of reversal bar
        up_bool_dir = np.sign(self._aggmin_data['Settle'] - 
                              self._aggmin_data['Open']) < 0 
        
        # Check if the reversal bar close is above a predefined range
        up_bool_close_range = np.sign(self._aggmin_data['Settle'] - 
                                     (self._aggmin_data['High'] -
                                      self.reversal_factor_short*bar_range_short)) <= 0
        
        # Additional close condition, reversal bar close above VWAP threshold
        up_bool_close_above_limit = np.sign(self._aggmin_data['High'] -self.VWAP_up) > 0
                                            
        # If any of these are true, it means we have a short signal
        #up_bool = [(bool1 or bool2) for bool1,bool2 in 
        #            zip(up_bool_high, up_bool_low)] # old configuration
        up_bool = [(bool1 and bool2 and bool3) 
                   for bool1, bool2, bool3 in 
                   zip(up_bool_close_range,
                       up_bool_close_above_limit,
                       up_bool_dir)] # Bar1 and 2 the same (situation 1)
        # up_bool = [bool1 for bool1 in up_bool_close_above_limit] # Bar1Bar2Bar3 not the same
        # ================For Long============================================
        # The boolean value for price going below the lower VWAP threshold
        low_bool_open = np.sign(self._aggmin_data['Open'] - self.VWAP_low) < 0
        low_bool_high = np.sign(self._aggmin_data['High'] - self.VWAP_low) < 0 
        
        # the low of the breach bar being lower than the VWAP threshold
        low_bool_low = np.sign(self._aggmin_data['Low'] - self.VWAP_low) < 0
        # Define barRange using the breach bar
        bar_range_long = self._aggmin_data['High'] - self._aggmin_data['Low']
        
        # Direction of reversal bar
        low_bool_dir = np.sign(self._aggmin_data['Settle'] - 
                               self._aggmin_data['Open']) > 0 
        
        # Check if the reversal close is below a predefined range
        low_bool_close_range = np.sign(self._aggmin_data['Settle'] - 
                                      (self._aggmin_data['Low'] +
                                       self.reversal_factor_long*bar_range_long)) >= 0
        # Additional close condition, reversal bar close above VWAP threshold
        low_bool_close_below_limit = np.sign(self._aggmin_data['Low'] - self.VWAP_low) < 0

        #print("up_bool_high", up_bool_high, "up_bool_low", up_bool_low)
        #print("low_bool_high", low_bool_high,"low_bool_low", low_bool_low)
        
        # If any of these are true, it means the bar has hit the threshold in this minute
        #low_bool = [(bool1 or bool2) for bool1,bool2 in 
        #             zip(low_bool_high, low_bool_low)] # old configuration
        low_bool = [(bool1 and bool2 and bool3)  
                    for bool1, bool2, bool3 in 
                    zip(low_bool_close_range,
                        low_bool_close_below_limit,
                        low_bool_dir)] # Bar1 and 2 the same (situation 1)
        #low_bool = [bool1 for bool1 in low_bool_close_below_limit]
        
        # ========== Exclude bars that hit both upbreach and downbreach =====
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
                     ) -> list[dict]:
        
        
        asset_name = self.asset_name
        QTY = self.qty
        signals_dt, signals = [], []
        signal_df = pd.DataFrame()

        #// === Entry Trigger ===
        #longEntry = revBullConfirmed and high >= reversalHigh
        #shortEntry = revBearConfirmed and low <= reversalLow

        # Loop through the day based on the upbreach_indices and downbreach_indices
        for upbreach_index in upbreach_indices:
            print('--upbreach loop--')
            # If 15mins data < VWAP upper Threshold
            # And next 15mins bar close at 70% above the previous bar
            # -> Sell direction
            bar_width = abs(self._aggmin_data_out['High'].iloc[upbreach_index] - \
                            self._aggmin_data_out['Low'].iloc[upbreach_index])
            #barclose_threshold = self._aggmin_data_out['Low'].iloc[upbreach_index] - \
            #                     bar_width* self.reversal_factor_short
            #barclose_threshold = self._aggmin_data_out['Low'].iloc[upbreach_index]
            #print('bar_width, barclose_thr', bar_width, barclose_threshold)
            barclose_threshold = self.VWAP_up_out.iloc[upbreach_index]

            #second_settle = self._aggmin_data_out['Settle'].iloc[upbreach_index+1]
            first_settle = self._aggmin_data_out['Settle'].iloc[upbreach_index]
            first_high = self._aggmin_data_out['High'].iloc[upbreach_index]
            first_low = self._aggmin_data_out['Low'].iloc[upbreach_index]
            first_open = self._aggmin_data_out['Open'].iloc[upbreach_index]
            
            # IF the close of the next bar is lower than the limit
            #cond_sell_list1= [(second_low <= barclose_threshold)]
            cond_sell_list1= [True] # Bar1Bar2 the same
            #cond_sell_list1= [((second_settle-second_open)<0), # Down direction
            #                  ((second_settle-(second_low+bar_width*self.reversal_factor_short))<=0), #settle lower than a range
            #                  ((second_settle-barclose_threshold)>0) # second close still higher than VWAP_up 
            #                  ] # Bar1Bar2Bar3 not the same
            
            # Assign direction
            if all(cond_sell_list1):
                direction = SignalType.SELL
            else:
                direction = SignalType.NEUTRAL
            
            ## for Sell signal, next 2 entry Sell
            # Define the price and time parameters
            # Target Entry time and price 
            # Start time is move after the upbreach index by startsignal_index steps
            TE_time = self._aggmin_data_out['Datetime'].iloc[upbreach_index+\
                                                             self.startsignal_index] 
            #TE_price = self._aggmin_data_out['Open'].iloc[upbreach_index+2]
            TE_price = self._aggmin_data_out['Open'].iloc[upbreach_index+\
                                                             self.startsignal_index]
            # Target Entry time and price 
            #TP_price = self._aggmin_data_out['Open'].iloc[upbreach_index+1] - \
            #          bar_width*self._TP_multiplier
            TP_price = first_low - \
                       bar_width*self._TP_multiplier

            # Stop-Loss time and price 
            #SL_price = self._aggmin_data_out['Open'].iloc[upbreach_index+1] + \
            #           bar_width*self._SL_multiplier + \
            #           self._aggmin_data_out['ATR'].iloc[upbreach_index]
            SL_price = self._aggmin_data_out['High'].iloc[upbreach_index] + \
                       self._aggmin_data_out['ATR'].iloc[upbreach_index]

            print("problem_index", upbreach_index, self._segment_barmulitplier,
                  upbreach_index+2+self._segment_barmulitplier)
            print("len", len(self._aggmin_data['Datetime']), 
                  len(self._aggmin_data_out['Datetime']))
            print(self._aggmin_data_out['Datetime'].iloc[upbreach_index+
                                                         self.startsignal_index+
                                                         self._segment_barmulitplier])

            # Close Order time
            #CO_time = self._aggmin_data_out['Datetime'].iloc[-1] #endofday closing condition
            CO_time = self._aggmin_data_out['Datetime'].iloc[upbreach_index+
                                                             self.startsignal_index+
                                                             self._segment_barmulitplier]


            # Make SELL Signal
            if direction == SignalType.SELL:
                # Target-Entry Order
                action_TEO_SHORT = CQGOrder(asset_name,
                                            OrderSide.SIDE_SELL,
                                            OrderType.ORDER_TYPE_MKT,
                                            QTY, open_=True, close_=False,
                                            kwargs={'MKT_time': TE_time,
                                                    'MKT_price':TE_price})
                
                #action_TEO_SHORT = CQGOrder(asset_name,
                #                            OrderSide.SIDE_SELL,
                #                            OrderType.ORDER_TYPE_LMT,
                #                            QTY, open_=True, close_=False,
                #                            kwargs={'LMT_price':TE_price})
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
                           SignalStatus.INACTIVE, # Signal status
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
            print('--downbreach loop--')

            # If 15mins data > VWAP upper Threshold
            # And next 15mins bar close at 70% Above the previous bar
            # ->Buy direction
            bar_width = abs(self._aggmin_data_out['High'].iloc[downbreach_index] - \
                            self._aggmin_data_out['Low'].iloc[downbreach_index])
            #barclose_threshold = self._aggmin_data_out['Low'].iloc[downbreach_index] - \
            #                     bar_width* self.reversal_factor_long # old configuration
            #barclose_threshold = self._aggmin_data_out['High'].iloc[downbreach_index]
            barclose_threshold = self.VWAP_low_out.iloc[downbreach_index]


            #print('bar_width, barclose_thr', bar_width, barclose_threshold)
            #print("second_settle_problem", downbreach_index+1, 
            #      len(self._aggmin_data_out['Settle']))
            first_settle = self._aggmin_data_out['Settle'].iloc[downbreach_index]
            first_open = self._aggmin_data_out['Open'].iloc[downbreach_index]
            first_high = self._aggmin_data_out['High'].iloc[downbreach_index]
            first_low = self._aggmin_data_out['Low'].iloc[downbreach_index]

            # IF the close of the next bar is higher than the limit
            #cond_buy_list1= [(second_high >= barclose_threshold)]
            cond_buy_list1= [True] # 
            #cond_buy_list1= [((second_settle-second_open)>0), # Up direction
            #                  ((second_settle-(second_high-bar_width*self.reversal_factor_long))>=0), #settle higher than a range
            #                  ((second_settle-barclose_threshold)<0) # second close still higher than VWAP_down
            #                  ] # Bar1Bar2Bar3 not the same

            # Assign direction
            if all(cond_buy_list1):
                direction = SignalType.BUY  
            else:
                direction =SignalType.NEUTRAL
            
            ## for Sell signal, next 2 entry Sell
            # Define the price and time parameters
            # Target Entry time and price 
            # Start time is move after the upbreach index by startsignal_index steps
            TE_time = self._aggmin_data_out['Datetime'].iloc[downbreach_index+
                                                             self.startsignal_index] 
            #TE_price = self._aggmin_data_out['Open'].iloc[downbreach_index+2]
            TE_price = self._aggmin_data_out['Open'].iloc[downbreach_index+
                                                             self.startsignal_index] 
            # Target Entry time and price 
            #TP_price = self._aggmin_data_out['Open'].iloc[downbreach_index+1] + \
            #          bar_width*self._TP_multiplier
            #TP_price = self._aggmin_data_out['High'].iloc[downbreach_index+1] + \
            #           bar_width*self._TP_multiplier
            TP_price = first_high + bar_width*self._TP_multiplier

            # Stop-Loss time and price 
            #SL_price = self._aggmin_data_out['Open'].iloc[downbreach_index+1] - \
            #           bar_width*self._SL_multiplier -\
            #           self._aggmin_data_out['ATR'].iloc[downbreach_index] # old configuration
            SL_price = self._aggmin_data_out['Low'].iloc[downbreach_index] - \
                       self._aggmin_data_out['ATR'].iloc[downbreach_index] # Bar1 Bar2 the same

                       
            print("problem_index", downbreach_index, self._segment_barmulitplier,
                  downbreach_index+2+self._segment_barmulitplier)
            print("len", len(self._aggmin_data['Datetime']), 
                  len(self._aggmin_data_out['Datetime']))
            print(self._aggmin_data_out['Datetime'].iloc[downbreach_index+
                                                         self.startsignal_index+
                                                         self._segment_barmulitplier])

            # Close Order time
            CO_time = self._aggmin_data_out['Datetime'].iloc[downbreach_index+
                                                             self.startsignal_index+
                                                             self._segment_barmulitplier]
            #CO_time = self._aggmin_data_out['Datetime'].iloc[-1]

            # Make BUY signal
            if direction == SignalType.BUY:
                # Target-Entry Order
                action_TEO_LONG = CQGOrder(asset_name,
                                           OrderSide.SIDE_BUY,
                                           OrderType.ORDER_TYPE_MKT,
                                           QTY, open_=True, close_=False,
                                           kwargs={'MKT_time': TE_time,
                                                   'MKT_price':TE_price})
                #action_TEO_LONG = CQGOrder(asset_name,
                #                           OrderSide.SIDE_BUY,
                #                           OrderType.ORDER_TYPE_LMT,
                #                           QTY, open_=True, close_=False,
                #                           kwargs={'LMT_price':TE_price})

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
                           SignalStatus.INACTIVE, # Signal status
                           TE_time, # start_time
                           CO_time, # end_time
                           actions) # Orders
                print('===============')
                print("BUY Signal:", TE_time, TE_price, downbreach_index, downbreach_index+2)
                signals.append(S)
                signals_dt.append(TE_time)
                print("signal, signal_datetime", S, TE_time)
                siganl_row = {"signal_datetime": [TE_time], 
                              "signal":[S]}
                signal_df = pd.concat([signal_df, pd.DataFrame(siganl_row)])
        
        #signal_df = signal_df.sort_values(by=["signal_datetime"], 
        #                                  ascending=True)
        return signal_df
    
    def plot_check(self, upbreach_indices, downbreach_indices):
        mkup_y = [self._aggmin_data['High'].iloc[i] for i in upbreach_indices]
        mkup_x = [self._aggmin_data['Datetime'].iloc[i] for i in upbreach_indices]
        mkdown_y = [self._aggmin_data['Low'].iloc[i] for i in downbreach_indices]
        mkdown_x = [self._aggmin_data['Datetime'].iloc[i] for i in downbreach_indices]
        
        print("plot_print", self._aggmin_data['Datetime'])
        
        date = self._aggmin_data['Datetime'].iloc[0]
        
        plot_VWAP(self._aggmin_data, 
                  title=f"{self.asset_name}: {date.strftime('%Y-%m-%d')}",
                  upmakersx=mkup_x, upmakersy=mkup_y,
                  downmakersx=mkdown_x, downmakersy=mkdown_y)

    def apply_strategy(self)-> None:
        
        # generate a pair of upbreach and downbreach indices
        # This shorten the loop by vectorising the intraday data.
        upbreach_indices, downbreach_indices = self.gen_data()
        print("up", upbreach_indices, len(upbreach_indices),
              "down", downbreach_indices, len(downbreach_indices))
        
        self.plot_check(upbreach_indices, downbreach_indices)

        #direction, cond_info = self.run_cond(upbreach_indices, downbreach_indices)
        signal_df = self.make_signals(upbreach_indices, downbreach_indices)
        
        return signal_df 

    

# Loop daily and find
def loop_signal(df: pd.DataFrame, 
                unique_dates: list, 
                asset_name: str, qty: int,
                open_hr: str, close_hr: str,
                **kwargs)->pd.DataFrame:
    
    master_signal_df = pd.DataFrame()
    for i, date in enumerate(unique_dates):
        # The start and end_datetime for the inner dataframe (For ESS orders)
        start_date = date + datetime.timedelta(hours = int(open_hr[0:2]),
                                               minutes = int(open_hr[2:4]))
        end_date = date + datetime.timedelta(hours = int(close_hr[0:2]),
                                             minutes = int(close_hr[2:4]))
        # The start and end date for outer dataframe (For open/close orders)
        # Buffer zone in case the signal happens at the bound of the origial
        # time window
        delta = datetime.timedelta(minutes=60*3)

        #outer_start_date = date - delta + datetime.timedelta(hours = int(close_hr[0:2]),
        #                                     minutes = int(close_hr[2:4]))

        outer_end_date = date + delta + datetime.timedelta(hours = int(close_hr[0:2]),
                                                           minutes = int(close_hr[2:4]))
        print(f"=========={i}, {start_date} to {end_date}========")

        # Select for a sub-dataframe to calculate the vwap of the day
        # sub_df is for making the EES orders and signal detection, 
        # EES orders must be within the timewindow, and order
        # sub_df is used for signal DETECTION
        sub_df = df[(df['Datetime'] >= start_date) & 
                    (df['Datetime'] <=end_date)]
        # sub_df_out is the outer bound of the dataframe, in case there are 
        # signals near market close, the code can still read the time/price 
        # few ticks away from the closing hours
        # sub_df_out is for getting the right time/price for the detected signals
        sub_df_out = df[(df['Datetime'] >= start_date) & 
                        (df['Datetime'] <=outer_end_date)]
        print(sub_df, sub_df_out)
        print("Sub_df", len(sub_df),
              date, delta,
              open_hr, close_hr,
              sub_df['Datetime'].iloc[0], 
              sub_df['Datetime'].iloc[-1],
              df['Datetime'].iloc[-1])
        print("subsub_df", sub_df_out)
        # Create
        signal_df = VWAPInversionStrategy(asset_name, qty, 
                                          sub_df, sub_df_out,
                                          kwargs['N_sigma'],
                                          TP_multiplier = kwargs['TP_multiplier'],
                                          SL_multiplier = kwargs['SL_multiplier'],
                                          segment_barmulitplier = \
                                          kwargs['segment_barmulitplier']).apply_strategy()

        master_signal_df = pd.concat([master_signal_df, signal_df])
    print("master_signal_df", master_signal_df)
    master_signal_df = master_signal_df.sort_values(by=["signal_datetime"], 
                                                   ascending=True)
    #master_signal_df = 
    return master_signal_df

