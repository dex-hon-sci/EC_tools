#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May  2 12:23:51 2025

@author: dexter

Run Backtest for dynamic SL. 
It reads in the 'features' of the Signal instruction.
Read in the multiple SL level and build a target cross over point and 
loop through them.
"""
# Python imports
import datetime as datetime
import time
import pickle
import copy
import pandas as pd
import numpy as np
# EC_tools imports
import EC_tools.base.read as read
import EC_tools.backtest as backtest
import EC_tools.utility as util
from EC_tools.backtest import LoopType, Loop
from EC_tools.trade import OneTradePerDay, MultiTradePerMonth
#from EC_tools.simple_trade import onetrade_simple
from EC_tools.portfolio import Portfolio
from EC_tools.trade import Trade 
from EC_tools.trade.order import Order, ExecuteOrder

from crudeoil_future_const import OPEN_HR_DICT, CLOSE_HR_DICT, SIZE_DICT, \
                                  WRONG_OPEN_HR_DICT,\
                                  DATA_FILEPATH, RESULT_FILEPATH,\
                                  TIMEZONE_DICT,\
                                  ARGUS_EXACT_SIGNAL_FILE_LOC, \
                                  TEST_FILE_LOC, TEST_FILE_PNL_LOC,\
                                  DAILY_MINUTE_DATA_PKL, MINUTE_CUMAVG_MONTH_PKL,\
                                  DAILY_MINUTE_DATA_INDI_PKL,\
                                  OIL_FUTURES_FEE, OIL_FUTURES_FEES, \
                                  TRAIL_PRICE_DELTA

DEFAULT_KWARGS= {'price_proxy':'Open',
                 'give_obj_name': 'USD',
                 'get_obj_quantity': 1,
                 'open_hr_dict': WRONG_OPEN_HR_DICT, 
                 'close_hr_dict': CLOSE_HR_DICT, 
                 'timezone_dict': TIMEZONE_DICT,
                 'save_filenames_loc':TEST_FILE_LOC,
                 'fee_dict': OIL_FUTURES_FEES,
                 'strategy_name': "Unamed Strategy",
                 'save_or_not': False,
                 'merge_or_not': True,
                 'plot_or_not' : False,
                 'open_hr': '0000', # assume the whole duration of the trading day
                 'close_hr': '2359',
                 'signal_file_loc': TEST_FILE_LOC, 
                 'save_file_loc': TEST_FILE_PNL_LOC, 
                 'master_signal_filename': 'master_signal.csv', 
                 'master_pnl_filename': 'master_pnl.csv',
                 'histroy_intraday_data_pkl': dict(),
                 'selected_directions': ["Buy", "Sell"],
                 'method': "preload",
                 'trail_price_delta':15}



class OneTradePerDay_DYNSL(Trade):
    """
    A class that perform one trade per day, the simplest form of trading.
    
    Four possible outcomes:
    1) Find the earliest entry point in the price action chart, 
    2) exit the position  as soon as the price it the target entry. 
    3) If the price hit the stop loss first, exit at stop loass. 
    4) If netiher the target exit nor the stop loss is hit, exit the trade 
        at the closing hour.
        
    """
    def __init__(self, portfolio, 
                 trade_id: int = 0, 
                 trail_price_delta: float = 0,
                 direction: str ='Neutral',
                 cross_decision: str = 'SL_B',
                 dyn_list: list[float] = [0,0,0,0]):
        super().__init__(portfolio)
        self.trade_id = trade_id
        
        # A set of points for execute_position function to take record. 
        # Only the final decision is taken as class variables
        self._TE_pt = (np.nan,np.nan)
        self._TP_pt = (np.nan,np.nan)
        self._SL_pt = (np.nan,np.nan)
        self._close_pt = (np.nan,np.nan)
        
        # the price difference for the trailing differences for dynamic SL
        if direction == 'Buy':
            self._trail_price_delta = trail_price_delta 
        elif direction =='Sell':
            self._trail_price_delta = -1.0*trail_price_delta
        else:
            self._trail_price_delta = 0
            
        # scenario for cross-sections decision]
        self._cross_decision = cross_decision
        self._dyn_list = dyn_list
        
    def cross_section_choice(self, num: int,
                             this_SL_price: float, 
                             close_pt: tuple[datetime.datetime, float],
                             trail_price_delta = 0):
     
        if self._cross_decision == 'SL_A':
            # scenario A
            self._dyn_list[num+1] = this_SL_price
            #next_SL_price = this_SL_price
        elif self._cross_decision == 'SL_B':
            # scenario B
            #self._SL_pt = trunc_dicts_val[num]['close']
            self._SL_pt = close_pt
        elif self._cross_decision == 'SL_C':
            # scenario C
            #next_SL_price = close_pt[1]+ trail_price_delta
            self._dyn_list[num+1] = close_pt[1]+ trail_price_delta
        return
            
    def choose_EES_values(self, 
                          trunc_dict: dict, 
                          dyn_list: list,
                          num: int,**kwargs) ->\
                          tuple[tuple, tuple, tuple, tuple]: 
            
        # trunc_dict: truncation dict for this section (singular)
        # dyn_list: Dynamic list of SL for reference
        # num: the index for the current value of the dyn_list
        # Goal. To get a set of pt for further evaluation:
        # (entry_pt, exit_pt, stop_pt, close_pt)
        default_kwargs = DEFAULT_KWARGS
        kwargs = dict(default_kwargs,**kwargs)

        # A method that search for correct EES points from a EES_dict
        #print("trunc_dicts", trunc_dicts)
        # initialise
        earliest_exit, earliest_stop = (np.nan,np.nan), (np.nan,np.nan)
            
        # entry price not hit in that sections and position is not entred before
        # Then No trade that section.
        if len(trunc_dict['entry']) == 0 and\
           self._TE_pt == (np.nan,np.nan): 
           pass
        else:           
          # Save it as a defacto entry point only if it is empty
          if self._TE_pt == (np.nan, np.nan):
              self._TE_pt = trunc_dict['entry'][0]

          # Search for the earliest exit pt after entry
          if len(trunc_dict['exit']) > 0:
             # Find exit point candidates
             for i, exit_cand in enumerate(trunc_dict['exit']):  
                 #print('exit_cand', exit_cand, self._TE_pt)
                 if exit_cand[0] > self._TE_pt[0]:
                     earliest_exit = exit_cand
                     #print('earliest_exit', earliest_exit)
                     break
                 
          # Search for the earliest stop pt after entry
          if len(trunc_dict['stop']) > 0:
             # Finde stop loss point candidates
             for i, stop_cand in enumerate(trunc_dict['stop']):
                 if stop_cand[0] > self._TE_pt[0]:
                     earliest_stop = stop_cand
                     #print('earliest_stop', earliest_stop)
                     break
                 
          # Put in the new exit and stop
          if self._TP_pt == (np.nan, np.nan):
              self._TP_pt = earliest_exit
          if self._SL_pt == (np.nan, np.nan):
              self._SL_pt = earliest_stop
                            
          # For the section that is not the last. 
          if num < len(self._dyn_list) - 1: 
              print(f'Cross Section {num}')

              # Process the cross sections decisions
              this_SL_price = self._dyn_list[num]
              next_SL_price = self._dyn_list[num+1]
              
              print('this_SL_price', this_SL_price, 
                    'next_SL_price', next_SL_price)
              # Check the closing price of this section,
              # Case 1: close_price > next_SL_price, -> continue
              if trunc_dict['close'][1] > next_SL_price:
                  print('close_price > next_SL_price: continue')
                  pass
              # Case 2: close_price > this_SL_price and close_price < next_SL_price, 
              # -> either (A.replace new with old, B.close, C.Trail_dyn, tbc)
              elif trunc_dict['close'][1] > this_SL_price and \
                   trunc_dict['close'][1] < next_SL_price:
                  print(f'next_SL_price > close_price > this_SL_price: \
                        {self._cross_decision}')
                  print(self._dyn_list)
                  print('section cross', trunc_dict['close'])
                  # This function control the cross-section choices
                  self.cross_section_choice(num, 
                                            this_SL_price,
                                            trunc_dict['close'],
                                            trail_price_delta=kwargs['trail_price_delta'])
                  print('this_SL_price',  dyn_list[num], 
                        'next_SL_price', dyn_list[num+1])
                  print(self._dyn_list)

              # Case 3: close_price < this_SL_price -> SL
              # no need to do anything because the earliest_stop 
              # should already capture this. This switch case is 
              # written only for clarity
              elif trunc_dict['close'][1] < this_SL_price:
                  print('this_SL_price > close_price: SL')
                  pass 
                 #self._SL_pt = earliest_stop
                 
          # For the last section
          else:
              print(f'Section {num} (Last) Done')

              
        print('entry_pt, exit_pt, stop_pt')
        print(self._TE_pt, self._TP_pt, self._SL_pt)
    
    def open_positions(self, 
                       give_obj_name: str, 
                       get_obj_name: str, 
                       get_obj_quantity: int | float, 
                       EES_target_price_list: list, 
                       order_type: str,
                       size: int | float = 1, 
                       fee: dict = None, 
                       open_time: datetime.datetime = datetime.datetime.now())\
                       -> list[Order]:

        if order_type == 'Long':
            order_type1 = 'Long-Buy'
            order_type2 = 'Long-Sell'

        elif order_type == 'Short':
            order_type1 = 'Short-Borrow'
            order_type2 = 'Short-Buyback'
            
        # a method that execute the one trade per day based on the cases of the EES
        entry_price, exit_price = EES_target_price_list[0], EES_target_price_list[1]
        stop_price, close_price = EES_target_price_list[2], EES_target_price_list[3]
        
        #### Collapse all these into an add_position function
        # Make positions for initial price estimation
        entry_order = super().add_order(give_obj_name, get_obj_name, 
                                         get_obj_quantity, entry_price, 
                                         size = size, fee = None, 
                                         order_type = order_type1,
                                         open_time=open_time,
                                         trade_id=self.trade_id)

        exit_order = super().add_order(give_obj_name, get_obj_name, 
                                        get_obj_quantity, exit_price, 
                                        size = size, fee = fee, 
                                        order_type = order_type2,
                                        open_time=open_time,
                                        trade_id=self.trade_id)

        stop_order = super().add_order(give_obj_name, get_obj_name, 
                                        get_obj_quantity, stop_price, 
                                        size = size, fee = fee, 
                                        order_type = order_type2,
                                        open_time=open_time,
                                        trade_id=self.trade_id)
        
        close_order = super().add_order(give_obj_name, get_obj_name, 
                                         get_obj_quantity, close_price,
                                         size = size, fee = fee, 
                                         order_type = order_type2,
                                         open_time=open_time,
                                         trade_id=self.trade_id)

        pos_list = [entry_order, exit_order, stop_order, close_order]
        #print("pos_list", pos_list)
        return pos_list
    
    def execute_positions(self, 
                          EES_pt_list: list, 
                          pos_list: list, 
                          order_type: str = "Long"):
        # Do things in the portfolio
        if order_type == 'Long':
            order_type1 = 'Long-Buy'
            order_type2 = 'Long-Sell'

        elif order_type == 'Short':
            order_type1 = 'Short-Borrow'
            order_type2 = 'Short-Buyback'
            
        # Unpack inputs
        entry_pos, exit_pos, stop_pos, close_pos = pos_list[0], pos_list[1], \
                                                   pos_list[2], pos_list[3]
              
        # Search for the appropiate time for entry, exit, stop loss,
        # and close time for the trade                                    
        #entry_pt, exit_pt, stop_pt, close_pt = self.choose_EES_values(trunc_dict)
        entry_pt, exit_pt, stop_pt, close_pt = EES_pt_list[0], EES_pt_list[1],\
                                               EES_pt_list[2], EES_pt_list[3]

        # initialise trade_open and trade_close time and prices
        trade_open, trade_close = (np.nan,np.nan), (np.nan,np.nan)
        opening_pos, closing_pos = None, None
        
        # pack the outputs objects into lists
        exec_pos_list = [opening_pos,closing_pos]

        # Run diagnosis to decide which outcome it is for the day
        # Case 1: No trade because entry is not hit
        if entry_pt == (np.nan,np.nan):
            print("No trade.")
            # Cancel all order 
            ExecuteOrder(entry_pos).cancel_pos(void_time=close_pt[0])
            ExecuteOrder(exit_pos).cancel_pos(void_time=close_pt[0])
            ExecuteOrder(stop_pos).cancel_pos(void_time=close_pt[0])
            ExecuteOrder(close_pos).cancel_pos(void_time=close_pt[0])   
            
            return trade_open, trade_close, pos_list, exec_pos_list
            
        elif entry_pt != (np.nan,np.nan):
            # Case 2: No SL points, normal exit
            if exit_pt != (np.nan,np.nan) and stop_pt == (np.nan,np.nan):
            #elif entry_pt != (np.nan,np.nan) and (exit_pt[0]<stop_pt[0]):
                print("Noraml exit. No Stop-loss hit")
                trade_open, trade_close = entry_pt, exit_pt
                opening_pos, closing_pos = entry_pos, exit_pos
                #print("Before price adjustment", opening_pos, closing_pos)
    
                # change the closing price
                closing_pos.price = round(exit_pt[1],9)
                
                # Cancel all order positions
                ExecuteOrder(stop_pos).cancel_pos(void_time= trade_close[0])
                ExecuteOrder(close_pos).cancel_pos(void_time= trade_close[0])  
                
            # Case 3: No exit points, noraml SL
            elif exit_pt == (np.nan,np.nan) and stop_pt != (np.nan,np.nan):
            #elif entry_pt != (np.nan,np.nan) and (exit_pt[0] > stop_pt[0]):
                print('Stop loss. No exit hit')
                trade_open, trade_close = entry_pt, stop_pt
                opening_pos, closing_pos = entry_pos, stop_pos
                #print("Before price adjustment", opening_pos, closing_pos)
    
                # change the closing price
                closing_pos.price = round(stop_pt[1],9)
                
                # Cancel all order positions
                ExecuteOrder(exit_pos).cancel_pos(void_time= trade_close[0])
                ExecuteOrder(close_pos).cancel_pos(void_time= trade_close[0]) 
                
            # Case 4: Both SL and exit points exist:
            elif exit_pt != (np.nan,np.nan) and stop_pt != (np.nan,np.nan):
                # Case 4.1: Stop pt is before exit pt
                if exit_pt[0] > stop_pt[0]: # SL happens first
                    print('Stop loss. Stop-loss before exit hit.')
                    trade_open, trade_close = entry_pt, stop_pt
                    opening_pos, closing_pos = entry_pos, stop_pos
                    #print("Before price adjustment", opening_pos, closing_pos)
        
                    # change the closing price
                    closing_pos.price = round(stop_pt[1],9)
                    
                    # Cancel all order positions
                    ExecuteOrder(exit_pos).cancel_pos(void_time= trade_close[0])
                    ExecuteOrder(close_pos).cancel_pos(void_time= trade_close[0]) 
                    
                # Case 4.2 Exit pt is before Stop pt
                elif exit_pt[0] < stop_pt[0]: # exit happens first
                    print('Normal exit. exit before stop-loss hit.')

                    trade_open, trade_close = entry_pt, exit_pt
                    opening_pos, closing_pos = entry_pos, exit_pos
                    #print("Before price adjustment", opening_pos, closing_pos)
        
                    # change the closing price
                    closing_pos.price = round(exit_pt[1],9)
                    
                    # Cancel all order positions
                    ExecuteOrder(stop_pos).cancel_pos(void_time= trade_close[0])
                    ExecuteOrder(close_pos).cancel_pos(void_time= trade_close[0])  
                    
           # Case 5: Neither an exit or stop loss is hit, exit position at close time
            elif exit_pt== (np.nan,np.nan) and stop_pt == (np.nan,np.nan):
                print("Exit at market close. No exit and no SL")
                trade_open, trade_close = entry_pt, close_pt
                opening_pos, closing_pos = entry_pos, close_pos
                #print("Before price adjustment", opening_pos, closing_pos)
                
                # change the closing price
                closing_pos.price = round(close_pt[1],9)
                
                # Cancel all order positions
                ExecuteOrder(stop_pos).cancel_pos(void_time=trade_close[0])
                ExecuteOrder(exit_pos).cancel_pos(void_time=trade_close[0])
        
        # change the price for the open position
        opening_pos.price = entry_pt[1]

        # Execute the positions
        ExecuteOrder(opening_pos).fill_pos(fill_time = trade_open[0], 
                                              order_type=order_type1)
        
        ExecuteOrder(closing_pos).fill_pos(fill_time = trade_close[0], 
                                              order_type=order_type2)


        # pack the outputs objects into lists
        exec_pos_list = [opening_pos, closing_pos]
        pos_list = [entry_pos, exit_pos, stop_pos, close_pos]
        
        #print("exec_pos_list", exec_pos_list)
        
        for pos in pos_list: # Add position in the position book
            self._portfolio._order_pool.append(copy.copy(pos))

        return trade_open, trade_close, pos_list, exec_pos_list
    
    def run_trade(self, 
                  trunc_dict: dict, #truncation_dicts with multi_Sections #day: pd.DataFrame, 
                  give_obj_name: str, 
                  get_obj_name: str, 
                  get_obj_quantity: float | int,
                  target_entry: float, 
                  target_exit: float, 
                  stop_exit: float,
                  open_hr: str = "0300", 
                  close_hr: str = "2000", 
                  direction: str = "Buy",
                  fee: dict =  OIL_FUTURES_FEE,
                  open_time: datetime.datetime = None) -> \
                  tuple[tuple, tuple, list, list]: 
        
        #Find the minute that the price crosses the EES values
        # Input the position type
        if direction == 'Buy':
            order_type= 'Long'
        elif direction == 'Sell':
            order_type = 'Short'
            
        # Note that this is not the EES_dict object from find_minute_EES.
        # This is just an initial estimation of the EES values for the 
        # open_position function in the begining of the day. As the positions
        # are executed, the prices will change according to the data.
        EES_target_list = [target_entry, target_exit, 
                           stop_exit, trunc_dict['close'][1]] 
        
        # run the trade via position module
        pos_list = self.open_positions(give_obj_name,
                                       get_obj_name, 
                                       get_obj_quantity, 
                                       EES_target_list, 
                                       order_type=order_type, 
                                       size=SIZE_DICT[get_obj_name],
                                       fee=fee, 
                                       open_time = open_time)

        # Execute the positions. As the function is ran, it chooses the 
        # appropiate EES values based on the choose_EES_values method of 
        # this class
        trade_open, trade_close, \
        pos_list, exec_pos_list = self.execute_positions(trunc_dict, pos_list,
                                                         order_type = order_type)
        #print(trade_open, trade_close, exec_pos_list)
        
        # the search function for entry and exit time should be completely 
        # sepearate to the trading actions
        return trade_open, trade_close, pos_list, exec_pos_list   
    
def find_minute_EES_dyn(histroy_data_intraday: pd.DataFrame, 
                        target_entry: float, target_exit: float, stop_exit: float,
                        open_hr: datetime.time, 
                        close_hr: datetime.time, 
                        price_proxy: str = 'Open', 
                        time_proxy: str= 'Time',
                        date_proxy: str ='Date',
                        direction: str = 'Neutral',
                        close_trade_hr: str = '1925', 
                        dt_scale: str = 'datetime') -> dict:
    
    # (This function can be made in one more layer of abstraction. Work on this later)
    
    # define subsample. turn the pandas series into a numpy array
    price_list = histroy_data_intraday[price_proxy].to_numpy()
    time_list = histroy_data_intraday[time_proxy].to_numpy()
    
    #print("time_list", time_list[0], type(time_list[0]))
    # read in date list
    date_list = histroy_data_intraday[date_proxy].to_numpy() 
    # Temporary solution. Can be made using two to three time layer

    # make datetime list
    datetime_list = np.array([datetime.datetime.combine(pd.to_datetime(d).date(), t) \
                              for d, t in zip(date_list,time_list)])
    
    if dt_scale == "time":
        time_proxy_list = time_list
    elif dt_scale == 'date':
        time_proxy_list = date_list
    elif dt_scale == 'datetime':
        time_proxy_list = datetime_list
        
    # Find the crossover indices
    entry_pt_dict = read.find_crossover(price_list, target_entry)
    exit_pt_dict = read.find_crossover(price_list, target_exit)
    stop_pt_dict = read.find_crossover(price_list, stop_exit)
    
    if direction == "Neitral":
        #print("Neutral day")
        # for 'Neutral' action, all info are empty
        entry_pts, entry_times = [], []
        exit_pts, exit_times = [], []
        stop_pts, stop_times = [], []
    
    elif direction == "Buy":
        #print("Finding Buy points.")
        # for 'Buy' action EES sequence is drop,rise,drop
        entry_pts = price_list[entry_pt_dict['all'][0]]
        entry_times = time_proxy_list[entry_pt_dict['all'][0]]
            
        exit_pts = price_list[exit_pt_dict['all'][0]]
        exit_times = time_proxy_list[exit_pt_dict['all'][0]]
        
        stop_pts = price_list[stop_pt_dict['all'][0]]
        stop_times = time_proxy_list[stop_pt_dict['all'][0]]
            
    elif direction == "Sell":
        #print("Finding Sell points.")
        # for 'Sell' action EES sequence is rise,drop,rise
        entry_pts = price_list[entry_pt_dict['all'][0]]
        entry_times = time_proxy_list[entry_pt_dict['all'][0]]
            
        exit_pts = price_list[exit_pt_dict['all'][0]]
        exit_times = time_proxy_list[exit_pt_dict['all'][0]]
        
        stop_pts = price_list[stop_pt_dict['all'][0]]
        stop_times = time_proxy_list[stop_pt_dict['all'][0]]
    else:
        raise ValueError('Direction has to be either Buy, Sell, or Neutral.')
    
    # Define the opening/closing time and closing price. 
    # Here we choose 19:25 for final trade
    open_hr_str = open_hr.strftime("%H%M")
    close_hr_str = close_hr.strftime("%H%M")

    ## Find the closest price and datettime instead of having it at exactly the open time
    open_date_new, open_pt = read.find_closest_price(histroy_data_intraday, 
                                                  target_hr = open_hr_str, 
                                                  direction = 'forward',
                                                  price_proxy = price_proxy,
                                                  time_proxy = time_proxy)
    
    open_date = date_list[np.where(time_list==open_date_new)[0]][0]
    open_datetime = datetime.datetime.combine(pd.to_datetime(open_date).date(), 
                                               open_date_new)

    # Find the closest price and datettime instead of having it at exactly the close time
    close_date_new, close_pt = read.find_closest_price(histroy_data_intraday, 
                                                  target_hr = close_hr_str, 
                                                  direction = 'backward',   
                                                  price_proxy = price_proxy,
                                                  time_proxy = time_proxy)

    
    close_date = date_list[np.where(time_list==close_date_new)[0]][0]
    close_datetime = datetime.datetime.combine(pd.to_datetime(close_date).date(), 
                                               close_date_new)

    # storage
    EES_dict = {'entry': list(zip(entry_times,entry_pts)),
                'exit': list(zip(exit_times,exit_pts)),
                'stop': list(zip(stop_times,stop_pts)),
                'open': tuple((open_datetime, open_pt)),
                'close': tuple((close_datetime, close_pt))}

    #print('EES_dict', EES_dict['close'])
    return EES_dict

def gen_trunc_dict_dyn(loop_type: LoopType,                    
                       day: pd.DataFrame, 
                       target_entry: float |list[float,float] | 
                                     tuple[float, float] | dict[str,float],
                       target_exit: float |list[float,float] | 
                                    tuple[float, float] | dict[str,float],
                       stop_exit: float, 
                       open_hr: datetime.datetime| datetime.time, 
                       close_hr: datetime.datetime| datetime.time, 
                       direction: str,
                       price_proxy:str='Open') \
                       -> tuple[dict[str,list|tuple], float, float, float]:

    if loop_type == LoopType.CROSSOVER:
        # Find the crossover points of EES
        trunc_dict = read.find_minute_EES_dyn(day, 
                                              target_entry, 
                                              target_exit, 
                                              stop_exit,
                                              open_hr = open_hr, 
                                              close_hr = close_hr, 
                                              direction = direction,
                                              price_proxy=price_proxy)

    return trunc_dict


def load_EES_from_signal_dynamic(item:pd.DataFrame, cols:list =[]):
    # A function that load the signal for a dynamic backtest setup
    TE_price = item['Target_Entry_Price']
    TP_price = item['Take_Profit_Price']
    SL_price = item[['StopLoss_Price_1', 'StopLoss_Price_2', 
                     'StopLoss_Price_3','StopLoss_Price_4']].to_list()
    
    SL_start_time = item[['SL1_start_time', 'SL2_start_time',
                          'SL3_start_time', 'SL4_start_time']].to_list()
    
    SL_end_time = item[['SL1_end_time', 'SL2_end_time',
                          'SL3_end_time', 'SL4_end_time']].to_list()
    direction = item['Direction']
    
    sections = {}
    
    #break down the backtest into several sections
    for i in range(len(SL_price)):
        section = {}
        section['target_entry'] = ((SL_start_time[i],SL_end_time[i]),
                                   TE_price) #((start_time, end_time), price)
        section['target_exit'] = ((SL_start_time[i],SL_end_time[i]),
                                  TP_price)
        section['stop_exit'] = ((SL_start_time[i],SL_end_time[i]),SL_price[i])        
        section['direction'] = ((SL_start_time[i],SL_end_time[i]),direction)        
        
        sections[str(i)] = section
    return sections
    

def loop_portfolio_preloaded_dSL(portfo: Portfolio, 
                                 trade_method,
                                 signal_table: pd.DataFrame, 
                                 histroy_intraday_data_pkl: dict[str, pd.DataFrame], 
                                 **kwargs):
    # Loop through signal master table and execute trade in the intraday data
    # Within this custom loop, there is another loop that go through a series of
    # sections and calculate entry point and exit point individually.
    default_kwargs = DEFAULT_KWARGS
    kwargs = dict(default_kwargs,**kwargs)

    for i in range(len(signal_table)):

        # setup trade inputs ###########
        item = signal_table.iloc[i]
                
        symbol = item['Price_Code']
        date_interest = item['Date']
        get_obj_name = item['Price_Code']

        open_hr = kwargs['open_hr_dict'][symbol]
        close_hr = kwargs['close_hr_dict'][symbol]
        
        histroy_intraday_data = histroy_intraday_data_pkl[symbol]
        
        day = backtest.extract_intraday_minute_data(histroy_intraday_data, 
                                                    date_interest, 
                                                    open_hr=open_hr, 
                                                    close_hr=close_hr)
        
        open_hr_dt, open_price = read.find_closest_price(day,
                                                         target_hr= open_hr,
                                                         direction='forward')
        
        close_hr_dt, close_price = read.find_closest_price(day,
                                                           target_hr= close_hr,
                                                           direction='backward')
            
        # The time to open all positions
        pos_open_dt = datetime.datetime.combine(date_interest.date(), open_hr_dt)
        
        print('===============================')
        print(i, pos_open_dt, symbol)
        #print('day', day)
        #print('Time', day['Time'].iloc[0], type(day['Time'].iloc[0]))
        # Target EES global (the initial targets)
        global_target_entry = item['Entry_Price']
        global_target_exit = item['Exit_Price']
        global_stop_exit = item['StopLoss_Price']

        # Build up sections, the output is a dict containing the EES for each 
        # section
        sections = load_EES_from_signal_dynamic(item)
        #print('sections', sections)
        # Setup trade ##########
        trade_id = i #direction + str(i)
        direction = sections['0']['direction'][1]
        # Make a list of SL for universal access
        dyn_list = item[['StopLoss_Price_1', 'StopLoss_Price_2', 
                         'StopLoss_Price_3','StopLoss_Price_4']].to_list()

        # Initialise trade 
        T = trade_method(portfo, trade_id, 
                         trail_price_delta=kwargs['trail_price_delta'], 
                         direction=direction,
                         cross_decision='SL_C',
                         dyn_list = dyn_list)
        
        # Setup the close hour exit point (remember to change the close_hr_dt 
        # from time to datetime)
        T._close_pt = (datetime.datetime.combine(date_interest, close_hr_dt), close_price)
        
        # Loop Through each section to find the suitable EES point, 
        # Store them in the class variable in the Trade object
        for num in sections:
            # Isolate day_section from day data according to the time range
            # of the EES
            start_time = datetime.datetime.strptime(sections[num]['stop_exit'][0][0], 
                                                    '%H:%M:%S').time()
            end_time = datetime.datetime.strptime(sections[num]['stop_exit'][0][1], 
                                                  '%H:%M:%S').time()
            
            day_section = day[(day['Time']>=start_time) & (day['Time']<=end_time)]
            #print('day_section', day_section)

            # The EES for this section
            target_entry = sections[num]['target_entry'][1]
            target_exit = sections[num]['target_exit'][1]
            stop_exit = sections[num]['stop_exit'][1]
            
            print(f'--------section {num}: {start_time} to {end_time}, "{direction}"--------')
            print(f'TE: {target_entry}, TP: {target_exit}, SL: {stop_exit}')
            print('------------------------------------------------------')

            # set the open_hr to the time specific to this section
            open_hr_dt, close_hr_dt = start_time, end_time

            # Generate truncation dictionary in this section of the day
            trunc_dict, target_entry, \
            target_exit, stop_exit = backtest.gen_trunc_dict(LoopType.CROSSOVER,
                                                             day_section, 
                                                             target_entry, 
                                                             target_exit, 
                                                             stop_exit, 
                                                             open_hr_dt, 
                                                             close_hr_dt, 
                                                             direction)
            #print(trunc_dict)
            
                
            # Choose the earliest EES for this section
            T.choose_EES_values(trunc_dict, dyn_list, int(num),
                                trail_price_delta = TRAIL_PRICE_DELTA[symbol])
            print('------------------------------------------------------')
        print('------------------------------------------------------')

        # Export the trade object defacto EES points
        # A list of initial target prices for opening position, it will be 
        # changed during execute_order based on EES_pt_list
        EES_target_price_list = [global_target_entry, global_target_exit, 
                                 global_stop_exit, close_price]
        
        # A list of final EES points
        EES_pt_list = [T._TE_pt, T._TP_pt, T._SL_pt, T._close_pt]
        
        ORDER_TYPE = {'Buy': 'Long', 'Sell':'Short'}
        #print('EES_target_list', EES_target_price_list)
        print('EES_pt_list', EES_pt_list)
        
        # Open position and add them in the portfolio
        pos_list = T.open_positions(kwargs['give_obj_name'], 
                                    get_obj_name, 
                                    kwargs['get_obj_quantity'],
                                    EES_target_price_list, 
                                    ORDER_TYPE[direction],
                                    size=SIZE_DICT[get_obj_name],
                                    fee=OIL_FUTURES_FEE, 
                                    open_time = open_hr_dt)
        #print('pos_list', pos_list)
        print('------------------------------------------------------')

        # Execute and exit position in the portfolio
        trade_open, trade_close, \
        pos_list, exec_pos_list = T.execute_positions(EES_pt_list, 
                                                      pos_list, 
                                                      order_type = \
                                                      ORDER_TYPE[direction])
        
        #print('pos_list', pos_list)
        print('------------------------------------------------------')

        #backtest.plot_in_backtest(date_interest,get_obj_name, trunc_dict, direction, 
        #                          plot_or_not=kwargs['plot_or_not'])
                                                 

    return portfo

def run_backtest_portfolio_preloaded(TradeMethod,
                                     start_date: str, end_date: str,
                                     loop_type: LoopType = LoopType.CROSSOVER,
                                     **kwargs): 
    default_kwargs = DEFAULT_KWARGS
    kwargs = dict(default_kwargs,**kwargs)

    t1 = time.time()
    start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')

    # Find the date for trading, only "Buy" or "Sell" date are taken.
    trade_date_table = backtest.prepare_signal_interest(kwargs['master_signal_filename'],
                                                        direction = kwargs['selected_directions'],
                                                        trim = False)
    trade_date_table = trade_date_table[(trade_date_table['Date'] >= start_date) & 
                                        (trade_date_table['Date'] <= end_date)]
    
    # Initialise Portfolio
    P1 = Portfolio()
    USD_initial = {'name':"USD", 'quantity': 10_000_000, 'unit':"dollars", 
                   'asset_type': "Cash", 'misc':{}} # initial fund
    P1.add(USD_initial,datetime=datetime.datetime(2020,12,31))
    
    # a list of input files
    P1 = loop_portfolio_preloaded_dSL(P1, TradeMethod,
                                      trade_date_table, 
                                      kwargs['histroy_intraday_data_pkl'],
                                      give_obj_name=kwargs['give_obj_name'],
                                      get_obj_quantity=kwargs['get_obj_quantity'],
                                      open_hr_dict=kwargs['open_hr_dict'],
                                      close_hr_dict=kwargs['close_hr_dict'],
                                      price_proxy=kwargs['price_proxy'])
                                            
    t2 = time.time()-t1
    print("It takes {} seconds to run the backtest".format(t2))

    return P1

def run_backtest_bulk(TradeMethod, 
                      start_date: str, end_date: str, 
                      loop_type: LoopType = LoopType.CROSSOVER,
                      **kwargs):
    
    default_kwargs = DEFAULT_KWARGS
    kwargs = dict(default_kwargs,**kwargs)

    if kwargs['method'] == "preload":
        PP = run_backtest_portfolio_preloaded(TradeMethod,
                                              start_date, end_date,
                                              loop_type = loop_type,
                                              master_signal_filename = kwargs['master_signal_filename'], 
                                              histroy_intraday_data_pkl = kwargs['histroy_intraday_data_pkl'],
                                              give_obj_name=kwargs['give_obj_name'],
                                              get_obj_quantity=kwargs['get_obj_quantity'],
                                              open_hr_dict = kwargs['open_hr_dict'], 
                                              close_hr_dict = kwargs['close_hr_dict'], 
                                              selected_directions = kwargs['selected_directions'])


        backtest_result = PP
        if kwargs['save_or_not']: # save pkl portfolio
            file = open(kwargs['master_pnl_filename'], 'wb')
            pickle.dump(PP, file)
                
    return backtest_result

if __name__ == "__main__":
    
    def load_source_data_bt(filenames_loc) -> dict:
        master_dict = {}
        for filename in filenames_loc:
            temp_dict = util.load_pkl(filename)
            master_dict = dict(master_dict, **temp_dict)
            
        return master_dict
    
    start_date = "2022-02-01"
    end_date = "2022-02-02"

    #end_date = "2024-06-28"
    
    MASTER_SIGNAL_FILENAME = RESULT_FILEPATH + "/test_results/test_master_signal_file.csv"
    MASTER_PNL_FILENAME = RESULT_FILEPATH + "/test_results/test_pnl.csv"
    HISTORY_MINUTE_PKL = load_source_data_bt(list(DAILY_MINUTE_DATA_INDI_PKL.values()))


    run_backtest_bulk(OneTradePerDay_DYNSL, 
                      start_date, end_date, 
                      method = "preload", 
                      master_signal_filename = MASTER_SIGNAL_FILENAME,
                      master_pnl_filename = MASTER_PNL_FILENAME,
                      histroy_intraday_data_pkl = HISTORY_MINUTE_PKL,
                      give_obj_name = 'USD',
                      get_obj_quantity = 1,
                      open_hr_dict = WRONG_OPEN_HR_DICT, 
                      close_hr_dict= CLOSE_HR_DICT,
                      loop_type = LoopType.CROSSOVER,
                      save_or_not=False, 
                      merge_or_not=True)
    

