#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 26 13:06:00 2025

@author: dexter

# New Backtest
# Save in object format, make function to redner it to 
# Signal_generation: def: use strategy, generate signals 
# Signal contains precise execution instructions (MKT: time, LMT:price, Dynamic) 
# Backtest use Trade method to calculate the correct entry/exit point (class attr)
# Trade method also add the correct exeuciton record to the Portfolio object

# input config, Define data (Signal list, historical price) input 
#####
# Backtest type

# Independent: process backtest by signals in a list intead of time
# Concurrent: process backtest by time instead of signal

# LMT order calculation method (RANGE VS CROSSOVER)
# OneActive Signal vs MultActive Signals per asset
#########
# Define Backtest, 
# loop start, define time increment (by signal or by fixed time)
# Look for Signal Segementation (isolate segment to calculate trade return)

# Indepednet:
# 0) Find active signal in a day (basetime setting)
# 1) Group signals by start_time
# 2) Extract intraday_minute_data (based on the ACTIVE signal of that asset)
# 3) Use Trade method, calculate correct entry/exit points
# 3.1) For Dynamic SL, trade caclculation is predefined segment loop.
# 4) Use the exit_point of Trade method, check if the signal in siganl_list comes after it
# If not, pop it. (garbage_signals)

# Concurrent:
# Group all assets signals and price data by date (or any time interval)
# Process all signals simultaneously
# Run crossover point check, align all cross-over points of all asset in
# one sequence sorted by time.
# Process each cross-over point one-by-one and after each step, calculate if 
# there is any factor changes if the strategy relies on aggegrated feedbacks
"""
import sys
sys.path.insert(0, "/home/dexter/Euler_Capital_codes/EC_tools")

import datetime
import copy

import pickle
import pandas as pd
import numpy as np

from EC_tools.portfolio import Portfolio, PortfolioLog
import EC_tools.utility as util
#from EC_tools.trade_2 import Trade

def load_source_data_bt(filenames_loc: list) -> dict:
    master_dict = {}
    for filename in filenames_loc:
        temp_dict = util.load_pkl(filename)
        master_dict = dict(master_dict, **temp_dict)
        
    return master_dict


def reindex_dt(df:pd.DataFrame):
    # Add Datetime column into the dataframe
    date_series = [ele.date() for ele in df['Date'].to_list()]
    time_series = df['Time'].to_list()
    datetime_series = [datetime.datetime.combine(date,time) 
                       for date, time in zip(date_series, time_series)]
    
    df['Datetime'] = datetime_series
    df = df.set_index('Datetime')
    #df.reset_index(inplace=True)
    df['Datetime'] = df.index

    return df

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

def plot_VWAP(df, title='', 
              upmakersx=[],upmakersy=[],
              downmakersx=[],downmakersy=[],
              artists=[],
              open_times =[],open_prices=[], 
              close_times=[], close_prices=[],
              txts = []):
    plt.style.use('dark_background')

    fig, axs = plt.subplots(1, 1, figsize=(10, 4), layout='constrained')
    fmt = mdates.DateFormatter("%H:%M:%S")
    

    axs.plot(df['Datetime'].to_list(), df['VWAP'].to_list(), 'o-', 
             color= 'grey', ms=1)
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
    
    # Plot raw OHLC data
    axs.plot(df['Datetime'].to_list(), df['Open'].to_list(), 'o-', 
             color='r',ms=1,lw=1)
    axs.plot(df['Datetime'].to_list(), df['Settle'].to_list(), 'o-', 
             color='b',ms=1,lw=1)
    axs.plot(df['Datetime'].to_list(), df['High'].to_list(), '-')
    axs.plot(df['Datetime'].to_list(), df['Low'].to_list(), '-')
    axs.fill_between(df['Datetime'].to_list(), df['Low'].to_list(), 
                     df['High'].to_list(), color='g',alpha=0.3)
    # draw boxes
    for art in artists:
        axs.add_patch(art)

        
    date_str = df['Datetime'].to_list()[0].strftime('%Y-%m-%d')
    
    # Add all the open and close pt to the plot
    for opentime, openprice, closetime, closeprice in \
        zip(open_times,open_prices, close_times, close_prices):
        
        entryexitpoints(axs, entry_time=opentime, 
                            exit_time=closetime, 
                            entry_price= openprice,
                            exit_price= closeprice)
    # Draw the PNL on the topleft of the 
    for x,y,z,colour in txts:
        axs.text(x,y+0.05,z,color=colour, fontsize =8, fontweight='bold', zorder =40)
        
    # manage the legend
    twin0=axs.twinx()
    twin0.plot([],[], '-',label=r"$Signal Range (Long)$", color ='cyan')
    twin0.plot([], [], '-', label=r"$\rm Signal Range (Short)$", color ='#e1b865')
    twin0.scatter([],[], label=r"$Open Order$", color ='green', 
               marker ="X",s=50)
    twin0.scatter([],[],label=r"$Close Order$", color ='blue', 
               marker ="X",s=50)

    twin0.legend(loc='upper center',fontsize=13, bbox_to_anchor=(0.5, 1.4),
                 fancybox=True, shadow=False, ncol=3)
    #twin0.set_yscale('log')
    
    #axs.plot(upmakersx, upmakersy,'+',color="green", ms=15)
    #axs.plot(downmakersx, downmakersy,'_',color="green",ms=15)
    
    axs.xaxis.set_major_formatter(fmt)
    axs.grid()
    axs.set_title(title)
    axs.set_ylabel('Price')
    axs.set_xlabel('Time')
    plt.setp(twin0.get_yticklabels(), visible=False)

    #plt.legend()
    #plt.show()
    plt.savefig(RESULT_FILEPATH+f"/VWAP_Inversion/plot_PNL/VWAP_{date_str}.png", 
                dpi=150)



from EC_tools.strategy_2.signal import SignalStatus, SignalType
from EC_tools.trade_2.onetradeperseg import OneTradePerSeg
from EC_tools.trade_2 import Trade
import EC_tools.base.read as read



def activate_signal(signal, latest_datetime):
    print('------------------------------------------')
    print("activate_signal func", signal.status, signal.start_time)
    print("latest_datetime", latest_datetime)
    print("signal.start_time > latest_datetime", signal.start_time > latest_datetime)
    if signal.status == SignalStatus.INACTIVE and\
       signal.start_time > latest_datetime:
           signal.status = SignalStatus.ACTIVE
    return signal

def backtest_engine(trade_method: Trade,
                    portfo: Portfolio,
                    signals: pd.DataFrame,
                    histroy_data: pd.DataFrame, 
                    **kwargs):
    # The main loop for backtesting

    signal_datetime = signals['signal_datetime'].to_list()
    signal_list = signals['signal'].to_list()
    # Loop through the signal list,  
    # Only test for the ACTIVE signals
    
    # Initiate latest_dateime
    latest_datetime = datetime.datetime(2020,12,31,0,0,0)
    
    active_signals = pd.DataFrame()

    # Loop through a list of time-ordered signals
    # This method assumes signals Independent backtest
    for i, signal in enumerate(signal_list):
        print("======================")
        print(i, signal.start_time, signal.type_)
        print('Open',signal.actions[0].kwargs)
        print('TP',signal.actions[1].kwargs)
        print('SL',signal.actions[2].kwargs)
        print('MCO',signal.actions[3].kwargs)
        print("======================")

        #### Signal activation Layer
        # First check and control if this is an active signal
        # Turn on ACTIVE signal if the signal start after 7:30 UTC for enough Volume. 
        if signal.start_time.time() > datetime.time(hour=7,minute=30):
            print("Signal comes after 7:30. Try to activate Signal.")
            # only turn on the signal if the last signal is already resolved
            signal = activate_signal(signal, latest_datetime) #Tested
            print(signal.status)

        #### Trading layer
        # Check if the signal is active
        if signal.status == SignalStatus.ACTIVE:
            # For plot_check
            active_signal_row ={'Datetime':signal.start_time,'signal':signal}
            
            print(f"======{active_signal_row}======")
            # Segmentation: isolate price data segment
            seg_start_dt = signal.start_time
            seg_end_dt = signal.end_time
            print("seg_start_dt, seg_end_dt", seg_start_dt, seg_end_dt)
            sub_history_data = histroy_data[(histroy_data['Datetime']>=seg_start_dt) &
                                            (histroy_data['Datetime']<=seg_end_dt)]
            print(sub_history_data)
            # Run_trade
            T = trade_method(portfo, signal, sub_history_data, i)
            T.run_trade()
            print("LATEST_DATE",latest_datetime)
            # Update the latest_datetime based on the closing trade 
            # of the Trade object for this signal
            print("T.close_pt[0]", T.close_pt[0], T.close_pt[0]==np.nan, type(T.close_pt[0]))
            if np.nan not in T.close_pt:
                print("Is not nan")
                latest_datetime = T.close_pt[0]
            
                active_signals = pd.concat([active_signals, 
                                        pd.DataFrame([active_signal_row])])
            elif np.nan in T.close_pt:
                print("WTGFGGG")
        
    return portfo, active_signals


def entryexitpoints(ax, 
                    entry_time: datetime.datetime = datetime.datetime.today(), 
                    exit_time: datetime.datetime = datetime.datetime.today(), 
                    entry_price: float =  86.05,
                    exit_price: float = 85.70):
    
    print(entry_time, entry_price)
    print(exit_time, exit_price)
    ax.scatter(entry_time, entry_price, s=80, facecolors='none', 
               edgecolors='b', zorder=50)
    ax.plot(entry_time, entry_price, 'x', ms=16, c='blue', zorder=50, 
            label = 'Entry_Point')

    ax.scatter(exit_time, exit_price, s=80, facecolors='none', 
               edgecolors='g', zorder=50)
    ax.plot(exit_time, exit_price, 'x', ms=16, c='green', zorder=50,
            label = 'Exit_Point')
    
def add_text(ax, x, y, s, fontsize=8, color ='g'):
    ax.text(x, y, s, )
    return 

def plot_check(history_data, signals_df, PNL_df):
    DT = PNL_df['Entry_Datetime'].to_list()
    DT = [datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S") 
                    for date_str in DT]
    PNL_df['Datetime'] = DT

    
    unique_dates = list(set([datetime.datetime.combine(dt.date(),
                        datetime.time(0,0,0)) for dt in DT]))
    print(unique_dates)

    # Loop everyday in the xlsx file
    for date in unique_dates:
        print(f"========={date}=========")
        start_dt = datetime.datetime.combine(date.date(), 
                                             datetime.time(hour =3, minute=30))
        end_dt = datetime.datetime.combine(date.date(), 
                                           datetime.time(hour =19, minute=59))
        
        # Isolate the day for plot
        sub_history_data = history_data[(history_data['Datetime'] >=start_dt) &
                                        (history_data['Datetime'] <=end_dt)]
        
        # Isolate the Signals of this day
        sub_signals_df = signals_df[(signals_df['Datetime']>=start_dt)&
                                    (signals_df['Datetime']<=end_dt)]
        sub_signals = sub_signals_df['signal'].to_list()\

        # Draw signal range Box ()
        artists, topleft_coord= [], []
        for S in sub_signals:
            print(S.start_time, S.type_)
            time_width = S.end_time-S.start_time
            price_width = S.actions[1].kwargs['LMT_price'] - S.actions[2].kwargs['LMT_price']
            print('price_width', price_width)
            box_origin_pt = (S.start_time, S.actions[2].kwargs['LMT_price'])
            
            openline_origin_pt = (S.start_time, S.actions[0].kwargs['LMT_price'])
            openprice_width = 0.01
            
            Long_colour, Short_colour = "cyan", "#e1b865"
            
            if S.type_ == SignalType.BUY:
                Edge_colour = Long_colour
            elif  S.type_ == SignalType.SELL:
                Edge_colour = Short_colour
                
            # Define top-left coordinate (for texts later)
            coord = (S.start_time, max(S.actions[1].kwargs['LMT_price'],
                                      S.actions[2].kwargs['LMT_price']))
            topleft_coord.append(coord)

            # Add signal effective range
            artists.append(mpatches.Rectangle(box_origin_pt, 
                                              time_width,  price_width,
                                              ec=Edge_colour, facecolor='None',lw=1.5,
                                              zorder =30))
            # Add open order line
            artists.append(mpatches.Rectangle(openline_origin_pt, 
                                              time_width,  openprice_width,
                                              ec=Edge_colour, facecolor='None', lw=1.5,
                                              zorder =30))


        # Isolate the Trades of this day
        sub_PNL_df = PNL_df[(PNL_df['Datetime'] >=start_dt)&
                            (PNL_df['Datetime'] <=end_dt)]
        
        # Get open and close points
        open_times = sub_PNL_df['Entry_Datetime'].to_list()
        open_times = [datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S") 
                      for date_str in open_times]
        close_times = sub_PNL_df['Exit_Datetime'].to_list()
        close_times = [datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S") 
                      for date_str in close_times]

        open_prices = sub_PNL_df['Entry_Price'].to_list()
        close_prices = sub_PNL_df['Exit_Price'].to_list()
        PNLs = sub_PNL_df['scaled returns from trades'].to_list()
        # Generate PNL text
        topleft_coord
        txt_list = []
        for (x, y), s in zip(topleft_coord, PNLs):
            if s > 0:
                colour = '#b0fe83'
            elif s<0:
                colour = '#fc7878'
            txt = (x,y, f'PNL: {round(s,1)}', colour)
            txt_list.append(txt)
            
        # Plotting
        plot_VWAP(sub_history_data,
                  title=f'{date.strftime("%Y-%m-%d")}', 
                  artists = artists,
                  open_times=open_times, open_prices=open_prices, 
                  close_times=close_times, close_prices=close_prices,
                  txts = txt_list)
    return 

def run_backtest(TradeMethod, signals, 
                 daily_minute_data_pkl, start_date, end_date, **kwargs):
    start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')

    # Run backtest control the range of datetime and signal selections
    # Initialise Portfolio
    P1 = Portfolio()
    USD_initial = {'name':"USD", 'quantity': 10_000_000, 'unit':"dollars", 
                   'asset_type': "Cash", 'misc':{}} # initial fund
    P1.add(USD_initial,datetime=datetime.datetime(2020,12,31))
    
    symbol_list = ['CLc1']
    for symbol in symbol_list:
        # Load Historical data
        HISTORY_MINUTE_PKL = load_source_data_bt([daily_minute_data_pkl[symbol]])
        # reindexing with time
        histroy_data = reindex_dt(HISTORY_MINUTE_PKL[symbol])
        #print(histroy_data)
        # No resample, run the backtest in 1Min intervals
        histroy_data = histroy_data[(histroy_data['Datetime'] >=start_date) &
                                    (histroy_data['Datetime'] <=end_date)]
        
        signals = signals[(signals['signal_datetime'] >=start_date) &
                          (signals['signal_datetime'] <=end_date)]
        
        P1, active_signals = backtest_engine(TradeMethod, P1, signals, histroy_data)
                
        # Save the portfolio
        if kwargs['save_or_not']: # save pkl portfolio
            file = open(kwargs['master_pnl_filename'], 'wb')
            file2 = open(kwargs['active_signal_filename'], 'wb')
            pickle.dump(P1, file)
            pickle.dump(active_signals, file2)
            

    return P1,active_signals

if __name__ == "__main__":
    from crudeoil_future_const import DAILY_MINUTE_DATA_INDI_PKL, RESULT_FILEPATH

    #start_date = datetime.datetime(2024,10,4,0,0,0)
    #end_date = datetime.datetime(2024,10,10,23,59,59)
    start_date = "2025-02-03"
    #end_date = "2021-01-06"

    end_date = "2025-06-16"

    # Load signals
    #Q = util.load_pkl(RESULT_FILEPATH+"/VWAP_Inversion/VWAP_Inversion_sigma_0_68_signal_CLc1_2021_TP1_5_SL3_full.pkl")
    #MASTER_PNL_FILENAME = RESULT_FILEPATH + "/VWAP_Inversion/VWAP_Inversion_sigma_0_68_PNL_CLc1_2021_TP1_5_SL3.pkl"
    Q = util.load_pkl(RESULT_FILEPATH+"/VWAP_Inversion/test_signal.pkl")
    MASTER_PNL_FILENAME = RESULT_FILEPATH + "/VWAP_Inversion/test_PNL.pkl"
    MASTER_AS_FILENAME = RESULT_FILEPATH + "/VWAP_Inversion/test_ActiveSignals.pkl"
    # run backtest
    P, AS = run_backtest(OneTradePerSeg, Q, DAILY_MINUTE_DATA_INDI_PKL, 
                    start_date, end_date,
                    master_pnl_filename = MASTER_PNL_FILENAME,
                    active_signal_filename = MASTER_AS_FILENAME,
                    save_or_not = True)
    
    #P = read.open_portfolio(MASTER_PNL_FILENAME)
    PL = PortfolioLog(P)
    PL.tradebook_filename = RESULT_FILEPATH + "/VWAP_Inversion/test_PNL.csv"
    
    PL.render_tradebook()
    PL.render_tradebook_xlsx()
    ################
    from app.run_VWAP_strat_step1 import add_VWAP2df, add_ATR

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
    #Plot_check
    symbol = "CLc1"
    open_hr, close_hr = '0330','1959'
    XL_filename = RESULT_FILEPATH + "/VWAP_Inversion/test_PNL_.xlsx"
    
    XL_df = read.read_xl_file(XL_filename, sheet_name = symbol)
    XL_df = XL_df.sort_values(by=["Entry_Datetime"], 
                                     ascending=True)
    # plot check
    HISTORY_MINUTE_PKL = load_source_data_bt([DAILY_MINUTE_DATA_INDI_PKL[symbol]])
    unique_dates = util.get_trading_date(datetime.datetime.strptime(start_date, "%Y-%m-%d"),
                                         datetime.datetime.strptime(end_date, "%Y-%m-%d"), 
                                         exchange=EXCHANGE[symbol])

    # reindexing with time
    history_data = reindex_dt(HISTORY_MINUTE_PKL[symbol])
    history_data = add_VWAP2df(history_data, unique_dates, open_hr, close_hr)
    history_data = add_ATR(history_data)

    plot_check(history_data, AS, XL_df)

