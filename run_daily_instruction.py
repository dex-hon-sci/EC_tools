#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 15 02:31:06 2024

@author: dexter
"""
import datetime as datetime
import openpyxl

from run_gen_MR_dir import run_gen_MR_signals_list, run_gen_MR_signals_preloaded_list
import EC_tools.utility as util
from crudeoil_future_const import CELL_LOC_DICT, MONTHS_TO_SYMBOLS, \
                                     CAT_LIST, KEYWORDS_LIST, \
                                        SYMBOL_LIST, APC_FILE_LOC, \
                                            HISTORY_DAILY_FILE_LOC, \
                                                HISTORY_MINTUE_FILE_LOC, \
                                                    TEST_FILE_LOC


CONTRACT_NUM_DICT = {'CLc1': 50, 'CLc2': 50, 
                     'HOc1': 50, 'HOc2': 50,
                     'RBc1': 50, 'RBc2': 50,
                     'QOc1': 50, 'QOc2': 50,
                     'QPc1': 50, 'QPc2': 50,}

SIGNAL_PKL = util.load_pkl("crudeoil_future_APC_full.pkl")
HISTORY_DAILY_PKL = util.load_pkl("crudeoil_future_daily_full.pkl")
#HISTORY_MINUTE_PKL = util.load_pkl("crudeoil_future_minute_full.pkl")
OPENPRICE_PKL = util.load_pkl("crudeoil_future_openprice_full.pkl")

def make_new_symbol(date_interest,old_symbol, forward_unit=1):
    """
    A function that generate a new price symbol based on the month and year of 
    today.
    
    """
    month_str = str(date_interest.month+forward_unit)
    year_str = str(date_interest.year)
    new_symbol = old_symbol[0:2] + MONTHS_TO_SYMBOLS[month_str] + year_str[-2:]

    return new_symbol

@util.time_it
def run_MR_list(start_date, end_date):
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
# =============================================================================
#     result = run_gen_MR_signals_list(FILENAME_LIST, CAT_LIST, KEYWORDS_LIST, 
#                             SYMBOL_LIST, 
#                             start_date, end_date,
#                             list(APC_FILE_LOC.values()), 
#                             list(HISTORY_DAILY_FILE_LOC.values()), 
#                             list(HISTORY_MINTUE_FILE_LOC.values())) 
# =============================================================================
    SAVE_SIGNAL_FILENAME_LIST = TEST_FILE_LOC
    result = run_gen_MR_signals_preloaded_list(SAVE_SIGNAL_FILENAME_LIST, 
                                               start_date, end_date,
                                               SIGNAL_PKL, HISTORY_DAILY_PKL, 
                                               OPENPRICE_PKL,
                                               save_or_not = False)
    return result

@util.time_it
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

@util.time_it
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
    
    @util.time_it
    def run_things():
        # Define the date of interest
        date_interest = datetime.datetime(2024,5,1) #datetime.datetime.today()
    
        # Input and output filename
        XL_TEMPLATE_FILENAME = "/home/dexter/Euler_Capital_codes/EC_tools/template/Leigh1.xlsx"
        OUTPUT_FILENAME = "./XLS_trading_sheet_MR_benchmark_{}.xlsx".format(
                                            date_interest.strftime('%Y_%m_%d'))
        
        #Define the end date as the date of interest
        END_DATE = date_interest.strftime("%Y-%m-%d")
        
        START_DATE = (date_interest - datetime.timedelta(days=5)).strftime("%Y-%m-%d")
        #START_DATE2 = (date_interest - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        #Check and update everything
        
        # Run the strategy by list
        SIGNAL_RESULT_DICT = run_MR_list(START_DATE, END_DATE)
    
        # Generate the excel file
        gen_new_xlfile(XL_TEMPLATE_FILENAME, OUTPUT_FILENAME, 
                       date_interest, SIGNAL_RESULT_DICT, 
                       cell_loc_dict = CELL_LOC_DICT, 
                       contract_num_dict=CONTRACT_NUM_DICT)
    run_things()
    # email this to the traders?