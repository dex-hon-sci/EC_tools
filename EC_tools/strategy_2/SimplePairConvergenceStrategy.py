#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 19 16:43:26 2025

@author: dexter
"""
import numpy as np
from EC_tools.order.cqg_order import CQGOrder
from EC_tools.order.cqg_enums import OrderSide, OrderType
from EC_tools.strategy_2 import Strategy
from EC_tools.strategy_2.signal import Signal, SignalType, SignalSide, SignalStatus

class SimplePairConvrgStrategy(Strategy):
    # When the residual is beyond a given value range, take MKT order
    # When the residual is within a giveen range, take a closing MKT order
    
    def __init__(self, 
                 data1: np.array, 
                 data2: np.array,
                 cov: float,
                 up_thresholds: tuple[float,float],
                 down_thresholds: tuple[float,float],
                 asset_name_1: str,
                 asset_name_2: str,
                 ):
        
        self.cov = cov # scaling factor
        # Residual 
        self.res = data1 - self.cov*data2
        self.up_array = np.repeat(up_thresholds[1], len(self.res))
        self.down_array = np.repeat(down_thresholds[0], len(self.res))
        self.asset_name_1 = asset_name_1
        self.asset_name_2 = asset_name_2
        
    def gen_data(self):
        # Run the strategy conditions based on the residual
        # Find the Target-Entry and Take-Profit Time accordingly.
        
        # Residual above the up_threshold
        up_bools = np.sign(self.res - self.up_array) > 0
        # Residual below the down_threshold
        down_bools = np.sign(self.down_array - self.res) < 0 
        
        # Get the indices for up and down breach
        upbreach_indices = np.arange(len(self.res))[up_bools]
        downbreach_indices = np.arange(len(self.res))[down_bools]
        
        # Loop through everything after each upbreach, find the earliest exit
        
        # Loop through everything after each downbreach, find the earliest exit

        return 
    
    def make_signals(self):
        
        if self.res >= self.up_threshold:
        # Asset_1 is significantly more expensive than Asset_2
        
            TE_time =  None # Target Entry time
            TE_price_1, TE_price_2 = None, None # Target Entry time
            TP_time =  None # Target Entry time
            TP_price_1, TP_price_2 = None, None # Target Profit time
            # Assume the last 
            CO_time = self.res['Datetime'].iloc[-1] 

            # Target Entry Order (TEO)
            action_TEO_short_1 = CQGOrder(self.asset_name_1,
                                        OrderSide.SIDE_SELL,
                                        OrderType.ORDER_TYPE_MKT,
                                        1, open_=True, close_=False,
                                        kwargs={'MKT_time': TE_time,
                                                'MKT_price':TE_price_1})
            action_TEO_long_2 = CQGOrder(self.asset_name_2,
                                        OrderSide.SIDE_SELL,
                                        OrderType.ORDER_TYPE_MKT,
                                        1, open_=True, close_=False,
                                        kwargs={'MKT_time': TE_time,
                                                'MKT_price':TE_price_2})
            # Take Profit Order (TPO)
            action_TPO_short_1 = CQGOrder(self.asset_name_1,
                                        OrderSide.SIDE_SELL,
                                        OrderType.ORDER_TYPE_MKT,
                                        1, open_=True, close_=False,
                                        kwargs={'MKT_time': TP_time,
                                                'MKT_price':TP_price_1})
            action_TPO_long_2 = CQGOrder(self.asset_name_2,
                                        OrderSide.SIDE_SELL,
                                        OrderType.ORDER_TYPE_MKT,
                                        1, open_=True, close_=False,
                                        kwargs={'MKT_time': TP_time,
                                                'MKT_price':TP_price_2})

            
            # Market-Close Order (MCO)
            action_MCO_1 = CQGOrder(self.asset_name_1,
                                    OrderSide.SIDE_BUY,
                                    OrderType.ORDER_TYPE_MKT,
                                    1,  open_=False, close_=True,
                                    kwargs={'MKT_time': CO_time})
            action_MCO_2 = CQGOrder(self.asset_name_2,
                                    OrderSide.SIDE_SELL,
                                    OrderType.ORDER_TYPE_MKT,
                                    1,  open_=False, close_=True,
                                    kwargs={'MKT_time': CO_time})

            # actions list
            actions_1 = [action_TEO_short_1, 
                         action_TPO_short_1, 
                         action_MCO_1]
            
            actions_1 = [action_TEO_short_1, 
                         action_TPO_short_1, 
                         action_MCO_1]
            
            # build Signals
            S1 = Signal(SignalType.SELL, # Signal type
                       SignalSide.SELL, # Signal Side
                       SignalStatus.INACTIVE, # Signal status
                       TE_time, # start_time
                       CO_time, # end_time
                       actions_1) # Orders
                
        elif self.res <= self.down_threshold:
        # Asset_1 is significantly cheaper than Asset_2

            pass
            
        
        pass
    
    def apply_strategy(self):
        
        signal_df = self.make_signals()
        
        return signal_df 
    
    
def loop_signal():
    pass

        