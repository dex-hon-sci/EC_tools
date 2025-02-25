#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 20 03:05:52 2025

@author: dexter
"""
from app.run_PNL_plot import extract_PNLplot_input, twopanel_plot

SYMBOL_LIST = ['CLc1', 'HOc1', 'RBc1', 'QOc1', 'QPc1', 'CLc2', 'HOc2', 'RBc2', 'QOc2', 'QPc2']
#label_list = ['CLc1 (x50)', 'HOc1 (x50)', 'RBc1 (x50)', 'QOc1 (x50)', 'QPc1 (x50)', 'CLc2 (x50)', 'HOc2 (x50)', 'RBc2 (x50)', 'QOc2 (x50)', 'QPc2 (x50)']
label_list = ['CLc1', 'HOc1', 'RBc1', 'QOc1', 'QPc1', 'CLc2', 'HOc2', 'RBc2', 'QOc2', 'QPc2']
col_list = ['#62A0E1','#EB634E','#E99938','#5CDE93','#6ABBC6', '#62A0E1','#EB634E','#E99938','#5CDE93','#6ABBC6']
line_list = ['-','-', '-','-','-', '--','--', '--','--','--']



def plot_one_portfolio(FILENAME):
    #FILENAME = PORTFOLIO_ARGUSEXACT_SHORT_SR #OLD_BENCHMARK
    date_col = 'Entry_Date'
    # Extract the cumulative PNL of the strategy
    date_all, cumPNL_all = extract_PNLplot_input(FILENAME, date_col=date_col)
    
    # Extract the trade_return of the strategy
    date_all2, return_all = extract_PNLplot_input(FILENAME,
                                                  val_col='scaled returns from trades', 
                                                  date_col=date_col,
                                                  fill_or_not=False)
    
    
    # Extract the individual asset PNL and dates
    date_list = [extract_PNLplot_input(FILENAME, 
                                       sheet_name=SYMBOL_LIST[i], \
                                       date_col = date_col)[0] \
                                       for i in range(len(SYMBOL_LIST))]
    data_list = [extract_PNLplot_input(FILENAME, 
                                       sheet_name=SYMBOL_LIST[i], 
                                       date_col = date_col)[1] \
                                       for i in range(len(SYMBOL_LIST))]
    return_list = [extract_PNLplot_input(FILENAME, 
                                         sheet_name=SYMBOL_LIST[i], 
                                         val_col='scaled returns from trades', 
                                         date_col = date_col,
                                         fill_or_not=False)[1] \
                                         for i in range(len(SYMBOL_LIST))]
    
    #date_list = [date_CLc1, date_HOc1, date_RBc1, date_QOc1, date_QPc1]
    #data_list = [cumPNL_50_CLc1, cumPNL_50_HOc1, cumPNL_50_RBc1, cumPNL_50_QOc1, cumPNL_50_QPc1]
    #cumPNL_plot(date_all, cumPNL_all, label='All (x50)')
    
    # =============================================================================
    twopanel_plot(date_all, cumPNL_all, return_all, label='All (x50)',
                  sub_x_list=date_list, 
                  sub_y1_list=data_list,
                  sub_label_list = label_list,
                  sub_col_list = col_list, 
                  sub_line_list =line_list)
    
def plot_compare_portfolio():
    
    return
FILENAME = '/home/dexter/Euler_Capital_codes/EC_tools/results/EC_benchmark/20240814_argusexact_cross_P20S35_0330_entry_PNL_full_.xlsx'

plot_one_portfolio(FILENAME)