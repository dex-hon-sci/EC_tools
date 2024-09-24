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


def build_filename_matrix(x_axis_list, y_axis_list,
                          folder_name = 'heatmap', 
                          file_prefix = 'PNL_argusexact_',
                          file_suffix = '_.xlsx'):
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

def extract_info_from_filename_matrix(filename_matrix):
    master_list = []
    for i in range(len(filename_matrix)):
        temp = [extract_PNLplot_input(ele,sheet_name='QPc2')[1][-1]
                for ele in filename_matrix[i]]
        
        print(i)
        master_list.append(temp)
    matrix = np.array(master_list)

    return matrix


def plot_heatmap():
    ...

Q = build_filename_matrix(gain_quantile_str, stoploss_quantile_str)
P = extract_PNLplot_input(Q[0][0])

MM = extract_info_from_filename_matrix(Q)

fig, ax = plt.subplots()
im = ax.imshow(MM)

cbarlabel = "USD (in mil)"

cbar = ax.figure.colorbar(im, ax=ax)
cbar.ax.set_ylabel(cbarlabel, rotation=-90, va="bottom")

ax.set_xticks(np.arange(len(gain_quantile)), labels=gain_quantile)
ax.set_yticks(np.arange(len(stoploss_quantile)), labels=stoploss_quantile)

for i in range(len(MM)):
    for j in range(len(MM[0])):
        text = ax.text(j, i, round(MM[i, j]/1e6,2),
                       ha="center", va="center", color="w")


ax.set_title("Argus Exact strategy with fixed \n \
             Entry quantile at Q0.4 for Buy and Q0.6 for Sell \n\
             for QPc2 (50 contracts)")
ax.set_ylabel("Quantile (in %) Range for Stop Loss")
ax.set_xlabel("Quantile (in %) Range for Gain")
fig.tight_layout()
plt.show()