#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun 22 23:32:11 2024

@author: dexter
"""
from crudeoil_future_const import *

from run_preprocess import run_preprocess
from run_gen_MR_dir import run_gen_MR_signals_list
# data management

#run_data_management

# run preprocessing (calculate earliest entry and update all database )

run_preprocess()

# run strategy, let the user to choose strategy here (add strategy id)

start_date, end_date = None, None

run_gen_MR_signals_list(SAVE_FILENAME_LIST, CAT_LIST, 
                        KEYWORDS_LIST, SYMBOL_LIST, 
                            start_date, end_date,
                            SIGNAL_LIST, HISTORY_DAILY_LIST, 
                            HISTORY_MINUTE_LIST)

#merge_CSV_table

# run backtest- let the user to generate backtest data using their method
#run_backtest_portfolio

# Visualise PNL plot and metrics.
#run_PNL