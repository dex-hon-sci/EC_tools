#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 27 13:01:43 2025

@author: dexter
"""
# python import
from dataclasses import dataclass, field
from functools import cached_property
import datetime as datetime
import re
import inspect
# package import
import pandas as pd
import numpy as np
from prettytable import PrettyTable

# EC_tools import
import EC_tools.utility as util
from EC_tools.portfolio.asset import Asset
from EC_tools.portfolio.bookkeep import Bookkeep
from EC_tools.portfolio_2.position import Position

import EC_tools.base.read as read

__all__ = ['Portfolio', 'PortfolioLog', 'PortfolioMetrics']

# Trade function looks like this
# Run_trade():
#   open_positions:
#       add_order (Make Order object)
#   execute_positions:
#       func: to find the right entry/exit points    
#       ExecuteOrder: (Change Order object status and add/sub to portfolio)
#           fill_pos/cancel_pos:
#               add/sub to portfolio 

class Portfolio(object):
    # Raw transaction data container
    # Portfolio track the followings
    # 1) Cash reserve Numbers
    # 2) Assets holding
    # 3) Active positions
    # 4) Order records
    # 5) Resolved Position records
    # Usage: Only filled orders, and thus closed positions are recorded
    
    def __init__(self):
        self.cash_dict: dict = dict() # Store latest cash value
        self.asset_dict: dict = dict()  # Store latest asset qty
        self.__pool_datetime: list = list()
        self.__pool_asset: list = list()
        #self.active_position: list = pd.DataFrame()
        self.order_record: list = list() # Store processed order
        self.position_record: list = list() # store closed poisitions
        self._zeropoint = 0.0
        
    def check_remainder(self,
                        asset_name: str,
                        quantity: int | float,
                        cash_or_not: bool = True,
                        asset_or_not: bool= False) -> bool:

        if not cash_or_not ^ asset_or_not:
            raise Exception("It can either be cash or asset.")
        
        if cash_or_not: remainder_dict = self.cash_dict
        elif asset_or_not: remainder_dict = self.asset_dict
            
        baseline = remainder_dict[asset_name] - self._zeropoint

        return baseline < quantity
    
    def add(self,
            asset: Asset | str | dict,
            dt: datetime.datetime = datetime.datetime.now(),
            quantity: int | float = 0,
            unit: str = 'contract',
            asset_type: str = 'future') -> None:  # tested

        # asset cannot be a list
        # check if it asset is an asset format
        if type(asset) == Asset:
            asset_name = asset.name
        elif type(asset) == str:
            # # search the dictionary to see what kind of asset is this
            # (potential improvement)
            # make a new asset
            # asset = Asset(asset, quantity, unit, asset_type)
            asset = {'name': asset, 'quantity': quantity,
                     'unit': unit, 'asset_type': asset_type, 'misc': {}}
            asset_name = asset['name']
            asset_quantity = asset['quantity']

        elif type(asset) == dict:
            asset_name = asset['name']
            asset_quantity = asset['quantity']
             
        # track latest cash and asset qty
        if asset_type == "Cash": # Adding Cash into the cash dictionary
            self.cash_dict[asset_name] += asset_quantity
        else: # Adding Asset into the cash dictionary
            self.asset_dict[asset_name] += asset_quantity
                
        # Add the asset into the pool
        self.__pool_datetime.append(dt)  # record datetime
        self.__pool_asset.append(asset)   # save new asset

    def sub(self,
            asset: Asset | str | dict,
            datetime: datetime.datetime = datetime.datetime.today(),
            quantity: int | float = 0,
            unit: str = 'contract',
            asset_type: str = 'future') -> None:  # tested

        # check if it asset is an asset format
        if type(asset) == dict:
            # call the quantity from table
            asset_name = asset['name']

            # check if the total amount is higher than the subtraction amount
            if asset['asset_type'] == "Cash": 
                rem_check = self.check_remainder(asset_name, asset['quantity'],
                                                 cash_or_not=True, 
                                                 asset_or_not = False)
 
            else: 
                rem_check = self.check_remainder(asset_name, asset['quantity'],
                                                 cash_or_not=False, 
                                                 asset_or_not = True)

                
            if rem_check:
                raise Exception('There is not enough {} to be subtracted \
                                from the portfolio.'.format(asset_name))
            
            quantity = asset['quantity']
            unit = asset['unit']
            asset_type = asset['asset_type']

        if type(asset) == str:
            # # search the dictionary to see what kind of asset is this
            # make a new asset
            asset_name = asset

        # make a new asset with a minus value for quantity
        new_asset = {'name': asset_name, 'quantity': quantity*-1,
                     'unit': unit, 'asset_type': asset_type, 'misc': {}}
        asset_quantity = new_asset['quantity']

        #print('sub','new_asset', new_asset)
        
        # track latest cash and asset qty
        if asset_type == "Cash": # Adding Cash into the cash dictionary
            self.cash_dict[asset_name] -= asset_quantity
        else: # Adding Asset into the cash dictionary
            self.asset_dict[asset_name] -= asset_quantity

        self.__pool_asset.append(new_asset)   # save new asset
        self.__pool_datetime.append(datetime)  # record datetime

    def value(self,
              date_time: datetime.datetime):
        return 
    
    def asset_value() -> float:
        return 
    def total_value():
        return
    
    def order_record(): # save all executed orders
        return 
    
    def render_position(self):
        # scan the Asset list with two pointers (sliding window)
        # OR scan the order list with two pointers, and resolve position one-by-one
        left_pt = 0
        right_pt = 0
        for left_pt in range(len(self.__pool_asset)):
            cur_asset = self.__pool_asset[left_pt]
            
            for right_pt in range(left_pt+1,len(self.__pool_asset)):
                
                next_asset = self.__pool_asset[right_pt]
                cond1 = None
                if True:
                    A = Position()
                else:
        return
    
@dataclass
class PortfolioLog(object):
    # Generate readable log and dataframe of the Portfolio
    def __init__():
        return
    def _make_log(self, simple_log=False):  # Decrepated time complexity too large
        return 
    @property
    def log(self) -> pd.DataFrame:

        return self._make_log(simple_log=True)

    @property
    def full_log(self) -> pd.DataFrame:

        return self._make_log(simple_log=False)

    def asset_log(self, asset_name) -> pd.DataFrame:  # tested
        asset_log = self.log[asset_name]
        return asset_log

    def asset_full_log(self, asset_name) -> pd.DataFrame:  # tested

        asset_log = self.full_log[asset_name]
        return asset_log
    
    def render_position_log(self)->pd.DataFrame:
        log = pd.DataFrame()
        for ele in self.poisition_record:
            temp = pd.DataFrame(ele.__dict__)
            pd.concat([log,temp])
        
        return log
    
    def render_tradebook_xlsx(self):
        tradebook_xlsx = read.render_PNL_xlsx([self.tradebook_filename],
                                              return_proxy='Trade_Return')
        return tradebook_xlsx

@dataclass
class PortfolioMetrics(object):
    # Calculated derived quantity, such as PNL from the Log
    _portfolio: Portfolio

    def __post_init__(self):
        self.portfolio_log = PortfolioLog(self._portfolio)
        self.tradebook = self.portfolio_log.tradebook
        
    def _load_filled_position_pool(self) -> list:
        """
        A function to load only the filled position to a list
        
        Returns
        -------
        list
            Filled position list
        """
        order_pool = self._portfolio.order_pool

        def select_func_fill(x): 
            return order_pool[x].status.value == 'Filled'
        
        PP = read.group_trade(order_pool,
                              select_func=select_func_fill)
        return PP
    
    def start_capital(self, 
                      dntr: str = 'USD', 
                      cash_only: bool = False) -> tuple[float, str, str]:
        
        first_date = self._portfolio.pool_datetime[0]

        if not cash_only:
            first_entry_total_value = self._portfolio.total_value(
                first_date, dntr=dntr)
            
        return first_entry_total_value, dntr, 'Starting Capital'
    
    def end_capital(self, 
                    dntr: str = 'USD', 
                    cash_only: bool = False) -> tuple[float, str, str]:
        
        last_date = self._portfolio.pool_datetime[-1]

        if not cash_only:
            last_entry_total_value = self._portfolio.total_value(
                last_date, dntr=dntr)
        return last_entry_total_value, dntr,  "Final Capital"
    
    def period(self, 
               time_proxy: str = 'Exit_Date', 
               unit: str = "Days") -> tuple[int, str, str]:
        """
        Total Days of trading

        Parameters
        ----------
        time_proxy : str, optional
            Column name for the time. The default is 'Exit_Date'.
        unit : str, optional
            Unit. The default is "Days".

        """
        
        period = self.tradebook[time_proxy].iloc[-1] - self.tradebook[time_proxy].iloc[0]
        return period, unit, "Period"

    def total_trades(self) -> tuple[int, str, str]:
        """
        The total number of trades in the tradebook.

        """
        return len(self.tradebook), '#', "Total Trades"

    def total_fee_paid(self) -> float: # WIP
        order_pool = self._portfolio.order_pool

        def select_func_fill(x): 
            return order_pool[x].status.value == 'Filled'
        
        PP = read.group_trade(order_pool,
                              select_func=select_func_fill)

        total_fee_dict = dict()
        total_fee = 0
        for ele in PP:
            # Assuming the second item in each element contains the fee
            total_fee = total_fee + ele[1].fee['quantity']

        return total_fee, '', 'Total Fee Paid'

    def total_returns(self, dntr='USD') -> tuple[float,str]:
        """
        The total returns given a currency denomanator 

        Parameters
        ----------
        dntr : str, optional
            Currency denomanator. The default is 'USD'.

        Returns
        -------
        tuple[float,str,str]
            total returns, unit, metric name.

        """
        first_date = self._portfolio.pool_datetime[0]
        last_date = self._portfolio.pool_datetime[-1]

        first_entry_total_value = self._portfolio.total_value(
            first_date, dntr=dntr)
        last_entry_total_value = self._portfolio.total_value(
            last_date, dntr=dntr)

        return (last_entry_total_value - first_entry_total_value), dntr, \
               "Total Returns"

    def total_returns_fraction(self, unit: str = '%') -> tuple[float,str, str]:
        """
        The total returns by fraction (percentage).

        Parameters
        ----------
        unit : str, optional
            Percentage. The default is '%'.

        Returns
        -------
        tuple[float,str]
            total return

        """
        first_date = self._portfolio.pool_datetime[0]
        last_date = self._portfolio.pool_datetime[-1]

        first_entry_total_value = self._portfolio.total_value(first_date)
        last_entry_total_value = self._portfolio.total_value(last_date)
        
        #print(first_entry_total_value, last_entry_total_value)

        return 100*(last_entry_total_value - first_entry_total_value) / \
               first_entry_total_value, unit, "Total Returns"

    def win_rate(self, return_proxy: str = "Trade_Return", unit: str = "%") -> \
                 tuple[float, str, str]:
        """
        The win rate by percentage.

        Parameters
        ----------
        return_proxy : str, optional
            The column name to query in the tradebook. 
            The default is "Trade_Return".
        unit : str, optional
            The Unit percentage. The default is "%".

        Returns
        -------
        tuple[float,str]
            Win Rate.

        """
        win_trades = sum(
            1 for i in self.tradebook[return_proxy].to_list() if i >= 0)
        lose_trades = sum(
            1 for i in self.tradebook[return_proxy].to_list() if i < 0)

        return (win_trades/(win_trades+lose_trades))*100, unit, "Win Rate"

    def profit_factor(self, return_proxy: str = "Trade_Return") -> \
        tuple[float, str, str]:
        """
        The Profit factor (Money Won /Money Lose)

        Parameters
        ----------
        return_proxy : str, optional
            The column name to query in the tradebook. 
            The default is "Trade_Return".

        Returns
        -------
        float
            The profit factor.

        """

        win_trades_val = sum(i for i in self.tradebook[return_proxy].to_list()
                             if i >= 0)
        lose_trades_val = sum(i for i in self.tradebook[return_proxy].to_list()
                              if i < 0)
        # print(win_trades_val, lose_trades_val)
        return abs(win_trades_val)/abs(lose_trades_val), '', 'Profit Factor'

    def total_open_positions(self) -> tuple[int, str, str]: #WIP
        position_pool = self._portfolio.position_pool
        
        trade_pool = read.group_trade(position_pool)
        
        total_open_pos = sum(1 for pos in trade_pool 
                             if pos[0].status.value == 'Filled' and 
                                pos[1].status.value == 'Pending' and
                                pos[2].status.value == 'Pending' and
                                pos[3].status.value == 'Pending')
        
        return total_open_pos, '#', 'Total Open Positions'
    
    def total_close_positions(self): 
        order_pool = self._portfolio.order_pool
        
        # Group the trades by ID and Filled status
        trade_pool = read.group_trade(order_pool, select_func= 
                                      lambda x : order_pool[x].status.value 
                                      == 'Filled')
        
        total_open_pos = sum(1 for pos in trade_pool if len(pos) == 2)
        
        return total_open_pos, '#', 'Total Close Positions'

    def avg_trade_return(self, 
                         return_proxy: str = "Trade_Return", 
                         unit: str = 'USD') -> tuple[str,str]:
        """
        A method that calculate average trade return

        Parameters
        ----------
        return_proxy : str, optional
            DESCRIPTION. The default is "Trade_Return".
        unit : str, optional
            The unit relies on user-input. 
            The default is 'USD'.

        Returns
        -------
        tuple[str,str]
            The average trade return and the currency unit.

        """
        
        filled_pos_list = self._load_filled_position_pool()
    
        trade_return = np.array([trade for trade 
                                 in self.tradebook[return_proxy].to_list()])
        trade_size = np.array([trade[1].size for trade in filled_pos_list])
        trade_quantity =  np.array([trade[1].get_obj['quantity'] 
                                    for trade in filled_pos_list])
        
        daily_return_amount = trade_return*trade_size*trade_quantity
        return np.average(daily_return_amount), unit, 'Average Trade Return'
    
    #def _daily_exposure(self):
    #    return

    def sharpe_ratio(self,
                     return_proxy: str = "Trade_Return",
                     riskfree_rate: float | list = 0.05) -> float:
        """
        The Sharpe Ratio (S).
        
            S = E(R_p - R_f)/std(S_p)

        Parameters
        ----------
        return_proxy : str, optional
            The column name to query in the tradebook. 
            The default is "Trade_Return".
        riskfree_rate : float | list, optional
            The proxy for risk-free rate. 
            The default is 0.05. Assuming 5 % yield in 5-years treasurey bond.

        Returns
        -------
        float
            The Sharpe Ratio.

        """
        #trade_return = self.tradebook[return_proxy].to_numpy()
        filled_pos_list = self._load_filled_position_pool()
        
        
        direction = np.array([trade for trade 
                                 in self.tradebook["Direction"].to_list()])
        
        entry_price = np.array([trade for trade 
                                 in self.tradebook["Entry_Price"].to_list()])

        exit_price = np.array([trade for trade 
                                         in self.tradebook["Exit_Price"].to_list()])

        #print("filled_pos_list", filled_pos_list[0:2])
        trade_return = np.array([trade for trade 
                                 in self.tradebook["Trade_Return"].to_list()])

        trade_return_fraction = np.array([trade for trade 
                                 in self.tradebook["Trade_Return_Fraction"].to_list()])
        
       # trade_open = np.array([trade[0].give_obj['quantity'] for trade in filled_pos_list])
       # trade_close = np.array([trade[1].give_obj['quantity'] for trade in filled_pos_list])
        
      #  print('trade_open', trade_open, 'trade_close', trade_close)
         
        trade_size = np.array([trade[1].size for trade in filled_pos_list])
        trade_quantity =  np.array([trade[1].get_obj['quantity'] 
                                    for trade in filled_pos_list])
        
        daily_return_amount = trade_return*trade_size*trade_quantity
        cumsum = np.cumsum(daily_return_amount)
        cumsum_growth = (cumsum[1:-1] - cumsum[0:-2])/cumsum[0:-2]
        
# =============================================================================
#         print('entry_price', entry_price)
#         print('exit_price', exit_price)
#         print('trade_return', trade_return)
#         print("trade_return_fraction", trade_return_fraction)
#         print('max, min', max(trade_return_fraction), min(trade_return_fraction))
#         print('daily_return_amount', daily_return_amount)
#         print('cumsum', cumsum, len(cumsum))
#         print('cumsum_growth', cumsum_growth, len(cumsum_growth))
#         print("self.total_returns_fraction()[0]*0.01", self.total_returns_fraction()[0]*0.01)
#         print('std(cumsum_growth)', np.std(cumsum_growth))
# =============================================================================
        
       # trade_return_fraction = (trade_close-trade_open)/trade_open
        
        #print('daily_return_amount', daily_return_amount, trade_close-trade_open)
        #print('trade_return_fraction', trade_return_fraction)
        
        #riskfree_rate = np.repeat(riskfree_rate, len(daily_return_amount))
        #sharpe_ratio = (self.total_returns_fraction()[0]*0.01 - riskfree_rate) / \
        #               np.std(daily_return_amount)
        sharpe_ratio = (self.total_returns_fraction()[0]*0.01-riskfree_rate)/\
                       np.std(cumsum_growth)**0.5
        return sharpe_ratio, '', 'Sharpe Ratio' 
    # so far it is the wrong number because the growth of cumsum is corss-asset, 
    # the return should be calculated using per day basis not per trade/

    def calmar_ratio(self):
        return

    def omega_ratio(self):
        return

    def sortino_ratio(self):
        return

    @classmethod
    def make_full_data(cls):
        # Calculate all metrics related to thid portfolio
        full_data = dict()

        attr_name = [value for value in dir(cls) if value not 
                     in dir(Portfolio) and value[0] != '_' 
                     and value[0:4] != 'make']
        
        attrs = (getattr(cls, name) for name in attr_name)

        #methods = filter(inspect.ismethod, attrs)
        
        for attr, name in zip(attrs, attr_name):
            print(attr, name)
            #df = method(cls)
            #full_data[name] = df
            
        print(attr_name, attrs)
        #full_data = {name: getattr(cls, name)() for name in attr_name}
        print(full_data)
        return full_data

    def make_full_report(self):
        print('Period [{}]'.format(self.period()[1]), self.period()[0])
        print("Initial Capital [{}]".format(self.start_capital()[1]), 
              self.start_capital()[0])
        print("Final Capital [{}]".format(self.end_capital()[1]), 
              self.end_capital()[0])  
        print('Total Trades [{}]'.format(self.total_trades()[1]), self.total_trades()[0])
        print('Total Fee []', self.total_fee_paid())
        print('Total Returns [{}]'.format(self.total_returns()[1]),
              self.total_returns()[0])
        print('Total_returns [{}]'.format(self.total_returns_fraction()[1]),
              self.total_returns_fraction()[0])
        print('win_rate [{}]'.format(self.win_rate()[1]), self.win_rate()[0])
        print('Profit Factor', self.profit_factor())
        print('Total Open Positions [{}]'.format(self.total_open_positions()[1]), 
              self.total_open_positions()[0])
        print('total Close Positions [{}]'.format(self.total_close_positions()[1]), 
              self.total_close_positions()[0])
        print('Average Trade Return [{}]'.format(self.avg_trade_return()[1]), 
              self.avg_trade_return()[0])
        print('Sharpe Ratio (#sigma not stable)', 
              self.sharpe_ratio()[0])
        x = PrettyTable()
