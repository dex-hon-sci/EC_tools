#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 31 02:54:13 2024

@author: dexter
"""
import datetime as datetime
import unittest

from EC_tools.position import PositionStatus, Position, ExecutePosition
from EC_tools.portfolio import Asset, Portfolio

def test_PositionStatus()->None:
    Pos = PositionStatus
    
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
    PP = Position('1', USD, A, 0.05,portfolio=P1, 
                    start_time= datetime.datetime(2020,1,1))
    
    assert PP.give_obj == USD
    assert PP.get_obj == A
    assert PP.pos_id == '1'
    assert PP.price == 0.05
    assert PP.portfolio == P1
    assert PP.status == PositionStatus.PENDING
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
    PP = Position('1', USD, A, 2000, portfolio=P1, 
                    start_time = datetime.datetime(2020,1,1))
    
    PP.__post_init__(void_time = datetime.datetime(2020,1,2))
                    
    assert PP._check == False
    assert PP.status == PositionStatus.VOID
    assert PP.start_time == datetime.datetime(2020,1,1)   
    assert PP.void_time == datetime.datetime(2020,1,2)


def test_Execute_open_close_pos()-> None:
    P1 = Portfolio()
    USD = Asset('USD', 1000, 'dollars', 'Cash')
    A = Asset("CL24N", 50, 'contracts', 'future')
    USD_minus = Asset('USD', -1000, 'dollars', 'Cash')
    
    P1.add(USD, datetime= datetime.datetime(2019,12,31))
    
    PP = Position('1', USD, A, A.quantity/ USD.quantity, portfolio=P1, 
                    start_time = datetime.datetime(2020,1,1))    
    
    print('beembeem',PP.portfolio.master_table[PP.portfolio.master_table['name']==PP.give_obj.name]['quantity'].iloc[0])
    new_state = ExecutePosition(PP).open_pos(open_time = datetime.datetime(2020,1,3))
    
    
    print(PP.status, PP.open_time)
    print('pool_asset',P1.pool_asset)

    # Test if the position can be turned open
    assert PP.status ==  PositionStatus.OPEN
    assert PP.open_time == datetime.datetime(2020,1,3)
    
    close_state = ExecutePosition(PP).close_pos(close_time = 
                                                datetime.datetime(2020,1,4))
    print(PP.status)
    print('pool_asset', P1.pool_asset)
    assert PP.status == PositionStatus.CLOSE
    assert A.__dict__ in [item.__dict__ for item in P1.pool_asset]
    assert USD.__dict__ in [item.__dict__ for item in P1.pool_asset]
    assert USD_minus.__dict__ in [item.__dict__ for item in P1.pool_asset]
    
class test_ErrorMsg(unittest.TestCase):
    
    def test_insufficient_asset_open_pos(self) -> None:
        P1 = Portfolio()
        USD = Asset('USD', 10, 'dollars', 'Cash')
        A = Asset("CL24N", 50, 'contracts', 'future')

        P1.add(USD, datetime= datetime.datetime(2019,12,31))
        
        PP = Position('1', USD, A, A.quantity/ USD.quantity, portfolio=P1, 
                    start_time = datetime.datetime(2020,1,1))        

        with self.assertRaises(Exception):
            ExecutePosition(PP).open_pos()
            
test_Execute_open_close_pos()

