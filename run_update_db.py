#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 24 23:27:00 2024

@author: dexter

This script updates the daily(weekly) data of apc and data with a timer.
It pulls data from external servers to the local directory.

"""
import datetime as datetime
import pandas as pd

import EC_tools.read as read
import EC_tools.utility as util
from crudeoil_future_const import APC_FILE_LOC, CAT_LIST, KEYWORDS_LIST, SYMBOL_LIST
__author__="Dexter S.-H. Hon"

# =============================================================================
# auth_pack = {'username': "dexter@eulercapital.com.au",
#             'password':"76tileArg56!"}
# =============================================================================

AUTH_PACK = {'username': "leigh@eulercapital.com.au",
            'password':"Li.96558356"}

DATE_PACK = {"start_date": "2021-01-01",
        "end_date": "2024-06-18"}

# =============================================================================
ASSET_PACK = {'categories': 'Argus Nymex WTI month 1, Daily',
               'keywords': "WTI",
               'symbol': "CL"}
# =============================================================================
categories_monthly_30avg_list = [ 'Argus Nymex WTI front month average 30-day interval, Weekly',
                           'Nymex Heating oil front month average 30-day interval, Weekly',
                           'Nymex RBOB gasoline front month average 30-day interval, Weekly',
                           'Argus Brent front month average 30-day interval, Weekly',
                           'ICE gasoil front month average 30-day interval, Weekly']

categories_monthly_list = [  'Argus Nymex WTI front month average, Monthly',
                                 'Nymex Heating oil front month average, Monthly',
                                 'Nymex RBOB gasoline front month average, Monthly',
                                 'Argus Brent front month average, Monthly',
                                 'ICE gasoil front month average, Monthly']

# checking function to see if the table is up to date


def download_latest_APC(auth_pack: dict, asset_pack: dict, 
                        start_date: str = "2021-01-01") -> pd.DataFrame:
    # input is a dictionary or json file
    username = auth_pack['username']
    password = auth_pack['password']
    
    categories = asset_pack['categories']
    keywords = asset_pack['keywords']
    symbol = asset_pack['symbol']
    end_date = datetime.date.today().strftime("%Y-%m-%d")
    
    # download the relevant APC data from the server
    signal_data = read.get_apc_from_server(username, password, start_date, 
                                      end_date, categories,
                            keywords=keywords, symbol=symbol)
    return signal_data

def download_latest_APC_fast(auth_pack, asset_pack, old_filename): #tested
    # Check the last entry in the old file and only download the data 
    # Read the old files
    old_data = pd.read_csv(old_filename)
    
    #Find the date of the latest entry
    latest_entry = str(old_data['Forecast Period'].iloc[-1])
    
    
    # download the latest APC from the latest_entry till today
    temp = download_latest_APC(auth_pack, asset_pack, start_date = latest_entry)
    
    # for some reason I have to turn the Forecast column elements to str first 
    # to align them with the old data
    temp['Forecast Period'] = [temp['Forecast Period'].iloc[i].\
                                      strftime("%Y-%m-%d") for 
                                i, _ in enumerate(temp['Forecast Period'])]
    
    # concandenate the old file
    signal_data = pd.concat([old_data, temp], ignore_index = True)
    signal_data.sort_values(by='Forecast Period')
    
    return signal_data

@util.time_it
def download_latest_APC_list(auth_pack, save_filename_list, categories_list, 
                         keywords_list, symbol_list, fast_dl=True):
    # a function to download the APC of a list of asset
    # input username and password.json

    for filename, cat, key, sym in zip(save_filename_list, categories_list, 
                                       keywords_list, symbol_list):
        @util.save_csv("{}".format(filename))
        def download_latest_APC_indi(cat, key, sym):
            asset_pack = {'categories': cat, 'keywords': key, 'symbol': sym}
            
            if fast_dl == True: # Fast download. It loads old files
                signal_data = download_latest_APC_fast(auth_pack, asset_pack, 
                                                   filename)
            elif fast_dl == False: # Slow download. It downlaod all data from db fresh
                signal_data = download_latest_APC(auth_pack, asset_pack)
                
            print("File: {} is generated.".format(filename))
            

            return signal_data
        
        download_latest_APC_indi(cat, key, sym)
    
    return "All APC files downloaded!"


def download_latest_Portara():
    # WIP
    # a function to download the newest Portara data
    return None



if __name__ == "__main__": 
    SAVE_FILENAME_LIST = list(APC_FILE_LOC.values())
# =============================================================================
#     save_filename_list = ["/home/dexter/Euler_Capital_codes/EC_tools/data/APC_latest/APC_latest_CLc2.csv", 
#                      "/home/dexter/Euler_Capital_codes/EC_tools/data/APC_latest/APC_latest_HOc2.csv", 
#                      "/home/dexter/Euler_Capital_codes/EC_tools/data/APC_latest/APC_latest_RBc2.csv", 
#                      "/home/dexter/Euler_Capital_codes/EC_tools/data/APC_latest/APC_latest_QOc2.csv",
#                      "/home/dexter/Euler_Capital_codes/EC_tools/data/APC_latest/APC_latest_QPc2.csv" ]
# 
#     categories_list = ['Argus Nymex WTI month 2, Daily', 
#                    'Argus Nymex Heating oil month 2, Daily', 
#                    'Argus Nymex RBOB Gasoline month 2, Daily', 
#                    'Argus Brent month 2, Daily', 
#                    'Argus ICE gasoil month 2, Daily']
# 
#     keywords_list = ["WTI","Heating", "Gasoline",'Brent', "gasoil"]
#     symbol_list = ['CLc2', 'HOc2', 'RBc2', 'QOc2', 'QPc2']
# =============================================================================
    
    
    download_latest_APC_list(AUTH_PACK, SAVE_FILENAME_LIST, CAT_LIST, 
                             KEYWORDS_LIST, SYMBOL_LIST,fast_dl=True)    
    #download_latest_APC(auth_pack, asset_pack)
