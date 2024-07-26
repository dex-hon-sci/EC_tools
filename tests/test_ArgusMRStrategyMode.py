#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 25 11:29:51 2024

@author: dexter
"""

import datetime as datetime
import numpy as np

from EC_tools.strategy import MRStrategyArgus, SignalStatus
import EC_tools.read as read
import EC_tools.math_func as mfunc
from crudeoil_future_const import CAT_LIST, KEYWORDS_LIST, SYMBOL_LIST, \
                                APC_FILE_LOC, HISTORY_DAILY_FILE_LOC,\
                                    HISTORY_MINTUE_FILE_LOC, TIMEZONE_DICT,\
                                        OPEN_HR_DICT, CLOSE_HR_DICT
                                        
from test_strategy import SingleRun

BUY_DATE_STR = "2021-03-02" #Buy date
SELL_DATE_STR = "2022-02-22" #Sell date
NEUTRAL_DATE_STR = "2021-01-27" #Neutral date

BuyTest = SingleRun(BUY_DATE_STR)
SellTest = SingleRun(SELL_DATE_STR)
NeutralTest =  SingleRun(NEUTRAL_DATE_STR)

def test_MRStrategyArgus_gen_data(Test, answer_tuple)->None:
    pass

def test_MRStrategyArgus_rund_cond(Test, signal_status, cond_list)->None:
    pass

def test_MRStrategyArgus_set_EES(Test, EES_answer_tuple)->None:
    pass


