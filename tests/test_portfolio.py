#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 28 02:08:35 2024

@author: dexter
"""

PRICE_TABLE = {"CLc1": "/home/dexter/Euler_Capital_codes/test_MS/data_zeroadjust_intradayportara_attempt1/Daily/CL.day",
               "CLc2": "/home/dexter/Euler_Capital_codes/test_MS/data_zeroadjust_intradayportara_attempt1/Daily/CL_d01.day",
               "HOc1": "/home/dexter/Euler_Capital_codes/test_MS/data_zeroadjust_intradayportara_attempt1/Daily/HO.day",
               "HOc2": "/home/dexter/Euler_Capital_codes/test_MS/data_zeroadjust_intradayportara_attempt1/Daily/HO_d01.day",
               "RBc1": "/home/dexter/Euler_Capital_codes/test_MS/data_zeroadjust_intradayportara_attempt1/Daily/RB.day",
               "RBc2": "/home/dexter/Euler_Capital_codes/test_MS/data_zeroadjust_intradayportara_attempt1/Daily/RB_d01.day",
               "QOc1": "/home/dexter/Euler_Capital_codes/test_MS/data_zeroadjust_intradayportara_attempt1/Daily/QO.day",
               "QOc2": "/home/dexter/Euler_Capital_codes/test_MS/data_zeroadjust_intradayportara_attempt1/Daily/QO_d01.day",
               "QPc1": "/home/dexter/Euler_Capital_codes/test_MS/data_zeroadjust_intradayportara_attempt1/Daily/QP.day",
               "QPc2": "/home/dexter/Euler_Capital_codes/test_MS/data_zeroadjust_intradayportara_attempt1/Daily/QP_d01.day"
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



import unittest
from werkzeug import exceptions
import datetime
import pandas as pd
import pytest

from EC_tools.portfolio import Asset, Portfolio
import EC_tools.utility as util

# Define the test inputs for assets
USD = {'name': 'USD', 'quantity': 1e7, 'unit':'dollars', 'asset_type':'Cash', 'misc':{}}
CL1 = {'name': "CLc1", 'quantity': 50, 'unit':'contracts', 'asset_type':'Future', 'misc':{}}
CL2 = {'name': "CLc2", 'quantity': 60, 'unit':'contracts', 'asset_type':'Future', 'misc':{}}
CL3 = {'name': 'CLc1', 'quantity': 10, 'unit':'contracts', 'asset_type':'Future', 'misc':{}}
HO1 = {'name': 'HOc1', 'quantity': 30, 'unit':'contracts', 'asset_type':'Future', 'misc':{}}
QO1 = {'name': 'QOc1', 'quantity': 20, 'unit':'contracts', 'asset_type':'Future', 'misc':{}}
CL4 = {'name': 'CLc1', 'quantity': 56, 'unit':'contracts', 'asset_type':'Future', 'misc':{}}
CL5 = {'name': 'CLc2', 'quantity': 36, 'unit':'contracts', 'asset_type':'Future', 'misc':{}}
CL6 = {'name': 'CLc1', 'quantity': 20, 'unit':'contracts', 'asset_type':'Future', 'misc':{}}


# Define the test inputs for datetime
day1= datetime.datetime(2024,1,10)
day2= datetime.datetime(2024,2,28)
day3= datetime.datetime(2024,3,1)
day4= datetime.datetime(2024,4,4)

def simple_fill_func(A):
    """
    A simple function that fills the portfolio.
    
    """
    # 
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
    #A.sub("CLc1", quantity = 11, unit='contracts', asset_type='Future',
    #      datetime = day4)
    return A


def test_Asset()->None:
    """
    Test asset inputs
    
    """
    A = Asset("test", 0, "test unit", "test type", 
                misc={"Comment":"This is a comment."})
    assert A.name == "test"
    assert A.quantity == 0
    assert A.unit == "test unit"
    assert A.asset_type == "test type"
    assert A.misc['Comment'] == "This is a comment."
    
def test_Portfolio_init()->None:
    PP = Portfolio()
    assert PP._Portfolio__pool_asset == [] 
    assert PP._Portfolio__pool_datetime == []
    assert PP._pool == []
    assert PP._pool_window == None
    assert PP._table == None
    assert PP._master_table == None
    assert PP._value == None
    assert PP._log == None

        
def test_Portfolio_entry() -> None:
    """
    Test Portfolio entry function.

    """
    PP = Portfolio()
    
    # fill the portfolio with existing assets
    PP = simple_fill_func(PP)
    asset_list = [USD, CL1, CL2, CL3, HO1, QO1, CL4, CL5, CL6]
    datetime_list = [day1, day1, day1, day2, day2, day2, day3, day3, day4]
    
    test_pool = list(zip(asset_list,  datetime_list))
    
    assert [PP.pool_asset[i] == asset_list[i] for i, item in enumerate(asset_list)]
    assert [PP.pool_datetime[i] == datetime_list[i] for i, item in enumerate(datetime_list)]
    assert [PP.pool[i] == test_pool[i] for i, item in enumerate(test_pool)]
    
def test_pool_df()->None:
    """
    Test if poo_df successfully create a data frame

    """
    PP = Portfolio()
    PP = simple_fill_func(PP)

    assert type(PP.pool_df) == pd.DataFrame
    # check the values in the dataframe
    
    
def test_pool_window() -> None:
    """
    Test the pool_window function to see if it isolate the correct entries.
    
    """
    PP = Portfolio()
    PP = simple_fill_func(PP)
    
    PP.set_pool_window(start_time=day2,end_time=day3)
    
    test_pool_window = [(day2,CL3), (day2,HO1),(day2,QO1), (day3,CL4), (day3,CL5)]
    assert [PP.pool_window[i] ==  test_pool_window[i] for i, item in enumerate(test_pool_window)]
    
    
def test_table() -> None:
    """
    Test the table function to see if it gets the correct value.
    """
    PP = Portfolio()
    PP = simple_fill_func(PP)
    
    PP.set_pool_window(start_time=day2,end_time=day3)
    
    #check asset name uniqueness
    assert len(set(PP.master_table['name'])) == len(PP.master_table['name'])
    assert len(set(PP.table['name'])) == len(PP.table['name'])
    
    #check the quantity of the assets for both table
    assert PP.master_table[PP.master_table['name']=='CLc1']['quantity'].iloc[0] == 96   
    assert PP.table[PP.table['name']=='CLc1']['quantity'].iloc[0] == 66


def test_add_str()-> None:
    """
    Test the add function with str input.
    
    """
    PP = Portfolio()
    PP.add('test',datetime=day1,quantity=10,unit='test unit', asset_type='test type')    
    
    assert PP.pool_asset[0]['name'] == 'test' 
    assert PP.pool_asset[0]['quantity'] == 10
    assert PP.pool_asset[0]['unit'] == 'test unit' 
    assert PP.pool_asset[0]['asset_type'] == 'test type' 
    
    
def test_sub_str()-> None:
    """
    Test the sub function with str input.
    
    """
    PP = Portfolio()
    PP.add('test',datetime=day1, 
           quantity=10,unit='test unit', asset_type='test type')    

    PP.sub('test', quantity=7)
    print(list(PP.pool[0]))
    assert PP.master_table[PP.master_table['name']=='test']['quantity'].iloc[0] == 3
test_sub_str() 
def test_value_asset_value_total_value()-> None:
    PP = Portfolio()
    PP.add(CL1,datetime=day1)
    PP.add(USD,datetime=day2)
    PP.add(HO1,datetime=day3)
    
    assert len(PP.value(day1)) == 1
    assert len(PP.value(day2)) == 2
    assert len(PP.value(day3)) == 3
    assert list(PP.value(day1).keys()) == ['CLc1']
    assert list(PP.value(day2).keys()) == ['CLc1', 'USD']
    assert list(PP.value(day3).keys()) == ['CLc1', 'USD', 'HOc1']
    
    # check asset value
    assert type(PP.asset_value('HOc1',day3)) == float
    assert type(PP.asset_value('CLc1',day3)) == float
    assert type(PP.asset_value('CLc1',day1)) == float
    assert type(PP.asset_value('USD',day2)) == float
    
    # check total value 
    assert PP.total_value(day1) < PP.total_value(day2) 
    assert PP.total_value(day2) < PP.total_value(day3)
    
def test_log_asset_log() -> None:
    PP = Portfolio()
    PP.add(CL1,datetime=day1)
    PP.add(USD,datetime=day2)
    PP.add(HO1,datetime=day3)
    print(PP.log)
    assert isinstance(PP.log, pd.DataFrame)
    assert len(PP.log) == 4
    assert isinstance(PP.asset_log('CLc1'), pd.Series)
    assert len(PP.asset_log('CLc1')) == 4

###################
# Error test
def test_table_invlaid()-> None:
    PP = Portfolio()

    with pytest.raises(Exception):
        PP.table 
        
# =============================================================================
#     
# class test_invalid(unittest.TestCase):
#     """
#     Test the invalid inputs and the Exception handling.
#     """
#     def test_table_invlaid(self) -> None:
#         PP = Portfolio()
#     
#         with self.assertRaises(Exception):
#             PP.table
#             
# =============================================================================
        