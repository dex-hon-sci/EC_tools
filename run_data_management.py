#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun 22 21:31:35 2024

@author: dexter
"""
import pandas as pd
import EC_tools.read as read
import EC_tools.utility as util

APC_FILE_LOC = {
    "CLc1": "/home/dexter/Euler_Capital_codes/EC_tools/data/APC_latest/APC_latest_CLc1.csv",
    "CLc2": "/home/dexter/Euler_Capital_codes/EC_tools/data/APC_latest/APC_latest_CLc2.csv",
    "HOc1": "/home/dexter/Euler_Capital_codes/EC_tools/data/APC_latest/APC_latest_HOc1.csv",
    "HOc2": "/home/dexter/Euler_Capital_codes/EC_tools/data/APC_latest/APC_latest_HOc2.csv",
    "RBc1": "/home/dexter/Euler_Capital_codes/EC_tools/data/APC_latest/APC_latest_RBc1.csv",
    "RBc2": "/home/dexter/Euler_Capital_codes/EC_tools/data/APC_latest/APC_latest_RBc2.csv",
    "QOc1": "/home/dexter/Euler_Capital_codes/EC_tools/data/APC_latest/APC_latest_QOc1.csv",
    "QOc2": "/home/dexter/Euler_Capital_codes/EC_tools/data/APC_latest/APC_latest_QOc2.csv",
    "QPc1": "/home/dexter/Euler_Capital_codes/EC_tools/data/APC_latest/APC_latest_QPc1.csv",
    "QPc2": "/home/dexter/Euler_Capital_codes/EC_tools/data/APC_latest/APC_latest_QPc2.csv"
    }

HISTORY_DAILY_FILE_LOC = {
    "CLc1": "/home/dexter/Euler_Capital_codes/EC_tools/data/history_data/Day/CL.day",
    "CLc2": "/home/dexter/Euler_Capital_codes/EC_tools/data/history_data/Day/CL_d01.day",
    "HOc1": "/home/dexter/Euler_Capital_codes/EC_tools/data/history_data/Day/HO.day",
    "HOc2": "/home/dexter/Euler_Capital_codes/EC_tools/data/history_data/Day/HO_d01.day",
    "RBc1": "/home/dexter/Euler_Capital_codes/EC_tools/data/history_data/Day/RB.day",
    "RBc2": "/home/dexter/Euler_Capital_codes/EC_tools/data/history_data/Day/RB_d01.day",
    "QOc1": "/home/dexter/Euler_Capital_codes/EC_tools/data/history_data/Day/QO.day",
    "QOc2": "/home/dexter/Euler_Capital_codes/EC_tools/data/history_data/Day/QO_d01.day",
    "QPc1": "/home/dexter/Euler_Capital_codes/EC_tools/data/history_data/Day/QP.day",
    "QPc2": "/home/dexter/Euler_Capital_codes/EC_tools/data/history_data/Day/QP_d01.day"
}

HISTORY_MINTUE_FILE_LOC = {
    "CLc1": "/home/dexter/Euler_Capital_codes/EC_tools/data/history_data/Minute/CL.001",
    "CLc2": "/home/dexter/Euler_Capital_codes/EC_tools/data/history_data/Minute/CL_d01.001",
    "HOc1": "/home/dexter/Euler_Capital_codes/EC_tools/data/history_data/Minute/HO.001",
    "HOc2": "/home/dexter/Euler_Capital_codes/EC_tools/data/history_data/Minute/HO_d01.001",
    "RBc1": "/home/dexter/Euler_Capital_codes/EC_tools/data/history_data/Minute/RB.001",
    "RBc2": "/home/dexter/Euler_Capital_codes/EC_tools/data/history_data/Minutatest/APC_latest_QPc2.csv"
    }

HISTORY_DAILY_FILE_LOC = {
    "CLc1": "/home/dexter/Euler_Capital_codes/EC_tools/data/history_data/Day/CL.day",
    "CLc2": "/home/dexter/Euler_Capital_codes/EC_tools/data/history_data/Day/CL_d01.day",
    "HOc1": "/home/dexter/Euler_Capital_codes/EC_tools/data/history_data/Day/HO.day",
    "HOc2": "/home/dexter/Euler_Capital_codes/EC_tools/data/history_data/Day/HO_d01.day",
    "RBc1": "/home/dexter/Euler_Capital_codes/EC_tools/data/history_data/Day/RB.day",
    "RBc2": "/home/dexter/Euler_Capital_codes/EC_tools/data/history_data/Day/RB_d01.day",
    "QOc1": "/home/dexter/Euler_Capital_codes/EC_tools/data/history_data/Day/QO.day",
    "QOc2": "/home/dexter/Euler_Capital_codes/EC_tools/data/history_data/Day/QO_d01.day",
    "QPc1": "/home/dexter/Euler_Capital_codes/EC_tools/data/history_data/Day/QP.day",
    "QPc2": "/home/dexter/Euler_Capital_codes/EC_tools/data/history_data/Day/QP_d01.day"
}

HISTORY_MINTUE_FILE_LOC = {
    "CLc1": "/home/dexter/Euler_Capital_codes/EC_tools/data/history_data/Minute/CL.001",
    "CLc2": "/home/dexter/Euler_Capital_codes/EC_tools/data/history_data/Minute/CL_d01.001",
    "HOc1": "/home/dexter/Euler_Capital_codes/EC_tools/data/history_data/Minute/HO.001",
    "HOc2": "/home/dexter/Euler_Capital_codes/EC_tools/data/history_data/Minute/HO_d01.001",
    "RBc1": "/home/dexter/Euler_Capital_codes/EC_tools/data/history_data/Minute/RB.001",
    "RBc2": "/home/dexter/Euler_Capital_codes/EC_tools/data/history_data/Minute/RB_d01.001",
    "QOc1": "/home/dexter/Euler_Capital_codes/EC_tools/data/history_data/Minute/QO.001",
    "QOc2": "/home/dexter/Euler_Capital_codes/EC_tools/data/history_data/Minute/QO_d01.001",
    "QPc1": "/home/dexter/Euler_Capital_codes/EC_tools/data/history_data/Minute/QP.001",
    "QPc2": "/home/dexter/Euler_Capital_codes/EC_tools/data/history_data/Minute/QP_d01.001"}

@util.time_it
def merge_raw_data(filename_list, save_filename, sort_by = "Forecast Period"):
    A = read.concat_CSVtable(filename_list, sort_by= sort_by)
    A.to_csv(save_filename,index=False)
    print(A)
    return A

#merge_raw_data(list(APC_FILE_LOC.values()), 'APC_latest_all.csv')

#merge_raw_data(list(HISTORY_DAILY_FILE_LOC.values()), 
#               'history_daily_data_all.csv', sort_by="Date")

merge_raw_data(list(HISTORY_MINTUE_FILE_LOC.values()), 
               'history_minute_data_all.csv', sort_by="Date")