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
import datetime as datetime
from crudeoil_future_const import APC_FILE_LOC, DATA_FILEPATH
import EC_tools.utility as util
#FILENAME = './data/profits_and_losses_data_benchmark_11_.xlsx'
#FILENAME = '/home/dexter/Euler_Capital_codes/EC_tools/results/benchmark_PNL_xlsx/benchmark_PNL_full_.xlsx'
ARGUS_EXACT_PNL_FILENAME = '/home/dexter/Euler_Capital_codes/EC_tools/results/argus_exact_PNL_full_.xlsx'
ARGUS_EXACT_PNL_AMB_FILENAME = '/home/dexter/Euler_Capital_codes/EC_tools/results/argus_exact_PNL_amb_full_.xlsx'
ARGUS_EXACT_PNL_AMB2_FILENAME = '/home/dexter/Euler_Capital_codes/EC_tools/results/argus_exact_PNL_amb2_full_.xlsx'
ARGUS_EXACT_PNL_AMB3_FILENAME = '/home/dexter/Euler_Capital_codes/EC_tools/results/argus_exact_PNL_amb3_full_.xlsx'
ARGUS_EXACT_MODE_PNL_FILENAME = '/home/dexter/Euler_Capital_codes/EC_tools/results/argus_exact_mode_PNL_full_.xlsx'
ARGUS_EXACT_PNL_AMB4_ROLL3_FILENAME = "/home/dexter/Euler_Capital_codes/EC_tools/results/argus_exact_PNL_amb4_roll3_.xlsx"
ARGUS_EXACT_PNL_EARLY = "/home/dexter/Euler_Capital_codes/EC_tools/results/argus_exact_early_PNL_test_.xlsx"
ARGUS_EXACT_PNL_Port_test = "/home/dexter/Euler_Capital_codes/EC_tools/tradebook_test_.xlsx"

OLD_MODE_FILENAME = "/home/dexter/Euler_Capital_codes/EC_tools/results/profits_and_losses_data_pdfmax_17_.xlsx"
ARGUS_EXACT_MODE_WRONGTIME_FILENAME = "/home/dexter/Euler_Capital_codes/EC_tools/results/argus_exact_mode_wrongtime_PNL_.xlsx"
test_FILENAME = "/home/dexter/Euler_Capital_codes/EC_tools/results/argus_exact_mode_op_PNL_test_.xlsx"
##########################33
OLD_BENCHMARK = "/home/dexter/Euler_Capital_codes/EC_tools/results/profits_and_losses_data_test_with_finiteentry_19_.xlsx"
PORTFOLIO_ARGUSEXACT_SR = "/home/dexter/Euler_Capital_codes/EC_tools/results/consistency/test_PNL_Portfolio_ArgusExact_Full_SR_.xlsx"

OLD_BENCHMARK_SHORT = "/home/dexter/Euler_Capital_codes/EC_tools/results/consistency/Old_Benchmark/profits_and_losses_data_benchmark_19_Short_.xlsx"
OLD_BENCHMARK_FINENTRY_SHORT = "/home/dexter/Euler_Capital_codes/EC_tools/results/consistency/Old_Benchmark/profits_and_losses_data_test_with_finiteentry_19_Short_.xlsx"
PORTFOLIO_ARGUSEXACT_SHORT_SR = "/home/dexter/Euler_Capital_codes/EC_tools/results/consistency/Portfolio_backtest_ArgusExact_Short_SR/test_PNL_Portfolio_ArgusExact_Short_SR_.xlsx"
PORTFOLIO_ARGUSEXACT_SHORT_SR2 = "/home/dexter/Euler_Capital_codes/EC_tools/results/consistency/Portfolio_backtest_ArgusExact_Short_SR2/test_PNL_Portfolio_ArgusExact_Short_SR2_.xlsx"
PORTFOLIO_ARGUSEXACT_SHORT_SR3 = "/home/dexter/Euler_Capital_codes/EC_tools/results/consistency/Portfolio_backtest_ArgusExact_Short_SR3/test_PNL_Portfolio_ArgusExact_Short_SR3_.xlsx"
PORTFOLIO_ARGUSEXACT_SHORT_SR_range = "/home/dexter/Euler_Capital_codes/EC_tools/results/consistency/Portfolio_backtest_ArgusExact_Short_SR_range/test_PNL_Portfolio_ArgusExact_Short_SR_range_.xlsx"

ARGUS_SAMPLE_SHORT = "/home/dexter/Euler_Capital_codes/EC_tools/results/consistency/Argus_sample/Argus_sample_trades_2_.xlsx"
ARGUS_SAMPLE_SHORT_MYBACKTEST = "/home/dexter/Euler_Capital_codes/EC_tools/results/consistency/Argus_sample_with_mybacktest/Argus_sample_PNL_with_mybacktest_.xlsx"

TEST_NEWLOOP_PORTFOLIO_ARGUSEXACT_SHORT_SR = "/home/dexter/Euler_Capital_codes/EC_tools/results/consistency/test_newloop/test_newloop_PNL_Portfolio_ArgusExact_Short_SR_crossover_.xlsx"
TEST_NEWLOOP_PORTFOLIO_ARGUSEXACT_SHORT_SR_range = "/home/dexter/Euler_Capital_codes/EC_tools/results/consistency/test_newloop/test_newloop_PNL_Portfolio_ArgusExact_Short_SR_range_.xlsx"

#####################
symbol_list = ['CLc1', 'HOc1', 'RBc1', 'QOc1', 'QPc1', 'CLc2', 'HOc2', 'RBc2', 'QOc2', 'QPc2']
label_list = ['CLc1 (x50)', 'HOc1 (x50)', 'RBc1 (x50)', 'QOc1 (x50)', 'QPc1 (x50)', 'CLc2 (x50)', 'HOc2 (x50)', 'RBc2 (x50)', 'QOc2 (x50)', 'QPc2 (x50)']
col_list = ['#62A0E1','#EB634E','#E99938','#5CDE93','#6ABBC6', '#62A0E1','#EB634E','#E99938','#5CDE93','#6ABBC6']
line_list = ['-','-', '-','-','-', '--','--', '--','--','--']



def fill_holes(cumPNL: list) -> list:
    if np.isnan(cumPNL[0]):
        cumPNL[0] = 0.0
    
    for i in range(len(cumPNL)):
        
        if np.isnan(cumPNL[i]):
            cumPNL[i] = cumPNL[i-1]
            
    return cumPNL
    
def extract_PNLplot_input(filename: str, 
                          sheet_name: str ='Total', 
                          date_col: str = 'Entry_Date', 
                          val_col: str = 'cumulative P&L from trades for contracts (x 50)',
                          fill_or_not: bool = True) -> tuple[list, list]:
          
    dataframe = pd.read_excel(filename,sheet_name=sheet_name)

    date_all = dataframe[date_col].to_numpy()
    cumPNL_all = dataframe[val_col].to_numpy()
    
    
    date_all = np.array([datetime.datetime.strptime(date_all[i], '%Y-%m-%d') 
                          for i in range(len(date_all))])

    if fill_or_not:
        cumPNL_all = fill_holes(cumPNL_all)
    else:
        pass
    
    return date_all, cumPNL_all


def twopanel_plot(x_data: list, y1_data: list, y2_data: list, 
                 upper_plot_ylabel: str = 'Cumulative return (USD)', 
                 lower_plot_ylabel: str = 'Scaled returns (USD)',
                 xlabel: str = 'Date', plot_title: str = "Cumulative PNL",
                 line_color: str = 'w', 
                 label: str = 'All (x50)',  
                 sub_x_list: list = [], 
                 sub_y1_list: list = [], 
                 sub_line_list: list = [],
                 sub_label_list: list = [], 
                 sub_col_list: list = [], alpha = 1.0) -> None:
    
    plt.style.use('dark_background')
    fig = plt.figure(figsize=(14,6))
    fig.set_tight_layout(True)
    # make a way to change the number of subplot based on nrows and ncols
    gs = fig.add_gridspec(nrows=2, ncols = 1, height_ratios=[6, 2.5])
    fig.suptitle(plot_title)
    
    ax1 = fig.add_subplot(gs[0])

    
    ax2 = fig.add_subplot(gs[1], sharex=ax1)

    ax2.bar(x_data, y2_data)
    ax2.hlines(0, datetime.datetime(2020,12,10), datetime.datetime(2024,7,1), 
               color='#B67C62', ls='--',lw=4)
    
    ax1.set_ylabel(upper_plot_ylabel)

    
    for i, (x_element, y1_element) in enumerate(zip(sub_x_list, sub_y1_list)):
        ax1.plot(x_element, y1_element, ls=sub_line_list[i], 
                 label=sub_label_list[i], color=sub_col_list[i])
        
    ax1.plot(x_data, y1_data,'-', c=line_color, label=label, alpha = alpha)
    
    fmt = mdates.DateFormatter('%y-%m-%d')
    ax1.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    ax1.xaxis.set_major_formatter(fmt)
    ax2.xaxis.set_major_formatter(fmt)
    
    ax2.set_ylabel(lower_plot_ylabel)
    ax2.set_xlabel(xlabel)

    ax1.grid()
    ax2.grid()
    
    plt.show()
# =============================================================================
# 
# def cumPNL_plot(date: list, PNL: list, return_rate: list,                  
#                sub_date_list: list = [], sub_data_list: list = [], 
#                sub_line_list: list = [], sub_label_list: list = [], 
#                sub_col_list: list = []):
#     
#     twopanel_plot(date, PNL, return_rate, 
#                     upper_plot_ylabel = 'Cumulative return (USD)', 
#                     lower_plot_ylabel = 'Scaled returns (USD)',
#                     xlabel = 'Date',
#                     line_color = 'w', 
#                     label = 'All (x50)',
#                     sub_date_list = sub_date_list, 
#                     sub_data_list = sub_data_list, 
#                     sub_line_list = sub_line_list,
#                     sub_label_list = sub_label_list, 
#                     sub_col_list = sub_col_list)
# =============================================================================

if __name__=='__main__':
    
    # PLot PNL for the cumulative return for a specific strategy as well as 
    # the PNL for inidividual assets
    FILENAME = PORTFOLIO_ARGUSEXACT_SHORT_SR #OLD_BENCHMARK
    date_col = 'Entry_Date'#'date'
    # Extract the cumulative PNL of the strategy
    date_all, cumPNL_all = extract_PNLplot_input(FILENAME, date_col=date_col)
    
    # Extract the trade_return of the strategy
    date_all2, return_all = extract_PNLplot_input(FILENAME,
                                                  val_col='scaled returns from trades', 
                                                  date_col=date_col,
                                                  fill_or_not=False)
    
    
    # Extract the individual asset PNL and dates
    date_list = [extract_PNLplot_input(FILENAME, 
                                       sheet_name=symbol_list[i], \
                                       date_col = date_col)[0] \
                                       for i in range(len(symbol_list))]
    data_list = [extract_PNLplot_input(FILENAME, 
                                       sheet_name=symbol_list[i], 
                                       date_col = date_col)[1] \
                                       for i in range(len(symbol_list))]
    return_list = [extract_PNLplot_input(FILENAME, 
                                         sheet_name=symbol_list[i], 
                                         val_col='scaled returns from trades', 
                                         date_col = date_col,
                                         fill_or_not=False)[1] \
                                         for i in range(len(symbol_list))]
    
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
    # =============================================================================
    # =============================================================================
    # twopanel_plot([], [], [], label='All (x50)',
    #               sub_date_list=date_list, sub_data_list=data_list,
    #               sub_label_list = label_list,
    #               sub_col_list = col_list, 
    #               sub_line_list =line_list)
    # =============================================================================
    
    
# =============================================================================
#     twopanel_plot([], [], [], label='CLc1',
#                    sub_x_list=date_list, 
#                    sub_y1_list=data_list,
#                    sub_label_list = label_list,
#                    sub_col_list = col_list, 
#                    sub_line_list =line_list)
# =============================================================================
    
    
    # Plot comparison between multiple different strategies
# =============================================================================
# Massive comparison
#     strategy_date_list = [extract_PNLplot_input(ARGUS_EXACT_PNL_FILENAME)[0],
#                           extract_PNLplot_input(ARGUS_EXACT_PNL_AMB_FILENAME)[0], 
#                           extract_PNLplot_input(ARGUS_EXACT_PNL_AMB2_FILENAME)[0],
#                           extract_PNLplot_input(ARGUS_EXACT_PNL_AMB3_FILENAME)[0],
#                           extract_PNLplot_input(ARGUS_EXACT_MODE_PNL_FILENAME)[0],
#                           extract_PNLplot_input(OLD_MODE_FILENAME,date_col='date')[0],
#                           extract_PNLplot_input(ARGUS_EXACT_PNL_AMB4_ROLL3_FILENAME)[0],
#                           extract_PNLplot_input(ARGUS_EXACT_MODE_WRONGTIME_FILENAME)[0],
#                           extract_PNLplot_input(test_FILENAME)[0],
#                           extract_PNLplot_input(ARGUS_EXACT_PNL_EARLY)[0],
#                           extract_PNLplot_input(ARGUS_EXACT_PNL_Port_test)[0]
#                           ]
#     strategy_data_list = [extract_PNLplot_input(ARGUS_EXACT_PNL_FILENAME)[1],
#                           extract_PNLplot_input(ARGUS_EXACT_PNL_AMB_FILENAME)[1], 
#                           extract_PNLplot_input(ARGUS_EXACT_PNL_AMB2_FILENAME)[1],
#                           extract_PNLplot_input(ARGUS_EXACT_PNL_AMB3_FILENAME)[1],
#                           extract_PNLplot_input(ARGUS_EXACT_MODE_PNL_FILENAME)[1],
#                           extract_PNLplot_input(OLD_MODE_FILENAME, date_col='date')[1],
#                           extract_PNLplot_input(ARGUS_EXACT_PNL_AMB4_ROLL3_FILENAME)[1],
#                           extract_PNLplot_input(ARGUS_EXACT_MODE_WRONGTIME_FILENAME)[1],
#                           extract_PNLplot_input(test_FILENAME)[1],
#                           extract_PNLplot_input(ARGUS_EXACT_PNL_EARLY)[1],
#                           extract_PNLplot_input(ARGUS_EXACT_PNL_Port_test)[1]
#                           ]
#     strategy_label_list = ['Argus_Exact', 'Ambituous', 'Ambituous2', 
#                            'Ambituous3', 'Argus_Exact_Mode', 'old_mode',
#                            'amb4_roll3', 'argus_exact_wrongtime','test_op_mode', 
#                            'argus_exact_early', 'Port_test']
#     strategy_col_list = ['b','w','w', 'y', 'r', 'g', 'w', '#b3c27a', 
#                          '#c32b2b', '#919191', '#c509c8']
#     strategy_line_list = ['solid','dotted', 'dashed', 'dashdot', 'dashdot', 
#                           'dashdot', 'solid', 'dashed', 'solid', 'solid', 'solid']
#     
#     # Plot different strategies cumulative PNL
#     twopanel_plot([], [], [], label='',
#                   sub_x_list=strategy_date_list,
#                   sub_y1_list=strategy_data_list,
#                   sub_label_list = strategy_label_list,
#                   sub_col_list = strategy_col_list, 
#                   sub_line_list =strategy_line_list)
# =============================================================================
    strategy_date_list = [extract_PNLplot_input(OLD_BENCHMARK_SHORT, date_col="date",
                                                val_col="cumulative P&L from trades")[0],
                          extract_PNLplot_input(OLD_BENCHMARK_FINENTRY_SHORT, date_col="date",
                                                val_col="cumulative P&L from trades")[0],
                          extract_PNLplot_input(PORTFOLIO_ARGUSEXACT_SHORT_SR3,
                                                val_col="cumulative P&L from trades")[0], 
                          extract_PNLplot_input(ARGUS_SAMPLE_SHORT,
                                                val_col="cumulative P&L from trades")[0],
                          extract_PNLplot_input(ARGUS_SAMPLE_SHORT_MYBACKTEST,
                                                val_col="cumulative P&L from trades")[0],
                          extract_PNLplot_input(PORTFOLIO_ARGUSEXACT_SHORT_SR_range,
                                                val_col="cumulative P&L from trades")[0],
                          extract_PNLplot_input(TEST_NEWLOOP_PORTFOLIO_ARGUSEXACT_SHORT_SR,
                                                val_col="cumulative P&L from trades")[0],
                          extract_PNLplot_input(TEST_NEWLOOP_PORTFOLIO_ARGUSEXACT_SHORT_SR_range,
                                                val_col="cumulative P&L from trades")[0]
                          ]
    strategy_data_list = [extract_PNLplot_input(OLD_BENCHMARK_SHORT, date_col="date",
                                                val_col="cumulative P&L from trades")[1],
                          extract_PNLplot_input(OLD_BENCHMARK_FINENTRY_SHORT, date_col="date",
                                                val_col="cumulative P&L from trades")[1],
                          extract_PNLplot_input(PORTFOLIO_ARGUSEXACT_SHORT_SR3,
                                                val_col="cumulative P&L from trades")[1],
                          extract_PNLplot_input(ARGUS_SAMPLE_SHORT,
                                                val_col="cumulative P&L from trades")[1],
                          extract_PNLplot_input(ARGUS_SAMPLE_SHORT_MYBACKTEST,
                                                val_col="cumulative P&L from trades")[1],
                          extract_PNLplot_input(PORTFOLIO_ARGUSEXACT_SHORT_SR_range,
                                                val_col="cumulative P&L from trades")[1],
                          extract_PNLplot_input(TEST_NEWLOOP_PORTFOLIO_ARGUSEXACT_SHORT_SR,
                                                val_col="cumulative P&L from trades")[1],
                          extract_PNLplot_input(TEST_NEWLOOP_PORTFOLIO_ARGUSEXACT_SHORT_SR_range,
                                                val_col="cumulative P&L from trades")[1]
                          ]
    strategy_label_list = ['Old_Benchmark_Short (Abbe-Signal, Abbe-Backtest)', 
                           'Old_Benchmark_finiteentry_short (Abbe-Signal, Abbe-Backtest)',
                           'Portfolio_ArgusExact_Short (Dex-Signal, Dex-Backtest)',
                           'Argus_Sample (Argus-Signal, Argus-Backtest)',
                           'Argus_Sample (Argus-Signal, Dex-Backtest)',
                           'Portfolio_ArgusExact_Short_range (Dex-Signal, Dex-Backtest)',
                           'test_newloop_crossover',
                           'test_newloop_range'
                           
                           ]
    TEST_NEWLOOP_PORTFOLIO_ARGUSEXACT_SHORT_SR = "/home/dexter/Euler_Capital_codes/EC_tools/results/test_newloop/test_newloop_PNL_Portfolio_ArgusExact_Short_SR_crossover_.xlsx"
    TEST_NEWLOOP_PORTFOLIO_ARGUSEXACT_SHORT_SR_range = "/home/dexter/Euler_Capital_codes/EC_tools/results/test_newloop/test_newloop_PNL_Portfolio_ArgusExact_Short_SR_range_.xlsx"

    strategy_col_list = ['r','r', 'w', 'b', '#28ebee', 'g', 'yellow', '#c509c8']
    strategy_line_list = ['solid','dashed','solid', 'solid','solid', 'solid', 'dotted', 'dotted']
    
    # Plot different strategies cumulative PNL
    twopanel_plot([], [], [], label='',
                  sub_x_list=strategy_date_list,
                  sub_y1_list=strategy_data_list,
                  sub_label_list = strategy_label_list,
                  sub_col_list = strategy_col_list, 
                  sub_line_list =strategy_line_list)
    
# =============================================================================
# 
#     # Plot individual asset cumulative PNL and returns    
#     for i in range(10):
#         cumPNL_plot(date_list[i], data_list[i], return_list[i], label=label_list[i],
#                 line_color = col_list[i])
# =============================================================================
