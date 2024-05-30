#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 31 02:54:13 2024

@author: dexter
"""

import EC_tools.position as P
from EC_tools.portfolio import Asset, Portfolio
import datetime as datetime

def test_PositionStatus()->None:
    Pos = P.PositionStatus
    
    assert Pos.PENDING.value =="Pending"
    assert Pos.OPEN.value =="Open"
    assert Pos.CLOSE.value =="Close"
    assert Pos.VOID.value =="Void"
    
def test_Position_input_valid()-> None:
    # Initilise portfolio
    P1 = Portfolio()
    
    # inputs
    USD = Asset('USD', 1000, 'dollars', 'Cash')
    A = Asset("CL24N", 50, 'contracts', 'future')
    
    # 
    PP = P.Position('1', USD, A, 0.05,portfolio=P1, 
                    start_time= datetime.datetime(2020,1,1))
    
    assert PP.give_obj == USD
    assert PP.get_obj == A
    assert PP.pos_id == '1'
    assert PP.price == 0.05
    assert PP.portfolio == P1
    assert PP.status == P.PositionStatus.PENDING
    assert PP.start_time == datetime.datetime(2020,1,1)
    assert PP.open_time == None   
    assert PP.close_time == None    
    assert PP.void_time == None
    assert PP._check == True
    
def test_Position_input_invalid()-> None:
    # Initilise portfolio
    P1 = Portfolio()
    
    # inputs
    USD = Asset('USD', 1000, 'dollars', 'Cash')
    A = Asset("CL24N", 50, 'contracts', 'future')
    
    # 
    PP = P.Position('1', USD, A, 2000, portfolio=P1, 
                    start_time = datetime.datetime(2020,1,1))
    
    PP.__post_init__(void_time = datetime.datetime(2020,1,2))
                    
    assert PP._check == False
    assert PP.status == P.PositionStatus.VOID
    assert PP.start_time == datetime.datetime(2020,1,1)   
    assert PP.void_time == datetime.datetime(2020,1,2)

