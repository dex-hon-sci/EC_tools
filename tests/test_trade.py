#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 29 16:50:39 2024

@author: dexter
"""

# make a Portfolio

from EC_tools.portfolio import Asset, Portfolio
from EC_tools.position import Position, ExecutePosition
import datetime as datetime

P1 = Portfolio()

USD = Asset('USD', 1e7, 'dollars', 'Cash')
CL1 = Asset("CLc1", 50, 'contracts', 'Future')
CL2 = Asset("CLc2", 60, 'contracts', 'Future')
CL3 = Asset('CLc1', 10, 'contracts', 'Future')
HO1 = Asset('HOc1', 30, 'contracts', 'Future')
QO1 = Asset('QOc1', 20, 'contracts', 'Future')
CL4 = Asset('CLc1', 56, 'contracts', 'Future')
CL5 = Asset('CLc2', 36, 'contracts', 'Future')
CL6 = Asset('CLc1',20,'contracts', 'Future')

day1= datetime.datetime(2024,1,10)
day2= datetime.datetime(2024,2,28)
day3= datetime.datetime(2024,3,1)
day4= datetime.datetime(2024,4,4)

def add_asset_to_portfolio(A):
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

#P1 = add_asset_to_portfolio(P1)
A = Asset("CL24N", 50, 'contracts', 'future')
PP = Position('1', USD, A, 0.05, datetime.datetime.now(),portfolio=P1)

print(PP.status)
print(ExecutePosition(PP).open_pos().status)
