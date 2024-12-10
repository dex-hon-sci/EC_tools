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
from crudeoil_future_const import APC_FILE_LOC, DATA_FILEPATH, make_path_list
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
                          file_suffix: str = '_.xlsx'):
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
        Q = make_path_list(folder_name = 'heatmap', 
                           file_prefix='PNL_argusexact_',
                           file_suffix='_.xlsx', 
                           syms=temp)
        master_list.append(Q)
    
    
    filename_matrix = np.array(master_list)
    #print(filename_matrix, len(filename_matrix))
    return filename_matrix

def extract_info_from_filename_matrix(filename_matrix: np.ndarray,
                                      sheetname: str = 'CLc1',
                                      date_col: str = "Entry_Date",
                                      val_col: str = "cumulative P&L from trades for contracts (x 50)"):
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
                                      fill_or_not=False)[1][-1]
                for ele in filename_matrix[i]]
        
        print(i)
        master_list.append(temp)
        
    matrix = np.array(master_list)

    return matrix


def plot_heatmap(x_axis_str_list: list[str], 
                 y_axis_str_list: list[str],
                 **kwargs):

    # make a matrix containing the name of the source file in the respective 
    # postions
    filename_matrix = build_filename_matrix(x_axis_str_list, y_axis_str_list)
        
    # Extract the particular columns and information to be plotted.
    heatmap_data = extract_info_from_filename_matrix(filename_matrix)
    
    # Start the plot
    fig, ax = plt.subplots()
    im = ax.imshow(heatmap_data)
    
    cbar = ax.figure.colorbar(im, ax=ax)
    cbar.ax.set_ylabel(kwargs['cbarlabel'], rotation=-90, va="bottom")
    
    ax.set_xticks(np.arange(len(x_axis_str_list)), labels=gain_quantile)
    ax.set_yticks(np.arange(len(y_axis_str_list)), labels=stoploss_quantile)
    
    for i in range(len(heatmap_data)):
        for j in range(len(heatmap_data[0])):
            text = ax.text(j, i, round(heatmap_data[i, j]/1e6,2),
                           ha="center", va="center", color="w")
    
    ax.set_title(kwargs['plot_title'])
    ax.set_xlabel(kwargs['xlabel'])
    ax.set_ylabel(kwargs['ylabel'])
    fig.tight_layout()
    plt.show()
    
def run_main():
    # make a matrix containing the name of the source file in the respective 
    # postions
    #Q = build_filename_matrix(gain_quantile_str, stoploss_quantile_str)
        
    # Extract the particular columns and information to be plotted.
    #MM = extract_info_from_filename_matrix(Q)
    
    plot_heatmap(gain_quantile_str, 
                 stoploss_quantile_str,
                 cbarlabel = "USD (in mil)",
                 plot_title = "Argus Exact strategy with fixed\nEntry quantile at Q0.4 for Buy\nand Q0.6 for Sell for QPc2 (50 contracts)",
                 xlabel = "Quantile (in %) Range for Take Profit",
                 ylabel = "Quantile (in %) Range for Stop Loss")
    
if __name__ == "__main__":
    run_main()
    