#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 10 18:33:06 2024

@author: dexter
"""
import numpy as np
from dataclasses import dataclass

from plotly.offline import iplot
from plotly.offline import plot, init_notebook_mode
import datetime as datetime

import matplotlib.dates as mdates
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt

import plotly.graph_objects as go

# import EC_tools
import EC_read as EC_read
import read as read
import math_func as mfunc
import utility as util

color_dict_light_mode = {'data_col':'k','bg_col':'white', 'col':'g'}
color_dict_dark_mode = {'data_col':'white','bg_col':'k', 'col':'g'}

pt_col='w'


class XObject(object):
    def __init__(self, x):
        self._x = x
        
    @property
    def x(self):
        return self._x
    
    @x.setter
    def x(self, value:str): # set the array of x axis to datetime format
    # This function convert all x-axis objects to the format of datetime
    
        # Trigger keyword to perform setter action
        if value == 'datetime': 
            pass
        else: return self._x
        
        # If the input is interable
        if type(self._x) == list or type(self._x)== np.ndarray: #tested
            pass
        
        elif type(self._x) in [int, float, str, complex]: # tested
            # put the element in list so that it is iterable
            self._x = [self._x] 
            
        #Find out what format is the input
        fmt = util.get_list_element_format(self._x)[0]
        
        # If the datetime is already in datetime.datetime format, pass
        if fmt == datetime.datetime: # tested
            return self._x
        
        if fmt == str: # tested
            # make sure the string is in the military format
            if list(set(util.get_list_element_str_len(self._x)))[0]==4: 
                
                self._x = [datetime.time(hour = int(t[-4:-2]), 
                                        minute = int(t[-2:])) 
                           for t in self._x] 

        if fmt == int: #tested
            self._x = util.convert_intmin_to_time(self._x)
            
            # If the format is datetime.time
        if fmt == datetime.time:  #tested
            pass

        self._x = [datetime.datetime.combine(datetime.date.today(), t) 
                   for t in self._x]
        return self._x
    
class AxisLimit(object):
    # make functions that check what datetime format we are operating in
    def __init__(self):
        # These attributes define the frame of the plot
        self.price_lower_limit = 70.0 
        self.price_upper_limit = 78.0
        self.start_line = datetime.datetime.combine(datetime.date.today(), 
                                                     datetime.time(hour=0,
                                                                   minute=0))
        self.end_line = datetime.datetime.combine(datetime.date.today(),
                                                   datetime.time(hour=23, 
                                                                 minute=59))

    
class ExtSubplot(object):
    # A class that control added external subplots
    def __inti__(self):
        self._add_pdf_panel = False

    @property
    def add_pdf_panel(self):
        return self._add_pdf_panel
    
    @add_pdf_panel.setter
    def add_pdf_panel(self, value):
        self._add_pdf_panel = value

    def add_pdf_panel(self, sharey, pdf, events, quant_list, 
                      quant_price_list,
                      title='APC', pt_col='orange'):
        
        
        # define the pixels of shift for the texts in both x and y axis
        txt_shift_x, txt_shift_y = np.std(pdf)/2, np.std(events)/20
        #define the shift in dates
        txt_shift_x_date = datetime.timedelta(hours = round(np.std(pdf)/2))
    
        ax_apc = self.fig.add_subplot(self.gs[1], sharey=sharey)
        ax_apc.plot(pdf, events, 'o', c = pt_col, ms =2)
        
        SubComponents(ax_apc).quant_lines(quant_list, quant_price_list, 
                                          txt_shift_x, txt_shift_y)

    
        ax_apc.set_xlim([-0.005, max(pdf)+ np.std(pdf)/4])
        ax_apc.set_title(title)
        ax_apc.set_xlabel("Probability")
        ax_apc.invert_xaxis()
        ax_apc.grid()  

class PlotPricing(object):
    # A clss that control the state of the pricing plots.
    # It can also create more subplot derived from the Pricing data
    
    def __init__(self, axis_limit = AxisLimit(), subcomp = None,
                 nrows=1, ncols = 2):
        
        self.fig = plt.figure(figsize=(10,4))
        
        # make a way to change the number of subplot based on nrows and ncols
        self.gs = self.fig.add_gridspec(nrows=1, ncols = 2, width_ratios = [4,1])

        self.axis_limit = axis_limit 
        self.subcomp = subcomp
        
        self._add_pdf_panel = False
        self._add_vol_panel = False
        self.add_subpot = False
        self._color_mode = color_dict_dark_mode
        #super().__init__()
        

        
    def controller(self, ax, *args, **kwargs):
        # A function that control which subcomponents and subplots are turned on      
        # Add subcomponents  
        return None


    def plot_price(self, x,y, events, pdf, 
                       quant_list, quant_price_list, direction="Neutral",
                       price_chart_title = "Date", 
                       events_lower_limit=70, events_upper_limit =78,

                       open_hr = '0330', close_hr='1930',
                       xlabel = "Time (minutes)",
                       x_format = '%H:%M',
                       bppt_x1 = [], bppt_y1 = [], 
                       bppt_x2 = [], bppt_y2 = [], 
                       bppt_x3 =[], bppt_y3 = []):
        """
        A function that plot the intraday minute pricing chart alongside the APC.
    
        Parameters
        ----------
        x : list
            The intraday minutes.
        y : list
            The price of intraday data.
        events : list
            The price of the APC.
        pdf : list
            The probability of the APC's pdf.
        quant_list : list
            A list of quantile name for text marking on the plot.
        quant_price_list : list
            The price of the horizontal lines corresponding to quant_list.
        direction : str
            Buy", "Sell", or "Neutral" signal.
        price_chart_title : str, optional
            The title of the plot. The default is "Date".
        open_hr : str, optional
            The opening hour of a trade day. The default is 0330 (03:30 at UK time).
        close_hr : str, optional
            The closing hour of a trade day. The default is 1900 (07:00 pm).
        events_lower_limit : TYPE, optional
            The lower bound in y-axis of the plot. The default is 70.
        events_upper_limit : TYPE, optional
            The upper bound in y-axis of the plot. The default is 78.
    
        Returns
        -------
        fig : <class 'matplotlib.figure.Figure'>
            The figure.
    
        """
        x_o = XObject(x)
        x_o.x = 'datetime'
        x_datetime = x_o.x
        
        o_hr = XObject(open_hr)
        c_hr = XObject(close_hr)
        o_hr.x = 'datetime'
        c_hr.x = 'datetime'
        open_hr = o_hr.x[0] 
        close_hr = c_hr.x[0]
                
        #buy_time = datetime.time(hour = int(buy_time[-4:-2]), minute = int(buy_time[-2:]))    
        #sell_time = datetime.time(hour = int(sell_time[-4:-2]), minute = int(sell_time[-2:]))
        EES_txt_start_time = datetime.time(hour = 20, minute = 50)
        
        #buy_time = datetime.datetime.combine(datetime.date.today(), buy_time)  
        #sell_time = datetime.datetime.combine(datetime.date.today(), sell_time)
        EES_txt_start_time = datetime.datetime.combine(datetime.date.today(), 
                                                       EES_txt_start_time)

        # choose the color mode
        plt.style.use('dark_background')
        pt_col = self._color_mode['data_col']

        # plotting area
        #fig = plt.figure(figsize=(10,4))
        #gs = fig.add_gridspec(nrows=1, ncols = 2, width_ratios = [4,1])
    
        ax1 = self.fig.add_subplot(self.gs[0])
        ax1.plot(x_datetime, y,'o--', ms=2, c=pt_col)
        
        # set plot limits
        ax1.set_xlim([self.axis_limit.start_line, self.axis_limit.end_line])
        ax1.set_ylim([self.axis_limit.price_lower_limit, 
                      self.axis_limit.price_upper_limit])
        
        ax1.set_xlabel(xlabel)
        ax1.set_ylabel("Price (USD)")
        ax1.set_title(price_chart_title)
        
        fmt = mdates.DateFormatter(x_format)
        ax1.xaxis.set_major_formatter(fmt)
        ax1.grid()
        
        # define the pixels of shift for the texts in both x and y axis
        txt_shift_x, txt_shift_y = np.std(pdf)/2, np.std(events)/20
        #define the shift in dates
        txt_shift_x_date = datetime.timedelta(hours = round(np.std(pdf)/2))
    
        # Add sub plots
        self._add_pdf_panel = True
            
        # add other subplots
        if self._add_pdf_panel == True:
        # add APC subplot
            self.add_pdf_panel(ax1, pdf, events, 
                      quant_list, quant_price_list)
            
        # Add subcomponents  
        subcomp = SubComponents(ax1)
        subcomp._quant_lines = True
        subcomp._add_EES_region = True
        subcomp._add_crossover_pts = True
        subcomp._add_trade_region = True

        # add the EES regions
        if subcomp._add_EES_region == True:
                
            if direction == "Buy":
                entry_price = quant_price_list[1]
                exit_price = quant_price_list[3]
                stop_loss = quant_price_list[0]
            elif direction == "Sell":
                entry_price = quant_price_list[3]
                exit_price = quant_price_list[1]
                stop_loss = quant_price_list[4]
            elif direction == "Neutral":
                entry_price = np.nan
                exit_price = np.nan
                stop_loss = np.nan
                
            subcomp.EES_region(entry_price, exit_price ,stop_loss, 
                                txt_shift_x_date, txt_shift_y, 
                                start_x = EES_txt_start_time,
                                end_x = self.axis_limit.end_line, 
                                direction = direction)
            
        # add quantile lines to the plot
        if subcomp._quant_lines == True:
            subcomp.quant_lines(quant_list, quant_price_list, 
                                        txt_shift_x_date, txt_shift_y, 
                            start_x = self.axis_limit.start_line, 
                            end_x = self.axis_limit.end_line, 
                            alpha = 0.5)
            
        # add cross over points
        if subcomp._add_crossover_pts == True:
            bppt_x1 = [datetime.datetime.combine(datetime.date.today(), t) 
                       for t in bppt_x1]
            bppt_x2 = [datetime.datetime.combine(datetime.date.today(), t) 
                       for t in bppt_x2]
            bppt_x3 = [datetime.datetime.combine(datetime.date.today(), t) 
                       for t in bppt_x3]
            
            subcomp.crossover_pts(bppt_x1, bppt_y1, bppt_x2, bppt_y2, 
                                  bppt_x3, bppt_y3)
            
        if subcomp._add_trade_region == True:
            subcomp.trade_region(open_hr, close_hr)
            
        # add the buying and selling points
        #add_buysell_points(ax1, buy_time, buy_price, sell_time, sell_price)
        
        plt.show()
        
        return self.fig
    
    def add_pdf_panel(self, sharey, pdf, events, quant_list, 
                      quant_price_list,
                      title='APC', pt_col='orange'):
        
        
        # define the pixels of shift for the texts in both x and y axis
        txt_shift_x, txt_shift_y = np.std(pdf)/2, np.std(events)/20
        #define the shift in dates
        txt_shift_x_date = datetime.timedelta(hours = round(np.std(pdf)/2))
    
        ax_apc = self.fig.add_subplot(self.gs[1], sharey=sharey)
        ax_apc.plot(pdf, events, 'o', c = pt_col, ms =2)
        
        SubComponents(ax_apc).quant_lines(quant_list, quant_price_list, 
                                          txt_shift_x, txt_shift_y)

    
        ax_apc.set_xlim([-0.005, max(pdf)+ np.std(pdf)/4])
        ax_apc.set_title(title)
        ax_apc.set_xlabel("Probability")
        ax_apc.invert_xaxis()
        ax_apc.grid()  
        
    @property
    def add_volume_panel(self):
        return None
    
class SubComponents(object):

    # All subcomponents for Price plotting. This can be inheretance class
    def __init__(self, ax, axis_limit = AxisLimit()):
        self.ax = ax # the location that these things should be added
        self._quant_lines = False
        self._add_EES_region = False
        self._add_trade_region = False
        self._add_crossover_pts = False
        
        self._add_entry_exit_points = False
        self._add_bol_band = False
        self._add_fibo_retract_lines = False

        self.txt_shift_x = None
        self.txt_shift_y = None
        self.axis_limit = axis_limit # WIP

       # super().__init__()
       
    def quant_lines(self, quant_list, quant_price_list, txt_shift_x, 
                    txt_shift_y, start_x = 0.0, end_x= 100, alpha = 0.5):
        """
        A function that add the quantile lines to a plot.
    
        Parameters
        ----------
        ax : <class 'matplotlib.axes._axes.Axes'>
            The figure.
        quant_list : list
            A list of quantile name for text marking on the plot.
        quant_price_list : list
            The price of the horizontal lines corresponding to quant_list.
        txt_shift_x : float
            The shift in x-axis for the text.
        txt_shift_y : float
            The shift in y-axis for the text.
        start_x: float, or datetime.time
            The starting position for the text in x-axis
        end_x: float, or datetime.time
            The ending position for the text in x-axis
        alpha : float, optional
            The transparency of the quantile line. The default is 0.5.
    
        """

        for quant, price in zip(quant_list, quant_price_list):
            self.ax.hlines(price, start_x, end_x, color='#C26F05', 
                           alpha = alpha)
            self.ax.text(start_x + txt_shift_x, price + txt_shift_y, quant, 
                     color=pt_col, bbox=dict(boxstyle="round",
                     ec= pt_col, fc='#C26F05'))        
    
    def EES_region(self, entry_price, exit_price, stop_loss, txt_shift_x, 
                   txt_shift_y, start_x = 0.0, end_x = 2150, 
                   direction="Neutral"):
        """
        A function that add the Entry, Exit, and Stop Loss regions to a plot.
        It plot only in horizontal line. I will change this to np.arrage later.
    
        Parameters
        ----------
        ax : <class 'matplotlib.axes._axes.Axes'>
            The figure.
        entry_price : float
            entry_price.
        exit_price : float
            exit_price.
        stop_loss : float
            stop_loss.
        txt_shift_x : float
            The shift in x-axis for the text.
        txt_shift_y : float
            The shift in y-axis for the text.
        direction : str, optional
            "Buy", "Sell", or "Neutral" signal. The default is "Neutral".
    
        """
        # dashed line is the entry line, solid line is the exit line
        # dashed red line is the stop loss
        
        if direction == "Buy":
            limit = -10000
        elif direction == "Sell":
            limit = 10000
        elif direction == "Neutral":
            limit = np.nan
        
        # The EES lines
        self.ax.hlines(entry_price, self.axis_limit.start_line, 
                       self.axis_limit.end_line, color='#18833D', 
                       ls="dashed", lw = 2)
        self.ax.hlines(exit_price, self.axis_limit.start_line, 
                       self.axis_limit.end_line, color='#18833D', 
                       ls="solid", lw = 2 )
        self.ax.hlines(stop_loss, self.axis_limit.start_line, 
                       self.axis_limit.end_line, color='#E5543D', 
                       ls = "dashed", lw = 2)
        
        # Green shade is the target region.
        self.ax.fill_between([self.axis_limit.start_line, 
                              self.axis_limit.end_line], 
                             entry_price, exit_price, 
                             color='green', alpha=0.3)
        # Red shade is the stop loss region. 
        self.ax.fill_between([self.axis_limit.start_line, 
                              self.axis_limit.end_line], 
                             stop_loss, limit, 
                             color='red', alpha=0.3)
        
        # The texts that indicate the regions
        self.ax.text(start_x + txt_shift_x, entry_price + txt_shift_y, 
                     "Entry Price", 
                      fontsize=8, color = pt_col, bbox=dict(boxstyle="round",
                       ec= pt_col,fc='#206829'))
                      
                     # facecolor='#206829')
        self.ax.text(start_x + txt_shift_x, exit_price + txt_shift_y, 
                     "Exit Price", 
                      fontsize=8, color= pt_col, bbox=dict(boxstyle="round",
                       ec= pt_col,fc='#206829'))
                      
        self.ax.text(start_x + txt_shift_x, stop_loss + txt_shift_y, 
                     "Stop Loss", 
                      fontsize=8, color=pt_col, bbox=dict(boxstyle="round",
                       ec= pt_col,fc='#80271B'))
        
    def trade_region(self, open_hr, close_hr):
        # fill the closed trading hours with shade
        # the vertical lines that
        self.ax.vlines(open_hr, 0, 2000, 'w')
        self.ax.vlines(close_hr, 0, 2000, 'w')
        
        self.ax.fill_between([self.axis_limit.start_line, open_hr], 0, 2000, 
                             color='grey', alpha=0.3)
        self.ax.fill_between([close_hr, self.axis_limit.end_line], 0, 2000, 
                             color='grey', alpha=0.3)
        
        # the vertical lines that
        self.ax.vlines(open_hr, 0, 2000, 'k')
        self.ax.vlines(close_hr, 0, 2000, 'k')
    
    def crossover_pts(self, bppt_x1, bppt_y1, bppt_x2, bppt_y2, 
                          bppt_x3, bppt_y3):
        # crossover points set 1 
        self.ax.plot(bppt_x1, bppt_y1,'o', ms=10, c='blue')
        self.ax.plot(bppt_x2, bppt_y2,'o', ms=10, c='green')
        self.ax.plot(bppt_x3, bppt_y3,'o', ms=10, c='red')
        
    def buysellpoints(self, buy_time = "1201", buy_price =  86.05,
                           sell_time = "1900", sell_price = 85.70):
        
        return None
        
        
def plot_minute(filename_minute, signal_filename, price_approx = 'Open',
                date_interest = "2022-05-19", direction = "Buy",
                bppt_x1 =[], bppt_y1 = [], 
                bppt_x2 =[], bppt_y2 = [], 
                bppt_x3 =[], bppt_y3 = []):
    
    # read the reformatted minute history data
    history_data = read.read_reformat_Portara_minute_data(filename_minute)
    
    #reformat the date of interest
    date_interest_year = int(date_interest[:4])
    date_interest_month = int(date_interest[5:7])
    date_interest_day = int(date_interest[-2:])
    
    #temporary solution here because to read the APC file I need to use string
    date_interest_dt = datetime.datetime(year = date_interest_year, 
                                      month = date_interest_month , 
                                      day = date_interest_day)
    
    # Get the history data on the date of interest
    interest = history_data[history_data['Date']  == date_interest_dt]
    
    # Change the time format from 0015 to 00:15 in string format
    #interest = util.convert_intmin_to_time(interest)
    
    x, y = interest['Time'], interest[price_approx]

    #read the APC file on the relevant date
    curve = read.read_apc_data(signal_filename)
    curve = curve[curve['Forecast Period'] == date_interest]
    
    # Calculate the pdf from the cdf for plotting
    quant0 = np.arange(0.0025, 0.9975, 0.0025)
    even_spaced_prices, pdf = mfunc.cal_pdf(quant0, curve.to_numpy()[0][1:-1])
    
    #print("find_quant", mfunc.find_quant(curve.to_numpy()[0][1:-1], quant0, 97.9366))
    
    # Define the quantile list of interest based on a strategy
    # The lists are for marking the lines only. 
    quant_list=['q0.1','q0.4','q0.5','q0.6','q0.9']
    quant_price_list = [curve['0.1'], curve['0.4'], curve['0.5'], 
                        curve['0.6'], curve['0.9']]

    # Define the upper and lower bound of the pricing plot in the y-axis
    price_lower_limit = curve['0.05'].to_numpy()
    price_upper_limit = curve['0.95'].to_numpy()
    
    # First set up the axes limit class to define the plot limit
    new_axis_limit = AxisLimit()
    new_axis_limit.price_lower_limit = price_lower_limit
    new_axis_limit.price_upper_limit = price_upper_limit
    
    
    # Then choose the subcomponents to be added
    subcomp = SubComponents(new_axis_limit)

    # Then plot
    # Plot the pricing chart.

    PP = PlotPricing(axis_limit = new_axis_limit)
    
    PP.plot_price(x,y, even_spaced_prices, pdf, 
                       quant_list, quant_price_list, 
                       direction="Buy",
                       price_chart_title = "Date", 
                       bppt_x1 = [], bppt_y1 = [], 
                       bppt_x2 = [], bppt_y2 = [], 
                       bppt_x3 =[], bppt_y3 = [])
    
    
if __name__ == "__main__":
    
    filename_daily = "../test_MS/data_zeroadjust_intradayportara_attempt1/Daily/CL.day"
    #################
    
    filename_minute = "../test_MS/data_zeroadjust_intradayportara_attempt1/intraday/1 Minute/CL.001"
    signal_filename = "APC_latest_CL.csv"
    #date_interest = "2022-05-19"
    #date_interest = "2024-04-03"
    date_interest = "2024-01-18"
    
    plot_minute(filename_minute, signal_filename, 
                date_interest = date_interest, direction="Sell")
