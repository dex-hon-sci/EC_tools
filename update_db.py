#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 24 23:27:00 2024

@author: dexter

This script updates the daily(weekly) data of apc and data with a timer.
It pulls data from external servers to the local directory.

"""
import datetime as datetime

import EC_read as EC_read
import utility as util

__author__="Dexter S.-H. Hon"


auth_pack = {'username': "dexter@eulercapital.com.au",
            'password':"76tileArg56!"}

date_pack = {"start_date": "2021-01-01",
        "end_date": "2024-04-25"}

asset_pack = {'categories': 'Argus Nymex WTI month 1, Daily',
              'keywords': "WTI",
              'symbol': "CL"}

# checking function to see if the table is up to date

@util.time_it
@util.save_csv("APC_latest_CL.csv")
def download_latest_APC():
    # input is a dictionary or json file
    
    # run meanreversion signal generation on the basis of individual programme  
    # Loop the whole list in one go with all the contracts or Loop it one contract at a time?
    
    #inputs: Portara data (1 Minute and Daily), APC
    
    username = "dexter@eulercapital.com.au"
    password = "76tileArg56!"
    
    filename_daily = "../test_MS/data_zeroadjust_intradayportara_attempt1/Daily/CL.day"
    filename_minute = "../test_MS/data_zeroadjust_intradayportara_attempt1/intraday/1 Minute/CL.001"

    start_date = "2021-01-01"
    #start_date_2 = "2024-01-01"
    end_date = "2024-04-25"
    categories = 'Argus Nymex WTI month 1, Daily'
    keywords = "WTI"
    symbol = "CL"
    
    # load the table in memory and test multple strategies
    # input APC file
    # download the relevant APC data from the server
    signal_data = EC_read.get_apc_from_server(username, password, start_date, 
                                      end_date, categories,
                            keywords=keywords,symbol=symbol)
    
    return signal_data

def download_latest_Portara():
    # a function to download the newest Portara data
    return None

def download_latest_APC_list():
    
    # input username and password.json
    # start_date and end_date.json
    
    file_list = []
    categories = []
    keywords = []
    symbol = []
    
    for i in file_list:  
        @util.save_csv("{}".format(file_list))
        def download_latest_APC_indi():
            signal_data = download_latest_APC()
            return signal_data
    
    return None

if __name__ == "__main__": 
    download_latest_APC()
    
