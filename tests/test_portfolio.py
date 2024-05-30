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

import EC_tools.portfolio as P
import EC_tools.utility as util

import datetime

# Define the test inputs for assets
USD = P.Asset('USD', 1e7, 'dollars', 'Cash')
CL1 = P.Asset("CLc1", 50, 'contracts', 'Future')
CL2 = P.Asset("CLc2", 60, 'contracts', 'Future')
CL3 = P.Asset('CLc1', 10, 'contracts', 'Future')
HO1 = P.Asset('HOc1', 30, 'contracts', 'Future')
QO1 = P.Asset('QOc1', 20, 'contracts', 'Future')
CL4 = P.Asset('CLc1', 56, 'contracts', 'Future')
CL5 = P.Asset('CLc2', 36, 'contracts', 'Future')

CL6 = P.Asset('CLc1',20,'contracts', 'Future')

# Define the test inputs for datetime
day1= datetime.datetime(2024,1,10)
day2= datetime.datetime(2024,2,28)
day3= datetime.datetime(2024,3,1)
day4= datetime.datetime(2024,4,4)

def simple_fill_func(A):
    # a simple function that fills the portfolio
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


def test_Asset()->None:
    A = P.Asset("test", 0, "test unit", "test type", misc={"Comment":"This is a comment."})
    assert A.name == "test"
    assert A.quantity == 0
    assert A.unit == "test unit"
    assert A.asset_type == "test type"
    assert A.misc['Comment'] == "This is a comment."
    
def test_Portfolio_init()->None:
    PP = P.Portfolio()
    assert None
    assert PP.__pool_asset == [] 
    assert PP.__pool_datetime == []
    assert PP._pool == []
    assert PP._pool_window == None
    assert PP._table == None
    assert PP._master_table == None
    assert PP._value == None
    assert PP._log == None
        
def test_Portfolio_entry() -> None:
    assert None
    

