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
        return t2, result, func.__name__
    return wrapper

def save_csv(savefilename, save_or_not = True):
    def decorator(func):
        def wrapper(*args, **kwargs):
            data = func(*args, **kwargs)
            if save_or_not:
                data.to_csv(savefilename, index=False)
                return data
            elif not save_or_not:
                return data
        return wrapper
    return decorator
         
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
        
def list_match(list1,list2):
    # A function to check if two list are identical
    if list1 == list2:
        pass
    else:
        # Find the exception
        bool_list = list( map(lambda x, y: x==y, list1, list2)) 
        
        mismatch_index = []
        for i in range(len(bool_list)):
            if bool_list[i] == False:         
                mismatch_index.append(i)
        
        raise Exception(
            "Mismatch at the following positions:{}".format(mismatch_index))

#tested
def convert_intmin_to_time(data, label='Time'):
    
    intmin = data[label]
    
    # bucket for storage.
    bucket = []
    #loop through each element
    for num in intmin:
        # if the integer time is less than 1000, then go through the string 
        # treatment
        if num < 1000:
            num = '0000'+str(num) # add the preceding zeroes as strings  
            #bucket.append(num[-4:-2]+':'+num[-2:])
            #bucket.append(num[-4:-2]+':'+num[-2:])
            hr_str, min_str = num[-4:-2], num[-2:]
        elif num >= 1000:
            num = str(num)
            #bucket.append(str(num)[-4:-2]+':'+str(num)[-2:])
            hr_str, min_str = num[-4:-2], num[-2:]

        time  = datetime.time(hour = int(hr_str), minute = int(min_str))
        bucket.append(time)
        
    data[label] = bucket
    
    return data

# Convert file from CSV to HDF5, npy? Npy might be faster, WIP
def convert_csv_to_npy(filename):
    # A function that turn big csv to npy file for faster read-time
    # This is meant to be run once only for each file
            
    #dat = pd.read_csv(filename)
    #dat['Forecast Period'] = pd.to_datetime(dat['Forecast Period']) # make columns datetime objects 
    dat = np.genfromtxt(filename, delimiter=",")
    print(dat[0:10])
    return dat
