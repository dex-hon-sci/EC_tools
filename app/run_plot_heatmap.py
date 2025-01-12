#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 24 14:37:07 2024

@author: dexter
"""

import pandas as pd
import numpy as np
import matplotlib.dates as mdates
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import datetime as datetime
import cmasher as cmr

from crudeoil_future_const import APC_FILE_LOC, DATA_FILEPATH, RESULT_FILEPATH, make_path_list
from app.run_PNL_plot import extract_PNLplot_input
import EC_tools.utility as util
from pathlib import Path

gain_quantile = [10,15,20,25,30,35,40,45,50,55]
stoploss_quantile = [10,15,20,25,30,35]

gain_quantile_str = ['G'+str(num) for num in gain_quantile]
stoploss_quantile_str = ['S'+str(num) for num in stoploss_quantile]


# =============================================================================
# name = "PNL_argusexact_G10S10_.xlsx"
# Q = make_path_list(folder_name = 'heatmap', 
#                    file_prefix='PNL_argusexact_',
#                    file_suffix='_.xlsx', 
#                    syms=gain_quantile_str)
# =============================================================================


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
                                      index: int = -1):
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
        temp = [extract_PNLplot_input(ele, 
                                      sheet_name=sheetname,
                                      date_col = date_col, 
                                      val_col = val_col,
                                      fill_or_not=False)[1][index]
                for ele in filename_matrix[i]]
        
        print(i)
        master_list.append(temp)
        
    matrix = np.array(master_list)

    return matrix


def plot_heatmap(heatmap_data, **kwargs):
    default_kwargs = {'xticks': gain_quantile, 'yticks': stoploss_quantile}
    kwargs = dict(default_kwargs, **kwargs)

    # Start the plot
    fig, ax = plt.subplots()
    im = ax.imshow(heatmap_data, cmap=cmr.ember)
    
    cbar = ax.figure.colorbar(im, ax=ax)
    cbar.ax.set_ylabel(kwargs['cbarlabel'], rotation=-90, va="bottom")
    
    ax.set_xticks(np.arange(len(heatmap_data[0])), labels=kwargs['xticks'])
    ax.set_yticks(np.arange(len(heatmap_data)), labels=kwargs['yticks'])
    
    for i in range(len(heatmap_data)):
        for j in range(len(heatmap_data[0])):
            ax.text(j, i, round(heatmap_data[i, j]/1e6,2),
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
                      'index':-1}
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
                                                     index= kwargs['index'])

    # Plot heatmap    
    plot_heatmap(heatmap_data,
                 cbarlabel = kwargs['cbarlabel'],
                 plot_title = kwargs['plot_title'],
                 xlabel = kwargs['xlabel'],
                 ylabel = kwargs['ylabel'],
                 xticks = kwargs['xticks'],
                 yticks = kwargs['yticks'])
    
if __name__ == "__main__":
# =============================================================================
#     run_main(gain_quantile_str,stoploss_quantile_str,
#              folder_name = 'heatmap',
#              file_prefix ='PNL_argusexact_',
#              file_suffix = '_.xlsx',
#              sheetname = 'Total',
#              date_col = 'Entry_Date',
#              val_col = 'cumulative P&L from trades for contracts (x 50)',
#              cbarlabel='USD (in mil)', 
#              plot_title='Argus Exact strategy with fixed\nEntry quantile at Q0.4 for Buy\nand Q0.6 for Sell for Total (50 contracts)',
#              xlabel = "Quantile (in %) Range for Take Profit",
#              ylabel = "Quantile (in %) Range for Stop Loss",
#              xticks = gain_quantile, yticks = stoploss_quantile)
# =============================================================================
    
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
    openhr_str_ticks['HOc1'] = ['13:00', '12:30', '12:00', '11:30', '11:00']
    openhr_str_ticks['HOc2'] = ['13:00', '12:30', '12:00', '11:30', '11:00']
    openhr_str_ticks['RBc1'] = ['13:00', '12:30', '12:00', '11:30', '11:00']
    openhr_str_ticks['RBc2'] = ['13:00', '12:30', '12:00', '11:30', '11:00']
    openhr_str_ticks['QOc1'] = ['3:30','3:00', '2:30','2:00','1:00']
    openhr_str_ticks['QOc2'] = ['3:30','3:00', '2:30','2:00','1:00']
    openhr_str_ticks['QPc1'] = ['8:00','7:30', '7:00','6:30','6:00']
    openhr_str_ticks['QPc2'] = ['8:00','7:30', '7:00','6:30','6:00']
    
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
    #openhr_str_ticks = ['0h','-0.5h', '-1h','-1.5h','-2h']
    #closehr_str_ticks = ['0h','+0.5h', '+1h','+1.5h','+2h']
    
    syms = list(APC_FILE_LOC.keys())
    
    for sym in syms:
        run_main(openhr_str,closehr_str,
                 folder_name = 'beyondmarketopen',
                 file_prefix ='20240813_argusexact_cross_TP25SL10_',
                 file_suffix = '_PNL_.xlsx',
                 sheetname = sym,
                 date_col = 'Entry_Date',
                 val_col = 'cumulative P&L from trades for contracts (x 50)',
                 cbarlabel='USD (in mil)', 
                 plot_title='Argus Exact Strategy (50 contracts) for {}'.format(sym),
                 xlabel = "Open Hour (UTC)",
                 ylabel = "Close Hour (UTC)",
                 xticks = openhr_str_ticks[sym], yticks = closehr_str_ticks[sym])
    
    

    