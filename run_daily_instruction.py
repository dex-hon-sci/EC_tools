#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 15 02:31:06 2024

@author: dexter
"""
import openpyxl
from run_gen_MR_dir import run_gen_MR_signals_list
import datetime as datetime



XL_TEMPLATE_FILENAME = "/home/dexter/Euler_Capital_codes/EC_tools/template/Leigh1.xlsx"

OUTPUT_FILENAME = "./temptemp.xlsx"

CONTRACT_NUM_DICT = {'CLc1': 50, 'CLc2': 50, 
                     'HOc1': 50, 'HOc2': 50,
                     'RBc1': 50, 'RBc2': 50,
                     'QOc1': 50, 'QOc2': 50,
                     'QPc1': 50, 'QPc2': 50,}

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


FILENAME_LIST = ['temp_signal_CLc1.csv',
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
               'Argus Nymex Heating oil month 1, Daily', 
               'Argus Nymex RBOB Gasoline month 1, Daily', 
               'Argus Brent month 1, Daily', 
               'Argus ICE gasoil month 1, Daily',
                'Argus Nymex WTI month 2, Daily', 
               'Argus Nymex Heating oil month 2, Daily', 
               'Argus Nymex RBOB Gasoline month 2, Daily', 
               'Argus Brent month 2, Daily', 
               'Argus ICE gasoil month 2, Daily']

KEYWORDS_LIST = ["WTI","Heating", "Gasoline",'Brent', "gasoil",
                 "WTI","Heating", "Gasoline",'Brent', "gasoil"]

SYMBOL_LIST = list(HISTORY_DAILY_FILE_LOC.keys())

# mapping for symbols for contract expiry months to months 
months_to_symbols = {
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

# Input the latest settlement data 
auth_pack = {'username': "dexter@eulercapital.com.au",
            'password':"76tileArg56!"}
asset_pack = {"categories" : 'Argus Nymex Heating oil month 1 Daily',
              "keywords" : "Heating",
              "symbol": "HOc1"}

def make_new_symbol(date_interest,old_symbol, forward_unit=1):
    """
    A function that generate a new price symbol based on the month and year of 
    today.
    
    """
    month_str = str(date_interest.month+forward_unit)
    year_str = str(date_interest.year)
    new_symbol = old_symbol[0:2] + months_to_symbols[month_str] + year_str[-2:]

    return new_symbol


def run_MR_list(start_date, start_date_2, end_date):
    """
    Run MR stratgy in a list.

    Parameters
    ----------
    start_date : TYPE
        DESCRIPTION.
    start_date_2 : TYPE
        DESCRIPTION.
    end_date : TYPE
        DESCRIPTION.

    Returns
    -------
    A : TYPE
        DESCRIPTION.

    """
    result = run_gen_MR_signals_list(FILENAME_LIST, CAT_LIST, KEYWORDS_LIST, 
                            SYMBOL_LIST, 
                            start_date, start_date_2, end_date,
                            list(APC_FILE_LOC.values()), 
                            list(HISTORY_DAILY_FILE_LOC.values()), 
                            list(HISTORY_MINTUE_FILE_LOC.values())) 
              
    return result


def enter_new_value(workbook,date_interest, cell_loc_dict, signal_result_dict, 
                    contract_num_dict, output_filename):
    """
    Enter new values to the excel workbook.

    Parameters
    ----------
    workbook : TYPE
        DESCRIPTION.
    date_interest : TYPE
        DESCRIPTION.
    cell_loc_dict : TYPE
        DESCRIPTION.
    signal_result_dict : TYPE
        DESCRIPTION.
    contract_num_dict : TYPE
        DESCRIPTION.
    output_filename : TYPE
        DESCRIPTION.

    Returns
    -------
    workbook : TYPE
        DESCRIPTION.

    """
    sheet_obj = workbook.active
    
    asset_name_list = list(cell_loc_dict.keys())

    for asset_name in asset_name_list:
    #if asset_name == 'CLc1':
        direction_cell = cell_loc_dict[asset_name]['signal_type']
        entry_cell = cell_loc_dict[asset_name]['target_entry']
        exit_cell = cell_loc_dict[asset_name]['target_exit']
        stop_cell = cell_loc_dict[asset_name]['stop_loss']
        symbol_cell = cell_loc_dict[asset_name]['symbol']
        number_cell = cell_loc_dict[asset_name]['number']
        
        sheet_obj[direction_cell].value = signal_result_dict[asset_name].iloc\
                                                            [-1]['direction']
        sheet_obj[entry_cell].value = signal_result_dict[asset_name].iloc\
                                                            [-1]['target entry']
        sheet_obj[exit_cell].value = signal_result_dict[asset_name].iloc\
                                                            [-1]['target exit']
        sheet_obj[stop_cell].value = signal_result_dict[asset_name].iloc\
                                                            [-1]['stop exit']
        sheet_obj[symbol_cell].value = make_new_symbol(date_interest,
                                                       asset_name, 
                                                       forward_unit = 
                                                       int(asset_name[-1]))
        sheet_obj[number_cell].value = contract_num_dict[asset_name]
       
    # a function that add new values into the new excel file
    return workbook

def gen_new_xlfile(xl_template_filename, output_filename, 
                   date_interest, signal_result_dict,
                   cell_loc_dict = CELL_LOC_DICT, 
                    contract_num_dict=CONTRACT_NUM_DICT):
    """
    Generate a new excel file.

    Parameters
    ----------
    xl_template_filename : TYPE
        DESCRIPTION.
    output_filename : TYPE
        DESCRIPTION.
    date_interest : TYPE
        DESCRIPTION.
    signal_result_dict : TYPE
        DESCRIPTION.
    cell_loc_dict : TYPE, optional
        DESCRIPTION. The default is CELL_LOC_DICT.
    contract_num_dict : TYPE, optional
        DESCRIPTION. The default is CONTRACT_NUM_DICT.

    Returns
    -------
    wb_obj : TYPE
        DESCRIPTION.

    """
    wb_obj = openpyxl.load_workbook(xl_template_filename)

    wb_obj = enter_new_value(wb_obj, date_interest, cell_loc_dict, 
                             signal_result_dict, 
                    contract_num_dict, output_filename)

    wb_obj.save(output_filename)

    return wb_obj

if __name__ == "__main__":
    XL_TEMPLATE_FILENAME = "/home/dexter/Euler_Capital_codes/EC_tools/template/Leigh1.xlsx"

    OUTPUT_FILENAME = "./temptemp.xlsx"
    
    date_interest = datetime.datetime.today()
    
    #Check and update everything
    
    # Run the strategy by list
    SIGNAL_RESULT_DICT = run_MR_list('2024-06-13', '2024-06-16', '2024-06-20')

    # Generate the excel file
    gen_new_xlfile(XL_TEMPLATE_FILENAME, OUTPUT_FILENAME, 
                   date_interest, SIGNAL_RESULT_DICT, 
                   cell_loc_dict = CELL_LOC_DICT, contract_num_dict=CONTRACT_NUM_DICT)
    
    # email this to the traders?