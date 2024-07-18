#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 10 04:35:17 2024

@author: dexter
"""

import pandas as pd
import numpy as np
import matplotlib.dates as mdates
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
from datetime import datetime

#FILENAME = './data/profits_and_losses_data_benchmark_11_.xlsx'
#FILENAME = '/home/dexter/Euler_Capital_codes/EC_tools/results/benchmark_PNL_xlsx/benchmark_PNL_full_.xlsx'
FILENAME = '/home/dexter/Euler_Capital_codes/EC_tools/results/benchmark_PNL_xlsx/benchmark_PNL_full_.xlsx'

dataframe = pd.read_excel(FILENAME,sheet_name='Total')

dataframe_CLc1 = pd.read_excel(FILENAME, sheet_name='CLc1')
dataframe_HOc1 = pd.read_excel(FILENAME, sheet_name='HOc1')
dataframe_RBc1 = pd.read_excel(FILENAME, sheet_name='RBc1')
dataframe_QOc1 = pd.read_excel(FILENAME, sheet_name='QOc1')
dataframe_QPc1 = pd.read_excel(FILENAME, sheet_name='QPc1')

dataframe_CLc2 = pd.read_excel(FILENAME, sheet_name='CLc1')
dataframe_HOc2 = pd.read_excel(FILENAME, sheet_name='HOc2')
dataframe_RBc2 = pd.read_excel(FILENAME, sheet_name='RBc2')
dataframe_QOc2 = pd.read_excel(FILENAME, sheet_name='QOc2')
dataframe_QPc2 = pd.read_excel(FILENAME, sheet_name='QPc2')


date_all = dataframe['date'].to_numpy()
cumPNL_all = dataframe['cumulative P&L from trades for contracts (x 50)'].to_numpy()

date_CLc1 = dataframe_CLc1['date'].to_numpy()
date_HOc1 = dataframe_HOc1['date'].to_numpy()
date_RBc1 = dataframe_RBc1['date'].to_numpy()
date_QOc1 = dataframe_QOc1['date'].to_numpy()
date_QPc1 = dataframe_QPc1['date'].to_numpy()

date_CLc2 = dataframe_CLc2['date'].to_numpy()
date_HOc2 = dataframe_HOc2['date'].to_numpy()
date_RBc2 = dataframe_RBc2['date'].to_numpy()
date_QOc2 = dataframe_QOc2['date'].to_numpy()
date_QPc2 = dataframe_QPc2['date'].to_numpy()

date_all = np.array([datetime.strptime(date_all[i], '%Y-%m-%d') 
                      for i in range(len(date_all))])


date_CLc1 = np.array([datetime.strptime(date_CLc1[i], '%Y-%m-%d') 
                      for i in range(len(date_CLc1))])
date_HOc1 = np.array([datetime.strptime(date_HOc1[i], '%Y-%m-%d') 
                      for i in range(len(date_HOc1))])
date_RBc1 = np.array([datetime.strptime(date_RBc1[i], '%Y-%m-%d') 
                      for i in range(len(date_RBc1))])
date_QOc1 = np.array([datetime.strptime(date_QOc1[i], '%Y-%m-%d') 
                      for i in range(len(date_QOc1))])
date_QPc1 = np.array([datetime.strptime(date_QPc1[i], '%Y-%m-%d') 
                      for i in range(len(date_QPc1))])

date_CLc2 = np.array([datetime.strptime(date_CLc2[i], '%Y-%m-%d') 
                      for i in range(len(date_CLc2))])
date_HOc2 = np.array([datetime.strptime(date_HOc2[i], '%Y-%m-%d') 
                      for i in range(len(date_HOc2))])
date_RBc2 = np.array([datetime.strptime(date_RBc2[i], '%Y-%m-%d') 
                      for i in range(len(date_RBc2))])
date_QOc2 = np.array([datetime.strptime(date_QOc2[i], '%Y-%m-%d') 
                      for i in range(len(date_QOc2))])
date_QPc2 = np.array([datetime.strptime(date_QPc2[i], '%Y-%m-%d') 
                      for i in range(len(date_QPc2))])

cumPNL_50_CLc1 = dataframe_CLc1['cumulative P&L from trades for contracts (x 50)'].to_numpy()
cumPNL_50_HOc1 = dataframe_HOc1['cumulative P&L from trades for contracts (x 50)'].to_numpy()
cumPNL_50_RBc1 = dataframe_RBc1['cumulative P&L from trades for contracts (x 50)'].to_numpy()
cumPNL_50_QOc1 = dataframe_QOc1['cumulative P&L from trades for contracts (x 50)'].to_numpy()
cumPNL_50_QPc1 = dataframe_QPc1['cumulative P&L from trades for contracts (x 50)'].to_numpy()

cumPNL_50_CLc2 = dataframe_CLc2['cumulative P&L from trades for contracts (x 50)'].to_numpy()
cumPNL_50_HOc2 = dataframe_HOc2['cumulative P&L from trades for contracts (x 50)'].to_numpy()
cumPNL_50_RBc2 = dataframe_RBc2['cumulative P&L from trades for contracts (x 50)'].to_numpy()
cumPNL_50_QOc2 = dataframe_QOc2['cumulative P&L from trades for contracts (x 50)'].to_numpy()
cumPNL_50_QPc2 = dataframe_QPc2['cumulative P&L from trades for contracts (x 50)'].to_numpy()

def fill_holes(cumPNL):
    if np.isnan(cumPNL[0]):
        cumPNL[0] = 0.0
    
    for i in range(len(cumPNL)):
        
        if np.isnan(cumPNL[i]):
            cumPNL[i] = cumPNL[i-1]
            
    return cumPNL

cumPNL_50_CLc1 = fill_holes(cumPNL_50_CLc1)
cumPNL_50_HOc1 = fill_holes(cumPNL_50_HOc1)
cumPNL_50_RBc1 = fill_holes(cumPNL_50_RBc1)
cumPNL_50_QOc1 = fill_holes(cumPNL_50_QOc1)
cumPNL_50_QPc1 = fill_holes(cumPNL_50_QPc1)

cumPNL_50_CLc2 = fill_holes(cumPNL_50_CLc2)
cumPNL_50_HOc2 = fill_holes(cumPNL_50_HOc2)
cumPNL_50_RBc2 = fill_holes(cumPNL_50_RBc2)
cumPNL_50_QOc2 = fill_holes(cumPNL_50_QOc2)
cumPNL_50_QPc2 = fill_holes(cumPNL_50_QPc2)

cumPNL_all = fill_holes(cumPNL_all)

# =============================================================================
# date_list = [date_CLc1, date_HOc1, date_RBc1, date_QOc1, date_QPc1,
#              date_CLc2, date_HOc2, date_RBc2, date_QOc2, date_QPc2]
# data_list = [cumPNL_50_CLc1, cumPNL_50_HOc1, cumPNL_50_RBc1, cumPNL_50_QOc1, cumPNL_50_QPc1,
#              cumPNL_50_CLc2, cumPNL_50_HOc2, cumPNL_50_RBc2, cumPNL_50_QOc2, cumPNL_50_QPc2]
#  
# label_list = ['CLc1 (x50)', 'HOc1 (x50)', 'RBc1 (x50)', 'QOc1 (x50)', 'QPc1 (x50)',
#               'CLc2 (x50)', 'HOc2 (x50)', 'RBc2 (x50)', 'QOc2 (x50)', 'QPc2 (x50)']
# col_list = ['#62A0E1','#EB634E','#E99938','#5CDE93','#6ABBC6',
#             '#62A0E1','#EB634E','#E99938','#5CDE93','#6ABBC6']
# 
# line_list = ['-','-','-','-','-',
#           '--','--', '--','--','--']
# 
# =============================================================================

# =============================================================================
# date_list = [date_CLc2, date_HOc2, date_RBc2, date_QOc2, date_QPc2]
# data_list = [cumPNL_50_CLc2, cumPNL_50_HOc2, cumPNL_50_RBc2, cumPNL_50_QOc2, cumPNL_50_QPc2]
#  
# label_list = ['CLc2 (x50)', 'HOc2 (x50)', 'RBc2 (x50)', 'QOc2 (x50)', 'QPc2 (x50)']
# col_list = ['#62A0E1','#EB634E','#E99938','#5CDE93','#6ABBC6']
#             
# 
# line_list = ['--','--', '--','--','--']
# 
# =============================================================================

date_list = [date_CLc1, date_HOc1, date_RBc1, date_QOc1, date_QPc1]
data_list = [cumPNL_50_CLc1, cumPNL_50_HOc1, cumPNL_50_RBc1, cumPNL_50_QOc1, cumPNL_50_QPc1]

label_list = ['CLc1 (x50)', 'HOc1 (x50)', 'RBc1 (x50)', 'QOc1 (x50)', 'QPc1 (x50)']
col_list = ['#62A0E1','#EB634E','#E99938','#5CDE93','#6ABBC6']
line_list = ['-','-', '-','-','-']

def cumPNL_plot(x,y):
    plt.style.use('dark_background')

    # plotting area

    fig, ax = plt.subplots(figsize=(10,4))
    
    ax.plot(x, y,'-', c='w', label='All (x50)')
    
    
    for i, (date, data) in enumerate(zip(date_list, data_list)):
        ax.plot(date, data,ls=line_list[i], label=label_list[i], color=col_list[i])
    
    fmt = mdates.DateFormatter('%y-%m-%d')
    ax.xaxis.set_major_formatter(fmt)
    #ax.set_yticks(np.arange(0,1e7,2e6), np.arange(0,10_000_000,2_000_000))

    ax.set_xlabel('Date')
    ax.set_ylabel('USD')
    ax.set_title('Cumulative PNL')
    plt.legend(loc='upper left')
    plt.grid()
    
    plt.show()
def cumPNL_compare():
    return
    
PNL_plot(date_all, cumPNL_all)