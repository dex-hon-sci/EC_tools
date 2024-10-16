#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 24 23:27:00 2024

@author: dexter

This script updates the daily APC data.
It pulls data from external servers to the local directory.

"""
import datetime as datetime
import pandas as pd

import EC_tools.read as read
import EC_tools.utility as util
from crudeoil_future_const import APC_FILE_LOC,\
                                  CAT_LIST, KEYWORDS_LIST, SYMBOL_LIST,\
                                  APC_FILE_COMPLETE_LOC,\
                                  APC_CAT_LIST_ALL, APC_KEYWORDS_LIST_ALL, \
                                  APC_SYMBOL_LIST_ALL,\
                                  MONTHLY_CAT_LIST, MONTHLY_KEYWORDS_LIST, \
                                  MONTHLY_SYMBOL_LIST,\
                                  WEEKLY_30AVG_CAT_LIST, WEEKLY_30AVG_KEYWORDS_LIST,\
                                  WEEKLY_30AVG_SYMBOL_LIST,\
                                  APC_FILE_MONTHLY_LOC, APC_FILE_WEEKLY_30AVG_LOC

import os
from dotenv import load_dotenv 

from pathlib import Path

# loading local global environment file
load_dotenv()
ARGUS_USR = os.environ.get("ARGUS_USR")
ARGUS_PW = os.environ.get("ARGUS_PW")


__author__ = "Dexter S.-H. Hon"
__all__ = ['download_latest_APC', 'download_latest_APC_fast', 
           'download_latest_APC_list']


AUTH_PACK = {'username':ARGUS_USR,
             'password':ARGUS_PW}

DATE_PACK = {"start_date": "2021-01-01",
             "end_date": "2024-06-18"}

ASSET_PACK = {'categories': 'Argus Nymex WTI month 1, Daily',
               'keywords': "WTI",
               'symbol': "CL"}

categories_monthly_30avg_list = [ 
                    'Argus Nymex WTI front month average 30-day interval, Weekly',
                    'Nymex Heating oil front month average 30-day interval, Weekly',
                    'Nymex RBOB gasoline front month average 30-day interval, Weekly',
                    'Argus Brent front month average 30-day interval, Weekly',
                    'ICE gasoil front month average 30-day interval, Weekly']

categories_monthly_list = ['Argus Nymex WTI front month average, Monthly',
                           'Nymex Heating oil front month average, Monthly',
                           'Nymex RBOB gasoline front month average, Monthly',
                           'Argus Brent front month average, Monthly',
                           'ICE gasoil front month average, Monthly']

# checking function to see if the table is up to date


def download_latest_APC(auth_pack: dict, 
                        asset_pack: dict, 
                        start_date: str = "2021-01-01") -> pd.DataFrame:
    """
    A method to download the latest APC from in its entirety. 
    This method is considered the 'slow' method due to the time in downloading 
    all the record directly from Argus.

    Parameters
    ----------
    auth_pack : dict
        A authethication package containing the username and the password 
        in access of Argus Data Studio.
    asset_pack : dict
        An asset package containing the categories, keywords, and symbol of 
        the asset itself.
    start_date : str, optional
        The start date. The default is "2021-01-01".

    Returns
    -------
    signal_data : DataFrame
        The APC data in a data frame.

    """

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

def download_latest_APC_fast(auth_pack: dict, 
                             asset_pack: dict, 
                             old_filename: str,
                             time_proxies: list[str] = ["PUBLICATION_DATE", 
                                                        "PERIOD"]) \
                             -> pd.DataFrame: #tested
    """
    A method to download the latest APC based on the existing APC file in 
    the data directory. 
    
    This method is considered the 'fast' method because it only downloads 
    and update the latest APC that is not in the old file.

    Parameters
    ----------
    auth_pack : dict
        A authethication package containing the username and the password 
        in access of Argus Data Studio.
    asset_pack : dict
        An asset package containing the categories, keywords, and symbol of 
        the asset itself.
    old_filename : str
        The name of the old APC file.
    time_proxies: list

    Returns
    -------
    signal_data : TYPE
        The APC data in a data frame.

    """
    # Check the last entry in the old file and only download the data 
    # Read the old files
    old_data = pd.read_csv(old_filename)
    
    #Find the date of the latest entry
    latest_entry = str(old_data[time_proxies[0]].iloc[-1])
    
    #    signal_data[time_proxy] = [datetime.datetime.strptime(x, '%Y-%m-%d')
    #                               for x in signal_data[time_proxy]]
    
    # download the latest APC from the latest_entry till today
    temp = download_latest_APC(auth_pack, asset_pack, start_date = latest_entry)
    
    #print('temp',temp[time_proxy] ,temp[time_proxy].iloc[0:10])
    
    # for some reason I have to turn the Forecast column elements to str first 
    # to align them with the old data
    
    for time_proxy in time_proxies:
        temp[time_proxy] = [temp[time_proxy].iloc[i].\
                                          strftime("%Y-%m-%d") for 
                                    i, _ in enumerate(temp[time_proxy])]
    
    # concandenate the old filedownload_latest_APC_list
    signal_data = pd.concat([old_data, temp], ignore_index = True)
    signal_data.sort_values(by=time_proxies[0])
    
    
    return signal_data

@util.time_it
def download_latest_APC_list(auth_pack: dict, 
                             save_filename_list: list, 
                             categories_list: list, 
                             keywords_list: list, 
                             symbol_list: list, 
                             fast_dl: bool = True) -> str:
    """
    The master method that allows you to download APC in bulk, as well as 
    choosing whether to use the fast or slow download method.

    Parameters
    ----------
    auth_pack : dict
        A authethication package containing the username and the password 
        in access of Argus Data Studio.
    save_filename_list : list
        A list of filename for saving.
    categories_list : list
        A list of category key words.
    keywords_list : list
        A list of keywords for a search.
    symbol_list : list
        A list of contract symbols.
    fast_dl : bool, optional
        Choose whether you want to enable fast download. The default is True.

    Returns
    -------
    str
        "All APC files downloaded!".

    """
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
    SAVE_FILENAME_LIST = list(APC_FILE_LOC.values()) # Daily APC for 10 assets (front, second months)
    SAVE_FILENAME_LIST_COMPLETE = list(APC_FILE_COMPLETE_LOC.values()) # Complete APC for all forecast from Argys
    SAVE_FILENAME_LIST_MONTHLY = list(APC_FILE_MONTHLY_LOC.values()) # Monthly APC for 5 assets (front month)
    SAVE_FILENAME_LIST_WEEKLY_30AVG = list(APC_FILE_WEEKLY_30AVG_LOC.values()) # Weekly average for 30 days interval (front month)
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

    # fast download on the 10 main crudeoil future contracts
    download_latest_APC_list(AUTH_PACK, SAVE_FILENAME_LIST, CAT_LIST, 
                             KEYWORDS_LIST, SYMBOL_LIST, fast_dl=True)   
    

    # slow downloading all argus APC from their server
    #download_latest_APC_list(AUTH_PACK, SAVE_FILENAME_LIST, CAT_LIST, 
    #                         KEYWORDS_LIST, SYMBOL_LIST,fast_dl=False)    

    #download_latest_APC_list(AUTH_PACK, SAVE_FILENAME_LIST_MONTHLY, MONTHLY_CAT_LIST, 
    #                         MONTHLY_KEYWORDS_LIST, MONTHLY_SYMBOL_LIST,fast_dl=False)    

    #download_latest_APC_list(AUTH_PACK, SAVE_FILENAME_LIST_WEEKLY_30AVG, WEEKLY_30AVG_CAT_LIST, 
    #                         WEEKLY_30AVG_KEYWORDS_LIST, WEEKLY_30AVG_SYMBOL_LIST,fast_dl=False)    
