#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 28 14:51:19 2025

@author: dexter
"""

import asyncio

async def run_backtest(n):
    for i in range(n):
        i +=1
    return i

async def main():
    
    task1 = run_backtest(6)
    task2 = run_backtest(12)
    
    result1 = await task1
    result2 = await task2
    
    return