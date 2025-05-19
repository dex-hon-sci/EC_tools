#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 12 10:14:12 2025

@author: dexter
"""
import pandas as pd
from dataclasses import dataclass

import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt

from EC_tools.plot import XObject, AxisLimit, SubComponents, SubPlot


DEFAULT_KWARGS= {'subplot': SubPlot(),
                 'axis_limit': AxisLimit(),
                 'subcomp': SubComponents()}

class PlotIntraDay(object):

    # A class strictly for making intraday plot 
    def __init__(self, 
                 subplot: SubPlot, 
                 intraday_data: pd.DataFrame, **kwargs):
        default_kwargs = DEFAULT_KWARGS
        kwargs = dict(default_kwargs,**kwargs)

            # Settings: 
        self.subplot = subplot
        self.axis_limit = kwargs['axis_limit'] 
        self.subcomp = kwargs['subcomp']
        
        #self._add_pdf_panel = False
        #self._add_vol_panel = False
        #self.add_subpot = False
       
        # self._color_mode = color_dict_dark_mode
        # Subplots: # Volume plot. # PDF
        # Subcompt: #Directions #EES lines, #EES range,#Tradinghours #point highlights
        
        return
    
    def plot(self, x,y,):
        plt.style.use('dark_background')
        pt_col = 'w'
        
        SubCompt1 = SubComponents()


        return 
    

        
if __name__ == "__main__":
    AxL = AxisLimit()
    SP = SubPlot(1, 2, [4,1], (10,4))
    
    
# =============================================================================
#     plot_minute(DAILY_MINUTE_DATA_INDI_PKL[symbol], # Historical Data Source
#                 date_interest = date_interest, #str, the relevant date
#                 DAILY_APC_PKL, # CDF or PDF
#                 title=symbol, 
#                 direction="Buy", 
#                 sym=symbol,
#                 price_approx='Open', #Price approximator 
#                 open_hr= WRONG_OPEN_HR_DICT[symbol], # Set the opening time
#                 close_hr = CLOSE_HR_DICT[symbol], # Set the closing time
#                 bppt_x1 =entry_time, bppt_y1 = entry_price,
#                 bppt_x2 =exit_time, bppt_y2 = exit_price,
#                 bppt_x3 =stop_time, bppt_y3 = stop_price)
# =============================================================================
