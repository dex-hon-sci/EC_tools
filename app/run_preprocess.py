"""
Created on Sun Jun 23 23:08:50 2024

@author: dexter

The purpose of this script is to convert data into a suitable format for
fast processing. While this script takes a longer time to complete, the rest 
of the back-test workflow will be less time consuming.

"""
import json
import pickle
import pandas as pd
from crudeoil_future_const import SYMBOL_LIST, HISTORY_DAILY_FILE_LOC,\
                                  HISTORY_MINTUE_FILE_LOC, APC_FILE_LOC,\
                                  ARGUS_BENCHMARK_SIGNAL_FILE_LOC,\
                                  OPEN_PRICE_FILE_LOC, OPEN_HR_DICT,\
                                  DAILY_DATA_PKL, DAILY_MINUTE_DATA_PKL,\
                                  DAILY_APC_PKL, DAILY_OPENPRICE_PKL,\
                                  APC_FILE_MONTHLY_LOC, APC_FILE_WEEKLY_30AVG_LOC,\
                                  MONTHLY_APC_PKL, WEEKLY_30AVG_APC_PKL,\
                                  HISTORY_DAILY_CUMAVG_IN_MONTH,\
                                  HISTORY_MINUTE_CUMAVG_IN_MONTH,\
                                  DAILY_CUMAVG_MONTH_PKL, MINUTE_CUMAVG_MONTH_PKL,\
                                  SYMBOL_LIST_SHORT


import EC_tools.read as read
import EC_tools.utility as util

@util.time_it
def create_aggegrate_pkl(file_loc_list: list[str], 
                         read_func, 
                         save_filename: str ="myfile.pkl",
                         symbol_list = SYMBOL_LIST) -> None:
    master_dict = dict()
    for symbol in symbol_list:
        print(symbol)
        individual_data = read_func(file_loc_list[symbol])

        # Add a symbol column
        individual_data['symbol'] = [symbol for i in range(len(individual_data))]
        
        #storage
        master_dict[symbol] = individual_data
            
    print("Saving")
    output = open(save_filename, 'wb')
    pickle.dump(master_dict, output)
    print("Saved")

    output.close()  
    

@util.time_it
def create_open_price_list(history_daily_file_loc: dict, 
                           history_minute_file_loc: dict,
                           symbol_list = SYMBOL_LIST) -> None:
    
    for symbol in symbol_list:
        history_daily_file = read.read_reformat_Portara_daily_data(
                                        history_daily_file_loc[symbol])
        history_minute_file = read.read_reformat_Portara_minute_data(
                                        history_minute_file_loc[symbol])
        
        @util.save_csv(OPEN_PRICE_FILE_LOC[symbol],save_or_not=True)
        def cal_open_price_indi():
            open_price = read.find_price_by_time(history_daily_file, 
                                                 history_minute_file,
                                                 open_hr=OPEN_HR_DICT[symbol])
            return open_price
        
        # execution
        cal_open_price_indi()
        
    print("Open price data created.")
    
def create_cumavg_list(history_daily_file_loc: dict, 
                       symbol_list=SYMBOL_LIST,
                       save_filenames = HISTORY_DAILY_CUMAVG_IN_MONTH):
    
    for symbol in symbol_list:
        history_daily_file = read.read_reformat_Portara_daily_data(
                                        history_daily_file_loc[symbol])
        
        @util.save_csv(save_filenames[symbol],save_or_not=True)
        def cal_cumavg_indi():
            cumavg_price_data = read.cal_cumavg(history_daily_file)
            return cumavg_price_data
        cal_cumavg_indi()
    print('Daily Cumulative average within each month is calculated.')
 
def create_minute_cumavg_list(history_minute_file_loc: dict,
                              cumavg_price_file_loc: dict,
                              symbol_list=SYMBOL_LIST,
                              save_filenames = HISTORY_MINUTE_CUMAVG_IN_MONTH):
    for symbol in symbol_list:
        print(symbol)
        history_minute_file = read.read_reformat_Portara_minute_data(
                                        history_minute_file_loc[symbol], 
                                        time_to_datetime=True)
                
        print("history_minute_file", history_minute_file, 
              history_minute_file['Time'].iloc[0], type(history_minute_file['Time'].iloc[0]))
        cumavg_price_file = pd.read_csv(cumavg_price_file_loc[symbol])
        
        @util.save_csv(save_filenames[symbol], save_or_not=True)
        def cal_minute_cumavg_indi():
            cumavg_price_data = read.cal_cumavg_minute(history_minute_file, 
                                                       cumavg_price_file)
            
            print(cumavg_price_data)
            return cumavg_price_data
        cal_minute_cumavg_indi()
        
    print('Minute Cumulative average within each month is calculated.')

        
# =============================================================================
# @util.time_it    
# def load_pkl(filename): # test function
#     output = open(filename, 'rb')
#     mydict = pickle.load(output)
#     
#     date_list = ['2021-03-04', '2021-03-05', '2021-03-06', '2021-03-07', '2021-03-08']
#     @util.time_it
#     def call_individual(date):
#         df = mydict['CLc1']
#         data = extract_intraday_minute_data(df, date)
#         return data
#     
#     for date in date_list:    
#         call_individual(date)
#     
#     output.close()
# =============================================================================
    
def run_preprocess() -> None:
    """
    The main method for preprocessing. The aim of preprocessing is to create 
    aggegrate pickle files so that the runtime of signal generation and back-test
    can be reduced.
    """
    print("============Running Preprocessing==========")
    
    # load all raw data into pkl format
    #create_aggegrate_pkl(APC_FILE_LOC, read.read_reformat_APC_data,
    #                     save_filename = DAILY_APC_PKL)
    #create_aggegrate_pkl(HISTORY_DAILY_FILE_LOC, read.read_reformat_Portara_daily_data,
    #                     save_filename = DAILY_DATA_PKL)
    #create_aggegrate_pkl(HISTORY_MINTUE_FILE_LOC, read.read_reformat_Portara_minute_data,
    #                     save_filename = DAILY_MINUTE_DATA_PKL)
    
    # calculate and load the open price data into a pkl file
    #create_open_price_list(HISTORY_DAILY_FILE_LOC, HISTORY_MINTUE_FILE_LOC)
    #create_aggegrate_pkl(OPEN_PRICE_FILE_LOC, read.read_reformat_openprice_data,
    #                     save_filename = DAILY_OPENPRICE_PKL)
    
    # make monthly APC pkl
    #create_aggegrate_pkl(APC_FILE_MONTHLY_LOC, read.read_reformat_APC_data,
    #                     save_filename = MONTHLY_APC_PKL,
    #                     symbol_list = SYMBOL_LIST_SHORT)
    #create_aggegrate_pkl(APC_FILE_WEEKLY_30AVG_LOC, read.read_reformat_APC_data,
    #                     save_filename = WEEKLY_30AVG_APC_PKL,
    #                     symbol_list = SYMBOL_LIST_SHORT)

    #create_cumavg_list(HISTORY_DAILY_FILE_LOC)
    #create_aggegrate_pkl(HISTORY_DAILY_CUMAVG_IN_MONTH, read.read_reformat_generic,
    #                     save_filename = DAILY_CUMAVG_MONTH_PKL)
    
    #create_minute_cumavg_list(HISTORY_MINTUE_FILE_LOC, HISTORY_DAILY_CUMAVG_IN_MONTH,
    #                          )
    create_aggegrate_pkl(HISTORY_MINUTE_CUMAVG_IN_MONTH, 
                         read.read_reformat_dateNtime,
                         save_filename = MINUTE_CUMAVG_MONTH_PKL)

if __name__ == "__main__":
    print(SYMBOL_LIST)
    run_preprocess()

