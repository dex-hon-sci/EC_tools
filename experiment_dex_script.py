#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 22 14:09:15 2024

@author: dexter
"""
import numpy as np
import utility as util
import pandas as pd
from scipy.interpolate import CubicSpline, UnivariateSpline
import matplotlib.pyplot as plt
import datetime as datetime
import EC_read as EC_read
import read as read


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
    
import portfolio as port
import time as time

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

@util.time_it
def simple_func(A):
    day1= datetime.datetime(2024,1,10)
    day2= datetime.datetime(2024,2,28)
    day3= datetime.datetime(2024,3,1)
    day4= datetime.datetime(2024,4,4)
    
    A.add(USD, datetime = day1)
    A.add(CL1, datetime = day1)
    A.add(CL2, datetime = day1)    

    A.add(CL3, datetime = day2)    
    A.add(HO1, datetime = day2)    
    A.add(QO1, datetime = day2)    

    A.add(CL4, datetime = day3)  
    A.add(CL5,datetime = day3)
    
    A.sub(CL6, datetime = day4)
    A.sub("CLc1", quantity = 11, unit='contracts', asset_type='Future',
          datetime = day4)
    return A1

# 4% of SPY weight, drive large portion of growth (FAANG)
# our own index with stock piles that has a certain quality

# =============================================================================
# def simple_func2(A):
#     A.add(USD.name, datetime = datetime.datetime.now())
#     A.add(CL1.name, datetime = datetime.datetime.now())
#     A.add(CL2.name, datetime = datetime.datetime.now())    
#     A.add(CL3.name, datetime = datetime.datetime.now())    
#     A.add(HO1.name, datetime = datetime.datetime.now())    
#     A.add(QO1.name, datetime = datetime.datetime.now())    
#     A.add(CL4.name, datetime = datetime.datetime.now())  
#     A.add(CL5.name, datetime = datetime.datetime.now())
#     return A
# =============================================================================
    
A1 = simple_func(A1)



start_day = datetime.datetime(2024,2,10)
end_day =  datetime.datetime(2024,3,10)

print(A1.get_pool_interest(start_day, end_day))

#A2 = simple_func2(A2)

#print(A1.table)

#print(A1.pool_df())
