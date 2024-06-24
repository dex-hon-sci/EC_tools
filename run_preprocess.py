#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jun 23 23:08:50 2024

@author: dexter

The purpose of this script is to convert data into a suitable format for
fast processing. While this script takes a longer time to complete, the rest 
of the back-test workflow will be less time consuming.

"""
import json
import pickle

from crudeoil_future_const import SYMBOL_LIST, HISTORY_DAILY_FILE_LOC,\
                                HISTORY_MINTUE_FILE_LOC, APC_FILE_LOC,\
                                    ARGUS_BENCHMARK_SIGNAL_FILE_LOC
import EC_tools.read as read
import EC_tools.utility as util
from EC_tools.backtest import extract_intraday_minute_data


@util.time_it
def create_aggegrate_pkl(file_loc_list, read_func, save_filename="myfile.pkl"):
    master_dict = dict()
    for symbol in SYMBOL_LIST:
        print(symbol)
        individual_data = read_func(file_loc_list[symbol])

        # Add a symbol column
        individual_data['symbol'] = [symbol for i in range(len(individual_data))]
        
        #storage
        master_dict[symbol] = individual_data
            
    output = open(save_filename, 'wb')
    pickle.dump(master_dict, output)
    output.close()  
        
@util.time_it
def merge_raw_data(filename_list, save_filename, sort_by = "Forecast Period"):
    merged_data = read.concat_CSVtable(filename_list, sort_by= sort_by)
    merged_data.to_csv(save_filename,index=False)
    return merged_data


# =============================================================================
#     
# def create_openprice_pkl(): # may not need it after the pickle operation
#     
#     return
# =============================================================================

@util.time_it    
def load_pkl(filename): # test function
    output = open(filename, 'rb')
    mydict = pickle.load(output)
    
    date_list = ['2021-03-04', '2021-03-05', '2021-03-06', '2021-03-07', '2021-03-08']
    @util.time_it
    def call_individual(date):
        df = mydict['CLc1']
        data = extract_intraday_minute_data(df, date)
        return data
    
    for date in date_list:    
        call_individual(date)
    
    output.close()
    
def run_preprocess():
    """
    The main method for preprocessing. The aim of preprocessing is to create 
    aggegrate pickle files so that the runtime of signal generation and back-test
    can be reduced.
    """
    create_aggegrate_pkl(APC_FILE_LOC, read.read_reformat_APC_data,
                         save_filename="crudeoil_future_APC_full.pkl")
    create_aggegrate_pkl(HISTORY_DAILY_FILE_LOC, read.read_reformat_Portara_daily_data,
                         save_filename="crudeoil_future_daily_full.pkl")
    #create_aggegrate_pkl(HISTORY_MINTUE_FILE_LOC, read.read_reformat_Portara_minute_data,
    #                     save_filename="crudeoil_future_minute_full.pkl")

if __name__ == "__main__":
    
    run_preprocess()

    SIGNAL_LIST = list(ARGUS_BENCHMARK_SIGNAL_FILE_LOC.values())   
    merge_raw_data(SIGNAL_LIST, "benchmark_signal_full.csv", sort_by="APC forecast period")

#load_pkl('crudeoil_future_minute_full.pkl')