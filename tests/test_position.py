#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 31 02:54:13 2024

@author: dexter
"""
import datetime as datetime
import pytest

from EC_tools.position import PositionStatus, Position, ExecutePosition
from EC_tools.portfolio import Portfolio

def test_PositionStatus()->None:
    Pos = PositionStatus
    
    assert Pos.PENDING.value =="Pending"
    assert Pos.FILLED.value =="Filled"
    assert Pos.VOID.value =="Cancelled"
    
def test_Position_input_valid()-> None:
    # Initilise portfolio
    P1 = Portfolio()
    
    # inputs
    USD = {'name':'USD', 'quantity':1000, 'unit':'dollars', 'asset_type':'Cash', 'misc':{}}
    A = {'name':"CL24N", 'quantity':50,  'unit':'contracts', 'asset_type':'future', 'misc':{}}
    
    # 
    PP = Position( USD, A, 1000/50,portfolio=P1, 
                    open_time= datetime.datetime(2020,1,1))
    
    assert PP.give_obj == USD
    assert PP.get_obj == A
    assert PP._price == 20.0
    assert PP.portfolio == P1
    assert PP.status == PositionStatus.PENDING
    assert PP.open_time == datetime.datetime(2020,1,1)
    assert PP.fill_time == None   
    assert PP.void_time == None
    assert PP._check == True
    
    # optional asset control
    assert PP.size == 1
    assert PP.fee == None
    assert len(PP.pos_id) == 16
    
    #test price get method
    assert PP.price ==  PP._price

def test_Position_input_invalid()-> None:
    # Initilise portfolio
    P1 = Portfolio()
    
    # inputs
    USD = {'name':'USD', 'quantity':1000, 'unit':'dollars', 'asset_type':'Cash', 'misc':{}}
    A = {'name':"CL24N", 'quantity':50,  'unit':'contracts', 'asset_type':'future', 'misc':{}}
    
    # 
    PP = Position(USD, A, 2000, portfolio=P1, 
                    open_time = datetime.datetime(2020,1,1))
    
    PP.__post_init__(void_time = datetime.datetime(2020,1,2))
                    
    assert PP._check == False
    assert PP.status == PositionStatus.VOID
    assert PP.open_time == datetime.datetime(2020,1,1)   
    assert PP.void_time == datetime.datetime(2020,1,2)


def test_position_price_setter()-> None:
    P1 = Portfolio()
    USD = {'name':'USD', 'quantity':1000, 'unit':'dollars', 'asset_type':'Cash', 'misc':{}}
    A = {'name':"CL24N", 'quantity':50,  'unit':'contracts', 'asset_type':'future', 'misc':{}}
    
    P1.add(USD, datetime= datetime.datetime(2019,12,31))
    
    PP = Position(USD, A, USD['quantity']/ A['quantity'], portfolio=P1, 
                    open_time = datetime.datetime(2020,1,1))    
    PP.fix_quantity = USD['quantity']
    # set new price
    PP.price = 21
    
    print(PP.price, A['quantity'], USD['quantity'])
    assert PP.price == 21
    assert PP.get_obj['quantity'] == 1000/21
    assert A['quantity'] == 1000/21

def test_Execute_fill_pos()-> None:
    P1 = Portfolio()
    
    USD = {'name':'USD', 'quantity':1025, 'unit':'dollars', 'asset_type':'Cash', 'misc':{}}
    USD_exchange = {'name':'USD', 'quantity':1000, 'unit':'dollars', 'asset_type':'Cash', 'misc':{}}
    A = {'name':'CL24N', 'quantity':50, 'unit':'contracts', 'asset_type':'future', 'misc':{}}

    fee = {'name':'USD', 'quantity':24, 'unit':'dollars', 'asset_type':'Cash', 'misc':{}}
    
    USD_minus = {'name':'USD', 'quantity':-1000, 'unit':'dollars', 'asset_type':'Cash', 'misc':{}}
    fee_minus =   {'name':'USD', 'quantity':-24, 'unit':'dollars', 'asset_type':'Cash', 'misc':{}}
    
    
    P1.add(USD, datetime= datetime.datetime(2019,12,31))
    
    PP = Position(USD_exchange, A, 10.0, portfolio=P1, 
                    open_time = datetime.datetime(2020,1,1), size= 2, fee=fee)    
    print(PP.size, A['quantity'])
    print('beembeem',PP.portfolio.master_table[PP.portfolio.master_table['name']==PP.give_obj['name']]['quantity'].iloc[0])
    #new_state = ExecutePosition(PP).open_pos(open_time = datetime.datetime(2020,1,3))
    
    print(PP.status, PP.open_time)
    print('pool_asset',P1.pool_asset)

    # Test if the position can be turned open
    assert PP.status ==  PositionStatus.PENDING
    assert PP.open_time == datetime.datetime(2020,1,1)
    
    ExecutePosition(PP).fill_pos(fill_time = datetime.datetime(2020,1,4))
    print(PP.status)
    print('pool_asset', P1.pool_asset)
    
    assert PP.status == PositionStatus.FILLED
    assert PP.fill_time == datetime.datetime(2020,1,4)
    assert A in [item for item in P1.pool_asset]
    assert USD in [item for item in P1.pool_asset]
    assert USD_minus in [item for item in P1.pool_asset]
    assert fee_minus in [item for item in P1.pool_asset]



def test_Execute_cancel_pos()->None:
    P1 = Portfolio()
    USD = {'name':'USD', 'quantity':1000, 'unit':'dollars', 'asset_type':'Cash', 'misc':{}}
    A = {'name':"CL24N", 'quantity':50,  'unit':'contracts', 'asset_type':'future', 'misc':{}}
    
    P1.add(USD, datetime= datetime.datetime(2019,12,31))
    
    PP = Position(USD, A,  USD['quantity']/ A['quantity'], portfolio=P1, 
                    open_time = datetime.datetime(2020,1,1))   
    
    print(PP.status)
    
    ExecutePosition(PP).cancel_pos(void_time= datetime.datetime(2020,1,3))
    
    assert PP.status == PositionStatus.VOID
    assert PP.void_time == datetime.datetime(2020,1,3)

#########Error tests###############################



def test_ErrorMsg_auto_adjust_off_invalid_price():
    P1 = Portfolio()
    USD = {'name':'USD', 'quantity':1000, 'unit':'dollars', 'asset_type':'Cash', 'misc':{}}
    A = {'name':"CL24N", 'quantity':50,  'unit':'contracts', 'asset_type':'future', 'misc':{}}
    P1.add(USD, datetime= datetime.datetime(2019,12,31))
    PP = Position(USD, A, USD['quantity']/ A['quantity'], 
                      portfolio=P1, open_time = datetime.datetime(2020,1,1),
                      auto_adjust=False)
    
    with pytest.raises(Exception):
        PP.price = 21
    
def test_ErrorMsg_invalid_portfolio()->None:
    P1 = None # An invalid Portfolio
    
    USD = {'name':'USD', 'quantity':1000, 'unit':'dollars', 'asset_type':'Cash', 'misc':{}}
    A = {'name':"CL24N", 'quantity':50,  'unit':'contracts', 'asset_type':'future', 'misc':{}}
    PP = Position(USD, A, USD['quantity']/ A['quantity'], 
                      portfolio=P1, open_time = datetime.datetime(2020,1,1))
    
    # A Position can belong to no Portfolio but it cannot be executed.
    with pytest.raises(Exception):
        ExecutePosition(PP)
        
#test_ErrorMsg_invalid_portfolio()
def test_ErrorMsg_insufficient_asset_fill_pos() -> None:
    # Test for insufficient fund
    P1 = Portfolio()
    USD = {'name':'USD','quantity': 2, 'unit':'dollars', 'asset_type':'Cash', 'misc':{}}
    A = {'name':"CL24N", 'quantity':50,  'unit':'contracts', 'asset_type':'future', 'misc':{}}
    USD_trade = {'name':'USD', 'quantity':1000, 'unit':'dollars', 'asset_type':'Cash', 'misc':{}}

    P1.add(USD, datetime= datetime.datetime(2019,12,31))
    
    PP = Position(USD_trade, A, USD_trade['quantity']/ A['quantity'], 
                  portfolio=P1, open_time = datetime.datetime(2020,1,1))        

    with pytest.raises(Exception):
        ExecutePosition(PP).fill_pos()
                
        
def test_ErrorMsg_fill_pos_error_msg()-> None:
    P1 = Portfolio()
    USD = {'name':'USD', 'quantity':1000, 'unit':'dollars', 'asset_type':'Cash', 'misc':{}}
    A = {'name':"CL24N", 'quantity':50,  'unit':'contracts', 'asset_type':'future', 'misc':{}}

    P1.add(USD, datetime= datetime.datetime(2019,12,31))
    
    # make an invalid position so that it is automatically cancelled
    PP = Position(USD, A, 1.0, portfolio=P1, 
                    open_time = datetime.datetime(2020,1,1), size= 2)    

    with pytest.raises(Exception):
        ExecutePosition(PP).fill_pos()

        
def test_ErrorMsg_close_pos_invalid_position() -> None:
    # Test for invalid input of Poistion
    P1 = Portfolio()
    #USD = Asset('USD', 1025, 'dollars', 'Cash')
    USD = {'name':'USD', 'quantity':1025, 'unit':'dollars', 'asset_type':'Cash', 'misc':{}}
    P1.add(USD, datetime= datetime.datetime(2019,12,31))

    USD_exchange = {'name':'USD', 'quantity':1000, 'unit':'dollars', 'asset_type':'Cash', 'misc':{}}
    A = {'name':"CL24N", 'quantity':50,  'unit':'contracts', 'asset_type':'future', 'misc':{}}
    fee = {'name':"USD", 'quantity':24,  'unit':'dollars', 'asset_type':'Cash', 'misc':{}}
    
    PP = Position(USD_exchange, A, 10.0, portfolio=P1, 
                    open_time = datetime.datetime(2020,1,1), size= 2, fee=fee)    
    
    #Execute a valid position so that it is in a filled state 
    ExecutePosition(PP).fill_pos()
    
    with pytest.raises(Exception):
        ExecutePosition(PP).cancel_pos()
        

