#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 15 02:31:06 2024

@author: dexter
"""
import openpyxl
from run_gen_MR_dir import *

# raw input file list
APC_FILE_LOC = {
    "CLc1": "/home/dexter/Euler_Capital_codes/EC_tools/data/APC_latest/APC_latest_CLc1.csv",
    "CLc2": "/home/dexter/Euler_Capital_codes/EC_tools/data/APC_latest/APC_latest_CLc2.csv",
    "HOc1": "/home/dexter/Euler_Capital_codes/EC_tools/data/APC_latest/APC_latest_CLc1.csv",
    "HOc2": "/home/dexter/Euler_Capital_codes/EC_tools/data/APC_latest/APC_latest_CLc2.csv",
    "RBc1": "/home/dexter/Euler_Capital_codes/EC_tools/data/APC_latest/APC_latest_CLc1.csv",
    "RBc2": "/home/dexter/Euler_Capital_codes/EC_tools/data/APC_latest/APC_latest_CLc2.csv",
    "QOc1": "/home/dexter/Euler_Capital_codes/EC_tools/data/APC_latest/APC_latest_CLc1.csv",
    "QOc2": "/home/dexter/Euler_Capital_codes/EC_tools/data/APC_latest/APC_latest_CLc2.csv",
    "QPc1": "/home/dexter/Euler_Capital_codes/EC_tools/data/APC_latest/APC_latest_CLc1.csv",
    "QPc2": "/home/dexter/Euler_Capital_codes/EC_tools/data/APC_latest/APC_latest_CLc2.csv"
    }

HISTORY_DAILY_FILE_LOC = {
    "CLc1": "/home/dexter/Euler_Capital_codes/EC_tools/data/APC_latest/APC_latest_CLc1.csv",
}

HISTORY_MINTUE_FILE_LOC = {
    "CLc1": "/home/dexter/Euler_Capital_codes/EC_tools/data/APC_latest/APC_latest_CLc1.csv",
    }

XL_TEMPLATE_FILENAME = "/home/dexter/Euler_Capital_codes/EC_tools/template/Leigh1.xlsx"

# mapping for symbols for contract expiry months to months 
symbols_to_months = {
   'F': '1',
   'G': '2',
   'H': '3',
   'J': '4',
   'K': '5',
   'M': '6',
   'N': '7',
   'Q': '8',
   'U': '9',
   'V': '10',
   'X': '11',
   'Z': '12',
}

months_to_symbols = {
   '1': 'F',
   '2': 'G',
   '3': 'H',
   '4': 'J',
   '5': 'K',
   '6': 'M',
   '7': 'N',
   '8': 'Q',
   '9': 'U',
   '10': 'V',
   '11': 'X',
   '12': 'Z'
}


# Check if this is the latest data. If not, download the latest data

# Input the latest settlement data 

# Use strategy module to determine the direction and EES
#run_gen_MR_signals(auth_pack, asset_pack, start_date, 
#                   start_date_2, end_date, signal_filename, 
#                   filename_daily, filename_minute)

# Modify the excel file
wb_obj = openpyxl.load_workbook(XL_TEMPLATE_FILENAME)

sheet_obj = wb_obj.active
max_col = sheet_obj.max_column


def enter_new_value():
    return

print(wb_obj)
print(sheet_obj, max_col)

print(sheet_obj['A5'].value, sheet_obj['G7'].value, sheet_obj['I7'].value)

sheet_obj['I7'].value = 50

print(sheet_obj['I7'].value)

# email this to the trader??

# Save all the newest value and contract in the xlsx template
