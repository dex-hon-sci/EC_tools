#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 24 17:31:37 2025

@author: dexter
"""
import sys
sys.path.insert(0, "/home/dexter/Euler_Capital_codes/EC_tools")
import datetime
import pandas as pd
import numpy as np
from ta.volatility import AverageTrueRange
import matplotlib.dates as mdates
import matplotlib.pyplot as plt

import EC_tools.utility as util
from EC_tools.strategy_2.VWAPInversionStrategy import loop_signal
from EC_tools.features.features import add_VWAP2df, add_ATR, reindex_dt, resample

from crudeoil_future_const import WRONG_OPEN_HR_DICT, CLOSE_HR_DICT,\
                                  TIMEZONE_DICT, TEST_FILE_LOC,\
                                  VWAP_SIGNAL_PKL_LOC, WRONGWRONG_OPEN_HR_DICT

from crudeoil_future_const import DAILY_MINUTE_DATA_INDI_PKL, RESULT_FILEPATH

def load_source_data_bt(filenames_loc: list) -> dict:
    master_dict = {}
    for filename in filenames_loc:
        temp_dict = util.load_pkl(filename)
        master_dict = dict(master_dict, **temp_dict)
    return master_dict


def plot_VWAP(df, title='', 
              upmakersx=[],upmakersy=[],
              downmakersx=[],downmakersy=[]):
    fig, axs = plt.subplots(1, 1, figsize=(10, 4), layout='constrained')
    fmt = mdates.DateFormatter("%H:%M:%S")

    axs.plot(df['Datetime'].to_list(), df['Open'].to_list(), 'o-', 
             color='r',ms=1,lw=1)
    axs.plot(df['Datetime'].to_list(), df['Settle'].to_list(), 'o-', 
             color='b',ms=1,lw=1)
    axs.plot(df['Datetime'].to_list(), df['High'].to_list(), '-')
    axs.plot(df['Datetime'].to_list(), df['Low'].to_list(), '-')
    axs.fill_between(df['Datetime'].to_list(), df['Low'].to_list(), 
                     df['High'].to_list(), color='g',alpha=0.3)
    
    axs.plot(df['Datetime'].to_list(), df['VWAP'].to_list(), 'o-', 
             color= 'grey', ms=3)
    axs.plot(df['Datetime'].to_list(), (df['VWAP']+1.28*df['VWAP_DEV']).to_list(), 
             '-', lw=1,color="#c5486a")
    axs.plot(df['Datetime'].to_list(), (df['VWAP']-1.28*df['VWAP_DEV']).to_list(), 
             '-', lw=1, color="#c5486a")
    axs.plot(df['Datetime'].to_list(), (df['VWAP']+2.01*df['VWAP_DEV']).to_list(), 
             '-', lw=1, color="#c5486a")
    axs.plot(df['Datetime'].to_list(), (df['VWAP']-2.01*df['VWAP_DEV']).to_list(), 
             '-', lw=1,color="#c5486a")
    axs.plot(df['Datetime'].to_list(), (df['VWAP']+2.51*df['VWAP_DEV']).to_list(), 
             '--', lw=1,color="#c5486a")
    axs.plot(df['Datetime'].to_list(), (df['VWAP']-2.51*df['VWAP_DEV']).to_list(), 
             '--', lw=1, color="#c5486a")
    axs.plot(df['Datetime'].to_list(), (df['VWAP']+3.09*df['VWAP_DEV']).to_list(), 
             '--', lw=1,color="#c5486a")
    axs.plot(df['Datetime'].to_list(), (df['VWAP']-3.09*df['VWAP_DEV']).to_list(), 
             '--', lw=1, color="#c5486a")
    axs.plot(df['Datetime'].to_list(), (df['VWAP']+4.01*df['VWAP_DEV']).to_list(), 
             '--', lw=1, color="#c5486a")
    axs.plot(df['Datetime'].to_list(), (df['VWAP']-4.01*df['VWAP_DEV']).to_list(), 
             '--', lw=1,color="#c5486a")
    
    date_str = df['Datetime'].to_list()[0].strftime('%Y-%m-%d')

    axs.plot(upmakersx, upmakersy,'+',color="green", ms=15)
    axs.plot(downmakersx, downmakersy,'_',color="green",ms=15)
    
    axs.xaxis.set_major_formatter(fmt)
    axs.grid()
    axs.set_title(title)
    axs.set_ylabel('Price')
    axs.set_xlabel('Time')
    plt.legend()
    #plt.show()
    plt.savefig(RESULT_FILEPATH+f"/VWAP_Inversion/plots_2_0sigma/VWAP_{date_str}.png", 
                dpi=150)

            
DEFAULT_KWARGS= {'open_hr_dict': WRONGWRONG_OPEN_HR_DICT, 
                 'close_hr_dict': CLOSE_HR_DICT, 
                 'timezone_dict': TIMEZONE_DICT,
                 'save_filenames_loc':VWAP_SIGNAL_PKL_LOC,
                 'master_signal_filename': "master_signal.csv",
                 'save_or_not': True,
                 'merge_or_not': True,
                 'contract_symbol_condse': False,
                 'loop_symbol': None,
                 'Timezone': "",
                 'N_sigma':2,
                 'TP_multiplier':2, 
                 'SL_multiplier':1,
                 'segment_barmulitplier':4,
                 'time_interval':'15Min'}

EXCHANGE = {'CLc1': "NYSE",
            'CLc2': "NYSE",
            'HOc1': "NYSE",
            'HOc2': "NYSE",
            'RBc1': "NYSE",
            'RBc2': "NYSE",
            'QOc1': "ICE",
            'QOc2': "ICE",
            'QPc1': "ICE",
            'QPc2': "ICE",
                        }

def run_gen_signals(daily_minute_data_pkl: dict[pd.DataFrame], 
                    start_date: datetime.datetime, 
                    end_date: datetime.datetime, 
                    symbol_list: list[str],
                    **kwargs):
    # Run_gen process signals from different assets one-by-one
    # Run_gen function consist of two parts
    # 1) Define "feature" inputs (Depends on the strategy)
    # 2) loop_signal: Go through each days (or some time interval), and 
    #    run the features over the strategy (that make a df if signal objects)
    default_kwargs = DEFAULT_KWARGS
    kwargs = dict(default_kwargs,**kwargs)

    master_dict  = dict()

    for symbol in symbol_list:
        # Load Historical data
        HISTORY_MINUTE_PKL = load_source_data_bt([daily_minute_data_pkl[symbol]])

        #### 
        # reindexing with time
        HISTORY_MINUTE_PKL[symbol] = reindex_dt(HISTORY_MINUTE_PKL[symbol])
        print(HISTORY_MINUTE_PKL[symbol])

        # Preprocess Resample
        # Turn historic data intpo 15 mins interval (default)
        new_df = resample(HISTORY_MINUTE_PKL[symbol], 
                          time_interval=kwargs['time_interval'])
        
        # Select for the range of dates
        new_df = new_df[(new_df['Datetime'] >= start_date) & 
                        (new_df['Datetime'] <= end_date)]
        
        # Define unique trading date for the script to loop through        
        unique_dates = util.get_trading_date(start_date,end_date,
                                             exchange=EXCHANGE[symbol])
        open_hr, close_hr = kwargs['open_hr_dict'][symbol], kwargs['close_hr_dict'][symbol]
        print("Outer_open_close_hr", open_hr, close_hr)
        ######### Feature Extraction Layer #################################
        #### (Can turn this into another changable function later)
    
        # Calculate VWAP, save it in the dataframe as a new column.
        new_df = add_VWAP2df(new_df, unique_dates, open_hr, close_hr)
        new_df = add_ATR(new_df)
        
        print(new_df)
        #plot_VWAP(new_df)
       
        ####################################################################
        asset_name = symbol
        QTY =1 
        print("new_df",new_df)
        print("unique_date",unique_dates)
        print("asset_name", asset_name)
        print("QTY", QTY)
        filename = kwargs['save_filenames_loc'][symbol]
        @util.pickle_save("{}".format(filename), save_or_not=kwargs['save_or_not'])
        def run_gen_MR_indi():
            master_signal_df = loop_signal(new_df, 
                                           unique_dates, 
                                           asset_name, QTY, 
                                           open_hr, close_hr,
                                           **kwargs)
            print("master_signal_df", master_signal_df)
            return master_signal_df
        
        master_dict[symbol] = run_gen_MR_indi()
        
    print("master_dict", master_dict)
    return master_dict

    
if __name__ == "__main__":
    VWAP_SIGNAL_PKL_LOC_C = {
    'CLc1': RESULT_FILEPATH + '/VWAP_Inversion/test_signal.pkl', #VWAP_Inversion_sigma_0_68_signal_CLc1_2021_TP1_5_SL3_full.pkl
    'CLc2': RESULT_FILEPATH + '/VWAP_Inversion/VWAP_Inversion_signal_CLc2_full.pkl',
    'HOc1': RESULT_FILEPATH + '/VWAP_Inversion/VWAP_Inversion_signal_HOc1_full.pkl',
    'HOc2': RESULT_FILEPATH + '/VWAP_Inversion/VWAP_Inversion_signal_HOc2_full.pkl',
    'RBc1': RESULT_FILEPATH + '/VWAP_Inversion/VWAP_Inversion_signal_RBc1_full.pkl',
    'RBc2': RESULT_FILEPATH + '/VWAP_Inversion/VWAP_Inversion_signal_RBc2_full.pkl',
    'QOc1': RESULT_FILEPATH + '/VWAP_Inversion/VWAP_Inversion_signal_QOc1_full.pkl',
    'QOc2': RESULT_FILEPATH + '/VWAP_Inversion/VWAP_Inversion_signal_QOc2_full.pkl',
    'QPc1': RESULT_FILEPATH + '/VWAP_Inversion/VWAP_Inversion_signal_QPc1_full.pkl',
    'QPc2': RESULT_FILEPATH + '/VWAP_Inversion/VWAP_Inversion_signal_QPc2_full.pkl'
    }
    
    #start_date = datetime.datetime(2025,2,1,0,0,0)
    start_date = datetime.datetime(2021,1,1,0,0,0)
    end_date = datetime.datetime(2025,6,16,23,59,59)
    #start_date = datetime.datetime(2025,7,7,0,0,0)
    #end_date = datetime.datetime(2025,7,7,23,59,59)

    #end_date = datetime.datetime(2021,1,5,23,59,59)
    #end_date = datetime.datetime(2023,1,5,23,59,59)
    run_gen_signals(DAILY_MINUTE_DATA_INDI_PKL, 
                    start_date, end_date,
                    ['CLc1'],
                    save_filenames_loc=VWAP_SIGNAL_PKL_LOC_C,
                    N_sigma=1.28, #1.5
                    TP_multiplier = 1,#0.618, # Level 2 exit take-profit
                    SL_multiplier = 1, # Level 1 +/- ATR exit stop-loss
                    segment_barmulitplier=4,
                    reversal_factor_long = 0.75, # Reversal 75% 
                    reversal_factor_short = 0.75,
                    startsignal_index = 1) # Execution start at +2 index 