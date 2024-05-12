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

dataframe = pd.read_excel('profits_and_losses_data_benchmark_11_.xlsx',sheet_name='Total')

dataframe_CLc1 = pd.read_excel('profits_and_losses_data_benchmark_11_.xlsx',sheet_name='CLc1')
dataframe_HOc1 = pd.read_excel('profits_and_losses_data_benchmark_11_.xlsx',sheet_name='HOc1')
dataframe_RBc1 = pd.read_excel('profits_and_losses_data_benchmark_11_.xlsx',sheet_name='RBc1')
dataframe_QOc1 = pd.read_excel('profits_and_losses_data_benchmark_11_.xlsx',sheet_name='QOc1')
dataframe_QPc1 = pd.read_excel('profits_and_losses_data_benchmark_11_.xlsx',sheet_name='QPc1')

date_all = dataframe['date'].to_numpy()
cumPNL_all = dataframe['cumulative P&L from trades for contracts (x 50)'].to_numpy()

date_CLc1 = dataframe_CLc1['date'].to_numpy()
date_HOc1 = dataframe_HOc1['date'].to_numpy()
date_RBc1 = dataframe_RBc1['date'].to_numpy()
date_QOc1 = dataframe_QOc1['date'].to_numpy()
date_QPc1 = dataframe_QPc1['date'].to_numpy()

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

cumPNL_50_CLc1 = dataframe_CLc1['cumulative P&L from trades for contracts (x 50)'].to_numpy()
cumPNL_50_HOc1 = dataframe_HOc1['cumulative P&L from trades for contracts (x 50)'].to_numpy()
cumPNL_50_RBc1 = dataframe_RBc1['cumulative P&L from trades for contracts (x 50)'].to_numpy()
cumPNL_50_QOc1 = dataframe_QOc1['cumulative P&L from trades for contracts (x 50)'].to_numpy()
cumPNL_50_QPc1 = dataframe_QPc1['cumulative P&L from trades for contracts (x 50)'].to_numpy()

date_list = [date_CLc1, date_HOc1, date_RBc1, date_QOc1, date_QPc1]
data_list = [cumPNL_50_CLc1, cumPNL_50_HOc1, cumPNL_50_RBc1, cumPNL_50_QOc1, cumPNL_50_QPc1]
label_list = ['CLc1 (x50)', 'HOc1 (x50)', 'RBc1 (x50)', 'QOc1 (x50)', 'QPc1 (x50)']

def PNL_plot(x,y):
    plt.style.use('dark_background')

    # plotting area

    fig, ax = plt.subplots(figsize=(10,4))
    
    ax.plot(x, y,'-', c='w', label='All (x50)')
    
    
    for i, (date, data) in enumerate(zip(date_list, data_list)):
        ax.plot(date, data,'-', label=label_list[i])

# =============================================================================
# ax.plot(date_CLc1, cumPNL_50_CLc1,'-', c='#667CEC', label='CLc1 (x50)')
# ax.plot(date_HOc1, cumPNL_50_HOc1,'-', c='#D6796D', label='HOc1 (x50)')
# ax.plot(date_RBc1, cumPNL_50_RBc1,'-', c='#E7B83B', label='RBc1 (x50)')
# ax.plot(date_QOc1, cumPNL_50_QOc1,'-', c='#52B780', label='QOc1 (x50)')
# ax.plot(date_QPc1, cumPNL_50_QPc1,'-', c='#66ECD6', label='QPc1 (x50)')
# 
# =============================================================================
    
    fmt = mdates.DateFormatter('%y-%m-%d')
    ax.xaxis.set_major_formatter(fmt)
    ax.set_yticks(np.arange(0,1e7,2e6), np.arange(0,10_000_000,2_000_000))

    ax.set_xlabel('Date')
    ax.set_ylabel('USD')
    ax.set_title('Cumulative PNL')
    plt.legend(loc='upper left')
    plt.grid()
    
    plt.show()
    
PNL_plot(date_all, cumPNL_all)