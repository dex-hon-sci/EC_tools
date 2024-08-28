#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun 22 21:31:35 2024

@author: dexter
"""
import pandas as pd
import EC_tools.read as read
import EC_tools.utility as util


@util.time_it
def merge_raw_data(filename_list, save_filename, sort_by = "Forecast Period"):
    A = read.concat_CSVtable(filename_list, sort_by= sort_by)
    A.to_csv(save_filename,index=False)
    print(A)
    return A

#merge_raw_data(list(APC_FILE_LOC.values()), 'APC_latest_all.csv')

#merge_raw_data(list(HISTORY_DAILY_FILE_LOC.values()), 
#               'history_daily_data_all.csv', sort_by="Date")

# =============================================================================
# merge_raw_data(list(HISTORY_MINTUE_FILE_LOC.values()), 
#                'history_minute_data_all.csv', sort_by="Date")
# =============================================================================
