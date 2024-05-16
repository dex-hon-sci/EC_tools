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
# =============================================================================
# asset_pack = {'categories': 'Argus Nymex WTI month 1, Daily',
#               'keywords': "WTI",
#               'symbol': "CL"}
# =============================================================================

# checking function to see if the table is up to date


def download_latest_APC(auth_pack, asset_pack):
    # input is a dictionary or json file
    username = auth_pack['username']
    password = auth_pack['password']
    
    categories = asset_pack['categories']
    keywords = asset_pack['keywords']
    symbol = asset_pack['symbol']
    
    start_date = "2021-01-01"
    end_date = datetime.date.today().strftime("%Y-%m-%d")
        
    # download the relevant APC data from the server
    signal_data = EC_read.get_apc_from_server(username, password, start_date, 
                                      end_date, categories,
                            keywords=keywords, symbol=symbol)
    return signal_data

def fast_download_latest_APC(auth_pack, asset_pack, old_filename): #WIP
    # input is a dictionary or json file
    username = auth_pack['username']
    password = auth_pack['password']
    
    categories = asset_pack['categories']
    keywords = asset_pack['keywords']
    symbol = asset_pack['symbol']
    
    #check the last entry in the old file and only download the data 

@util.time_it
def download_latest_APC_list(auth_pack, save_filename_list, categories_list, 
                         keywords_list, symbol_list):
    # a function to download the APC of a list of asset
    # input username and password.json

    for filename, cat, key, sym in zip(save_filename_list, categories_list, 
                                       keywords_list, symbol_list):
        @util.save_csv("{}".format(filename))
        def download_latest_APC_indi(cat, key, sym):
            asset_pack = {'categories': cat, 'keywords': key, 'symbol': sym}
            signal_data = download_latest_APC(auth_pack, asset_pack)
            print("File: {} is generated.".format(filename))

            return signal_data
        
        download_latest_APC_indi(cat, key, sym)
    
    return "All APC files downloaded!"


def operate_list(auth_pack, save_filename_list, categories_list, 
                         keywords_list, symbol_list):
    return 

def download_latest_Portara():
    # WIP
    # a function to download the newest Portara data
    return None

if __name__ == "__main__": 
    save_filename_list = ["APC_latest_CL.csv", 
                     "APC_latest_HO.csv", 
                     "APC_latest_RB.csv", 
                     "APC_latest_QO.csv",
                     "APC_latest_QP.csv" ]

    categories_list = ['Argus Nymex WTI month 1, Daily', 
                   'Argus Nymex Heating oil month 1, Daily', 
                   'Argus Nymex RBOB Gasoline month 1, Daily', 
                   'Argus Brent month 1, Daily', 
                   'Argus ICE gasoil month 1, Daily']

    keywords_list = ["WTI","Heating", "Gasoline",'Brent', "gasoil"]
    symbol_list = ['CLc1', 'HOc1', 'RBc1', 'QOc1', 'QPc1']
    
    download_latest_APC_list(auth_pack, save_filename_list, categories_list, 
                             keywords_list, symbol_list)
    
