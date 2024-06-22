#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 22 14:09:15 2024

@author: dexter
"""
# =============================================================================
# import numpy as np
# import utility as util
# import pandas as pd
# from scipy.interpolate import CubicSpline, UnivariateSpline
# import matplotlib.pyplot as plt
# import datetime as datetime
# =============================================================================

import numpy as np
import datetime as datetime
import pandas as pd
from scipy.interpolate import CubicSpline, UnivariateSpline
import matplotlib.pyplot as plt
import time as time


import EC_tools.read as read
import EC_tools.utility as util
import EC_tools.portfolio as port


username = "dexter@eulercapital.com.au"
password = "76tileArg56!"
start_date = "2021-01-01"
end_date = "2021-03-31"
categories = 'Argus Brent month 1, Daily'
keywords = "Brent"
symbol = "QOc1"
filename_daily = "../test_MS/data_zeroadjust_intradayportara_attempt1/Daily/CL.day"
filename_minute = "../test_MS/data_zeroadjust_intradayportara_attempt1/intraday/1 Minute/CL.001"

# =============================================================================
# 
# ## test one case (check)
# ## test multiple list (check)
# curve = EC_read.get_apc_from_server(username, password, "2024-03-01", "2024-03-05", categories,
#                         keywords=keywords,symbol=symbol)
# 
# print(curve)
# 
# quantiles_forwantedprices = [0.1, 0.4, 0.5, 0.6, 0.9]
# 
# from ArgusPossibilityCurves2 import ArgusPossibilityCurves
# 
# apc = ArgusPossibilityCurves(username=username, password=password)
# apc.authenticate()
# apc.getMetadataCSV(filepath="argus_latest_meta.csv")
# 
# 
# # Make the start and end date in the datetime.date format
# start_date = datetime.date(int(start_date[:4]), int(start_date[5:7]), int(start_date[8:10]))
# end_date = datetime.date(int(end_date[:4]), int(end_date[5:7]), int(end_date[8:10]))
# 
# apc_data = apc.getPossibilityCurves(start_date=start_date, end_date=end_date, categories=[categories])
# 
# 
# 
# print(apc_data)
# =============================================================================
    
PRICE_TABLE = {"CLc1": "../test_MS/data_zeroadjust_intradayportara_attempt1/Daily/CL.day",
               "CLc2": "../test_MS/data_zeroadjust_intradayportara_attempt1/Daily/CL_d01.day",
               "HOc1": "../test_MS/data_zeroadjust_intradayportara_attempt1/Daily/HO.day",
               "HOc2": "../test_MS/data_zeroadjust_intradayportara_attempt1/Daily/HO_d01.day",
               "RBc1": "../test_MS/data_zeroadjust_intradayportara_attempt1/Daily/RB.day",
               "RBc2": "../test_MS/data_zeroadjust_intradayportara_attempt1/Daily/RB_d01.day",
               "QOc1": "../test_MS/data_zeroadjust_intradayportara_attempt1/Daily/QO.day",
               "QOc2": "../test_MS/data_zeroadjust_intradayportara_attempt1/Daily/QO_d01.day",
               "QPc1": "../test_MS/data_zeroadjust_intradayportara_attempt1/Daily/QP.day",
               "QPc2": "../test_MS/data_zeroadjust_intradayportara_attempt1/Daily/QP_d01.day"
               }

num_per_contract = {
    'CLc1': 1000.0,
    'CLc2': 1000.0,
    'HOc1': 42000.0,
    'HOc2': 42000.0,
    'RBc1': 42000.0,
    'RBc2': 42000.0,
    'QOc1': 1000.0,
    'QOc2': 1000.0,
    'QPc1': 100.0,
    'QPc2': 100.0,
}

round_turn_fees = {
'CLc1': 24.0,
'CLc2': 24.0,
'HOc1': 25.2,
'HOc2': 25.2,
'RBc1': 25.2,
'RBc2': 25.2,
'QOc1': 24.0,
'QOc2': 24.0,
'QPc1': 24.0,
'QPc2': 24.0,
}



USD = port.Asset('USD', 1e7, 'dollars', 'Cash')
CL1 = port.Asset("CLc1", 50, 'contracts', 'Future')
CL2 = port.Asset("CLc2", 60, 'contracts', 'Future')
CL3 = port.Asset('CLc1', 10, 'contracts', 'Future')
HO1 = port.Asset('HOc1', 30, 'contracts', 'Future')
QO1 = port.Asset('QOc1', 20, 'contracts', 'Future')
CL4 = port.Asset('CLc1', 56, 'contracts', 'Future')
CL5 = port.Asset('CLc2', 36, 'contracts', 'Future')

CL6 = port.Asset('CLc1',20,'contracts', 'Future')

A1 = port.Portfolio()
#A2 = port.Portfolio()

day1= datetime.datetime(2024,1,10)
day2= datetime.datetime(2024,2,28)
day3= datetime.datetime(2024,3,1)
day4= datetime.datetime(2024,4,4)

@util.time_it
def simple_func(A):
    A.add(USD, datetime = day1)
    A.add(CL1, datetime = day1)
    A.add(CL2, datetime = day1)    

    A.add(CL3, datetime = day2)    
    A.add(HO1, datetime = day2)    
    A.add(QO1, datetime = day2)    

    A.add(CL4, datetime = day3)  
    A.add(CL5,datetime = day3)
    
    print('pool_window', A.pool_window)
    print(A.table)
    A.sub(CL6, datetime = day4)
    A.sub("CLc1", quantity = 11, unit='contracts', asset_type='Future',
          datetime = day4)
    return A

# 4% of SPY weight, drive large portion of growth (FAANG)
# our own index with stock piles that has a certain quality
    
# =============================================================================
# A1 = simple_func(A1)
# 
# start_day = datetime.datetime(2024,2,10)
# end_day =  datetime.datetime(2024,3,8)
# 
# A1_newpool = A1.set_pool_window(day1, end_day)
# 
# print('A1_newpool', A1_newpool)
# print('====================================')
# 
# print(A1.value(end_day, PRICE_TABLE, size_dict = num_per_contract))
# print('====================================')
# 
# =============================================================================

import sqlite3

con = sqlite3.connect("tutorial.db")
cur = con.cursor()

print(con,cur)