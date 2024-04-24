#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 22 14:09:15 2024

@author: dexter
"""
import numpy as np
import method_gen_MR_dir_signals as mr
import utility as util
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
curve = mr.get_apc_from_server(username, password, "2024-03-01", "2024-03-05", categories,
                        keywords=keywords,symbol=symbol)


        
quantiles_forwantedprices = [0.1, 0.4, 0.5, 0.6, 0.9]

@util.time_it
def AAA():
    APCs_this_date_and_contract = curve.iloc[0] # get the ith row 
        
    wanted_quantiles = CubicSpline(np.arange(0.0025, 0.9975, 0.0025),   # wanted quantiles for benchmark algorithm entry/exit/stop loss 
                APCs_this_date_and_contract.to_numpy()[1:-1])(quantiles_forwantedprices)
    
    x = np.arange(0.0025, 0.9975, 0.0025)
        
    return wanted_quantiles
 
    
@util.time_it
def BBB():
    wanted_quantiles=[]
    APCs_this_date_and_contract = curve.iloc[0] # get the ith row 
        
    for i in quantiles_forwantedprices:
        wanted_quantiles.append(APCs_this_date_and_contract[str(i)])
        
    return wanted_quantiles 
