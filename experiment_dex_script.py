#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 22 14:09:15 2024

@author: dexter
"""
import numpy as np
import method_gen_MR_dir_signals as mr
import pandas as pd
from scipy.interpolate import CubicSpline, UnivariateSpline
import matplotlib.pyplot as plt

username = "dexter@eulercapital.com.au"
password = "76tileArg56!"
start_date = "2024-03-01"
end_date = "2024-03-31"
categories = 'Argus Nymex WTI month 1, Daily'
keywords = "WTI"
symbol = "CL"
filename_daily = "../test_MS/data_zeroadjust_intradayportara_attempt1/Daily/CL.day"
filename_minute = "../test_MS/data_zeroadjust_intradayportara_attempt1/intraday/1 Minute/CL.001"

##categories = ['Argus Nymex WTI month 1, Daily',  'Argus Nymex Heating oil month 1, Daily']
#categories = ['Argus Nymex WTI month 1, Daily', 
#               'Argus Nymex Heating oil month 1, Daily', 
#               'Argus Nymex RBOB Gasoline month 1, Daily', 
#               'Argus Brent month 1, Daily', 
#               'Argus ICE gasoil month 1, Daily']

#keywords = ["WTI","Heating", "Gasoline","gasoil",'Brent']
#symbol = ['CL', 'HO', 'RB', 'QO', 'QP']



## test one case (check)
## test multiple list (check)
#curve = mr.get_apc_from_server(username, password, "2024-03-01", "2024-03-05", categories,
#                        keywords=keywords,symbol=symbol)

#x = np.arange(0.0025, 0.9975, 0.0025)
#print("curve",curve,type(curve))


def signal_today(price_330):

    
    APCs_this_date_and_contract = curve.iloc[0] # get the ith row 
        
               
    forecast_date = APCs_this_date_and_contract.to_numpy()[0]
    symbol = APCs_this_date_and_contract.to_numpy()[-1]


    apcdat = APCs_this_date_and_contract.to_numpy()[1:-1]
    uapcdat = np.unique(apcdat)
    indices_wanted = np.arange(0, len(apcdat))
    indices_wanted = np.argmin(abs(apcdat[:,None] - uapcdat), axis=0)
    yvals = np.arange(0.0025, 0.9975, 0.0025)[indices_wanted]
    get_330_uk_quantile = CubicSpline(uapcdat, yvals)([price_330])          
    
    quant_330UKtime = get_330_uk_quantile[0]
        
    if quant_330UKtime > 1.0: 
        quant_330UKtime = 0.999990
    elif quant_330UKtime < 0.0:
        quant_330UKtime = 0.000001
        
        
    lag = 0 # number of days lag 
    end_prices = -1

    lag_settlement_data = []
    lag_apc_data = []
    
    curvecurve = mr.get_apc_from_server(username, password, "2024-03-26", "2024-04-03", categories,
                        keywords=keywords,symbol=symbol)
    
    # Get the APC for the past 5 trading days
    #curve1 = mr.get_apc_from_server(username, password, "2024-03-26", "2024-03-27", categories,
    #                    keywords=keywords,symbol=symbol)
    #curve2 = mr.get_apc_from_server(username, password, "2024-03-27", "2024-03-28", categories,
    #                    keywords=keywords,symbol=symbol)
    #curve3 = mr.get_apc_from_server(username, password, "2024-03-31", "2024-04-01", categories,
    #                    keywords=keywords,symbol=symbol)
    #curve4 = mr.get_apc_from_server(username, password, "2024-04-01", "2024-04-02", categories,
    #                    keywords=keywords,symbol=symbol)
    #curve5 = mr.get_apc_from_server(username, password, "2024-04-02", "2024-04-03", categories,
    #                    keywords=keywords,symbol=symbol)
    
    curve1, curve2, curve3, curve4, curve5 = curvecurve.iloc[0], curvecurve.iloc[1], curvecurve.iloc[2], curvecurve.iloc[3], curvecurve.iloc[4]
    lag_apc_data = [curve1,curve2,curve3,curve4,curve5]
    
    print(curve1)
    settledatdata1 = 81.62 #2024-03-26
    settledatdata2 = 81.35 #2024-03-27
    settledatdata3 = 83.17 #2024-03-28
    settledatdata4 = 83.71 #2024-04-01
    settledatdata5 = 85.15 #2024-04-02
    settledatdata6 = 85.43 #2024-04-03
    

    #print("curve1 median", curve1['0.5'], "settled", settledatdata1)
    print("curve2 median", curve1['Forecast Period'], curve1['0.5'], "settle", settledatdata2)
    print("curve3 median", curve2['Forecast Period'], curve2['0.5'], "settle", settledatdata3)
    print("curve4 median", curve3['Forecast Period'], curve3['0.5'], "settle", settledatdata4)
    print("curve5 median", curve4['Forecast Period'], curve4['0.5'], "settle", settledatdata5)
    print("curve6 median", curve5['Forecast Period'], curve5['0.5'], "settle", settledatdata6)

    lag_settlement_data = [settledatdata2, settledatdata3, settledatdata4, settledatdata5, settledatdata6]

    
    lag1q = settledatdata2
    lag2q = settledatdata3
    lag3q = settledatdata4
    lag4q = settledatdata5
    lag5q = settledatdata6
    
    rollinglagq5day = (lag1q+lag2q+lag3q+lag4q+lag5q)/5.0 
    median_apc_5days = np.median([curve1['0.5'],curve2['0.5'],curve3['0.5'],curve4['0.5'],curve5['0.5']])
    
    cond1_buy = lag4q < curve4['0.5']
    cond2_buy = lag5q < curve5['0.5']
    cond3_buy = rollinglagq5day < median_apc_5days
    cond4_buy = quant_330UKtime >= curve['0.1']
    cond_extra_OBOS_buy = True 
    cond_skewness_buy = True # skewness_this_apc > skewness_this_apc_lag1 # increased volatility 
    cond_IQR_buy = True 
           

    cond1_sell = lag4q > curve4['0.5']
    cond2_sell = lag5q > curve5['0.5']
    cond3_sell = rollinglagq5day > median_apc_5days
    cond4_sell = quant_330UKtime <= curve['0.9']
    cond_extra_OBOS_sell = True 
    cond_skewness_sell = True # skewness_this_apc < skewness_this_apc_lag1 # increased volatility 
    cond_IQR_sell = True 
    print("============================================")
    print("symbol", symbol)
    print("rollinglagq5day", rollinglagq5day, "median_apc_5days", median_apc_5days)
    print('quant_330UKtime', quant_330UKtime)
    print("BUY",  cond1_buy and cond2_buy and cond3_buy and cond4_buy)
    print("SELL", cond1_sell and cond2_sell and cond3_sell and cond4_sell)
    print(curve['Forecast Period'])
    print(curve['0.1'],
          curve['0.4'], 
          curve['0.5'], 
          curve['0.6'], 
          curve['0.9'])
    
#signal_today(85.61)

import datetime as datetime



def gen_signal_simple(signal_data, history_data, price_330):
    signal_data, history_data = None, None
    
    today = str(datetime.date.today()-datetime.timedelta(days=1))
    yesterday = str(datetime.date.today()-datetime.timedelta(days=2))
    date_lag_5days = str(datetime.date.today()-datetime.timedelta(days=7))
    
    
    #Input: get apc_today
    today_curve = mr.get_apc_from_server(username, password, yesterday, today, categories,
                        keywords=keywords,symbol=symbol)
    print(today_curve)

    lag_5days_curve = mr.get_apc_from_server(username, password, date_lag_5days, today, categories,
                        keywords=keywords,symbol=symbol)
    
    #Input: get historic data for the last 5 days
    
    lag4q = 85.15 #2024-04-02
    lag5q = 85.43 #2024-04-03  

    settledatdata1, date1 = 81.62, datetime.date(2024,3,26) #2024-03-26
    settledatdata2, date2 = 81.35, datetime.date(2024,3,27)  #2024-03-27
    settledatdata3, date3 = 83.17, datetime.date(2024,3,28)  #2024-03-28
    settledatdata4, date4 = 83.71, datetime.date(2024,4,1)  #2024-04-01
    settledatdata5, date5 = 85.15, datetime.date(2024,4,2)  #2024-04-02
    settledatdata6, date6 = 85.43, datetime.date(2024,4,3)  #2024-04-03
    
    date_list = [date2,date3,date4,date5,date6]
    
    # Date match
    for i in range(5):
        date_a, date_b = date_list[i], lag_5days_curve.iloc[i+1]['Forecast Period'].date()
        print(date_a,date_b)
    
        mr.date_matching(date_a, date_b)
    
    # define the lag two days APC. Get the last two rows in the 5 days lag object
    lag_2days_curve = lag_5days_curve[-2:]
    
    median_apc_5days = np.median([lag_5days_curve.iloc[-5]['0.5'],
                                  lag_5days_curve.iloc[-4]['0.5'],
                                  lag_5days_curve.iloc[-3]['0.5'],
                                  lag_5days_curve.iloc[-2]['0.5'],
                                  lag_5days_curve.iloc[-1]['0.5']])

    print(lag_2days_curve.iloc[0]['0.5'])
    print(lag_2days_curve.iloc[1]['0.5'])
    
    print([lag_5days_curve.iloc[-5]['Forecast Period'],
           lag_5days_curve.iloc[-4]['Forecast Period'],
           lag_5days_curve.iloc[-3]['Forecast Period'],
           lag_5days_curve.iloc[-2]['Forecast Period'],
           lag_5days_curve.iloc[-1]['Forecast Period']])
    
    # benchmark strategy condition

    #Conditions
    # "BUY" condition
    cond1_buy = (lag4q < lag_2days_curve.iloc[0]['0.5'])
    cond2_buy = (lag5q < lag_2days_curve.iloc[1]['0.5'])
    
    # "SELL" condition
    cond1_sell = (lag4q > lag_2days_curve.iloc[0]['0.5'])
    cond2_sell = (lag5q > lag_2days_curve.iloc[1]['0.5'])    
    
    Buy_cond = cond1_buy and cond2_buy
    Sell_cond =  cond1_sell and cond2_sell
    
    
    if Buy_cond and not Sell_cond:
        print("Buy")
    elif Sell_cond and not Buy_cond:
        print("Sell")
    elif not Buy_cond and not Sell_cond:
        print("Neutral")
        
        
quantiles_forwantedprices = [0.1, 0.4, 0.5, 0.6, 0.9]

@mr.time_it
def AAA():
    APCs_this_date_and_contract = curve.iloc[0] # get the ith row 
        
    wanted_quantiles = CubicSpline(np.arange(0.0025, 0.9975, 0.0025),   # wanted quantiles for benchmark algorithm entry/exit/stop loss 
                APCs_this_date_and_contract.to_numpy()[1:-1])(quantiles_forwantedprices)
    
    x = np.arange(0.0025, 0.9975, 0.0025)
        
    return wanted_quantiles
 
    
@mr.time_it
def BBB():
    wanted_quantiles=[]
    APCs_this_date_and_contract = curve.iloc[0] # get the ith row 
        
    for i in quantiles_forwantedprices:
        wanted_quantiles.append(APCs_this_date_and_contract[str(i)])
        
    return wanted_quantiles 
   
#APCs_this_date_and_contract = curve.iloc[0] # get the ith row #
#
#spline_apc_lag1 = CubicSpline(APCs_this_date_and_contract.to_numpy()[1:-1], 
#                            np.arange(0.0025, 0.9975, 0.0025))
#
#spline_apc_lag2 = CubicSpline(np.arange(0.0025, 0.9975, 0.0025),APCs_this_date_and_contract.to_numpy()[1:-1])(np.arange(0.0025, 0.9975, 0.0025)) 
#                            
#spline_apc_lag2 = pd.DataFrame({'x': np.arange(0.0025, 0.9975, 0.0025), 'y':spline_apc_lag2})
#print("spline_apc_lag1", spline_apc_lag1)
#print("spline_apc_lag2", spline_apc_lag2)
#
#spline_apc_lag1 = spline_apc_lag1(79.5)#
#
#print("spline_apc_lag1",spline_apc_lag1)

#AAA()
#BBB()
#gen_signal_simple(None,None)

#history_data_daily = mr.read_portara_data(filename_daily,'CL',start_date,end_date)
#history_data_minute = mr.read_portara_data_minute(filename_minute,'CL', start_date, end_date)
#history_data = mr.merge_portara_data(history_data_daily, history_data_minute)
    
## Deal with the date problem in Portara data
#history_data = mr.portara_data_handling(history_data)

mr.run_generate_MR_signals()


