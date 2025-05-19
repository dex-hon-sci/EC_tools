#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 12 10:14:12 2025

@author: dexter
"""
import datetime

import pandas as pd
import numpy as np

import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from EC_tools.plot import XObject, AxisLimit, SubComponents, SubPlot
import EC_tools.utility as util

from crudeoil_future_const import DAILY_MINUTE_DATA_INDI_PKL

DEFAULT_KWARGS= {'subplot': SubPlot(1, 2, [4,1], (10,4)),
                 'axis_limit': AxisLimit(),
                 #'subcomp': SubComponents(),
                 'xlabel': "Time (minutes)",
                 'x_format': '%H:%M',
                 'price_chart_title': ""}

COLOR_DICT_LIGHT_MODE = {'data_col':'k','bg_col':'white', 'col':'g'}
COLOR_DICT_DARK_MODE= {'data_col':'white','bg_col':'k', 'col':'g'}

class PlotIntraDay(object):

    # A class strictly for making intraday plot 
    def __init__(self, 
                 subplot: SubPlot, **kwargs):
                 #intraday_data: pd.DataFrame, **kwargs):
        default_kwargs = DEFAULT_KWARGS
        kwargs = dict(default_kwargs,**kwargs)

        # Settings: 
        self.subplot = subplot
        self.axis_limit = kwargs['axis_limit'] 
        #self.subcomp = kwargs['subcomp']
        
        #self._add_pdf_panel = False
        #self._add_vol_panel = False
        self.add_subcompt = False
        self._color_mode = COLOR_DICT_DARK_MODE

        # Subplots: # Volume plot. # PDF
        # Subcompt: #Directions #EES lines, #EES range,#Tradinghours #point highlights
        
    
    def plot_main(self, 
                  x,y,date_interest, 
                  open_hr = '0330', close_hr='1930', **kwargs):
        default_kwargs = DEFAULT_KWARGS
        kwargs = dict(default_kwargs,**kwargs)

        x_o = XObject(x,date_interest) #input data
        x_o.x = 'datetime'
        x_datetime = x_o.x
        
        o_hr = XObject(open_hr,date_interest) # open hour
        c_hr = XObject(close_hr,date_interest) # close hour
        o_hr.x = 'datetime'
        c_hr.x = 'datetime'
        open_hr = o_hr.x[0] 
        close_hr = c_hr.x[0]
        
        EES_txt_start_time = datetime.time(hour = 20, minute = 50)
        EES_txt_start_time = datetime.datetime.combine(date_interest.date(), 
                                                       EES_txt_start_time)
        
        plt.style.use('dark_background')
        pt_col = 'w'
        
        # Main Panel
        ax_main = self.subplot.fig.add_subplot(self.subplot.panel_dict['main_panel'])
        ax_main.plot(x_datetime, y,'o--', ms=2, c=pt_col)
        
        # set plot limits
        ax_main.set_xlim([self.axis_limit.start_line, self.axis_limit.end_line])
        ax_main.set_ylim([self.axis_limit.price_lower_limit, 
                      self.axis_limit.price_upper_limit])
        
        ax_main.set_xlabel(kwargs['xlabel'])
        ax_main.set_ylabel("Price (USD)")
        ax_main.set_title(kwargs['price_chart_title'])
        
        fmt = mdates.DateFormatter(kwargs['x_format'])
        ax_main.xaxis.set_major_formatter(fmt)
        ax_main.grid()
        
        plt.show()
        
        #return self.fig


# =============================================================================
#         if self.add_subcompt: # If adding subcompt is True
#             # define the pixels of shift for the texts in both x and y axis
#             txt_shift_x, txt_shift_y = np.std(pdf)/2, np.std(events)/20
#             #define the shift in dates
#             txt_shift_x_date = datetime.timedelta(hours = round(np.std(pdf)/2))
#         
#             # Add sub plots
#             self._add_pdf_panel = True
#                 
#             # add other subplots
#             if self._add_pdf_panel == True:
#             # add APC subplot
#                 self.add_pdf_panel(ax_main, pdf, events, 
#                           quant_list, quant_price_list)
#                 
#             # Add subcomponents  
#             subcomp_main = SubComponents(ax_main,axis_limit=self.axis_limit)
#             subcomp_main._quant_lines = True
#             subcomp_main._add_EES_region = False
#             subcomp_main._add_EES_range_region = True
#             subcomp_main._add_crossover_pts = True
#             subcomp_main._add_trade_region = True
# =============================================================================



    

        
if __name__ == "__main__":
    AxL = AxisLimit(60,86)
    SP = SubPlot(1, 2, [4,1], (10,4))
    
    PID = PlotIntraDay(SP)
    sym = 'CLc1'
    date_interest = '2022-11-18'
    filename_minute = DAILY_MINUTE_DATA_INDI_PKL[sym]
    price_approx = 'Open'
    
    # read the reformatted minute history data
    history_data = util.load_pkl(filename_minute)[sym]
    
    
    #print('history_data', history_data)
    #temporary solution here because to read the APC file I need to use string
    date_interest_dt = datetime.datetime.strptime(date_interest,'%Y-%m-%d')
    
    # Get the history data on the date of interest
    interest = history_data[history_data['Date']  == date_interest_dt]
    
    # Change the time format from 0015 to 00:15 in string format
    #interest = util.convert_intmin_to_time(interest)
    
    x, y = interest['Time'], interest[price_approx]
    print(x, y)
    PID.plot_main(x,y,date_interest_dt, axis_limit=AxL)
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
