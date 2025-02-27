#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 24 14:37:07 2024

@author: dexter
"""
# Ptyhon import
import datetime as datetime
from pathlib import Path
import logging

# Common packages mport
import pandas as pd
import numpy as np
import matplotlib.dates as mdates
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import cmasher as cmr

#EC_tools import
import EC_tools.utility as util
from crudeoil_future_const import APC_FILE_LOC, DATA_FILEPATH, RESULT_FILEPATH, make_path_list

# application imports
from app.run_PNL_plot import extract_PNLplot_input


#gain_quantile = [5,10,15,20,25,30,35,40,45,50,55,60]
#stoploss_quantile = [5,10,15,20,25,30,35,40]
gain_quantile = [5,10,15,20,25,30,35,40,45,50]
stoploss_quantile = [5,10,15,20,25,30,35,40,45,50]


gain_quantile_str = ['P'+str(num) for num in gain_quantile]
stoploss_quantile_str = ['S'+str(num) for num in stoploss_quantile]



def build_filename_matrix(x_axis_list: list[str], 
                          y_axis_list: list[str],
                          folder_name: str = 'heatmap', 
                          file_prefix: str = 'PNL_argusexact_',
                          file_suffix: str = '_.xlsx',
                          path: dict = RESULT_FILEPATH):
    """
    A function that build a heatmap matrix with each element the name of the 
    source data file 

    Parameters
    ----------
    x_axis_list : list
        A list of str containing the name of the x-axis quantity.
    y_axis_list : list
        A list of str containing the name of the y-axis quantity.
    folder_name : str, optional
        The parent folder name. The default is 'heatmap'.
    file_prefix : str, optional
        The file prefix. The default is 'PNL_argusexact_'.
    file_suffix : str, optional
        The file suffix. The default is '_.xlsx'.

    Returns
    -------
    filename_matrix : 2D nd.array
        A 2D matrix that has the full filename and address for the source data.

    """
    master_list = []
    # read a list of 
    for i in range(len(y_axis_list)):
        temp = [ele + y_axis_list[i] for ele in x_axis_list]
        #print(temp)
        Q = make_path_list(folder_name = folder_name, 
                           file_prefix= file_prefix,
                           file_suffix= file_suffix,
                           path= path,
                           syms=temp)
        master_list.append(Q)
    
    
    filename_matrix = np.array(master_list)
    return filename_matrix

def extract_info_from_filename_matrix(filename_matrix: np.ndarray,
                                      sheetname: str = 'Total',
                                      date_col: str = "Entry_Date",
                                      val_col: str = "cumulative P&L from trades for contracts (x 50)",
                                      #index: int = -1,
                                      func = lambda X: X[-1]):
    """
    A function that extra the parrticular information from the source files in 
    filename matrix.

    Parameters
    ----------
    filename_matrix : 2D np.ndarray
        A 2D matrix that contains source filename str as its element.
    sheetname : str, optional
        The excel sheet names. The default is 'CLc1'.

    Returns
    -------
    matrix : 2D np.ndarray
        A 2D matrix that contains the extracted value as its element..

    """
    master_list = []
    for i in range(len(filename_matrix)):
        temp = [func(extract_PNLplot_input(ele, 
                                      sheet_name=sheetname,
                                      date_col = date_col, 
                                      val_col = val_col,
                                      fill_or_not=False)[1])
                for ele in filename_matrix[i]]
        
        
        print(i)
        master_list.append(temp)
        
    matrix = np.array(master_list)

    return matrix


def plot_heatmap(heatmap_data, **kwargs):
    default_kwargs = {'xticks': gain_quantile, 'yticks': stoploss_quantile,
                      'norm':1e6}
    kwargs = dict(default_kwargs, **kwargs)
    plt.style.use('dark_background')

    # Start the plot
    fig, ax = plt.subplots()
    im = ax.imshow(heatmap_data, cmap=cmr.ember)
    
    cbar = ax.figure.colorbar(im, ax=ax)
    cbar.ax.set_ylabel(kwargs['cbarlabel'], rotation=-90, va="bottom")
    
    ax.set_xticks(np.arange(len(heatmap_data[0])), labels=kwargs['xticks'])
    ax.set_yticks(np.arange(len(heatmap_data)), labels=kwargs['yticks'])
    
    for i in range(len(heatmap_data)):
        for j in range(len(heatmap_data[0])):
            ax.text(j, i, round(heatmap_data[i, j]/kwargs['norm'],2),
                           ha="center", va="center", color="w")
    
    ax.set_title(kwargs['plot_title'])
    ax.set_xlabel(kwargs['xlabel'])
    ax.set_ylabel(kwargs['ylabel'])
    fig.tight_layout()
    plt.show()
    
def run_main(x_axis_str_list, y_axis_str_list, **kwargs):
    default_kwargs = {'path': RESULT_FILEPATH,
                      'folder_name': 'heatmap',
                      'file_prefix': '',
                      'file_suffix': '_.xlsx',
                      'sheetname':'Total',
                      'date_col': 'Entry_Date',
                      'val_col': 'cumulative P&L from trades for contracts (x 50)',
                      'cbarlabel':'', 
                      'plot_title': '', 
                      'xlabel':'','ylabel':'',
                      'xticks':[],'yticks':[],
                      'index':-1,
                      'func':lambda X: X[-1],
                      'norm':1e6}
    kwargs = dict(default_kwargs, **kwargs)

    # make a matrix containing the name of the source file in the respective 
    # postions
    filename_matrix = build_filename_matrix(x_axis_str_list, y_axis_str_list,
                                            folder_name = kwargs['folder_name'], 
                                            file_prefix = kwargs['file_prefix'],
                                            file_suffix = kwargs['file_suffix'],
                                            path = kwargs['path'])
        
    # Extract the particular columns and information to be plotted.
    heatmap_data = extract_info_from_filename_matrix(filename_matrix, 
                                                     sheetname = kwargs['sheetname'],
                                                     date_col = kwargs['date_col'],
                                                     val_col = kwargs['val_col'],
                                                     func=kwargs['func'])
                                                     #index= kwargs['index'])

    # Plot heatmap    
    plot_heatmap(heatmap_data,
                 cbarlabel = kwargs['cbarlabel'],
                 plot_title = kwargs['plot_title'],
                 xlabel = kwargs['xlabel'],
                 ylabel = kwargs['ylabel'],
                 xticks = kwargs['xticks'],
                 yticks = kwargs['yticks'],
                 norm = kwargs['norm'])
    
if __name__ == "__main__":
    
    def custom_median(X: list):
        positive = [ele for ele in X if ele>0]
        negative = [ele for ele in X if ele<0]
        
        #result = (np.median(positive)*len(positive))/sum(positive)
        result = abs((np.median(positive)*len(positive))/(np.median(negative)*len(negative)))
        return result
    
    def sharpe_ratio(X):
        return np.average(X)/np.std(X)
    
    def profit_factor(X):
        win_trades_val = sum(i for i in X
                             if i >= 0)
        lose_trades_val = sum(i for i in X
                              if i < 0)
        print(win_trades_val, lose_trades_val)
        return abs(win_trades_val)/abs(lose_trades_val)#, '', 'Profit Factor'

    
    if False:
    # plot total median scaled returns (1 contract)
        run_main(gain_quantile_str,
                 stoploss_quantile_str,
                 folder_name = 'heatmap2',
                 file_prefix ='20240813_argusexact_cross_',
                 file_suffix = '_PNL_.xlsx',
                 sheetname = 'Total',
                 date_col = 'Entry_Date',
                 val_col = 'scaled returns from trades',#'cumulative P&L from trades for contracts (x 50)',
                 cbarlabel='USD', 
                 plot_title='Standard Deviation for \nArgus Exact strategy with fixed\nEntry quantile at Q0.4 for Buy\nand Q0.6 for Sell for Total (1 contracts)',
                 xlabel = "Quantile (in %) Range for Take Profit",
                 ylabel = "Quantile (in %) Range for Stop Loss",
                 xticks = gain_quantile, 
                 yticks = stoploss_quantile,
                 func=np.median,
                 norm = 1)
    
    
    if True:
    # plot total cumulative returns (50 contract)
        run_main(gain_quantile_str,
                 stoploss_quantile_str,
                 folder_name = 'heatmap3_buyQ50sellQ50',
                 file_prefix ='20240813_argusexact_cross_',
                 file_suffix = '_PNL_.xlsx',
                 sheetname = 'Total',
                 date_col = 'Entry_Date',
                 val_col = 'cumulative P&L from trades for contracts (x 50)',#'cumulative P&L from trades for contracts (x 50)',
                 cbarlabel='USD (mil)', 
                 plot_title='Cumulative Return for \nArgus Exact strategy with fixed\nEntry quantile at Q0.4 for Buy\nand Q0.6 for Sell for Total (50 contracts)',
                 xlabel = "Quantile (in %) Range for Take Profit",
                 ylabel = "Quantile (in %) Range for Stop Loss",
                 xticks = gain_quantile, 
                 yticks = stoploss_quantile,
                 norm = 1e6)
    
    if False:
        syms = list(APC_FILE_LOC.keys())

        for sym in syms:
            print(sym)
            run_main(gain_quantile_str,
                     stoploss_quantile_str,
                     folder_name = 'heatmap3_buyQ50sellQ50',
                     file_prefix ='20240813_argusexact_cross_',
                     file_suffix = '_PNL_.xlsx',
                     sheetname = sym,
                     date_col = 'Entry_Date',
                     val_col = 'scaled returns from trades',
                     cbarlabel='USD', 
                     plot_title='Standard Deviation for \nArgus Exact strategy with fixed\nEntry quantile at Q0.4 for Buy\nand Q0.6 for Sell for {} (1 contracts)'.format(sym),
                     xlabel = "Quantile (in %) Range for Take Profit",
                     ylabel = "Quantile (in %) Range for Stop Loss",
                     xticks = gain_quantile, 
                     yticks = stoploss_quantile,
                     func=custom_median,
                     norm = 1)        
        
    if False:
    # plot total cumulative returns for each asset (50 contracts)

        syms = list(APC_FILE_LOC.keys())

        for sym in syms:
            print(sym)
            run_main(gain_quantile_str,
                     stoploss_quantile_str,
                     folder_name = 'heatmap3_buyQ50sellQ50',
                     file_prefix ='20240813_argusexact_cross_',
                     file_suffix = '_PNL_.xlsx',
                     sheetname = sym,
                     date_col = 'Entry_Date',
                     val_col = 'cumulative P&L from trades for contracts (x 50)',
                     cbarlabel='USD (in mil)', 
                     plot_title='Median Return for \nArgus Exact strategy with fixed\nEntry quantile at Q0.4 for Buy\nand Q0.6 for Sell for {} (50 contracts)'.format(sym),
                     xlabel = "Quantile (in %) Range for Take Profit",
                     ylabel = "Quantile (in %) Range for Stop Loss",
                     xticks = gain_quantile, 
                     yticks = stoploss_quantile,
                     func=np.median,
                     norm = 1e6)
            
        if False:
            openhr_str = ['Open0h0m','Open0h30m',
                          'Open1h0m','Open1h30m',
                          'Open2h0m']
            
            closehr_str = ['Close0h0m','Close0h30m',
                           'Close1h0m','Close1h30m',
                           'Close2h0m']
            openhr_str_ticks = dict()
            closehr_str_ticks = dict()
            openhr_str_ticks['CLc1'] = ['3:30','3:00', '2:30','2:00','1:00']
            openhr_str_ticks['CLc2'] = ['3:30','3:00', '2:30','2:00','1:00']
            openhr_str_ticks['HOc1'] = ['5:30','5:00', '4:30','4:00','3:30']
            openhr_str_ticks['HOc2'] = ['5:30','5:00', '4:30','4:00','3:30']
            openhr_str_ticks['RBc1'] = ['5:30','5:00', '4:30','4:00','3:30']
            openhr_str_ticks['RBc2'] = ['5:30','5:00', '4:30','4:00','3:30']
            openhr_str_ticks['QOc1'] = ['3:30','3:00', '2:30','2:00','1:00']
            openhr_str_ticks['QOc2'] = ['3:30','3:00', '2:30','2:00','1:00']
            openhr_str_ticks['QPc1'] = ['5:30','5:00', '4:30','4:00','3:30']
            openhr_str_ticks['QPc2'] = ['5:30','5:00', '4:30','4:00','3:30']
            
            closehr_str_ticks['CLc1'] = ['19:59','20:29', '20:59', '21:29','21:59']
            closehr_str_ticks['CLc2'] = ['19:59','20:29', '20:59', '21:29','21:59']
            closehr_str_ticks['HOc1'] = ['18:29','18:59', '19:29', '19:59', '20:29']
            closehr_str_ticks['HOc2'] = ['18:29','18:59', '19:29', '19:59', '20:29']
            closehr_str_ticks['RBc1'] = ['18:29','18:59', '19:29', '19:59', '20:29']
            closehr_str_ticks['RBc2'] = ['18:29','18:59', '19:29', '19:59', '20:29']
            closehr_str_ticks['QOc1'] = ['19:59','20:29', '20:59', '21:29','21:59']
            closehr_str_ticks['QOc2'] = ['19:59','20:29', '20:59', '21:29','21:59']
            closehr_str_ticks['QPc1'] = ['16:29','16:59', '17:29', '17:59','18:29']
            closehr_str_ticks['QPc2'] = ['16:29','16:59', '17:29', '17:59','18:29']
            
        # =============================================================================
        #     openhr_str_ticks['CLc1'] = ['3:30','3:00', '2:30','2:00','1:00']
        #     openhr_str_ticks['CLc2'] = ['3:30','3:00', '2:30','2:00','1:00']
        #     openhr_str_ticks['HOc1'] = ['13:00', '12:30', '12:00', '11:30', '11:00']
        #     openhr_str_ticks['HOc2'] = ['13:00', '12:30', '12:00', '11:30', '11:00']
        #     openhr_str_ticks['RBc1'] = ['13:00', '12:30', '12:00', '11:30', '11:00']
        #     openhr_str_ticks['RBc2'] = ['13:00', '12:30', '12:00', '11:30', '11:00']
        #     openhr_str_ticks['QOc1'] = ['3:30','3:00', '2:30','2:00','1:00']
        #     openhr_str_ticks['QOc2'] = ['3:30','3:00', '2:30','2:00','1:00']
        #     openhr_str_ticks['QPc1'] = ['8:00','7:30', '7:00','6:30','6:00']
        #     openhr_str_ticks['QPc2'] = ['8:00','7:30', '7:00','6:30','6:00']
        #     
        #     closehr_str_ticks['CLc1'] = ['19:59','20:29', '20:59', '21:29','21:59']
        #     closehr_str_ticks['CLc2'] = ['19:59','20:29', '20:59', '21:29','21:59']
        #     closehr_str_ticks['HOc1'] = ['18:29','18:59', '19:29', '19:59', '20:29']
        #     closehr_str_ticks['HOc2'] = ['18:29','18:59', '19:29', '19:59', '20:29']
        #     closehr_str_ticks['RBc1'] = ['18:29','18:59', '19:29', '19:59', '20:29']
        #     closehr_str_ticks['RBc2'] = ['18:29','18:59', '19:29', '19:59', '20:29']
        #     closehr_str_ticks['QOc1'] = ['19:59','20:29', '20:59', '21:29','21:59']
        #     closehr_str_ticks['QOc2'] = ['19:59','20:29', '20:59', '21:29','21:59']
        #     closehr_str_ticks['QPc1'] = ['16:29','16:59', '17:29', '17:59','18:29']
        #     closehr_str_ticks['QPc2'] = ['16:29','16:59', '17:29', '17:59','18:29']
        # =============================================================================
            #openhr_str_ticks = ['0h','-0.5h', '-1h','-1.5h','-2h']
            #closehr_str_ticks = ['0h','+0.5h', '+1h','+1.5h','+2h']
            
            syms = list(APC_FILE_LOC.keys())
            
            for sym in syms:
                run_main(openhr_str,closehr_str,
                         folder_name = 'beyondmarketopen2',
                         file_prefix ='20240813_argusexact_cross_TP25SL10_',
                         file_suffix = '_PNL_.xlsx',
                         sheetname = sym,
                         date_col = 'Entry_Date',
                         val_col = 'cumulative P&L from trades for contracts (x 50)',
                         cbarlabel='USD (in mil)', 
                         plot_title='Argus Exact Strategy (50 contracts) for {}'.format(sym),
                         xlabel = "Open Hour (UTC)",
                         ylabel = "Close Hour (UTC)",
                         xticks = openhr_str_ticks[sym], 
                         yticks = closehr_str_ticks[sym])
    
    

    