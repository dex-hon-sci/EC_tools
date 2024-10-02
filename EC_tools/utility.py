#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 28 22:46:34 2024

@author: dexter

General utility functions

"""
import time
import datetime
import numpy as np
import random
import pickle

def random_string(length:int=16):
    """
    Generate a random x-digits alphanumerical string

    Parameters
    ----------
    length : int
        The number of digits.

    Returns
    -------
    Shortcode.

    """
    base = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    
    # Pick a random 6 digits string from base
    # The amount to 56,800,235,584 possibilities
    code = ''.join([random.choice(base) for i in range(length)])

    return code

def time_it(func):
    """
    Simple time it function. Use this in a decorator

    Parameters
    ----------
    func : TYPE
        DESCRIPTION.

    Returns
    -------
    TYPE
        DESCRIPTION.

    """
    # simple timing function
    def wrapper(*args, **kwargs):
        t1 = time.time()
        result = func(*args, **kwargs)
        t2 = time.time()-t1
        print(f"{func.__name__!r} ran in {t2:.4f} seconds.")
        return result
    
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
         
def pickle_save(savefilename, save_or_not = True):
    file = open(savefilename, 'wb')
    def decorator(func):
        def wrapper(*args, **kwargs):
            data = func(*args, **kwargs)
            if save_or_not:
                pickle.dump(data, file)
                return data
            elif not save_or_not:
                return data
        return wrapper
    return decorator
         
def load_pkl(filename): # test function
    output = open(filename, 'rb')
    my_pkl = pickle.load(output)
    print("File:{} is loaded.".format(filename))
    output.close()
    return my_pkl

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
        
def get_list_element_format(x):
    # a function that finid the type of each element, collapse it into a set, 
    # and return a list of datatype contains in the list/array
    type_x = [type(i) for i in x]
    fmt = list(set(type_x))
    return fmt

def get_list_element_str_len(x):
    len_x = [len(i) for i in x]
    return len_x


def list_to_datetime(x): # set the array of x axis to datetime format
# This function convert all x-axis objects to the format of datetime
    
    # If the input is interable
    if type(x) == list or type(x)== np.ndarray: #tested
        pass
    
    elif type(x) in [int, float, str, complex]: # tested
        # put the element in list so that it is iterable
        x = [x] 
        
    #Find out what format is the input
    fmt = get_list_element_format(x)[0]
    
    # If the datetime is already in datetime.datetime format, pass
    if fmt == datetime.datetime: # tested
        return x
    
    if fmt == str: # tested
        # make sure the string is in the military format
        if list(set(get_list_element_str_len(x)))[0]==4: 
            
            x = [datetime.time(hour = int(t[-4:-2]), 
                                    minute = int(t[-2:])) 
                       for t in x] 

    if fmt == int: #tested
        x = convert_intmin_to_time(x)
        
        # If the format is datetime.time
    if fmt == datetime.time:  #tested
        pass

    x = [datetime.datetime.combine(datetime.date.today(), t) for t in x]
    return x

#tested
def convert_intmin_to_time(intmin)->list:
    # A function that convert elements in the time column in a dataframe from 
    # 0330 to datetime.time(hour=3,minute=30)

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
  
    return bucket

# Convert file from CSV to HDF5, npy? Npy might be faster, WIP
def convert_csv_to_npy(filename):
    # A function that turn big csv to npy file for faster read-time
    # This is meant to be run once only for each file
            
    #dat = pd.read_csv(filename)
    #dat['Forecast Period'] = pd.to_datetime(dat['Forecast Period']) # make columns datetime objects 
    dat = np.genfromtxt(filename, delimiter=",")
    print(dat[0:10])
    return dat
