#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 22 14:09:15 2024

@author: dexter
"""
import numpy as np
import utility as util
import pandas as pd
from scipy.interpolate import CubicSpline, UnivariateSpline
import matplotlib.pyplot as plt
import datetime as datetime
import EC_read as EC_read

username = "dexter@eulercapital.com.au"
password = "76tileArg56!"
start_date = "2021-01-01"
end_date = "2021-03-31"
categories = 'Argus Brent month 1, Daily'
keywords = "Brent"
symbol = "QOc1"
filename_daily = "../test_MS/data_zeroadjust_intradayportara_attempt1/Daily/CL.day"
filename_minute = "../test_MS/data_zeroadjust_intradayportara_attempt1/intraday/1 Minute/CL.001"


## test one case (check)
## test multiple list (check)
curve = EC_read.get_apc_from_server(username, password, "2024-03-01", "2024-03-05", categories,
                        keywords=keywords,symbol=symbol)

print(curve)

quantiles_forwantedprices = [0.1, 0.4, 0.5, 0.6, 0.9]

from ArgusPossibilityCurves2 import ArgusPossibilityCurves

apc = ArgusPossibilityCurves(username=username, password=password)
apc.authenticate()
apc.getMetadataCSV(filepath="argus_latest_meta.csv")


# Make the start and end date in the datetime.date format
start_date = datetime.date(int(start_date[:4]), int(start_date[5:7]), int(start_date[8:10]))
end_date = datetime.date(int(end_date[:4]), int(end_date[5:7]), int(end_date[8:10]))

apc_data = apc.getPossibilityCurves(start_date=start_date, end_date=end_date, categories=[categories])



print(apc_data)
