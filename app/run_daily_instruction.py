#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 15 02:31:06 2024

@author: dexter
"""
# Python import
import sys
import os

sys.path.insert(0, 'C:\\EC_tools-pure-code')

# common package import
import datetime as datetime
import openpyxl

# EC_tools import
import EC_tools.utility as util
from EC_tools.strategy import ArgusMRStrategy

#EC_tools application import
from run_gen_MR_dir import run_gen_MR_signals_list, \
                           run_gen_MR_signals_preloaded,\
                           run_gen_MR_signals_preloaded_single
from crudeoil_future_const import CELL_LOC_DICT, MONTHS_TO_SYMBOLS, \
                                  CAT_LIST, KEYWORDS_LIST, \
                                  SYMBOL_LIST, APC_FILE_LOC, \
                                  HISTORY_DAILY_FILE_LOC, \
                                  HISTORY_MINTUE_FILE_LOC, \
                                  TEST_FILE_LOC, \
                                  DAILY_APC_PKL, DAILY_DATA_PKL, \
                                  DAILY_OPENPRICE_PKL,\
                                  OPEN_HR_DICT, CLOSE_HR_DICT, TIMEZONE_DICT

# adding Folder_2 to the system path

CONTRACT_NUM_DICT = {'CLc1': 1, 'CLc2': 1, 
                     'HOc1': 1, 'HOc2': 1,
                     'RBc1': 1, 'RBc2': 1,
                     'QOc1': 1, 'QOc2': 1,
                     'QPc1': 1, 'QPc2': 1}

CQG_SYMBOL = {'CL':'CLE', 'HO':'HOE', 'RB':'RBE', 
              'QO': 'QO', 'QP':'QP'}


SIGNAL_PKL = util.load_pkl(DAILY_APC_PKL)
HISTORY_DAILY_PKL = util.load_pkl(DAILY_DATA_PKL)
#HISTORY_MINUTE_PKL = util.load_pkl("crudeoil_future_minute_full.pkl")
OPENPRICE_PKL = util.load_pkl(DAILY_OPENPRICE_PKL)

def make_new_symbol(date_interest: datetime.datetime, 
                    old_symbol: str, 
                    forward_unit: int = 1) -> str:
    """
    A function that generate a new price symbol based on the month and year of 
    today.

    Parameters
    ----------
    date_interest : datetime.datetime
        DESCRIPTION.
    old_symbol : str
        DESCRIPTION.
    forward_unit : int, optional
        DESCRIPTION. The default is 1.

    Returns
    -------
    str
        DESCRIPTION.

    """
    contract_symbol = CQG_SYMBOL[old_symbol[0:2]]

    month_str = str(date_interest.month+forward_unit)
    year_str = str(date_interest.year)
    new_symbol = contract_symbol + MONTHS_TO_SYMBOLS[month_str] + year_str[-2:]

    return new_symbol

def truncate_symbol(old_symbol: str) -> str:
    """
    A function that truncate an old asset symbol from Portara format 
    to CQG format.

    Parameters
    ----------
    old_symbol : str
        Portara Format.

    Returns
    -------
    str
        DESCRIPTION.

    """
    contract_symbol = CQG_SYMBOL[old_symbol[0:2]]
    contract_month = old_symbol[7:]
    contract_year = old_symbol[5:7]

    new_symbol = contract_symbol + contract_month + contract_year

    return new_symbol

def run_MR(date_interest,
           buy_range: tuple[float] =\
                      ([0.2,0.25],[0.75,0.8],0.1),
           sell_range: tuple[float] = \
                      ([0.75,0.8],[0.2,0.25],0.9),
           MR_method=run_gen_MR_signals_preloaded_single):
    
    
    SAVE_SIGNAL_FILENAME_LIST = TEST_FILE_LOC
    
    
    result = MR_method(ArgusMRStrategy,
                       SAVE_SIGNAL_FILENAME_LIST, 
                       SIGNAL_PKL, 
                       HISTORY_DAILY_PKL, 
                       date_interest,
                       open_hr_dict = OPEN_HR_DICT, 
                       close_hr_dict = CLOSE_HR_DICT, 
                       timezone_dict = TIMEZONE_DICT,
                       save_or_not = False)
    
    return result 

#@util.time_it
def run_MR_list(start_date: datetime.datetime, 
                end_date: datetime.datetime, 
                MR_method=run_gen_MR_signals_preloaded):
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
    SAVE_SIGNAL_FILENAME_LIST = TEST_FILE_LOC
    result = MR_method(ArgusMRStrategy,
                       SAVE_SIGNAL_FILENAME_LIST, 
                       SIGNAL_PKL, 
                       HISTORY_DAILY_PKL, 
                       OPENPRICE_PKL,
                       start_date, end_date,
                       open_hr_dict = OPEN_HR_DICT, 
                       close_hr_dict = CLOSE_HR_DICT, 
                       timezone_dict = TIMEZONE_DICT,
                       buy_range=([0.25,0.4],[0.6,0.75],0.3),
                       sell_range=([0.6,0.75],[0.25,0.4],0.7),
                       save_or_not = False)
    
    return result

#@util.time_it
def enter_new_value(workbook, 
                    date_interest: datetime.datetime, 
                    cell_loc_dict: dict, 
                    signal_result_dict: dict, 
                    contract_num_dict: dict, 
                    output_filename: str):
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
        print("=====================")
        direction_cell = cell_loc_dict[asset_name]['signal_type']
        entry_cell = cell_loc_dict[asset_name]['target_entry']
        exit_cell = cell_loc_dict[asset_name]['target_exit']
        stop_cell = cell_loc_dict[asset_name]['stop_loss']
        symbol_cell = cell_loc_dict[asset_name]['symbol']
        number_cell = cell_loc_dict[asset_name]['number']
        
        sheet_obj[direction_cell].value = signal_result_dict[asset_name].iloc\
                                                            [-1]['Direction']
        sheet_obj[entry_cell].value = signal_result_dict[asset_name].iloc\
                                                            [-1]['Entry_Price']
        sheet_obj[exit_cell].value = signal_result_dict[asset_name].iloc\
                                                            [-1]['Exit_Price']
        sheet_obj[stop_cell].value = signal_result_dict[asset_name].iloc\
                                                            [-1]['StopLoss_Price']
        print(asset_name)
        print(direction_cell, signal_result_dict[asset_name].iloc\
                                                            [-1]['Direction'])
        print(entry_cell, signal_result_dict[asset_name].iloc\
                                                            [-1]['Entry_Price'])
        print(exit_cell,  signal_result_dict[asset_name].iloc\
                                                            [-1]['Exit_Price'])
        print(stop_cell, signal_result_dict[asset_name].iloc\
                                                            [-1]['StopLoss_Price'])
                                                            
        portara_assetname = signal_result_dict[asset_name].iloc\
                                                            [-1]['Contract_Month']                                      
                                                            
        sheet_obj[symbol_cell].value = truncate_symbol(portara_assetname)
        
        
                                        #make_new_symbol(date_interest,
                                        #               asset_name, 
                                        #               forward_unit = 
                                        #               int(asset_name[-1]))
        sheet_obj[number_cell].value = contract_num_dict[asset_name]
       
    # a function that add new values into the new excel file
    return workbook

#@util.time_it
def gen_new_xlfile(xl_template_filename: str, output_filename: str, 
                   date_interest: datetime.datetime, 
                   signal_result_dict: dict,
                   cell_loc_dict: dict = CELL_LOC_DICT, 
                   contract_num_dict: dict = CONTRACT_NUM_DICT):
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
    wb_obj = openpyxl.load_workbook(xl_template_filename, keep_vba=True)

    wb_obj = enter_new_value(wb_obj, date_interest, cell_loc_dict, 
                             signal_result_dict, 
                             contract_num_dict, output_filename)

    wb_obj.save(output_filename)

    return wb_obj

if __name__ == "__main__":
    XLS_TEMPLATE_FILEPATH  = "/home/dexter/Euler_Capital_codes/EC_tools/app/template/"
    
    #from app.run_send_email import send_trading_sheet_email
    #@util.time_it
    def run_things():
        # Define the date of interest
        date_interest = datetime.datetime(2024,11,20)#datetime.datetime.today()#datetime.datetime(2024,11,29)
        print("date_interest", date_interest)
        is_open = util.market_is_open(date_interest.strftime("%Y-%m-%d"))
        # check if market is open today
        if is_open:
            print("Market Open")
            # Input and output filename
            XL_TEMPLATE_FILENAME = XLS_TEMPLATE_FILEPATH  + \
                                   "argus_exact_MR_strategy_wb_light_auto_on.xlsm"
            OUTPUT_FILENAME = XLS_TEMPLATE_FILEPATH  + \
                              "XLS_trading_sheet_MR_{}.xlsm".format(
                                                date_interest.strftime('%Y_%m_%d'))
            print("OUTPUT_FILENAME", OUTPUT_FILENAME)
            #Define the end date as the date of interest
            END_DATE = date_interest.strftime("%Y-%m-%d")
            
            START_DATE = (date_interest - datetime.timedelta(days=7)).strftime("%Y-%m-%d")
            #START_DATE2 = (date_interest - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
            #Check and update everything
            print("START_DATE, END_DATE", START_DATE, END_DATE)
            # Run the strategy by list
            #date_interest = date_interest.strftime("%Y-%m-%d")


            SIGNAL_RESULT_DICT = run_MR(date_interest)
        
            # Generate the excel file
            gen_new_xlfile(XL_TEMPLATE_FILENAME, OUTPUT_FILENAME, 
                           date_interest, SIGNAL_RESULT_DICT, 
                           cell_loc_dict = CELL_LOC_DICT, 
                           contract_num_dict=CONTRACT_NUM_DICT)
            
            # Send email to Leigh
            #send_trading_sheet_email()
            
            # Run batch script that open the excel file
            #os.chdir("C:\\trading_operation")
            #os.startfile("open_xls.bat")
        else:
            print("Market Close")
    run_things()
    # email this to the traders?