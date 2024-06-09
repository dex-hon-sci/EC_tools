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
    assert Pos.FILLED.value =="Filled"
    assert Pos.VOID.value =="Cancelled"
    
def test_Position_input_valid()-> None:
    # Initilise portfolio
    P1 = Portfolio()
    
    # inputs
    USD = Asset('USD', 1000, 'dollars', 'Cash')
    A = Asset("CL24N", 50, 'contracts', 'future')
    
    # 
    PP = Position( USD, A, 0.05,portfolio=P1, 
                    open_time= datetime.datetime(2020,1,1))
    
    assert PP.give_obj == USD
    assert PP.get_obj == A
    assert PP.pos_id == '1'
    assert PP._price == 0.05
    assert PP.portfolio == P1
    assert PP.status == PositionStatus.PENDING
    assert PP.open_time == datetime.datetime(2020,1,1)
    assert PP.fill_time == None   
    assert PP.void_time == None
    assert PP._check == True
    
    # optional asset control
    assert PP.size == 1
    assert PP.fee == None
    assert len(PP.pos_id) == 12
    
    #test price get method
    assert PP.price ==  PP._price

def test_Position_input_invalid()-> None:
    # Initilise portfolio
    P1 = Portfolio()
    
    # inputs
    USD = Asset('USD', 1000, 'dollars', 'Cash')
    A = Asset("CL24N", 50, 'contracts', 'future')
    
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
    USD = Asset('USD', 1000, 'dollars', 'Cash')
    A = Asset("CL24N", 50, 'contracts', 'future')
    
    P1.add(USD, datetime= datetime.datetime(2019,12,31))
    
    PP = Position(USD, A, USD.quantity/ A.quantity, portfolio=P1, 
                    open_time = datetime.datetime(2020,1,1))    
    # set new price
    PP.price == 21
    
    
    assert PP.price == 21
    assert PP.get_obj.quantity == 1000/21
    assert A.quantity == 1000/21

def test_Execute_fill_pos()-> None:
    P1 = Portfolio()
    USD = Asset('USD', 1025, 'dollars', 'Cash')
    USD_exchange = Asset('USD', 1000, 'dollars', 'Cash')
    A = Asset("CL24N", 50, 'contracts', 'future')
    fee = Asset('USD', 24, 'dollars', 'Cash')
    
    USD_minus = Asset('USD', -1000, 'dollars', 'Cash')
    fee_minus =  Asset('USD', -24, 'dollars', 'Cash')
    
    
    P1.add(USD, datetime= datetime.datetime(2019,12,31))
    
    PP = Position(USD_exchange, A, 10.0, portfolio=P1, 
                    open_time = datetime.datetime(2020,1,1), size= 2, fee=fee)    
    print(PP.size, A.quantity)
    print('beembeem',PP.portfolio.master_table[PP.portfolio.master_table['name']==PP.give_obj.name]['quantity'].iloc[0])
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
    assert A.__dict__ in [item.__dict__ for item in P1.pool_asset]
    assert USD.__dict__ in [item.__dict__ for item in P1.pool_asset]
    assert USD_minus.__dict__ in [item.__dict__ for item in P1.pool_asset]
    assert fee_minus.__dict__ in [item.__dict__ for item in P1.pool_asset]



def test_Execute_cancel_pos()->None:
    P1 = Portfolio()
    USD = Asset('USD', 1000, 'dollars', 'Cash')
    A = Asset("CL24N", 50, 'contracts', 'future')
    
    P1.add(USD, datetime= datetime.datetime(2019,12,31))
    
    PP = Position(USD, A, A.quantity/ USD.quantity, portfolio=P1, 
                    open_time = datetime.datetime(2020,1,1))   
    
    ExecutePosition(PP).cancel_pos(void_time= datetime.datetime(2020,1,3))
    
    assert PP.status == PositionStatus.VOID
    assert PP.void_time == datetime.datetime(2020,1,3)

    
class test_ErrorMsg(unittest.TestCase):
    
    def test_insufficient_asset_open_pos(self) -> None:
        P1 = Portfolio()
        USD = Asset('USD', 10, 'dollars', 'Cash')
        A = Asset("CL24N", 50, 'contracts', 'future')

        P1.add(USD, datetime= datetime.datetime(2019,12,31))
        
        PP = Position(USD, A, A.quantity/ USD.quantity, portfolio=P1, 
                    open_time = datetime.datetime(2020,1,1))        

        with self.assertRaises(Exception):
            ExecutePosition(PP).fill_pos()
            

