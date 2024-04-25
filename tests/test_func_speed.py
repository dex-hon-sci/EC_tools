#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 26 01:50:26 2024

@author: dexter
"""
from random import shuffle

func_list = [locals()[key] for key in locals().keys()
             if callable(locals()[key]) and key.startswith('time')]
shuffle(func_list)  # Shuffle, just in case the order matters

alist = range(1000000)
times = []
for f in func_list:
    times.append(f(alist, 31))

times.sort(key=lambda x: x[0])
for (time, result, func_name) in times:
    print('%s took %0.3fms.' % (func_name, time * 1000.))