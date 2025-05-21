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
import EC_tools.utility.math_func as mfunc
import EC_tools.base.read as read

from crudeoil_future_const import DAILY_MINUTE_DATA_INDI_PKL, DAILY_APC_PKL, \
                                  APC_LENGTH, RESULT_FILEPATH, \
                                  WRONG_OPEN_HR_DICT, CLOSE_HR_DICT

DEFAULT_KWARGS = {'subplot': SubPlot(1, 1, [1], [1], (10,4)),
                  'axis_limit': AxisLimit(),
                  'subcompt': SubComponents(),
                  'add_pdf_panel': False,
                  'add_vol_panel': False}

DEFAULT_KWARGS_main = {'open_hr':'0330', 
                       'close_hr':'1930',
                       'main_panel_xlabel': "Time (minutes)",
                       'main_panel_x_format': '%H:%M',
                       'main_panel_title':""} 

DEFAULT_KWARGS_pdf = {'pdf':[0.0], 
                      'events': [1.0], 
                      'pt_col':'orange',
                      'pdf_panel_title': "",
                      'pdf_panel_xlabel': "Probability"} 

COLOR_DICT_LIGHT_MODE = {'data_col':'k','bg_col':'white', 'col':'g'}
COLOR_DICT_DARK_MODE= {'data_col':'white','bg_col':'k', 'col':'g'}

class PlotIntraDay(object):

    # A class strictly for making intraday plot 
    def __init__(self, 
                 subplot: SubPlot = None, 
                 **kwargs):
        # The class attributes concern with the main plot
                 #intraday_data: pd.DataFrame, **kwargs):
        default_kwargs = DEFAULT_KWARGS
        kwargs = dict(default_kwargs,**kwargs)

        # Settings (For the main Intraday plot): 
        # later change this to autocalculate how many panels are needed        
        self.axis_limit = kwargs['axis_limit'] 
        self.subcompt = kwargs['subcompt']
        # Add other subplot panels
        self.add_pdf_panel = kwargs['add_pdf_panel']
        self.add_vol_panel = kwargs['add_vol_panel']
        
        self.subplot = subplot
        print('subplot', subplot, self.add_pdf_panel, self.add_vol_panel)

        if self.subplot == None:
            if not self.add_pdf_panel and not self.add_vol_panel:
                self.subplot = SubPlot()
            elif self.add_pdf_panel and not self.add_vol_panel:
                self.subplot = SubPlot(nrows=1, ncols=2, 
                                       width_ratios=[4,1],
                                       height_ratios=[1,1], 
                                       figsize = (10,4),
                                       panel_names_list=\
                                           ['main_panel', 'pdf_panel'])
            elif self.add_vol_panel and not self.add_pdf_panel:
                self.subplot = SubPlot(nrows=2, ncols=1, 
                                       width_ratios = [1,1], 
                                       height_ratios=[3,1], 
                                       figsize= (10,4),
                                       panel_names_list=\
                                           ['main_panel', 'vol_panel'])
            elif self.add_pdf_panel and self.add_vol_panel:
                print("add pdf and vol")
                self.subplot = SubPlot(nrows=2, ncols=2, 
                                       width_ratios =[4,1], 
                                       height_ratios=[3,1], 
                                       figsize=(10,4),
                                       panel_names_list=\
                                           ['main_panel', 'pdf_panel',
                                            'vol_panel'])
            
        print(self.subplot)
        # The main instance of matplotlib.axes._base._AxesBase.
        # Define here for sharing attributes
        self.ax_main = None
        
        # Stylistic choice
        self._color_mode = COLOR_DICT_DARK_MODE

        # Subplots: # Volume plot. # PDF
        # Subcompt: #Directions #EES lines, #EES range,#Tradinghours #point highlights
        
    def plot_main(self, 
                  x: list| np.ndarray, 
                  y: list| np.ndarray, 
                  date_interest: str, 
                  **kwargs):
        default_kwargs = DEFAULT_KWARGS_main
        kwargs = dict(default_kwargs,**kwargs)

        x_o = XObject(x,date_interest) #input data
        x_o.x = 'datetime'
        x_datetime = x_o.x
        
        o_hr = XObject(kwargs['open_hr'],date_interest) # open hour
        c_hr = XObject(kwargs['close_hr'],date_interest) # close hour
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
        self.ax_main = self.subplot.fig.add_subplot(self.subplot.panel_dict['main_panel'])
        self.ax_main.plot(x_datetime, y,'o--', ms=2, c=pt_col)

        # set plot limits
        self.ax_main.set_xlim([self.axis_limit.start_line, 
                          self.axis_limit.end_line])
        self.ax_main.set_ylim([self.axis_limit.price_lower_limit, 
                          self.axis_limit.price_upper_limit])
        
        self.ax_main.set_xlabel(kwargs['main_panel_xlabel'])
        self.ax_main.set_ylabel("Price (USD)")
        self.ax_main.set_title(kwargs['main_panel_title'])
        
        fmt = mdates.DateFormatter(kwargs['main_panel_x_format'])
        
        self.ax_main.xaxis.set_major_formatter(fmt)
        self.ax_main.grid()
        
        # define the pixels of shift for the texts in both x and y axis
        txt_shift_x = 0.1/2
        txt_shift_y =  (max(y)-min(y))/20
        #define the shift in dates
        txt_shift_x_date = datetime.timedelta(hours = round(txt_shift_x))

        if self.subcompt._add_trade_region:
            self.subcompt.trade_region(self.ax_main,open_hr, close_hr)
            
        if self.subcompt._add_quant_line:
            self.subcompt.quant_lines(self.ax_main, 
                                      kwargs['quant_list'], 
                                      kwargs['quant_price_list'], 
                                      txt_shift_x_date, txt_shift_y, 
                                      start_x = self.axis_limit.start_line, 
                                      end_x = self.axis_limit.end_line, 
                                      alpha = 0.5)
            
        if self.subcompt._add_EES_region_step:
            self.subcompt.EES_region_step(self.ax_main, 
                                          kwargs['TE_time_list'], 
                                          kwargs['TE_price_list'], 
                                          kwargs['TP_time_list'], 
                                          kwargs['TP_price_list'], 
                                          kwargs['SL_time_list'], 
                                          kwargs['SL_loss_list'], 
                                          txt_shift_x_date, txt_shift_y,
                                          EES_start_x = kwargs['EES_start_x'], 
                                          EES_end_x = kwargs['EES_end_x'], 
                                          direction=kwargs['direction'])
            
        if self.subcompt._add_entryexitpoints:
            self.subcompt.entryexitpoints(self.ax_main,
                                          entry_time = kwargs['entry_time'], 
                                          exit_time = kwargs['exit_time'],
                                          entry_price = kwargs['entry_price'],
                                          exit_price = kwargs['exit_price'])

        self.ax_main.legend(loc="lower right")

    def plot_pdf_panel(self, **kwargs):
        # A Function that plot the pdf panel
        default_kwargs = DEFAULT_KWARGS_pdf
        kwargs = dict(default_kwargs,**kwargs)
        
        # Define subplots
        ax_pdf = self.subplot.fig.add_subplot(self.subplot.panel_dict['pdf_panel'],
                                              sharey=self.ax_main)

        
        ax_pdf.plot(kwargs['pdf'], kwargs['events'], 'o', 
                    c = kwargs['pt_col'], ms =2)
        
        txt_shift_x = np.std(kwargs['pdf'])/2
        txt_shift_y = np.std(kwargs['events'])/20

        SubComponents().quant_lines(ax_pdf, 
                                    kwargs['quant_list'], 
                                    kwargs['quant_price_list'], 
                                    txt_shift_x, txt_shift_y)

    
        ax_pdf.set_xlim([-0.005, max(kwargs['pdf'])+ np.std(kwargs['pdf'])/4])
        ax_pdf.set_title(kwargs['pdf_panel_title'])
        ax_pdf.set_xlabel(kwargs['pdf_panel_xlabel'])
        ax_pdf.invert_xaxis()
        ax_pdf.grid() 
        return 
    
    def plot_vol_panel(self, **kwargs):
        ax_vol = self.subplot.fig.add_subplot(self.subplot.panel_dict['vol_panel'],
                                              sharex=self.ax_main)
#        ax_vol.plot(kwargs['vol_x'],kwargs['vol_y'], ms =2)
        ax_vol.set_xlabel('Time (Minutes)')

        ax_vol.grid() 

        return 

    def plot_all(self, x,y,date_interest_dt, **kwargs):
        self.plot_main(x,y,date_interest_dt, **kwargs)
        
        if self.add_pdf_panel:
            self.plot_pdf_panel(**kwargs)
        if self.add_vol_panel:
            self.plot_vol_panel(**kwargs)
            
        plt.show()

                


def make_plot(symbol, date_interest, direction):
    # Import Historical Data
    filename_minute = DAILY_MINUTE_DATA_INDI_PKL[symbol]
    price_approx = 'Open'
    
    # read the reformatted minute history data
    history_data = util.load_pkl(filename_minute)[symbol]
    
    #temporary solution here because to read the APC file I need to use string
    date_interest_dt = datetime.datetime.strptime(date_interest,'%Y-%m-%d')
    
    # Get the history data on the date of interest
    interest = history_data[history_data['Date']  == date_interest_dt]
    
    # Get the APC data 
    APC_time_str = 'PERIOD'
    curve = util.load_pkl(DAILY_APC_PKL)[symbol]
    curve = curve[curve[APC_time_str] == date_interest]
    # Calculate the pdf from the cdf for plotting
    quant0 = np.arange(0.0025, 0.9975, 0.0025)
    even_spaced_prices, pdf = mfunc.cal_pdf(quant0,
                                            curve.to_numpy()[0][-1-APC_LENGTH:-1])
    curve_spline =  mfunc.generic_spline(quant0,  curve.to_numpy()[0][-1-APC_LENGTH:-1])
    
    # Define the quantile list of interest based on a strategy
    # The lists are for marking the lines only. #live trading range
    #quant_list=['q0.05','q0.35', 'q0.4', 'q0.5', 'q0.6', 'q0.65', 'q0.95']
    #quant_price_list = [curve_spline(0.05), 
    #                    curve_spline(0.35), curve_spline(0.4), 
    #                    curve_spline(0.5),
    #                    curve_spline(0.6), curve_spline(0.65),
    #                    curve_spline(0.95)]
    quant_list=['q0.05','q0.35', 'q0.4', 'q0.5', 'q0.6', 'q0.65', 'q0.95']
    quant_price_list = [curve_spline(0.05), 
                        curve_spline(0.35), curve_spline(0.4), 
                        curve_spline(0.5),
                        curve_spline(0.6), curve_spline(0.65),
                        curve_spline(0.95)]
    
    price_lower_limit = curve_spline(0.03)
    price_upper_limit = curve_spline(0.97)
    
    # Define the Dynamic EES time and prices
    buy_range = ([0.25,0.4],[0.65,0.75],0.05) # (-0.1,0.1,-0.45)
    sell_range = ([0.6,0.75],[0.25,0.35],0.95) # (0.1,-0.1,0.45)

    TE_time = [datetime.time(3,30,0), datetime.time(16,0,0)]
    TP_time = [datetime.time(3,30,0), datetime.time(19,59,0)]
    # A list of pairs of datetime in a tuple #1959
# =============================================================================
#     dSL_time = [datetime.time(3,30,0), datetime.time(8,0,0), #setting 1 and 2
#                 datetime.time(8,0,0), datetime.time(14,0,0),
#                 datetime.time(14,0,0), datetime.time(16,0,0),
#                 datetime.time(16,0,0), datetime.time(19,59,0)] 
# =============================================================================

# =============================================================================
#     dSL_time = [datetime.time(3,30,0), datetime.time(8,0,0), #setting3
#                 datetime.time(8,0,0), datetime.time(14,30,0),
#                 datetime.time(14,30,0), datetime.time(16,0,0),
#                 datetime.time(16,0,0), datetime.time(19,59,0)] 
# =============================================================================
    # A list of pairs of datetime in a tuple #1959
    dSL_time = [datetime.time(3,30,0), datetime.time(8,0,0),
                datetime.time(8,0,0), datetime.time(12,0,0),
                datetime.time(12,0,0), datetime.time(16,0,0),
                datetime.time(16,0,0), datetime.time(19,59,0)] 
    # Dynamic SL quantiles
    #dSL = [0.0,0.1,0.25,0.4] # setting 1
    #dSL = [0.0,0.05,0.1,0.25] # setting 2

    #dSL = [0.0,0.05,0.25,0.25] 
    #dSL = [0.0,0.05,0.25,0.4]# setting 3
    dSL = [0.0,0.0,0.4,0.4]# setting 4


    dSL_p = dSL*2 # a list for plot hence p
    dSL_p.sort()
    
    if direction == "Buy":
        TE_price = curve_spline(buy_range[0][1])
        TP_price = curve_spline(buy_range[1][0])
        SL_price = curve_spline(buy_range[2])
        SL_price_list = [curve_spline(buy_range[2]+ele) for ele in dSL_p]
        
    elif direction == "Sell":
        TE_price = curve_spline(sell_range[0][0])
        TP_price = curve_spline(sell_range[1][1])
        SL_price = curve_spline(sell_range[2])
        SL_price_list = [curve_spline(sell_range[2]-ele) for ele in dSL_p]
    else:
        TE_price = np.nan
        TP_price = np.nan
        SL_price = np.nan
        SL_price_list = [np.nan for ele in dSL_p]

    TE_time_list =[datetime.datetime.combine(date_interest_dt.date(),ele) 
                   for ele in TE_time] 
    TE_price_list = [TE_price for ele in TE_time]  
    TP_time_list = [datetime.datetime.combine(date_interest_dt.date(),ele)
                    for ele in TP_time] 
    TP_price_list = [TP_price for ele in TP_time] 
    SL_time_list = [datetime.datetime.combine(date_interest_dt.date(), ele) 
                    for ele in dSL_time] 
    
    EES_txt_start_time = datetime.time(hour = 20, minute = 50)
    EES_txt_start_time = datetime.datetime.combine(date_interest_dt.date(), 
                                                   EES_txt_start_time)

    # Get the data from Trade files and define Entry and Exit points
    TRADE_FILENAME = RESULT_FILEPATH +'/MR_signal_study/SLD4/test_master_pnl_SLD4_.xlsx'
    XL_df = read.read_xl_file(TRADE_FILENAME, sheet_name = symbol)
    XL_date_interest = XL_df[XL_df['Entry_Date'] == date_interest]
    print('XL_date_interest', XL_date_interest)
    entry_time = datetime.datetime.strptime(\
                                XL_date_interest['Entry_Datetime'].iloc[0],
                                '%Y-%m-%d %H:%M:%S')
    exit_time = datetime.datetime.strptime(\
                                 XL_date_interest['Exit_Datetime'].iloc[0],
                                 '%Y-%m-%d %H:%M:%S')
    entry_price = XL_date_interest['Entry_Price'].iloc[0]
    exit_price = XL_date_interest['Exit_Price'].iloc[0]

    print(entry_time, exit_time, entry_price, exit_price)
    print(type(entry_time), type(exit_time), type(entry_price), type(exit_price))
    
    # Define input time-series
    x, y = interest['Time'], interest[price_approx]
    
    # Set plot upper and lower bound
    up_limit = max(max(y) + (max(y)-min(y))/3, price_upper_limit)
    bottom_limit = min(min(y) - (max(y)-min(y))/3, price_lower_limit)
    
    # Making the plot
    AxL = AxisLimit(bottom_limit, up_limit, date_interest=date_interest_dt)
    
    # Make a subcompt object here so that we can change the setting and feed 
    # it into PID
    subcomp_main = SubComponents(axis_limit=AxL)
    subcomp_main._add_trade_region = True
    subcomp_main._add_quant_line = True
    subcomp_main._add_EES_region_step = True
    subcomp_main._add_entryexitpoints = True
    
    # Make the PlotIntraDay object with all the setting as inputs
    PID = PlotIntraDay(axis_limit = AxL, 
                       subcompt = subcomp_main,
                       add_pdf_panel=True,
                       add_vol_panel=True)
    
    PID.plot_all(x, y, date_interest_dt, # Essential Parameters
                 open_hr = WRONG_OPEN_HR_DICT[symbol],
                 close_hr = CLOSE_HR_DICT[symbol],
                 quant_list=quant_list, # Parameters for quannlines
                 quant_price_list=quant_price_list, # Parameters for quannlines
                 events = even_spaced_prices, # Parameters for PDF panel
                 pdf=pdf, # Parameters for PDF panel
                 direction = direction,
                 TE_time_list = TE_time_list, # Inputs for plotting Dyamic EES regions
                 TE_price_list = TE_price_list, 
                 TP_time_list = TP_time_list, 
                 TP_price_list = TP_price_list,
                 SL_time_list = SL_time_list,
                 SL_loss_list = SL_price_list,
                 EES_start_x = EES_txt_start_time,
                 EES_end_x = AxL.end_line,
                 entry_time = entry_time, entry_price = entry_price,
                 exit_time = exit_time, exit_price = exit_price,
                 main_panel_title = date_interest + "_" + symbol,
                 pdf_panel_title = "APC"
                 ) 


        
if __name__ == "__main__":
    #make_plot('HOc2', '2022-01-31', 'Buy') #'2022-11-18'
    #make_plot('RBc1', '2023-03-16', 'Buy') #"2022-11-30' clearly wrong
    make_plot('RBc1', '2022-11-18', 'Buy')
    

# =============================================================================
# Accidental winning trades gone
# I tried a block-like SL shape where the last SL price is above/below the entry (for buy/sell):
# 
# The backtest for this setup is done in the SL_D fashion.
# The result is that it reduces the total returns the least (See SLD_block).
# =============================================================================
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
