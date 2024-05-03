#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 16 01:56:28 2024

@author: dexter
"""

     # This part is to select out the relevant Portara data for this loop
     # make an function for the matching
     portara_dat_filtered = portara_dat[portara_dat['Contract Symbol'].apply(lambda x: str(x)[:-3] == symbol)]
     portara_dat_filtered = portara_dat_filtered.reset_index(drop=True)
     #print("portara_dat_filtered",portara_dat_filtered)

     index_thisapc = portara_dat_filtered[portara_dat_filtered['Date only'] == (forecast_date)] 
     
     print("index_thisapc",index_thisapc)

     
     full_contract_symbol = index_thisapc.to_numpy()[0][-1]
     full_price_code = index_thisapc.to_numpy()[0][-2]
     index_thisapc = index_thisapc.index[0]
     
     print("index_thisapc",index_thisapc)
     ################################     
     #scan with strategy 1
     
     # this is wrong, because when i = 0, it will scan the back of the list
     # Both APC and historical data has to be at least 5 days longer prior to the test date
     
      # the location of this APC in the big list
     apc_curve_lag5 = signal_data.iloc[index_thisapc-6:index_thisapc-1]
     
     print("apc_curve_lag5", apc_curve_lag5,
           "APCs_dat.iloc[i][0]", APCs_dat.iloc[i][0])
     
     curve_today= APCs_this_date_and_contract 
     
     #---------
     # need to make sure there is at least 5 days prior data
     

     # use index to find it
 
         
     day5 = forecast_date.date() - datetime.timedelta(days=5)
     day4 = forecast_date.date() - datetime.timedelta(days=4)
     day3 = forecast_date.date() - datetime.timedelta(days=3)
     day2 = forecast_date.date() - datetime.timedelta(days=2)
     day1 = forecast_date.date() - datetime.timedelta(days=1)
        
     # match the date by APC because there may be weekends and gap data
     
 
     history_data_lag5_5 = history_data.iloc[index_thisapc-5]
     history_data_lag5_4 = history_data.iloc[index_thisapc-4]
     history_data_lag5_3 = history_data.iloc[index_thisapc-3]
     history_data_lag5_2 = history_data.iloc[index_thisapc-2]
     history_data_lag5_1 = history_data.iloc[index_thisapc-1]
     
     #history_data_lag5 = pd.concat([history_data_lag5_5, history_data_lag5_4, 
     #           history_data_lag5_3, history_data_lag5_2, 
     #           history_data_lag5_1])
     
     history_data_lag5 = history_data.iloc[index_thisapc-6: index_thisapc-1]

     #history_data_lag5 = portara_dat_filtered[portara_dat_filtered['Date only'] == (forecast_date) ] 
     
     print("history_data_lag5", history_data_lag5)
     #---------
     print("day5", day5)
     #print("history_data_lag5_1", history_data_lag5_1)
     #print("history_data_lag5_2",history_data_lag5_2)
     #print("history_data_lag5_3",history_data_lag5_3)
     #print("history_data_lag5_4",history_data_lag5_4)
     #print("history_data_lag5_5",history_data_lag5_5)
     
def loop_signal(signal_data, history_data, dict_contracts_quant_signals, 
                loop_start_date="2024-01-10"):
    
    start_date = loop_start_date
    #def wrapper(*args, **kwargs):
        
    # success
    APCs_dat = signal_data[signal_data['Forecast Period'] > start_date]
    portara_dat = history_data[history_data["Date only"] > start_date]
    
    print("APCs_dat", APCs_dat)
    print("portara_dat", portara_dat)
    print("==================================")
    
    for i in np.arange(len(APCs_dat)): # loop through every forecast date and contract symbol 
        
        APCs_this_date_and_contract = APCs_dat.iloc[i] # get the ith row 
        
        forecast_date = APCs_this_date_and_contract.to_numpy()[0]
        symbol = APCs_this_date_and_contract.to_numpy()[-1]
        
                ###############################
        # select for only rows in the history data with date matching the signal data
        dat_330 = portara_dat[portara_dat['Date only'] == forecast_date]
        
        # select for only rows in the history data with date matching the symbol, "CL"
        # can delete 
        dat_330 = dat_330[dat_330['Contract Symbol'].apply(lambda x: str(x)[:-3])==symbol]
        
        quant_330UKtime = np.NaN 
                        
        if dat_330.shape[0] > 0:
                
            price_330 = dat_330.iloc[0].to_numpy()[1] # 330 UK time 
                    
            if np.isnan(price_330):
                continue 
        else: 
            continue # data not available! 
            
        quantiles_forwantedprices = [0.1, 0.4, 0.5, 0.6, 0.9] 
            
        end_prices = -1 
            
        # input quantiles_forwantedprices range in the interpolation of the APC scatter plot
        # Here it get the probabilty at different x axis
        wanted_quantiles = CubicSpline(np.arange(0.0025, 0.9975, 0.0025),   # wanted quantiles for benchmark algorithm entry/exit/stop loss 
                APCs_this_date_and_contract.to_numpy()[1:end_prices])(quantiles_forwantedprices)
        
        #print("dat_330",dat_330)
        #print("wanted_quantiles", wanted_quantiles)
        
        ###############################   
        # calculate the quantile where the starting pice (3:30am UK) sits
        apcdat = APCs_this_date_and_contract.to_numpy()[1:end_prices]
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
            
        
        # input for strategy
        price_330 = quant_330UKtime
            
        ###############################
        apc_curve_lag5, history_data_lag5 = extract_lag_data(signal_data, history_data, date)
        
        # Run the strategy
        # direction = strategy()
        
        direction = argus_benchmark_strategy(
             price_330, history_data_lag5, apc_curve_lag5, curve_today)
        
        print("direction done", direction)

        # Find the quantile of the relevant price for the last two dats
        lag1q = find_quant(curve_today, curve_today['0.5'])  
        lag2q = find_quant(curve_today, curve_today['0.5'])
        
        rollinglagq5day = 0 #np.average(history_data_lag5["Settle"].to_numpy())
        
        ##################################################################################
        # Make a function later to do this 
        # based on the strategy chosen, the setup of the bucket should be different
        # (make_buket)-> Strategy (loop)->(store_to_bucket)
        # function: store_to_bucket
       
def lag_conditions():
    # now moving on to finding the quantiles for lag settlement prices 
    lag = 0 # number of days lag 
    lag_apc_data = []
    lag_settlement_data = []
            
    portara_dat_filtered = portara_dat[portara_dat['Contract Symbol'].apply(lambda x: str(x)[:-3] == symbol)]
    portara_dat_filtered = portara_dat_filtered.reset_index(drop=True)
    
    index_thisapc = portara_dat_filtered[portara_dat_filtered['Date only'] == (forecast_date)] 
    if not index_thisapc.shape[0] > 0: 
        pass
#        continue 
           
    full_contract_symbol = index_thisapc.to_numpy()[0][-1]
    full_price_code = index_thisapc.to_numpy()[0][-2]
    index_thisapc = index_thisapc.index[0]
            
    looplength = 5 
    if use_OB_OS_levels_for_lag_conditions: 
        looplength = 2 
        
    for k in np.arange(looplength): # get the APC for the same contract symbol, but forecast date lag # of days before 
                
        check = False 
        dataexists = True 
                
        while (not check):
            lag -= 1 
                   
            index = index_thisapc + lag 
                   
            try: 
                settledatdata = portara_dat_filtered.iloc[index]
            except:
                check = True # breaks out of loop 
                dataexists = False   
                continue 
                    
            date_thisapc = settledatdata.to_numpy()[0] # get the date for this lag 
                    
            # if forecast_date == pd.to_datetime('2022-05-27') and symbol == 'QO':
                #     print(date_thisapc)
                    
            relevant_APC_lag = APCs_dat[np.logical_and(APCs_dat['APC symbol'] == symbol, 
            APCs_dat['APC Forecast Period'] == date_thisapc)] #<----???? both these two columns being true?
                
            check = relevant_APC_lag.shape[0] > 0
                            
            if lag > 14: # probably dont have data for this contract so move on 
                check = True # break out of while loop 
                dataexists = False # we dont have the data to add yet 
                    
        if dataexists:  # add data for date to list to get settlement prices for lags 
            lag_apc_data.append(relevant_APC_lag)
            lag_settlement_data.append(settledatdata)
                  
                
    if len(lag_apc_data) < looplength: # we don't have all the APC data that we need for this contract symbol and forecast date in benchmark strategy 
        count_no_apc_data += 1 
        pass 
                
def simple_plot(x,y):
    
    plt.plot(x,y,'o-')
    plt.show()
    return None

def conditions():
    

    portara_dat_filtered = portara_dat[portara_dat['Contract Symbol'].apply(lambda x: str(x)[:-3] == symbol)]
    portara_dat_filtered = portara_dat_filtered.reset_index(drop=True)
    
    lag = 0 # number of days lag 
    end_prices = -1

    lag_settlement_data = []
    lag_apc_data = []
    
    spline_apc_lag1 = CubicSpline(lag_apc_data[0].to_numpy()[0][1:end_prices], 
                            np.arange(0.0025, 0.9975, 0.0025))
    spline_apc_lag2 = CubicSpline(lag_apc_data[1].to_numpy()[0][1:end_prices], 
                            np.arange(0.0025, 0.9975, 0.00225))

    spline_apc_lag3 = CubicSpline(lag_apc_data[2].to_numpy()[0][1:end_prices], 
                            np.arange(0.0025, 0.9975, 0.00225))
    spline_apc_lag4 = CubicSpline(lag_apc_data[3].to_numpy()[0][1:end_prices], 
                            np.arange(0.0025, 0.9975, 0.00225))
    spline_apc_lag5 = CubicSpline(lag_apc_data[4].to_numpy()[0][1:end_prices], 
                            np.arange(0.0025, 0.9975, 0.00225))


    #spline_apc_lag1 = spline_apc_lag1([lag_settlement_data[0].to_numpy()[2]])
    #spline_apc_lag2 = spline_apc_lag2([lag_settlement_data[1].to_numpy()[2]])
    #spline_apc_lag3 = spline_apc_lag3([lag_settlement_data[2].to_numpy()[2]])
    #spline_apc_lag4 = spline_apc_lag4([lag_settlement_data[3].to_numpy()[2]])
    #spline_apc_lag5 = spline_apc_lag5([lag_settlement_data[4].to_numpy()[2]])

    lag1q = spline_apc_lag1[0]
    if lag1q < 0.0:
        lag1q = 0.00001
    if lag1q > 1.0:
        lag1q = 0.99999
    lag2q = spline_apc_lag2[0]
    if lag2q < 0.0:
        lag2q = 0.00001
    if lag2q > 1.0:
        lag2q = 0.99999
    lag3q = spline_apc_lag3[0]
    if lag3q < 0.0:
        lag3q = 0.00001
    if lag3q > 1.0:
        lag3q = 0.99999
    lag4q = spline_apc_lag4[0]
    if lag4q < 0.0:
        lag4q = 0.00001
    if lag4q > 1.0:
        lag4q = 0.99999
    lag5q = spline_apc_lag5[0]
    if lag5q < 0.0:
        lag5q = 0.00001
    if lag5q > 1.0:
        lag5q = 0.99999
        
    rollinglagq5day = (lag1q+lag2q+lag3q+lag4q+lag5q)/5.0 

    cond1_buy = lag1q < 0.5
    cond2_buy = lag2q < 0.5
    cond3_buy = rollinglagq5day < 0.5
    cond4_buy = quant_330UKtime >= 0.1
    cond_extra_OBOS_buy = True 
    cond_skewness_buy = True # skewness_this_apc > skewness_this_apc_lag1 # increased volatility 
    cond_IQR_buy = True 
           
    cond1_sell = lag1q > 0.5
    cond2_sell = lag2q > 0.5
    cond3_sell = rollinglagq5day > 0.5
    cond4_sell = quant_330UKtime <= 0.9
    cond_extra_OBOS_sell = True 
    cond_skewness_sell = True # skewness_this_apc < skewness_this_apc_lag1 # increased volatility 
    cond_IQR_sell = True 
    
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
        

def cal_APC_pdf(apc_prices):
    #cdf
    even_spaced_prices = np.arange(np.min(apc_prices), np.max(apc_prices), 0.005)
    
    print(len(even_spaced_prices))
    
    spline_apc_rev = UnivariateSpline(apc_prices, np.arange(0.0025, 0.9975, 0.0025), s = 0)
    quantiles_even_prices = spline_apc_rev(even_spaced_prices)

    dq = even_spaced_prices[1]-even_spaced_prices[0]
    deriv = fd.FinDiff(0, dq, 1)
    pdf = deriv(quantiles_even_prices)
    
    print(len(pdf))
    
    spline_pdf = UnivariateSpline(even_spaced_prices, pdf,  s = 0.0015)
    pdf = spline_pdf(even_spaced_prices)
    
    print(len(pdf))
    return even_spaced_prices, pdf

def cal_APC_pdf_2(apc_prices):
    #cdf
    x = np.arange(0.0025, 0.9975, 0.0025)
    print(len(x))
    
    spline_apc = UnivariateSpline(x, apc_prices, s = 0)
    
    quantiles_even_prices = spline_apc(x)
    print(quantiles_even_prices)
    
    dq = x[1]-x[0]
    deriv = fd.FinDiff(0, dq, 1)
    pdf = deriv(quantiles_even_prices)
        
    #spline_pdf = UnivariateSpline(x, pdf,  s = 0.0015)
    #pdf = spline_pdf(x)
    
    print(len(pdf))
    return pdf
    

def cal_APC_pdf(apc_prices):
    #cdf
    even_spaced_prices = np.arange(np.min(apc_prices), np.max(apc_prices), 0.005)
    spline_apc_rev = UnivariateSpline(apc_prices, np.arange(0.0025, 0.9975, 0.0025), s = 0)
    quantiles_even_prices = spline_apc_rev(even_spaced_prices)

    dq = even_spaced_prices[1]-even_spaced_prices[0]
    deriv = fd.FinDiff(0, dq, 1)
    pdf = deriv(quantiles_even_prices)
    spline_pdf = UnivariateSpline(even_spaced_prices, pdf,  s = 0.0015)
    pdf = spline_pdf(even_spaced_prices)
    
    return pdf
    
#tested
def extract_lag_data(signal_data, history_data, date, lag_size=5):
    """
    Extract the Lag data based on a given date.

    Parameters
    ----------
    signal_data : pandas dataframe
        The signal data.
    history_data : pandas dataframe
        The historical data.
    date : str
        The date of interest, format like this "2024-01-10".
    lag_size : TYPE, optional
        The size of the lag window. The default is 5 (days).

    Returns
    -------
    signal_data_lag : pandas data frame
        The signal data five (lag_size) days prior to the given date.
    history_data_lag : pandas data frame
        The historical data five (lag_size) days prior to the given date.

    """

    # Find the row index of the history data first
    row_index = history_data.index[history_data['Date only'] == date].tolist()[0]
    
    # extract exactly 5 (default) lag days array
    history_data_lag = history_data.loc[row_index-lag_size:row_index-1]

    # use the relevant date from history data to get signal data to ensure matching date
    window = history_data_lag['Date only'].tolist()
    
    #Store the lag signal data in a list
    signal_data_lag = signal_data[signal_data['Forecast Period'] == window[0]]
    
    for i in range(lag_size-1):
        curve = signal_data[signal_data['Forecast Period'] == window[i+1]]
        signal_data_lag = pd.concat([signal_data_lag, curve])
        
    return signal_data_lag, history_data_lag

