#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 28 02:08:35 2024

@author: dexter
"""

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

import portfolio as port
import time as time
import datetime
import utility as util

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
end_day =  datetime.datetime(2024,3,8)

A1_newpool = A1.set_pool_window(day1, end_day)

print('A1_newpool', A1_newpool)
print('====================================')

print(A1.value(end_day, PRICE_TABLE, size_dict = num_per_contract))
print('====================================')

#print(A1.log)

#values = [list(A2[i][1].__dict__.values()) for i in range(len(A2))]
#keys = [list(A2[i][1].__dict__.keys()) for i in range(len(A2))][0]
#print(values, keys)


#A2 = simple_func2(A2)

#print(A1.table)

#print(A1.pool_df())
