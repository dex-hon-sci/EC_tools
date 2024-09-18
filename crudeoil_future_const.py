#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jun 23 09:00:12 2024

@author: dexter
"""
import numpy as np
from dotenv import load_dotenv 
import os
from pathlib import Path

# loading local global environment file
load_dotenv()
DATA_FILEPATH = os.environ.get("DATA_FILEPATH")
RESULT_FILEPATH = os.environ.get("RESULT_FILEPATH")

DAILY_DATA_PKL = DATA_FILEPATH +"/pkl_vault/crudeoil_future_daily_full.pkl"
DAILY_MINUTE_DATA_PKL = DATA_FILEPATH +"/pkl_vault/crudeoil_future_minute_full.pkl"
DAILY_APC_PKL = DATA_FILEPATH +"/pkl_vault/crudeoil_future_APC_full.pkl"
DAILY_OPENPRICE_PKL = DATA_FILEPATH +'/pkl_vault/crudeoil_future_openprice_full.pkl'

MONTHLY_APC_PKL = DATA_FILEPATH +"/pkl_vault/crudeoil_future_Monthly_APC_full.pkl"
WEEKLY_30AVG_APC_PKL = DATA_FILEPATH +"/pkl_vault/crudeoil_future_Weekly_30AVG_APC_full.pkl"

DAILY_CUMAVG_MONTH = DATA_FILEPATH +"/pkl_vault/crudeoil_future_daily_cumavg_full.pkl"
MINUTE_CUMAVG_MONTH = DATA_FILEPATH +"/pkl_vault/crudeoil_future_minute_cumavg_full.pkl"

# Define the contracts of interest
ASSET_DICT = {"USD": {"unit":'dollars', "asset_type":'Cash'},
              "AUD": {"unit":'dollars',"asset_type":'Cash'},
              "CLc1": {"unit":'contracts',"asset_type":'Future'},
              "CLc2": {"unit":'contracts', "asset_type":'Future'},
              "HOc1": {"unit":'contracts',"asset_type":'Future'},
              "HOc2": {"unit":'contracts',"asset_type":'Future'},
              "RBc1": {"unit":'contracts',"asset_type":'Future'},
              "RBc2": {"unit":'contracts',"asset_type":'Future'},
              "QOc1": {"unit":'contracts',"asset_type":'Future'},
              "QOc2": {"unit":'contracts',"asset_type":'Future'},
              "QPc1": {"unit":'contracts',"asset_type":'Future'},
              "QPc2": {"unit":'contracts',"asset_type":'Future'}
              }

CAT_LIST = [ 'Argus Nymex WTI month 1, Daily', 
             'Argus Nymex WTI month 2, Daily', 
             'Argus Nymex Heating oil month 1, Daily', 
             'Argus Nymex Heating oil month 2, Daily', 
             'Argus Nymex RBOB Gasoline month 1, Daily', 
             'Argus Nymex RBOB Gasoline month 2, Daily', 
             'Argus Brent month 1, Daily', 
             'Argus Brent month 2, Daily', 
             'Argus ICE gasoil month 1, Daily',
             'Argus ICE gasoil month 2, Daily']

KEYWORDS_LIST = ["WTI","WTI","Heating", "Heating","Gasoline","Gasoline",
                 'Brent', 'Brent',"gasoil", 'gasoil']

SYMBOL_LIST = ["CLc1", "CLc2", "HOc1", "HOc2", "RBc1", "RBc2", 
               "QOc1", "QOc2", "QPc1", "QPc2"]

# Monthly lists
MONTHLY_CAT_LIST = ['Argus Nymex WTI front month average, Monthly',
                    'Nymex Heating oil front month average, Monthly',
                    'Nymex RBOB gasoline front month average, Monthly',
                    'Argus Brent front month average, Monthly',
                    'ICE gasoil front month average, Monthly']

MONTHLY_KEYWORDS_LIST = ["WTI","Heating","Gasoline",
                         'Brent', 'gasoil']

MONTHLY_SYMBOL_LIST = ["CLc1_avg_M", "HOc1_avg_M", "RBc1_avg_M",
                       "QOc1_avg_M", "QPc1_avg_M"]


WEEKLY_30AVG_CAT_LIST = ['Argus Nymex WTI front month average 30-day interval, Weekly',
                         'Nymex Heating oil front month average 30-day interval, Weekly',
                         'Nymex RBOB gasoline front month average 30-day interval, Weekly',
                         'Argus Brent front month average 30-day interval, Weekly',
                         'ICE gasoil front month average 30-day interval, Weekly']

WEEKLY_30AVG_KEYWORDS_LIST = ["WTI","Heating","Gasoline",'Brent', 'gasoil']

WEEKLY_30AVG_SYMBOL_LIST = ["CLc1_avg30_W", "HOc1_avg30_W", "RBc1_avg30_W",
                            "QOc1_avg30_W", "QPc1_avg30_W"]
                                  
APC_CAT_LIST_ALL = ['Argus Nymex Heating oil month 7, Daily',
                     'Argus Nymex WTI month 8, Daily',
                     'Argus ICE gasoil month 4, Daily',
                     'Argus Nymex WTI month 1, Daily',
                     'Argus Brent month 3, Daily',
                     'Argus Nymex WTI month 3, Daily',
                     'ICE gasoil front month average 30-day interval, Weekly',
                     'Argus Brent month 4, Daily',
                     'Argus Nymex RBOB Gasoline month 8, Daily',
                     'Argus Nymex WTI month 10, Daily',
                     'Argus Brent front month spread, Daily',
                     'Argus Nymex WTI front month spread, Daily',
                     'Argus Nymex WTI month 2, Daily',
                     'ICE gasoil front month average, Monthly',
                     'Argus Brent month 10, Daily',
                     'Argus Nymex RBOB Gasoline month 6, Daily',
                     'Argus Nymex Heating oil month 6, Daily',
                     'Argus Brent front month average 30-day interval, Weekly',
                     'Argus Brent month 7, Daily',
                     'Argus WCS front month average, Monthly',
                     'Argus ICE gasoil month 5, Daily',
                     'Argus ICE gasoil month 11, Daily',
                     'Argus Nymex Heating oil month 8, Daily',
                     'Argus Nymex RBOB Gasoline month 4, Daily',
                     'Argus Nymex WTI month 4, Daily',
                     'Argus ICE gasoil month 7, Daily',
                     'Argus Nymex RBOB Gasoline month 7, Daily',
                     'Argus Nymex Heating oil month 11, Daily',
                     'Argus Nymex Heating oil month 3, Daily',
                     'Argus Nymex WTI month 9, Daily',
                     'Argus Nymex Heating oil month 2, Daily',
                     'Nymex RBOB gasoline front month average 30-day interval, Weekly',
                     'Argus Nymex RBOB Gasoline month 2, Daily',
                     'Argus Brent month 2, Daily',
                     'Argus Nymex WTI month 12, Daily',
                     'Argus Nymex WTI month 6, Daily',
                     'Argus Nymex RBOB Gasoline month 9, Daily',
                     'Argus Nymex Heating oil month 12, Daily',
                     'Argus Nymex WTI month 7, Daily',
                     'Argus Brent month 1, Daily',
                     'Argus Nymex Heating oil month 1, Daily',
                     'Argus Nymex WTI month 5, Daily',
                     'Argus ICE gasoil month 6, Daily',
                     'Argus Brent month 8, Daily',
                     'Nymex Heating oil front month average, Monthly',
                     'Nymex RBOB gasoline front month average, Monthly',
                     'Argus ICE gasoil month 3, Daily',
                     'Argus Nymex RBOB Gasoline month 10, Daily',
                     'Argus Nymex RBOB Gasoline month 3, Daily',
                     'Argus Nymex Heating oil month 5, Daily',
                     'Argus Nymex Heating oil month 9, Daily',
                     'Argus Brent month 11, Daily',
                     'Argus Nymex WTI front month average 30-day interval, Weekly',
                     'Argus Brent month 12, Daily',
                     'Argus Brent month 5, Daily',
                     'Argus ICE gasoil month 1, Daily',
                     'Argus Mars front month average, Monthly',
                     'Argus Nymex WTI month 11, Daily',
                     'Argus Brent month 6, Daily',
                     'Argus Brent month 9, Daily',
                     'Nymex Heating oil front month average 30-day interval, Weekly',
                     'Argus Nymex Heating oil month 4, Daily',
                     'Argus WTI Houston front month average, Monthly',
                     'Argus ICE gasoil month 10, Daily',
                     'Argus Nymex Heating oil month 10, Daily',
                     'Argus Nymex RBOB Gasoline month 5, Daily',
                     'Argus Nymex RBOB Gasoline month 1, Daily',
                     'Argus Nymex RBOB Gasoline month 12, Daily',
                     'Argus Nymex WTI front month average, Monthly',
                     'Argus ICE gasoil month 9, Daily',
                     'Argus ICE gasoil month 12, Daily',
                     'Argus Brent front month average, Monthly',
                     'Argus ICE gasoil month 8, Daily',
                     'Argus Nymex RBOB Gasoline month 11, Daily',
                     'Argus ICE gasoil month 2, Daily']


APC_KEYWORDS_LIST_ALL = ['Heating','WTI','gasoil','WTI','Brent','WTI',
                         'gasoil','Brent','Gasoline','WTI','Brent','WTI',
                         'WTI','gasoil','Brent','Gasoline','Heating',
                         'Brent','Brent','WCS','gasoil','gasoil','Heating',
                         'Gasoline','WTI','gasoil','Gasoline','Heating',
                         'Heating','WTI','Heating','gasoline','Gasoline',
                         'Brent','WTI','WTI','Gasoline','Heating','WTI',
                         'Brent','Heating','WTI','gasoil','Brent','Heating',
                         'gasoline','gasoil','Gasoline','Gasoline','Heating',
                         'Heating','Brent','WTI','Brent','Brent','gasoil',
                         'Mars','WTI','Brent','Brent','Heating','Heating',
                         'WTI','gasoil','Heating','Gasoline','Gasoline',
                         'Gasoline','WTI','gasoil','gasoil','Brent','gasoil',
                         'Gasoline','gasoil']

APC_SYMBOL_LIST_ALL = ['HOc7','CLc8','QPc4','CLc1','QOc3','CLc3','QPc1_avg30_W',
                       'QOc4','RBc8','CLc10','QOc1','CLc1','CLc2',
                       'QPc1_avg_M','QOc10','RBc6','HOc6','QOc1_avg30_W',
                       'QOc7','WCSc1_avg_M', 'QPc5','QPc11','HOc8','RBc4',
                       'CLc4','QPc7','RBc7','HOc11','HOc3','CLc9', 'HOc2',
                       'RBc1_avg30_W','RBc2','QOc2','CLc12','CLc6','RBc9',
                       'HOc12','CLc7','CLc1','HOc1','CLc5','QPc6','QOc8',
                       'HOc1_avg_M','RBc1_avg_M', 'QPc3','RBc10','RB3','HOc5',
                       'HOc9','QOc11','CLc1_avg30_W','QOc12','QOc5','QPc1',
                       'Marsc1_avg_M','CLc11', 'QOc6','QOc9','HOc1_avg30_W',
                       'HOc4','CLc1_Houston_avg_M','QPc10','HOc10','RBc5',
                       'RBc1','RBc12','CLc1_avg_M','QPc9','QPc12','QOc1_avg_M',
                       'QPc8','RBc11','QPc2']
APC_LENGTH = len(np.arange(0.0025, 0.9975, 0.0025))

#list(HISTORY_DAILY_FILE_LOC.keys())

SYMBOL_KEYWORDS_DICT = {"CLc1": "WTI", "CLc2": "WTI",
                        "HOc1": "Heating", "HOc2": "Heating",
                        "RBc1": "Gasoline", "RBc2": "Gasoline",
                        "QOc1": "Brent", "QOc2": "Brent", 
                        "QPc1": "gasoil", "QPc2": "gasoil"}

OIL_FUTURES_FEE = {'name':'USD', 'quantity': 15.0, 
                   'unit':'dollars', 'asset_type': 'Cash'}

def make_path_dict(folder_name: str, file_prefix: str, 
                   file_suffix: str = '.csv',  
                   path: str = RESULT_FILEPATH,
                   syms: list = SYMBOL_LIST): #WIP
    
    bucket = dict()
    for sym in syms: 
        file_path = Path(path) / folder_name 
        bucket[sym] = str(file_path / str(file_prefix + sym + file_suffix))
    return bucket
        
APC_FILE_COMPLETE_LOC = make_path_dict(folder_name = 'APC_latest_complete',
                                       file_prefix = "APC_latest_",
                                       file_suffix='.csv',
                                       path = DATA_FILEPATH,
                                       syms=APC_SYMBOL_LIST_ALL)

APC_FILE_MONTHLY_LOC = make_path_dict(folder_name = 'APC_latest_complete',
                                      file_prefix = "APC_latest_",
                                      file_suffix='_avg_M.csv',
                                      path = DATA_FILEPATH,
                                      syms=SYMBOL_LIST)


APC_FILE_WEEKLY_30AVG_LOC = make_path_dict(folder_name = 'APC_latest_complete',
                                           file_prefix = "APC_latest_",
                                           file_suffix='_avg30_W.csv',
                                           path = DATA_FILEPATH,
                                           syms=SYMBOL_LIST)


SIZE_DICT = {
    'CLc1': 1000.0,
    'CLc2': 1000.0,
    'HOc1': 42000.0,
    'HOc2': 42000.0,
    'RBc1': 42000.0,
    'RBc2': 42000.0,
    'QOc1': 1000.0,
    'QOc2': 1000.0,
    'QPc1': 100.0,
    'QPc2': 100.0
    } # num_per_contract

# =============================================================================
# round_turn_fees = {
#     'CLc1': 24.0,
#     'CLc2': 24.0,
#     'HOc1': 25.2,
#     'HOc2': 25.2,
#     'RBc1': 25.2,
#     'RBc2': 25.2,
#     'QOc1': 24.0,
#     'QOc2': 24.0,
#     'QPc1': 24.0,
#     'QPc2': 24.0
# } #30
# =============================================================================

round_turn_fees = {
    'CLc1': 15.0,
    'CLc2': 15.0,
    'HOc1': 15.0,
    'HOc2': 15.0,
    'RBc1': 15.0,
    'RBc2': 15.0,
    'QOc1': 15.0,
    'QOc2': 15.0,
    'QPc1': 15.0,
    'QPc2': 15.0
} #30

OIL_FUTURES_FEES = {    
    'CLc1': {'name':'USD', 'quantity': 15.0, 
             'unit':'dollars', 'asset_type': 'Cash'},
    'CLc2': {'name':'USD', 'quantity': 15.0, 
             'unit':'dollars', 'asset_type': 'Cash'},
    'HOc1': {'name':'USD', 'quantity': 15.0, 
             'unit':'dollars', 'asset_type': 'Cash'},
    'HOc2': {'name':'USD', 'quantity': 15.0, 
             'unit':'dollars', 'asset_type': 'Cash'},
    'RBc1': {'name':'USD', 'quantity': 15.0, 
             'unit':'dollars', 'asset_type': 'Cash'},
    'RBc2': {'name':'USD', 'quantity': 15.0, 
             'unit':'dollars', 'asset_type': 'Cash'},
    'QOc1': {'name':'USD', 'quantity': 15.0, 
             'unit':'dollars', 'asset_type': 'Cash'},
    'QOc2': {'name':'USD', 'quantity': 15.0, 
             'unit':'dollars', 'asset_type': 'Cash'},
    'QPc1': {'name':'USD', 'quantity': 15.0, 
             'unit':'dollars', 'asset_type': 'Cash'},
    'QPc2': {'name':'USD', 'quantity': 15.0, 
             'unit':'dollars', 'asset_type': 'Cash'}
    }


OPEN_HR_DICT = {
    'CLc1':'0330', # UTC
    'CLc2':'0330', # UTC
    'HOc1':'1300', #0800 NY #1300 UTC
    'HOc2':'1300', #0800 NY #1300 UTC
    'RBc1':'1300', #0800 NY #1300 UTC
    'RBc2':'1300', #0800 NY #1300 UTC
    'QOc1':'0330', # UTC
    'QOc2':'0330', # UTC
    'QPc1':'0800', # UTC
    'QPc2':'0800'} # UTC

CLOSE_HR_DICT = {
    'CLc1':'1959', #2000 UTC
    'CLc2':'1959', #2000 UTC
    'HOc1':'1829', #1430 NY #1830 UTC
    'HOc2':'1829', #1430 NY #1830 UTC
    'RBc1':'1829', #1430 NY #1830 UTC
    'RBc2':'1829', #1430 NY #1830 UTC
    'QOc1':'1959', #2000 UTC
    'QOc2':'1959', #2000 UTC
    'QPc1':'1629', #1630 UTC
    'QPc2':'1629'} #1630 UTC


OPEN_HR_DICT_EARLY = {
    'CLc1':'0330', # UTC
    'CLc2':'0330', # UTC
    'HOc1':'1300', #0800 NY #1300 UTC
    'HOc2':'1300', #0800 NY #1300 UTC
    'RBc1':'1300', #0800 NY #1300 UTC
    'RBc2':'1300', #0800 NY #1300 UTC
    'QOc1':'0330', # UTC
    'QOc2':'0330', # UTC
    'QPc1':'0800', # UTC
    'QPc2':'0800'} # UTC

CLOSE_HR_DICT_EARLY = {
    'CLc1':'0830', #2000 UTC
    'CLc2':'0830', #2000 UTC
    'HOc1':'1500', #1430 NY #1830 UTC
    'HOc2':'1500', #1430 NY #1830 UTC
    'RBc1':'1500', #1430 NY #1830 UTC
    'RBc2':'1500', #1430 NY #1830 UTC
    'QOc1':'0830', #2000 UTC
    'QOc2':'0830', #2000 UTC
    'QPc1':'1100', #1630 UTC
    'QPc2':'1100'} #1630 UTC

WRONG_OPEN_HR_DICT = {
    'CLc1':'0330', # UTC
    'CLc2':'0330', # UTC
    'HOc1':'0330', #0800 NY #1300 UTC
    'HOc2':'0330', #0800 NY #1300 UTC
    'RBc1':'0330', #0800 NY #1300 UTC
    'RBc2':'0330', #0800 NY #1300 UTC
    'QOc1':'0330', # UTC
    'QOc2':'0330', # UTC
    'QPc1':'0800', # UTC
    'QPc2':'0800'} # UTC

WRONG_CLOSE_HR_DICT = {
    'CLc1':'1959', #2000 UTC
    'CLc2':'1959', #2000 UTC
    'HOc1':'1959', #1430 NY #1830 UTC
    'HOc2':'1959', #1430 NY #1830 UTC
    'RBc1':'1959', #1430 NY #1830 UTC
    'RBc2':'1959', #1430 NY #1830 UTC
    'QOc1':'1959', #2000 UTC
    'QOc2':'1959', #2000 UTC
    'QPc1':'1959', #1630 UTC
    'QPc2':'1959'} #1630 UTC

TIMEZONE_DICT = {
    'CLc1':'Europe/London',
    'CLc2':'Europe/London',
    'HOc1':'America/New_York',
    'HOc2':'America/New_York',
    'RBc1':'America/New_York',
    'RBc2':'America/New_York',
    'QOc1':'Europe/London',
    'QOc2':'Europe/London',
    'QPc1':'Europe/London',
    'QPc2':'Europe/London'}

# raw input file list
APC_FILE_LOC = {
    "CLc1": DATA_FILEPATH + "/APC_latest/APC_latest_CLc1.csv",
    "CLc2": DATA_FILEPATH + "/APC_latest/APC_latest_CLc2.csv",
    "HOc1": DATA_FILEPATH + "/APC_latest/APC_latest_HOc1.csv",
    "HOc2": DATA_FILEPATH + "/APC_latest/APC_latest_HOc2.csv",
    "RBc1": DATA_FILEPATH + "/APC_latest/APC_latest_RBc1.csv",
    "RBc2": DATA_FILEPATH + "/APC_latest/APC_latest_RBc2.csv",
    "QOc1": DATA_FILEPATH + "/APC_latest/APC_latest_QOc1.csv",
    "QOc2": DATA_FILEPATH + "/APC_latest/APC_latest_QOc2.csv",
    "QPc1": DATA_FILEPATH + "/APC_latest/APC_latest_QPc1.csv",
    "QPc2": DATA_FILEPATH + "/APC_latest/APC_latest_QPc2.csv"
    }

HISTORY_DAILY_FILE_LOC = {
    "CLc1": DATA_FILEPATH + "/history_data/Day/CL.day",
    "CLc2": DATA_FILEPATH + "/history_data/Day/CL_d01.day",
    "HOc1": DATA_FILEPATH + "/history_data/Day/HO.day",
    "HOc2": DATA_FILEPATH + "/history_data/Day/HO_d01.day",
    "RBc1": DATA_FILEPATH + "/history_data/Day/RB.day",
    "RBc2": DATA_FILEPATH + "/history_data/Day/RB_d01.day",
    "QOc1": DATA_FILEPATH + "/history_data/Day/QO.day",
    "QOc2": DATA_FILEPATH + "/history_data/Day/QO_d01.day",
    "QPc1": DATA_FILEPATH + "/history_data/Day/QP.day",
    "QPc2": DATA_FILEPATH + "/history_data/Day/QP_d01.day"
}

HISTORY_MINTUE_FILE_LOC = {
    "CLc1": DATA_FILEPATH + "/history_data/Minute/CL.001",
    "CLc2": DATA_FILEPATH + "/history_data/Minute/CL_d01.001",
    "HOc1": DATA_FILEPATH + "/history_data/Minute/HO.001",
    "HOc2": DATA_FILEPATH + "/history_data/Minute/HO_d01.001",
    "RBc1": DATA_FILEPATH + "/history_data/Minute/RB.001",
    "RBc2": DATA_FILEPATH + "/history_data/Minute/RB_d01.001",
    "QOc1": DATA_FILEPATH + "/history_data/Minute/QO.001",
    "QOc2": DATA_FILEPATH + "/history_data/Minute/QO_d01.001",
    "QPc1": DATA_FILEPATH + "/history_data/Minute/QP.001",
    "QPc2": DATA_FILEPATH + "/history_data/Minute/QP_d01.001"
    }

OPEN_PRICE_FILE_LOC = {    
    "CLc1": DATA_FILEPATH + "/history_data/open_price/CL_op.day",
    "CLc2": DATA_FILEPATH + "/history_data/open_price/CL_d01_op.day",
    "HOc1": DATA_FILEPATH + "/history_data/open_price/HO_op.day",
    "HOc2": DATA_FILEPATH + "/history_data/open_price/HO_d01_op.day",
    "RBc1": DATA_FILEPATH + "/history_data/open_price/RB_op.day",
    "RBc2": DATA_FILEPATH + "/history_data/open_price/RB_d01_op.day",
    "QOc1": DATA_FILEPATH + "/history_data/open_price/QO_op.day",
    "QOc2": DATA_FILEPATH + "/history_data/open_price/QO_d01_op.day",
    "QPc1": DATA_FILEPATH + "/history_data/open_price/QP_op.day",
    "QPc2": DATA_FILEPATH + "/history_data/open_price/QP_d01_op.day"}

HISTORY_DAILY_CUMAVG_IN_MONTH = make_path_dict(folder_name = 'history_data/daily_cumavg_month',
                                               file_prefix = "",
                                               file_suffix='_daily_cumavg_month.csv',
                                               path = DATA_FILEPATH,
                                               syms=SYMBOL_LIST)

HISTORY_MINUTE_CUMAVG_IN_MONTH = make_path_dict(folder_name = 'history_data/minute_cumavg_month',
                                               file_prefix = "",
                                               file_suffix='_minute_cumavg_month.csv',
                                               path = DATA_FILEPATH,
                                               syms=SYMBOL_LIST)

ARGUS_BENCHMARK_SIGNAL_FILE_LOC = {
    'CLc1': RESULT_FILEPATH + '/benchmark_signals/benchmark_signal_CLc1_full.csv',
    'CLc2': RESULT_FILEPATH + '/benchmark_signals/benchmark_signal_CLc2_full.csv',
    'HOc1': RESULT_FILEPATH + '/benchmark_signals/benchmark_signal_HOc1_full.csv',
    'HOc2': RESULT_FILEPATH + '/benchmark_signals/benchmark_signal_HOc2_full.csv',
    'RBc1': RESULT_FILEPATH + '/benchmark_signals/benchmark_signal_RBc1_full.csv',
    'RBc2': RESULT_FILEPATH + '/benchmark_signals/benchmark_signal_RBc2_full.csv',
    'QOc1': RESULT_FILEPATH + '/benchmark_signals/benchmark_signal_QOc1_full.csv',
    'QOc2': RESULT_FILEPATH + '/benchmark_signals/benchmark_signal_QOc2_full.csv',
    'QPc1': RESULT_FILEPATH + '/benchmark_signals/benchmark_signal_QPc1_full.csv',
    'QPc2': RESULT_FILEPATH + '/benchmark_signals/benchmark_signal_QPc2_full.csv'
    }

ARGUS_BENCHMARK_SIGNAL_AMB_FILE_LOC = {
    'CLc1': RESULT_FILEPATH + '/benchmark_signals_amb/benchmark_signal_CLc1_full.csv',
    'CLc2': RESULT_FILEPATH + '/benchmark_signals_amb/benchmark_signal_CLc2_full.csv',
    'HOc1': RESULT_FILEPATH + '/benchmark_signals_amb/benchmark_signal_HOc1_full.csv',
    'HOc2': RESULT_FILEPATH + '/benchmark_signals_amb/benchmark_signal_HOc2_full.csv',
    'RBc1': RESULT_FILEPATH + '/benchmark_signals_amb/benchmark_signal_RBc1_full.csv',
    'RBc2': RESULT_FILEPATH + '/benchmark_signals_amb/benchmark_signal_RBc2_full.csv',
    'QOc1': RESULT_FILEPATH + '/benchmark_signals_amb/benchmark_signal_QOc1_full.csv',
    'QOc2': RESULT_FILEPATH + '/benchmark_signals_amb/benchmark_signal_QOc2_full.csv',
    'QPc1': RESULT_FILEPATH + '/benchmark_signals_amb/benchmark_signal_QPc1_full.csv',
    'QPc2': RESULT_FILEPATH + '/benchmark_signals_amb/benchmark_signal_QPc2_full.csv'
    }

ARGUS_BENCHMARK_SIGNAL_AMB_BUY_FILE_LOC = {
    'CLc1': RESULT_FILEPATH + '/benchmark_signals_amb_buy/benchmark_signal_CLc1_full.csv',
    'CLc2': RESULT_FILEPATH + '/benchmark_signals_amb_buy/benchmark_signal_CLc2_full.csv',
    'HOc1': RESULT_FILEPATH + '/benchmark_signals_amb_buy/benchmark_signal_HOc1_full.csv',
    'HOc2': RESULT_FILEPATH + '/benchmark_signals_amb_buy/benchmark_signal_HOc2_full.csv',
    'RBc1': RESULT_FILEPATH + '/benchmark_signals_amb_buy/benchmark_signal_RBc1_full.csv',
    'RBc2': RESULT_FILEPATH + '/benchmark_signals_amb_buy/benchmark_signal_RBc2_full.csv',
    'QOc1': RESULT_FILEPATH + '/benchmark_signals_amb_buy/benchmark_signal_QOc1_full.csv',
    'QOc2': RESULT_FILEPATH + '/benchmark_signals_amb_buy/benchmark_signal_QOc2_full.csv',
    'QPc1': RESULT_FILEPATH + '/benchmark_signals_amb_buy/benchmark_signal_QPc1_full.csv',
    'QPc2': RESULT_FILEPATH + '/benchmark_signals_amb_buy/benchmark_signal_QPc2_full.csv'
    }

ARGUS_BENCHMARK_SIGNAL_AMB_SELL_FILE_LOC = {
    'CLc1': RESULT_FILEPATH + '/benchmark_signals_amb_sell/benchmark_signal_CLc1_full.csv',
    'CLc2': RESULT_FILEPATH + '/benchmark_signals_amb_sell/benchmark_signal_CLc2_full.csv',
    'HOc1': RESULT_FILEPATH + '/benchmark_signals_amb_sell/benchmark_signal_HOc1_full.csv',
    'HOc2': RESULT_FILEPATH + '/benchmark_signals_amb_sell/benchmark_signal_HOc2_full.csv',
    'RBc1': RESULT_FILEPATH + '/benchmark_signals_amb_sell/benchmark_signal_RBc1_full.csv',
    'RBc2': RESULT_FILEPATH + '/benchmark_signals_amb_sell/benchmark_signal_RBc2_full.csv',
    'QOc1': RESULT_FILEPATH + '/benchmark_signals_amb_sell/benchmark_signal_QOc1_full.csv',
    'QOc2': RESULT_FILEPATH + '/benchmark_signals_amb_sell/benchmark_signal_QOc2_full.csv',
    'QPc1': RESULT_FILEPATH + '/benchmark_signals_amb_sell/benchmark_signal_QPc1_full.csv',
    'QPc2': RESULT_FILEPATH + '/benchmark_signals_amb_sell/benchmark_signal_QPc2_full.csv'
    } 

ARGUS_BENCHMARK_PNL_FILE_LOC = {
    'CLc1': RESULT_FILEPATH + '/benchmark_PNL/benchmark_PNL_CLc1_full.csv',
    'CLc2': RESULT_FILEPATH + '/benchmark_PNL/benchmark_PNL_CLc2_full.csv',
    'HOc1': RESULT_FILEPATH + '/benchmark_PNL/benchmark_PNL_HOc1_full.csv',
    'HOc2': RESULT_FILEPATH + '/benchmark_PNL/benchmark_PNL_HOc2_full.csv',
    'RBc1': RESULT_FILEPATH + '/benchmark_PNL/benchmark_PNL_RBc1_full.csv',
    'RBc2': RESULT_FILEPATH + '/benchmark_PNL/benchmark_PNL_RBc2_full.csv',
    'QOc1': RESULT_FILEPATH + '/benchmark_PNL/benchmark_PNL_QOc1_full.csv',
    'QOc2': RESULT_FILEPATH + '/benchmark_PNL/benchmark_PNL_QOc2_full.csv',
    'QPc1': RESULT_FILEPATH + '/benchmark_PNL/benchmark_PNL_QPc1_full.csv',
    'QPc2': RESULT_FILEPATH + '/benchmark_PNL/benchmark_PNL_QPc2_full.csv'
}

ARGUS_EXACT_SIGNAL_FILE_LOC = {
    'CLc1': RESULT_FILEPATH + "/argus_exact_signal/argus_exact_signal_CLc1_full.csv", 
    'CLc2': RESULT_FILEPATH + "/argus_exact_signal/argus_exact_signal_CLc2_full.csv", 
    'HOc1': RESULT_FILEPATH + "/argus_exact_signal/argus_exact_signal_HOc1_full.csv", 
    'HOc2': RESULT_FILEPATH + "/argus_exact_signal/argus_exact_signal_HOc2_full.csv", 
    'RBc1': RESULT_FILEPATH + "/argus_exact_signal/argus_exact_signal_RBc1_full.csv", 
    'RBc2': RESULT_FILEPATH + "/argus_exact_signal/argus_exact_signal_RBc2_full.csv", 
    'QOc1': RESULT_FILEPATH + "/argus_exact_signal/argus_exact_signal_QOc1_full.csv",
    'QOc2': RESULT_FILEPATH + "/argus_exact_signal/argus_exact_signal_QOc2_full.csv",
    'QPc1': RESULT_FILEPATH + "/argus_exact_signal/argus_exact_signal_QPc1_full.csv",
    'QPc2': RESULT_FILEPATH + "/argus_exact_signal/argus_exact_signal_QPc2_full.csv" 
    }

ARGUS_EXACT_SIGNAL_AMB_FILE_LOC = {
    'CLc1': RESULT_FILEPATH + "/argus_exact_signal_amb/argus_exact_signal_amb_CLc1_full.csv", 
    'CLc2': RESULT_FILEPATH + "/argus_exact_signal_amb/argus_exact_signal_amb_CLc2_full.csv", 
    'HOc1': RESULT_FILEPATH + "/argus_exact_signal_amb/argus_exact_signal_amb_HOc1_full.csv", 
    'HOc2': RESULT_FILEPATH + "/argus_exact_signal_amb/argus_exact_signal_amb_HOc2_full.csv", 
    'RBc1': RESULT_FILEPATH + "/argus_exact_signal_amb/argus_exact_signal_amb_RBc1_full.csv", 
    'RBc2': RESULT_FILEPATH + "/argus_exact_signal_amb/argus_exact_signal_amb_RBc2_full.csv", 
    'QOc1': RESULT_FILEPATH + "/argus_exact_signal_amb/argus_exact_signal_amb_QOc1_full.csv",
    'QOc2': RESULT_FILEPATH + "/argus_exact_signal_amb/argus_exact_signal_amb_QOc2_full.csv",
    'QPc1': RESULT_FILEPATH + "/argus_exact_signal_amb/argus_exact_signal_amb_QPc1_full.csv",
    'QPc2': RESULT_FILEPATH + "/argus_exact_signal_amb/argus_exact_signal_amb_QPc2_full.csv" 
    }

ARGUS_EXACT_SIGNAL_AMB2_FILE_LOC = {
    'CLc1': RESULT_FILEPATH + "/argus_exact_signal_amb2/argus_exact_signal_amb2_CLc1_full.csv", 
    'CLc2': RESULT_FILEPATH + "/argus_exact_signal_amb2/argus_exact_signal_amb2_CLc2_full.csv", 
    'HOc1': RESULT_FILEPATH + "/argus_exact_signal_amb2/argus_exact_signal_amb2_HOc1_full.csv", 
    'HOc2': RESULT_FILEPATH + "/argus_exact_signal_amb2/argus_exact_signal_amb2_HOc2_full.csv", 
    'RBc1': RESULT_FILEPATH + "/argus_exact_signal_amb2/argus_exact_signal_amb2_RBc1_full.csv", 
    'RBc2': RESULT_FILEPATH + "/argus_exact_signal_amb2/argus_exact_signal_amb2_RBc2_full.csv", 
    'QOc1': RESULT_FILEPATH + "/argus_exact_signal_amb2/argus_exact_signal_amb2_QOc1_full.csv",
    'QOc2': RESULT_FILEPATH + "/argus_exact_signal_amb2/argus_exact_signal_amb2_QOc2_full.csv",
    'QPc1': RESULT_FILEPATH + "/argus_exact_signal_amb2/argus_exact_signal_amb2_QPc1_full.csv",
    'QPc2': RESULT_FILEPATH + "/argus_exact_signal_amb2/argus_exact_signal_amb2_QPc2_full.csv" 
    }
ARGUS_EXACT_SIGNAL_AMB3_FILE_LOC = {
    'CLc1': RESULT_FILEPATH + "/argus_exact_signal_amb3/argus_exact_signal_amb3_CLc1_full.csv", 
    'CLc2': RESULT_FILEPATH + "/argus_exact_signal_amb3/argus_exact_signal_amb3_CLc2_full.csv", 
    'HOc1': RESULT_FILEPATH + "/argus_exact_signal_amb3/argus_exact_signal_amb3_HOc1_full.csv", 
    'HOc2': RESULT_FILEPATH + "/argus_exact_signal_amb3/argus_exact_signal_amb3_HOc2_full.csv", 
    'RBc1': RESULT_FILEPATH + "/argus_exact_signal_amb3/argus_exact_signal_amb3_RBc1_full.csv", 
    'RBc2': RESULT_FILEPATH + "/argus_exact_signal_amb3/argus_exact_signal_amb3_RBc2_full.csv", 
    'QOc1': RESULT_FILEPATH + "/argus_exact_signal_amb3/argus_exact_signal_amb3_QOc1_full.csv",
    'QOc2': RESULT_FILEPATH + "/argus_exact_signal_amb3/argus_exact_signal_amb3_QOc2_full.csv",
    'QPc1': RESULT_FILEPATH + "/argus_exact_signal_amb3/argus_exact_signal_amb3_QPc1_full.csv",
    'QPc2': RESULT_FILEPATH + "/argus_exact_signal_amb3/argus_exact_signal_amb3_QPc2_full.csv" 
    }
ARGUS_EXACT_SIGNAL_MODE_FILE_LOC = {
    'CLc1': RESULT_FILEPATH + "/argus_exact_mode_signal/argus_exact_signal_mode_CLc1_full.csv", 
    'CLc2': RESULT_FILEPATH + "/argus_exact_mode_signal/argus_exact_signal_mode_CLc2_full.csv", 
    'HOc1': RESULT_FILEPATH + "/argus_exact_mode_signal/argus_exact_signal_mode_HOc1_full.csv", 
    'HOc2': RESULT_FILEPATH + "/argus_exact_mode_signal/argus_exact_signal_mode_HOc2_full.csv", 
    'RBc1': RESULT_FILEPATH + "/argus_exact_mode_signal/argus_exact_signal_mode_RBc1_full.csv", 
    'RBc2': RESULT_FILEPATH + "/argus_exact_mode_signal/argus_exact_signal_mode_RBc2_full.csv", 
    'QOc1': RESULT_FILEPATH + "/argus_exact_mode_signal/argus_exact_signal_mode_QOc1_full.csv",
    'QOc2': RESULT_FILEPATH + "/argus_exact_mode_signal/argus_exact_signal_mode_QOc2_full.csv",
    'QPc1': RESULT_FILEPATH + "/argus_exact_mode_signal/argus_exact_signal_mode_QPc1_full.csv",
    'QPc2': RESULT_FILEPATH + "/argus_exact_mode_signal/argus_exact_signal_mode_QPc2_full.csv" 
    }

ARGUS_EXACT_SIGNAL_MODE_WRONGTIME_FILE_LOC = {
    'CLc1': RESULT_FILEPATH + "/argus_exact_mode_signal_wrongtime/argus_exact_signal_mode_wrongtime_CLc1_full.csv", 
    'CLc2': RESULT_FILEPATH + "/argus_exact_mode_signal_wrongtime/argus_exact_signal_mode_wrongtime_CLc2_full.csv", 
    'HOc1': RESULT_FILEPATH + "/argus_exact_mode_signal_wrongtime/argus_exact_signal_mode_wrongtime_HOc1_full.csv", 
    'HOc2': RESULT_FILEPATH + "/argus_exact_mode_signal_wrongtime/argus_exact_signal_mode_wrongtime_HOc2_full.csv", 
    'RBc1': RESULT_FILEPATH + "/argus_exact_mode_signal_wrongtime/argus_exact_signal_mode_wrongtime_RBc1_full.csv", 
    'RBc2': RESULT_FILEPATH + "/argus_exact_mode_signal_wrongtime/argus_exact_signal_mode_wrongtime_RBc2_full.csv", 
    'QOc1': RESULT_FILEPATH + "/argus_exact_mode_signal_wrongtime/argus_exact_signal_mode_wrongtime_QOc1_full.csv",
    'QOc2': RESULT_FILEPATH + "/argus_exact_mode_signal_wrongtime/argus_exact_signal_mode_wrongtime_QOc2_full.csv",
    'QPc1': RESULT_FILEPATH + "/argus_exact_mode_signal_wrongtime/argus_exact_signal_mode_wrongtime_QPc1_full.csv",
    'QPc2': RESULT_FILEPATH + "/argus_exact_mode_signal_wrongtime/argus_exact_signal_mode_wrongtime_QPc2_full.csv" 
    }

ARGUS_EXACT_SIGNAL_AMB4_3ROLL_FILE_LOC = {
    'CLc1': RESULT_FILEPATH + "/argus_exact_signal_amb4_3roll/argus_exact_signal_amb4_3roll_CLc1_full.csv", 
    'CLc2': RESULT_FILEPATH + "/argus_exact_signal_amb4_3roll/argus_exact_signal_amb4_3roll_CLc2_full.csv", 
    'HOc1': RESULT_FILEPATH + "/argus_exact_signal_amb4_3roll/argus_exact_signal_amb4_3roll_HOc1_full.csv", 
    'HOc2': RESULT_FILEPATH + "/argus_exact_signal_amb4_3roll/argus_exact_signal_amb4_3roll_HOc2_full.csv", 
    'RBc1': RESULT_FILEPATH + "/argus_exact_signal_amb4_3roll/argus_exact_signal_amb4_3roll_RBc1_full.csv", 
    'RBc2': RESULT_FILEPATH + "/argus_exact_signal_amb4_3roll/argus_exact_signal_amb4_3roll_RBc2_full.csv", 
    'QOc1': RESULT_FILEPATH + "/argus_exact_signal_amb4_3roll/argus_exact_signal_amb4_3roll_QOc1_full.csv",
    'QOc2': RESULT_FILEPATH + "/argus_exact_signal_amb4_3roll/argus_exact_signal_amb4_3roll_QOc2_full.csv",
    'QPc1': RESULT_FILEPATH + "/argus_exact_signal_amb4_3roll/argus_exact_signal_amb4_3roll_QPc1_full.csv",
    'QPc2': RESULT_FILEPATH + "/argus_exact_signal_amb4_3roll/argus_exact_signal_amb4_3roll_QPc2_full.csv" 
    }

ARGUS_EXACT_SIGNAL_EARLY_FILE_LOC = {
    'CLc1': RESULT_FILEPATH + "/argus_exact_signal_early/argus_exact_signal_early_CLc1_full.csv", 
    'CLc2': RESULT_FILEPATH + "/argus_exact_signal_early/argus_exact_signal_early_CLc2_full.csv", 
    'HOc1': RESULT_FILEPATH + "/argus_exact_signal_early/argus_exact_signal_early_HOc1_full.csv", 
    'HOc2': RESULT_FILEPATH + "/argus_exact_signal_early/argus_exact_signal_early_HOc2_full.csv", 
    'RBc1': RESULT_FILEPATH + "/argus_exact_signal_early/argus_exact_signal_early_RBc1_full.csv", 
    'RBc2': RESULT_FILEPATH + "/argus_exact_signal_early/argus_exact_signal_early_RBc2_full.csv", 
    'QOc1': RESULT_FILEPATH + "/argus_exact_signal_early/argus_exact_signal_early_QOc1_full.csv",
    'QOc2': RESULT_FILEPATH + "/argus_exact_signal_early/argus_exact_signal_early_QOc2_full.csv",
    'QPc1': RESULT_FILEPATH + "/argus_exact_signal_early/argus_exact_signal_early_QPc1_full.csv",
    'QPc2': RESULT_FILEPATH + "/argus_exact_signal_early/argus_exact_signal_early_QPc2_full.csv" 
    }

ARGUS_EXACT_SIGNAL_FILE_SHORT_LOC = {
    'CLc1': RESULT_FILEPATH + "/argus_exact_signal_short_2_3cond/argus_exact_signal_CLc1_short.csv", 
    'CLc2': RESULT_FILEPATH + "/argus_exact_signal_short_2_3cond/argus_exact_signal_CLc2_short.csv", 
    'HOc1': RESULT_FILEPATH + "/argus_exact_signal_short_2_3cond/argus_exact_signal_HOc1_short.csv", 
    'HOc2': RESULT_FILEPATH + "/argus_exact_signal_short_2_3cond/argus_exact_signal_HOc2_short.csv", 
    'RBc1': RESULT_FILEPATH + "/argus_exact_signal_short_2_3cond/argus_exact_signal_RBc1_short.csv", 
    'RBc2': RESULT_FILEPATH + "/argus_exact_signal_short_2_3cond/argus_exact_signal_RBc2_short.csv", 
    'QOc1': RESULT_FILEPATH + "/argus_exact_signal_short_2_3cond/argus_exact_signal_QOc1_short.csv",
    'QOc2': RESULT_FILEPATH + "/argus_exact_signal_short_2_3cond/argus_exact_signal_QOc2_short.csv",
    'QPc1': RESULT_FILEPATH + "/argus_exact_signal_short_2_3cond/argus_exact_signal_QPc1_short.csv",
    'QPc2': RESULT_FILEPATH + "/argus_exact_signal_short_2_3cond/argus_exact_signal_QPc2_short.csv" 
    }

ARGUS_EXACT_PNL_LOC = {
    'CLc1': RESULT_FILEPATH + "/argus_exact_PNL/argus_exact_PNL_CLc1_full.csv", 
    'CLc2': RESULT_FILEPATH + "/argus_exact_PNL/argus_exact_PNL_CLc2_full.csv", 
    'HOc1': RESULT_FILEPATH + "/argus_exact_PNL/argus_exact_PNL_HOc1_full.csv", 
    'HOc2': RESULT_FILEPATH + "/argus_exact_PNL/argus_exact_PNL_HOc2_full.csv", 
    'RBc1': RESULT_FILEPATH + "/argus_exact_PNL/argus_exact_PNL_RBc1_full.csv", 
    'RBc2': RESULT_FILEPATH + "/argus_exact_PNL/argus_exact_PNL_RBc2_full.csv", 
    'QOc1': RESULT_FILEPATH + "/argus_exact_PNL/argus_exact_PNL_QOc1_full.csv",
    'QOc2': RESULT_FILEPATH + "/argus_exact_PNL/argus_exact_PNL_QOc2_full.csv",
    'QPc1': RESULT_FILEPATH + "/argus_exact_PNL/argus_exact_PNL_QPc1_full.csv",
    'QPc2': RESULT_FILEPATH + "/argus_exact_PNL/argus_exact_PNL_QPc2_full.csv" 
}
ARGUS_EXACT_PNL_AMB_LOC = {
    'CLc1': RESULT_FILEPATH + "/argus_exact_PNL_amb/argus_exact_PNL_amb_CLc1_full.csv", 
    'CLc2': RESULT_FILEPATH + "/argus_exact_PNL_amb/argus_exact_PNL_amb_CLc2_full.csv", 
    'HOc1': RESULT_FILEPATH + "/argus_exact_PNL_amb/argus_exact_PNL_amb_HOc1_full.csv", 
    'HOc2': RESULT_FILEPATH + "/argus_exact_PNL_amb/argus_exact_PNL_amb_HOc2_full.csv", 
    'RBc1': RESULT_FILEPATH + "/argus_exact_PNL_amb/argus_exact_PNL_amb_RBc1_full.csv", 
    'RBc2': RESULT_FILEPATH + "/argus_exact_PNL_amb/argus_exact_PNL_amb_RBc2_full.csv", 
    'QOc1': RESULT_FILEPATH + "/argus_exact_PNL_amb/argus_exact_PNL_amb_QOc1_full.csv",
    'QOc2': RESULT_FILEPATH + "/argus_exact_PNL_amb/argus_exact_PNL_amb_QOc2_full.csv",
    'QPc1': RESULT_FILEPATH + "/argus_exact_PNL_amb/argus_exact_PNL_amb_QPc1_full.csv",
    'QPc2': RESULT_FILEPATH + "/argus_exact_PNL_amb/argus_exact_PNL_amb_QPc2_full.csv" 
    }
ARGUS_EXACT_PNL_AMB2_LOC = {
    'CLc1': RESULT_FILEPATH + "/argus_exact_PNL_amb2/argus_exact_PNL_amb2_CLc1_full.csv", 
    'CLc2': RESULT_FILEPATH + "/argus_exact_PNL_amb2/argus_exact_PNL_amb2_CLc2_full.csv", 
    'HOc1': RESULT_FILEPATH + "/argus_exact_PNL_amb2/argus_exact_PNL_amb2_HOc1_full.csv", 
    'HOc2': RESULT_FILEPATH + "/argus_exact_PNL_amb2/argus_exact_PNL_amb2_HOc2_full.csv", 
    'RBc1': RESULT_FILEPATH + "/argus_exact_PNL_amb2/argus_exact_PNL_amb2_RBc1_full.csv", 
    'RBc2': RESULT_FILEPATH + "/argus_exact_PNL_amb2/argus_exact_PNL_amb2_RBc2_full.csv", 
    'QOc1': RESULT_FILEPATH + "/argus_exact_PNL_amb2/argus_exact_PNL_amb2_QOc1_full.csv",
    'QOc2': RESULT_FILEPATH + "/argus_exact_PNL_amb2/argus_exact_PNL_amb2_QOc2_full.csv",
    'QPc1': RESULT_FILEPATH + "/argus_exact_PNL_amb2/argus_exact_PNL_amb2_QPc1_full.csv",
    'QPc2': RESULT_FILEPATH + "/argus_exact_PNL_amb2/argus_exact_PNL_amb2_QPc2_full.csv" 
    }

ARGUS_EXACT_PNL_AMB3_LOC = {
    'CLc1': RESULT_FILEPATH + "/argus_exact_PNL_amb3/argus_exact_PNL_amb3_CLc1_full.csv", 
    'CLc2': RESULT_FILEPATH + "/argus_exact_PNL_amb3/argus_exact_PNL_amb3_CLc2_full.csv", 
    'HOc1': RESULT_FILEPATH + "/argus_exact_PNL_amb3/argus_exact_PNL_amb3_HOc1_full.csv", 
    'HOc2': RESULT_FILEPATH + "/argus_exact_PNL_amb3/argus_exact_PNL_amb3_HOc2_full.csv", 
    'RBc1': RESULT_FILEPATH + "/argus_exact_PNL_amb3/argus_exact_PNL_amb3_RBc1_full.csv", 
    'RBc2': RESULT_FILEPATH + "/argus_exact_PNL_amb3/argus_exact_PNL_amb3_RBc2_full.csv", 
    'QOc1': RESULT_FILEPATH + "/argus_exact_PNL_amb3/argus_exact_PNL_amb3_QOc1_full.csv",
    'QOc2': RESULT_FILEPATH + "/argus_exact_PNL_amb3/argus_exact_PNL_amb3_QOc2_full.csv",
    'QPc1': RESULT_FILEPATH + "/argus_exact_PNL_amb3/argus_exact_PNL_amb3_QPc1_full.csv",
    'QPc2': RESULT_FILEPATH + "/argus_exact_PNL_amb3/argus_exact_PNL_amb3_QPc2_full.csv" 
    }

ARGUS_EXACT_PNL_MODE_LOC = {
    'CLc1': RESULT_FILEPATH + "/argus_exact_mode_PNL/argus_exact_mode_PNL_CLc1_full.csv", 
    'CLc2': RESULT_FILEPATH + "/argus_exact_mode_PNL/argus_exact_mode_PNL_CLc2_full.csv", 
    'HOc1': RESULT_FILEPATH + "/argus_exact_mode_PNL/argus_exact_mode_PNL_HOc1_full.csv", 
    'HOc2': RESULT_FILEPATH + "/argus_exact_mode_PNL/argus_exact_mode_PNL_HOc2_full.csv", 
    'RBc1': RESULT_FILEPATH + "/argus_exact_mode_PNL/argus_exact_mode_PNL_RBc1_full.csv", 
    'RBc2': RESULT_FILEPATH + "/argus_exact_mode_PNL/argus_exact_mode_PNL_RBc2_full.csv", 
    'QOc1': RESULT_FILEPATH + "/argus_exact_mode_PNL/argus_exact_mode_PNL_QOc1_full.csv",
    'QOc2': RESULT_FILEPATH + "/argus_exact_mode_PNL/argus_exact_mode_PNL_QOc2_full.csv",
    'QPc1': RESULT_FILEPATH + "/argus_exact_mode_PNL/argus_exact_mode_PNL_QPc1_full.csv",
    'QPc2': RESULT_FILEPATH + "/argus_exact_mode_PNL/argus_exact_mode_PNL_QPc2_full.csv" 
    }

ARGUS_EXACT_MODE_PNL_WRONGTIME_LOC = {
    'CLc1': RESULT_FILEPATH + "/argus_exact_mode_PNL_wrongtime/argus_exact_mode_wrongtime_PNL_CLc1_full.csv", 
    'CLc2': RESULT_FILEPATH + "/argus_exact_mode_PNL_wrongtime/argus_exact_mode_wrongtime_PNL_CLc2_full.csv", 
    'HOc1': RESULT_FILEPATH + "/argus_exact_mode_PNL_wrongtime/argus_exact_mode_wrongtime_PNL_HOc1_full.csv", 
    'HOc2': RESULT_FILEPATH + "/argus_exact_mode_PNL_wrongtime/argus_exact_mode_wrongtime_PNL_HOc2_full.csv", 
    'RBc1': RESULT_FILEPATH + "/argus_exact_mode_PNL_wrongtime/argus_exact_mode_wrongtime_PNL_RBc1_full.csv", 
    'RBc2': RESULT_FILEPATH + "/argus_exact_mode_PNL_wrongtime/argus_exact_mode_wrongtime_PNL_RBc2_full.csv", 
    'QOc1': RESULT_FILEPATH + "/argus_exact_mode_PNL_wrongtime/argus_exact_mode_wrongtime_PNL_QOc1_full.csv",
    'QOc2': RESULT_FILEPATH + "/argus_exact_mode_PNL_wrongtime/argus_exact_mode_wrongtime_PNL_QOc2_full.csv",
    'QPc1': RESULT_FILEPATH + "/argus_exact_mode_PNL_wrongtime/argus_exact_mode_wrongtime_PNL_QPc1_full.csv",
    'QPc2': RESULT_FILEPATH + "/argus_exact_mode_PNL_wrongtime/argus_exact_mode_wrongtime_PNL_QPc2_full.csv" 
    }

ARGUS_EXACT_PNL_AMB4_3ROLL_FILE_LOC = {
    'CLc1': RESULT_FILEPATH + "/argus_exact_PNL_amb4_3roll/argus_exact_PNL_amb4_3roll_CLc1_full.csv", 
    'CLc2': RESULT_FILEPATH + "/argus_exact_PNL_amb4_3roll/argus_exact_PNL_amb4_3roll_CLc2_full.csv", 
    'HOc1': RESULT_FILEPATH + "/argus_exact_PNL_amb4_3roll/argus_exact_PNL_amb4_3roll_HOc1_full.csv", 
    'HOc2': RESULT_FILEPATH + "/argus_exact_PNL_amb4_3roll/argus_exact_PNL_amb4_3roll_HOc2_full.csv", 
    'RBc1': RESULT_FILEPATH + "/argus_exact_PNL_amb4_3roll/argus_exact_PNL_amb4_3roll_RBc1_full.csv", 
    'RBc2': RESULT_FILEPATH + "/argus_exact_PNL_amb4_3roll/argus_exact_PNL_amb4_3roll_RBc2_full.csv", 
    'QOc1': RESULT_FILEPATH + "/argus_exact_PNL_amb4_3roll/argus_exact_PNL_amb4_3roll_QOc1_full.csv",
    'QOc2': RESULT_FILEPATH + "/argus_exact_PNL_amb4_3roll/argus_exact_PNL_amb4_3roll_QOc2_full.csv",
    'QPc1': RESULT_FILEPATH + "/argus_exact_PNL_amb4_3roll/argus_exact_PNL_amb4_3roll_QPc1_full.csv",
    'QPc2': RESULT_FILEPATH + "/argus_exact_PNL_amb4_3roll/argus_exact_PNL_amb4_3roll_QPc2_full.csv" 
    }

ARGUS_EXACT_PNL_EARLY_FILE_LOC = {
    'CLc1': RESULT_FILEPATH + "/argus_exact_PNL_early/argus_exact_PNL_early_CLc1_full.csv", 
    'CLc2': RESULT_FILEPATH + "/argus_exact_PNL_early/argus_exact_PNL_early_CLc2_full.csv", 
    'HOc1': RESULT_FILEPATH + "/argus_exact_PNL_early/argus_exact_PNL_early_HOc1_full.csv", 
    'HOc2': RESULT_FILEPATH + "/argus_exact_PNL_early/argus_exact_PNL_early_HOc2_full.csv", 
    'RBc1': RESULT_FILEPATH + "/argus_exact_PNL_early/argus_exact_PNL_early_RBc1_full.csv", 
    'RBc2': RESULT_FILEPATH + "/argus_exact_PNL_early/argus_exact_PNL_early_RBc2_full.csv", 
    'QOc1': RESULT_FILEPATH + "/argus_exact_PNL_early/argus_exact_PNL_early_QOc1_full.csv",
    'QOc2': RESULT_FILEPATH + "/argus_exact_PNL_early/argus_exact_PNL_early_QOc2_full.csv",
    'QPc1': RESULT_FILEPATH + "/argus_exact_PNL_early/argus_exact_PNL_early_QPc1_full.csv",
    'QPc2': RESULT_FILEPATH + "/argus_exact_PNL_early/argus_exact_PNL_early_QPc2_full.csv" 
    }

ARGUS_EXACT_PNL_SHORT_LOC = {
    'CLc1': RESULT_FILEPATH + "/argus_exact_PNL_short/argus_exact_PNL_CLc1_short.csv", 
    'CLc2': RESULT_FILEPATH + "/argus_exact_PNL_short/argus_exact_PNL_CLc2_short.csv", 
    'HOc1': RESULT_FILEPATH + "/argus_exact_PNL_short/argus_exact_PNL_HOc1_short.csv", 
    'HOc2': RESULT_FILEPATH + "/argus_exact_PNL_short/argus_exact_PNL_HOc2_short.csv", 
    'RBc1': RESULT_FILEPATH + "/argus_exact_PNL_short/argus_exact_PNL_RBc1_short.csv", 
    'RBc2': RESULT_FILEPATH + "/argus_exact_PNL_short/argus_exact_PNL_RBc2_short.csv", 
    'QOc1': RESULT_FILEPATH + "/argus_exact_PNL_short/argus_exact_PNL_QOc1_short.csv",
    'QOc2': RESULT_FILEPATH + "/argus_exact_PNL_short/argus_exact_PNL_QOc2_short.csv",
    'QPc1': RESULT_FILEPATH + "/argus_exact_PNL_short/argus_exact_PNL_QPc1_short.csv",
    'QPc2': RESULT_FILEPATH + "/argus_exact_PNL_short/argus_exact_PNL_QPc2_short.csv" 
    }

TEST_FILE_LOC = {
    'CLc1': RESULT_FILEPATH + '/test_results/test_CLc1_full.csv',
    'CLc2': RESULT_FILEPATH + '/test_results/test_CLc2_full.csv',
    'HOc1': RESULT_FILEPATH + '/test_results/test_HOc1_full.csv',
    'HOc2': RESULT_FILEPATH + '/test_results/test_HOc2_full.csv',
    'RBc1': RESULT_FILEPATH + '/test_results/test_RBc1_full.csv',
    'RBc2': RESULT_FILEPATH + '/test_results/test_RBc2_full.csv',
    'QOc1': RESULT_FILEPATH + '/test_results/test_QOc1_full.csv',
    'QOc2': RESULT_FILEPATH + '/test_results/test_QOc2_full.csv',
    'QPc1': RESULT_FILEPATH + '/test_results/test_QPc1_full.csv',
    'QPc2': RESULT_FILEPATH + '/test_results/test_QPc2_full.csv'
}

TEST_FILE_PNL_LOC = {
    'CLc1': RESULT_FILEPATH + '/test_results/test_PNL_CLc1_full.csv',
    'CLc2': RESULT_FILEPATH + '/test_results/test_PNL_CLc2_full.csv',
    'HOc1': RESULT_FILEPATH + '/test_results/test_PNL_HOc1_full.csv',
    'HOc2': RESULT_FILEPATH + '/test_results/test_PNL_HOc2_full.csv',
    'RBc1': RESULT_FILEPATH + '/test_results/test_PNL_RBc1_full.csv',
    'RBc2': RESULT_FILEPATH + '/test_results/test_PNL_RBc2_full.csv',
    'QOc1': RESULT_FILEPATH + '/test_results/test_PNL_QOc1_full.csv',
    'QOc2': RESULT_FILEPATH + '/test_results/test_PNL_QOc2_full.csv',
    'QPc1': RESULT_FILEPATH + '/test_results/test_PNL_QPc1_full.csv',
    'QPc2': RESULT_FILEPATH + '/test_results/test_PNL_QPc2_full.csv'
}

ARGUS_BENCHMARK_PNL_Portfolio_LOC = {}
ARGUS_BENCHMARK_PNL_MASTER_FILE_LOC = None
ARGUS_BENCHMARK_PNL_MASTER_Portfolio_LOC = None
    
TEMP_FILENAME_LIST = ['temp_signal_CLc1.csv',
                      'temp_signal_CLc2.csv',
                      'temp_signal_HOc1.csv',
                      'temp_signal_HOc2.csv',
                      'temp_signal_RBc1.csv',
                      'temp_signal_RBc2.csv',
                      'temp_signal_QOc1.csv',
                      'temp_signal_QOc2.csv',
                      'temp_signal_QPc1.csv',
                      'temp_signal_QPc2.csv']



# mapping for symbols for contract expiry months to months 
MONTHS_TO_SYMBOLS = {
   '1': 'F',
   '2': 'G',
   '3': 'H',
   '4': 'J',
   '5': 'K',
   '6': 'M',
   '7': 'N',
   '8': 'Q',
   '9': 'U',
   '10': 'V',
   '11': 'X',
   '12': 'Z'
}

# Cell location for XLS trader templates
CELL_LOC_DICT = {'CLc1' : {'signal_type': 'G6' , 'target_entry': 'G7', 
                           'target_exit': 'G8', 'stop_loss': 'G9', 
                           'symbol': 'I6', 'number': 'I7'}, 
                'HOc1' : {'signal_type': 'G32' , 'target_entry': 'G33', 
                           'target_exit': 'G34', 'stop_loss': 'G35', 
                            'symbol': 'I32', 'number': 'I33'},
                'RBc1' : {'signal_type': 'G19' , 'target_entry': 'G20', 
                           'target_exit': 'G21', 'stop_loss': 'G22', 
                            'symbol': 'I19', 'number': 'I20'}, 
                'QOc1' :  {'signal_type': 'G45' , 'target_entry': 'G46', 
                            'target_exit': 'G47', 'stop_loss': 'G48', 
                            'symbol': 'I45', 'number': 'I46'} ,
                'QPc1' :  {'signal_type': 'G58' , 'target_entry': 'G59', 
                            'target_exit': 'G60', 'stop_loss': 'G61', 
                            'symbol': 'I58', 'number': 'I59'},  
                'CLc2' : {'signal_type': 'G71' , 'target_entry': 'G72', 
                          'target_exit': 'G73', 'stop_loss': 'G74', 
                'HOc2' : {'signal_type': 'G97' , 'target_entry': 'G98', 
                          'target_exit': 'G99', 'stop_loss': 'G100', 
                           'symbol': 'I97', 'number': 'I98'},
                          'symbol': 'I71', 'number': 'I72'}, 
                'RBc2' : {'signal_type': 'G84' , 'target_entry': 'G85', 
                          'target_exit': 'G86', 'stop_loss': 'G87', 
                           'symbol': 'I84', 'number': 'I85'}, 
                'QOc2' :  {'signal_type': 'G110' , 'target_entry': 'G111', 
                           'target_exit': 'G112', 'stop_loss': 'G113', 
                           'symbol': 'I110', 'number': 'I111'} ,
                'QPc2' :  {'signal_type': 'G123' , 'target_entry': 'G124', 
                           'target_exit': 'G125', 'stop_loss': 'G126', 
                           'symbol': 'I123', 'number': 'I124'}
                 }

