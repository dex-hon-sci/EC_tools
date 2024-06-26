#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jun 23 09:00:12 2024

@author: dexter
"""

# Define the contracts of interest

ASSET_DICT = {"USD": {"unit":'dollars', "asset_type":'Cash'},
              "AUD": {"unit":'dollars',"asset_type":'Cash'},
              "CLc1": {"unit":'contracts',"asset_type":'Future'},
              "CLc2": {"unit":'contracts', "asset_type":'Future'},
              "HOc1": {"unit":'contracts',"asset_type":'Future'},
              "HOc2": {"unit":'contracts',"asset_type":'Future'},
              "RBc1":  {"unit":'contracts',"asset_type":'Future'},
              "RBc2":  {"unit":'contracts',"asset_type":'Future'},
              "QOc1":  {"unit":'contracts',"asset_type":'Future'},
              "QOc2":  {"unit":'contracts',"asset_type":'Future'},
              "QPc1":  {"unit":'contracts',"asset_type":'Future'},
              "QPc2":  {"unit":'contracts',"asset_type":'Future'}
              }

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

round_turn_fees = {
    'CLc1': 24.0,
    'CLc2': 24.0,
    'HOc1': 25.2,
    'HOc2': 25.2,
    'RBc1': 25.2,
    'RBc2': 25.2,
    'QOc1': 24.0,
    'QOc2': 24.0,
    'QPc1': 24.0,
    'QPc2': 24.0
}

OPEN_HR_DICT = {
    'CLc1':'0330',
    'CLc2':'0330',
    'HOc1':'1300',
    'HOc2':'1300',
    'RBc1':'1300',
    'RBc2':'1300',
    'QOc1':'0330',
    'QOc2':'0330',
    'QPc1':'0800',
    'QPc2':'0800'}

CLOSE_HR_DICT = {
    'CLc1':'1958',
    'CLc2':'1958',
    'HOc1':'1828',
    'HOc2':'1828',
    'RBc1':'1828',
    'RBc2':'1828',
    'QOc1':'1958',
    'QOc2':'1958',
    'QPc1':'1628',
    'QPc2':'1628'}


# raw input file list
APC_FILE_LOC = {
    "CLc1": "/home/dexter/Euler_Capital_codes/EC_tools/data/APC_latest/APC_latest_CLc1.csv",
    "CLc2": "/home/dexter/Euler_Capital_codes/EC_tools/data/APC_latest/APC_latest_CLc2.csv",
    "HOc1": "/home/dexter/Euler_Capital_codes/EC_tools/data/APC_latest/APC_latest_HOc1.csv",
    "HOc2": "/home/dexter/Euler_Capital_codes/EC_tools/data/APC_latest/APC_latest_HOc2.csv",
    "RBc1": "/home/dexter/Euler_Capital_codes/EC_tools/data/APC_latest/APC_latest_RBc1.csv",
    "RBc2": "/home/dexter/Euler_Capital_codes/EC_tools/data/APC_latest/APC_latest_RBc2.csv",
    "QOc1": "/home/dexter/Euler_Capital_codes/EC_tools/data/APC_latest/APC_latest_QOc1.csv",
    "QOc2": "/home/dexter/Euler_Capital_codes/EC_tools/data/APC_latest/APC_latest_QOc2.csv",
    "QPc1": "/home/dexter/Euler_Capital_codes/EC_tools/data/APC_latest/APC_latest_QPc1.csv",
    "QPc2": "/home/dexter/Euler_Capital_codes/EC_tools/data/APC_latest/APC_latest_QPc2.csv"
    }

HISTORY_DAILY_FILE_LOC = {
    "CLc1": "/home/dexter/Euler_Capital_codes/EC_tools/data/history_data/Day/CL.day",
    "CLc2": "/home/dexter/Euler_Capital_codes/EC_tools/data/history_data/Day/CL_d01.day",
    "HOc1": "/home/dexter/Euler_Capital_codes/EC_tools/data/history_data/Day/HO.day",
    "HOc2": "/home/dexter/Euler_Capital_codes/EC_tools/data/history_data/Day/HO_d01.day",
    "RBc1": "/home/dexter/Euler_Capital_codes/EC_tools/data/history_data/Day/RB.day",
    "RBc2": "/home/dexter/Euler_Capital_codes/EC_tools/data/history_data/Day/RB_d01.day",
    "QOc1": "/home/dexter/Euler_Capital_codes/EC_tools/data/history_data/Day/QO.day",
    "QOc2": "/home/dexter/Euler_Capital_codes/EC_tools/data/history_data/Day/QO_d01.day",
    "QPc1": "/home/dexter/Euler_Capital_codes/EC_tools/data/history_data/Day/QP.day",
    "QPc2": "/home/dexter/Euler_Capital_codes/EC_tools/data/history_data/Day/QP_d01.day"
}

HISTORY_MINTUE_FILE_LOC = {
    "CLc1": "/home/dexter/Euler_Capital_codes/EC_tools/data/history_data/Minute/CL.001",
    "CLc2": "/home/dexter/Euler_Capital_codes/EC_tools/data/history_data/Minute/CL_d01.001",
    "HOc1": "/home/dexter/Euler_Capital_codes/EC_tools/data/history_data/Minute/HO.001",
    "HOc2": "/home/dexter/Euler_Capital_codes/EC_tools/data/history_data/Minute/HO_d01.001",
    "RBc1": "/home/dexter/Euler_Capital_codes/EC_tools/data/history_data/Minute/RB.001",
    "RBc2": "/home/dexter/Euler_Capital_codes/EC_tools/data/history_data/Minute/RB_d01.001",
    "QOc1": "/home/dexter/Euler_Capital_codes/EC_tools/data/history_data/Minute/QO.001",
    "QOc2": "/home/dexter/Euler_Capital_codes/EC_tools/data/history_data/Minute/QO_d01.001",
    "QPc1": "/home/dexter/Euler_Capital_codes/EC_tools/data/history_data/Minute/QP.001",
    "QPc2": "/home/dexter/Euler_Capital_codes/EC_tools/data/history_data/Minute/QP_d01.001"}

OPEN_PRICE_FILE_LOC = {    
    "CLc1": "/home/dexter/Euler_Capital_codes/EC_tools/data/history_data/open_price/CL_op.day",
    "CLc2": "/home/dexter/Euler_Capital_codes/EC_tools/data/history_data/open_price/CL_d01_op.day",
    "HOc1": "/home/dexter/Euler_Capital_codes/EC_tools/data/history_data/open_price/HO_op.day",
    "HOc2": "/home/dexter/Euler_Capital_codes/EC_tools/data/history_data/open_price/HO_d01_op.day",
    "RBc1": "/home/dexter/Euler_Capital_codes/EC_tools/data/history_data/open_price/RB_op.day",
    "RBc2": "/home/dexter/Euler_Capital_codes/EC_tools/data/history_data/open_price/RB_d01_op.day",
    "QOc1": "/home/dexter/Euler_Capital_codes/EC_tools/data/history_data/open_price/QO_op.day",
    "QOc2": "/home/dexter/Euler_Capital_codes/EC_tools/data/history_data/open_price/QO_d01_op.day",
    "QPc1": "/home/dexter/Euler_Capital_codes/EC_tools/data/history_data/open_price/QP_op.day",
    "QPc2": "/home/dexter/Euler_Capital_codes/EC_tools/data/history_data/open_price/QP_d01_op.day"}

ARGUS_BENCHMARK_SIGNAL_FILE_LOC = {
    'CLc1':'/home/dexter/Euler_Capital_codes/EC_tools/results/benchmark_signals/benchmark_signal_CLc1_full.csv',
    'CLc2':'/home/dexter/Euler_Capital_codes/EC_tools/results/benchmark_signals/benchmark_signal_CLc2_full.csv',
    'HOc1':'/home/dexter/Euler_Capital_codes/EC_tools/results/benchmark_signals/benchmark_signal_HOc1_full.csv',
    'HOc2':'/home/dexter/Euler_Capital_codes/EC_tools/results/benchmark_signals/benchmark_signal_HOc2_full.csv',
    'RBc1':'/home/dexter/Euler_Capital_codes/EC_tools/results/benchmark_signals/benchmark_signal_RBc1_full.csv',
    'RBc2':'/home/dexter/Euler_Capital_codes/EC_tools/results/benchmark_signals/benchmark_signal_RBc2_full.csv',
    'QOc1':'/home/dexter/Euler_Capital_codes/EC_tools/results/benchmark_signals/benchmark_signal_QOc1_full.csv',
    'QOc2':'/home/dexter/Euler_Capital_codes/EC_tools/results/benchmark_signals/benchmark_signal_QOc2_full.csv',
    'QPc1':'/home/dexter/Euler_Capital_codes/EC_tools/results/benchmark_signals/benchmark_signal_QPc1_full.csv',
    'QPc2':'/home/dexter/Euler_Capital_codes/EC_tools/results/benchmark_signals/benchmark_signal_QPc2_full.csv'
    }

 
ARGUS_BENCHMARK_PNL_FILE_LOC = {
    'CLc1':'/home/dexter/Euler_Capital_codes/EC_tools/results/benchmark_PNL/benchmark_PNL_CLc1_full.csv',
    'CLc2':'/home/dexter/Euler_Capital_codes/EC_tools/results/benchmark_PNL/benchmark_PNL_CLc2_full.csv',
    'HOc1':'/home/dexter/Euler_Capital_codes/EC_tools/results/benchmark_PNL/benchmark_PNL_HOc1_full.csv',
    'HOc2':'/home/dexter/Euler_Capital_codes/EC_tools/results/benchmark_PNL/benchmark_PNL_HOc2_full.csv',
    'RBc1':'/home/dexter/Euler_Capital_codes/EC_tools/results/benchmark_PNL/benchmark_PNL_RBc1_full.csv',
    'RBc2':'/home/dexter/Euler_Capital_codes/EC_tools/results/benchmark_PNL/benchmark_PNL_RBc2_full.csv',
    'QOc1':'/home/dexter/Euler_Capital_codes/EC_tools/results/benchmark_PNL/benchmark_PNL_QOc1_full.csv',
    'QOc2':'/home/dexter/Euler_Capital_codes/EC_tools/results/benchmark_PNL/benchmark_PNL_QOc2_full.csv',
    'QPc1':'/home/dexter/Euler_Capital_codes/EC_tools/results/benchmark_PNL/benchmark_PNL_QPc1_full.csv',
    'QPc2':'/home/dexter/Euler_Capital_codes/EC_tools/results/benchmark_PNL/benchmark_PNL_QPc2_full.csv'
}


TEST_FILE_LOC = {
    'CLc1':'/home/dexter/Euler_Capital_codes/EC_tools/results/test_results/test_CLc1_full.csv',
    'CLc2':'/home/dexter/Euler_Capital_codes/EC_tools/results/test_results/test_CLc2_full.csv',
    'HOc1':'/home/dexter/Euler_Capital_codes/EC_tools/results/test_results/test_HOc1_full.csv',
    'HOc2':'/home/dexter/Euler_Capital_codes/EC_tools/results/test_results/test_HOc2_full.csv',
    'RBc1':'/home/dexter/Euler_Capital_codes/EC_tools/results/test_results/test_RBc1_full.csv',
    'RBc2':'/home/dexter/Euler_Capital_codes/EC_tools/results/test_results/test_RBc2_full.csv',
    'QOc1':'/home/dexter/Euler_Capital_codes/EC_tools/results/test_results/test_QOc1_full.csv',
    'QOc2':'/home/dexter/Euler_Capital_codes/EC_tools/results/test_results/test_QOc2_full.csv',
    'QPc1':'/home/dexter/Euler_Capital_codes/EC_tools/results/test_results/test_QPc1_full.csv',
    'QPc2':'/home/dexter/Euler_Capital_codes/EC_tools/results/test_results/test_QPc2_full.csv'
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
            'temp_signal_QPc2.csv'
            ]


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

SYMBOL_LIST = list(HISTORY_DAILY_FILE_LOC.keys())

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

