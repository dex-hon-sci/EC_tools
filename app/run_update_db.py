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
import pickle
from pathlib import Path

import EC_tools.read as read
import EC_tools.utility as util
from crudeoil_future_const import CAT_LIST, KEYWORDS_LIST, SYMBOL_LIST,\
                                  APC_FILE_COMPLETE_LOC,\
                                  APC_CAT_LIST_ALL, APC_KEYWORDS_LIST_ALL, \
                                  APC_SYMBOL_LIST_ALL,\
                                  MONTHLY_CAT_LIST, MONTHLY_KEYWORDS_LIST, \
                                  MONTHLY_SYMBOL_LIST,\
                                  WEEKLY_30AVG_CAT_LIST, WEEKLY_30AVG_KEYWORDS_LIST,\
                                  WEEKLY_30AVG_SYMBOL_LIST,\
                                  APC_FILE_MONTHLY_LOC, APC_FILE_WEEKLY_30AVG_LOC
                                  
from crudeoil_future_const import DAILY_APC_PKL, DAILY_DATA_PKL, \
                                  DAILY_MINUTE_DATA_PKL, APC_FILE_LOC, \
                                  HISTORY_DAILY_FILE_LOC, \
                                  HISTORY_MINTUE_FILE_LOC,\
                                  MONTHS_TO_SYMBOLS, DATA_FILEPATH,\
                                  PORTARA_CONTINUOUS_MINTUE_FILE_LOC,\
                                  PORTARA_CONITNUOUS_DAILY_FILE_LOC

import os
from dotenv import load_dotenv 


# Get the base directory
basepath = Path()
basedir = str(basepath.cwd())
# Load the environment variables
envars = basepath.cwd() / '.env'
load_dotenv(envars)
# Read an environment variable.
SECRET_KEY = os.getenv('SECRET_KEY')

print(envars)
# loading local global environment file
load_dotenv()
ARGUS_USR = os.environ.get("ARGUS_USRX")
ARGUS_PW = os.environ.get("ARGUS_PWX")

print("ARGUS_USRX", ARGUS_USR,"ARGUS_PW", ARGUS_PW)

__author__ = "Dexter S.-H. Hon"
__all__ = ['download_latest_APC', 'download_latest_APC_fast', 
           'download_latest_APC_list']


AUTH_PACK = {'username': ARGUS_USR,
             'password': ARGUS_PW}

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
        
    # download the latest APC from the latest_entry till today
    temp = download_latest_APC(auth_pack, asset_pack, start_date = latest_entry)
    
    print('temp',temp[time_proxies[0]] ,temp[time_proxies[0]].iloc[0:10])
    
    # for some reason I have to turn the Forecast column elements to str first 
    # to align them with the old data
    
    for time_proxy in time_proxies:
        temp[time_proxy] = [temp[time_proxy].iloc[i].strftime("%Y-%m-%d") for 
                                    i, _ in enumerate(temp[time_proxy])]
    
    # concandenate the old filedownload_latest_APC_list
    signal_data = pd.concat([old_data, temp[1:]], ignore_index = True)
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

def create_rolling_futures_Portara(start_date: datetime.datetime,
                                   start_roll_date: datetime.datetime,
                                   symbol: str, forward: int,
                                   initial_roll_year: str, 
                                   initial_roll_month: str, 
                                   path: str, file_prefix: str, 
                                   file_suffix: str = '.txt',
                                   rolling_timescale: str ='Day'):
    
    read_funcs = {'Day': read.read_reformat_Portara_daily_data, 
                  'Minute': read.read_reformat_Portara_minute_data}
    
    col_format_dict = {'Day': ['Date', 'Open', 'High', 'Low', 'Settle', 'Volume', 
                               'OpenInterest'], 
                       'Minute': ['Date', 'Time', 'Open', 'High', 'Low', 
                                  'Settle', 'Volume']}    
    
    path = DATA_FILEPATH+"/roll_exp"
    folder_name = "/Day/"
    
    first_filename_path = str(Path(path)) + str(folder_name) + initial_roll_year + initial_roll_month +'.txt'
    first_P_data = read_funcs[rolling_timescale](first_filename_path, 
                                                 col_format = col_format_dict['Day'])

    first_P_data = first_P_data[first_P_data['Date']>=start_date][:-2]
    first_P_data['Contract Code'] = [symbol+ initial_roll_year + initial_roll_month for i in range(len(first_P_data))]
    print(first_P_data)
            
    master_table = first_P_data[:-1]
    up_pt = first_P_data['Date'].iloc[-1] 
    i = 1
    while i <2:
        temp_roll_date = up_pt + datetime.timedelta(days=forward+30)
        print('start_date',i, temp_roll_date)

        month, year = temp_roll_date.month, temp_roll_date.year
        print("year+month", year, month)
    
        
        filename = symbol + str(year) + MONTHS_TO_SYMBOLS[str(month)] 
        filename_path = str(Path(path)) + str(folder_name) + filename +'.txt'

        print('filename_path', filename_path)
        # read source files
        P_data = read_funcs['Day'](filename_path, col_format = \
                                   col_format_dict[rolling_timescale])
        # If the file is a full month, then the last entry will be zero for both volumne and openinterest
        if P_data['Volume'].iloc[-1] == 0 and P_data['OpenInterest'].iloc[-1]==0:
            P_data = P_data[P_data['Date']>=up_pt][:-2]
            up_pt = P_data['Date'].iloc[-1]
            print("roll_date", up_pt)
        else:
            P_data = P_data[P_data['Date']>=up_pt]
            
        # add contract name
        P_data['Contract Code'] = [filename for i in range(len(P_data))]

        print(P_data)
        # Check if this is the full month (last element volume ==0)

        
        #date_point = P_data['Date'].iloc[-1]
        #roll_date = roll_date 
        print("next_entry", up_pt)
        print("===========")

        i = i +1 
        
        master_table = pd.concat([master_table, P_data[:-1]])
    
    # build rolling data 
    print(master_table)
    return

def copy_Portara_data():
    symbols = list(PORTARA_CONTINUOUS_MINTUE_FILE_LOC.keys())
    print("Copying continuous data to data folder.")
    for symbol in symbols:
        #print("{} {}".format(PORTARA_CONITNUOUS_DAILY_FILE_LOC[symbol],
        #                              HISTORY_DAILY_FILE_LOC[symbol]))
        os.system('copy "{}" "{}"'.format(PORTARA_CONITNUOUS_DAILY_FILE_LOC[symbol],
                                          HISTORY_DAILY_FILE_LOC[symbol]))
        os.system('copy "{}" "{}"'.format(PORTARA_CONTINUOUS_MINTUE_FILE_LOC[symbol],
                                          HISTORY_MINTUE_FILE_LOC[symbol]))
    print("Copy Complete!!")


# =============================================================================
#         
# def update_rolling_futures_Portara(old_filename):
#    # CSV (Portara format)-> CSV (c1c2 Foramt)
#    # WIP
#    # a function to download the newest Portara data
#    return None
# def rolling_Portara_futures():
#     return
# 
# def update_Portara_data(old_filename):
#     # CSV (Portara format)-> CSV (c1c2 Foramt)
#     # WIP
#     # a function to download the newest Portara data
#     return None
# 
# =============================================================================
@util.time_it
def update_pkl(old_pkl_filename: str,
               file_loc_dict: dict,
               time_proxies: list[str],
               read_func):
    
    old_pkl = util.load_pkl(old_pkl_filename)
    symbols = list(file_loc_dict.keys())

    for symbol in symbols:
        
        old_data = old_pkl[symbol]
    
        print('old_data',old_data)
        #Find the date of the latest entry
        latest_entry = old_data[time_proxies[0]].iloc[-1]
    
        print('latest_entry',latest_entry)

        # read the latest_entry till today
        temp = read_func(file_loc_dict[symbol])
        # select for the latest entry
        temp = temp[temp[time_proxies[0]]>latest_entry]
        print('temp',temp)

        new_data = pd.concat([old_data, temp], ignore_index = True)
        new_data.sort_values(by=time_proxies[0])

        print(new_data[-10:])
            
        #Store them in the pkl
        old_pkl[symbol] = new_data
        
    # Saving the pkl
    print("Saving")
    output = open(old_pkl_filename, 'wb')
    pickle.dump(old_pkl, output)
    print("Saved")

    return old_pkl

def build_db():
    return

def main():
    # RUN update
    # First check if the old source data exists
    
    # Second update the source data
    # update APC,
    download_latest_APC_list(AUTH_PACK, list(APC_FILE_LOC.values()), CAT_LIST, 
                             KEYWORDS_LIST, SYMBOL_LIST, fast_dl=True)   
    # update Portara
    # Roll Portara data # new just used to roll function in Portara
    # Copy all new continuous data from Portara to the master data folder.
    #copy_Portara_data()
    
    # Third update the pkl data
    # Update APC pkl
    update_pkl(DAILY_APC_PKL, APC_FILE_LOC, ["PERIOD"], 
               read.read_reformat_APC_data)
    # Update Portara Daily data (crudeoil futures) pkl
    #update_pkl(DAILY_DATA_PKL, HISTORY_DAILY_FILE_LOC, ["Date"], 
    #           read.read_reformat_Portara_daily_data)
    # Update Portara Intraday minute data (crudeoil futures) pkl
    #update_pkl(DAILY_MINUTE_DATA_PKL, HISTORY_MINTUE_FILE_LOC, ["Date"], 
    #           read.read_reformat_Portara_minute_data)
    
    
    # Fourth update the data base
    return "Update Complete"

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
    main()

    # fast download on the 10 main crudeoil future contracts
    #download_latest_APC_list(AUTH_PACK, SAVE_FILENAME_LIST, CAT_LIST, 
    #                         KEYWORDS_LIST, SYMBOL_LIST, fast_dl=True)   
    

    # slow downloading all argus APC from their server
    #download_latest_APC_list(AUTH_PACK, SAVE_FILENAME_LIST, CAT_LIST, 
    #                         KEYWORDS_LIST, SYMBOL_LIST,fast_dl=False)    

    #download_latest_APC_list(AUTH_PACK, SAVE_FILENAME_LIST_MONTHLY, MONTHLY_CAT_LIST, 
    #                         MONTHLY_KEYWORDS_LIST, MONTHLY_SYMBOL_LIST,fast_dl=False)    

    #download_latest_APC_list(AUTH_PACK, SAVE_FILENAME_LIST_WEEKLY_30AVG, WEEKLY_30AVG_CAT_LIST, 
    #                         WEEKLY_30AVG_KEYWORDS_LIST, WEEKLY_30AVG_SYMBOL_LIST,fast_dl=False)    
