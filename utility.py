#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 28 22:46:34 2024

@author: dexter

"""
import time
import datetime
import numpy as np
def time_it(func):
    # simple timing function
    def wrapper(*args, **kwargs):
        t1 = time.time()
        result = func(*args, **kwargs)
        t2 = time.time()-t1
        print(f"{func.__name__} ran in {t2} seconds.")
        return result
    return wrapper

def save_csv(savefilename, save_or_not = True):
    def decorator(func):
        def wrapper(*args, **kwargs):
            data = func(*args, **kwargs)
            if save_or_not:
                return data.to_csv(savefilename, index=False)
            elif not save_or_not:
                return None
        return wrapper
    return decorator
         
@time_it
def date_matching(date1,date2):
    # A simple function that ensure the date from two data sources match
    if date1 == date2:
        pass
    else:
        raise Exception("Date not match. Date1:{}, Date2:{}".format(
            str(date1),str(date2)))
        
def date_matching_list(date_list1, date_list2):
    if len(date_list1) == len(date_list2):
        pass
    else:
        raise Exception("Date list missmatch dimenstion")
    for i in range(len(date_list1)):
        date_matching(date_list1[i], date_list2[i])
  
    
#check today and see if things are up to date.
def check_format():
    return None



# Convert file from CSV to HDF5, npy? Npy might be faster
def convert_csv_to_npy(filename):
    # A function that turn big csv to npy file for faster read-time
    # This is meant to be run once only for each file
            
    #dat = pd.read_csv(filename)
    #dat['Forecast Period'] = pd.to_datetime(dat['Forecast Period']) # make columns datetime objects 
    dat = np.genfromtxt(filename, delimiter=",")
    print(dat[0:10])
    return dat