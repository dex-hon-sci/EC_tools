#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 29 23:49:08 2024

@author: dexter
"""
# python import
from dataclasses import dataclass, field, replace
from typing import Protocol
from enum import Enum, auto
import datetime as datetime

# EC_tools import
from EC_tools.portfolio import Asset, Portfolio
from EC_tools.utility import random_string
    
__all__=['PositionStatus', 'Position', 'ExecutePosition']

class PositionStatus(Enum):
    """
    A set of possible status for positions.
    
    """
    PENDING = "Pending" # When the position is added but not filled
    FILLED = "Filled" # When the position is executed
    VOID = "Cancelled" # When the position is cancelled

    
@dataclass
class Position(object):
    """
    Position class that create and manage position objects.
    
    """
    # key attributes
    give_obj: Asset
    get_obj: Asset
    _price: float
    status: PositionStatus = PositionStatus.PENDING
    portfolio: Portfolio = None
    
    # optional asset control
    size: float = 1
    fee: Asset = None
    pos_type: str = 'Long-Buy'
    
    # position attribute adjustable
    open_time: datetime = datetime.datetime.now()
    fill_time: datetime = None
    void_time: datetime = None
    auto_adjust: bool = True
    pos_id: str = random_string()  
    
    def __post_init__(self, void_time = datetime.datetime.now(), 
                      epi = 1e-8):
        """
        The post init function that checks if the input price is correct.
        If it is not. the position is voided.
        
        """
        # check if the quantity of both assets are 
        #correct_ratio = self.give_obj.quantity / (self.get_obj.quantity*self.size)
        
        # reminder: give is cash, get is asset (usually)
        if self.pos_type == 'Long-Buy' or 'Long-Sell':
            correct_ratio = self.give_obj.quantity / (self.get_obj.quantity*self.size)

        elif self.pos_type == 'Short-Borrow':
            correct_ratio = self.give_obj.quantity / (self.get_obj.quantity*self.size)
        elif self.pos_type == 'Short-Buyback':
            correct_ratio =  (self.get_obj.quantity*self.size) / self.give_obj.quantity 

        #print(correct_ratio, self.price)
        #self._check = (self._price == correct_ratio)
        
        # If the price is within the interval of (-epi, +epi) upon the correct ratio
        # We consider it is equal to the correct ratio
        self._check = (self._price  < correct_ratio + epi) and \
                        (self._price > correct_ratio- epi)
                        
        #print('Position created. Check:', self._check)
        #If this value is false, the position is automatically voided.
        if self._check == False:
            self.status = PositionStatus.VOID
            self.void_time = void_time
            print("Position voided due to invalid price entry.")
            
        # define fix quantity
        self._fix_quantity = self.get_obj.quantity
        
    @property
    def fix_quantity(self):
        return self._fix_quantity
    
    @fix_quantity.setter
    def fix_quantity(self, value):
        self._fix_quantity = value
        return self._fix_quantity
    
    @property
    def price(self):
        # getter method for seld._price
        return self._price
    
    @price.setter
    def price(self, value):
        
        # check if the new price is the same 
        if value != self.give_obj.quantity / (self.get_obj.quantity*self.size):
            if self.auto_adjust == True:
                pass
            elif self.auto_adjust == False:
                raise Exception("The new price value does not align with the \
                                asset quantities in the position.")
        
        # set a new price in the position.
        self._price = value
        
        # Assuming the give_obj is the one in the portfolio, we anchor the 
        # exchange rate using what we have. So we only changes the quantity in
        # the get_obj atrribute
        if self.fix_quantity == self.give_obj.quantity:
            self.get_obj.quantity = self.give_obj.quantity  / (self._price*self.size)
            
        elif self.fix_quantity == self.get_obj.quantity:
            self.give_obj.quantity = self.get_obj.quantity*(self._price*self.size)
            
class ExecutePosition(object):
    """
    A class that execute the position.
    
    """
    
    def __init__(self,  Position):
        self.position = Position
        
        #check if there is a Portfolio attached to the position.
        if not isinstance(self.position.portfolio, Portfolio):
            raise Exception("The position does not belong to a valid \
                            Portfolio.")

    def fill_pos(self, fill_time = datetime.datetime.now(), pos_type='Long-Buy'):
        """
        Fill position method.

        Parameters
        ----------
        fill_time : datetime, optional
            The filling time. The default is datetime.datetime.now().

        Raises
        ------
        Exception
            If the position status is not pending or there are not enough 
            give_obj in the portfolio.

        Returns
        -------
        position object

        """
        # check if the position is Pending
        if self.position.status == PositionStatus.PENDING:
            pass
        else:
            raise Exception("The position must be in Pending state to be filled.")
            
        port = self.position.portfolio

        # check if you have the avaliable fund in the portfolio
        if port.master_table[port.master_table['name']==
                             self.position.give_obj.name]['quantity'].iloc[0] <\
                                                self.position.give_obj.quantity:
                                                
            raise Exception('{} action failed. You do not have enough {} in \
                            your portfolio'.format(pos_type, 
                                                self.position.give_obj.name))
        else: pass
    

        if pos_type == 'Long-Buy':
            print('Execute Long-buy position.')
            
            # Pay pre-existing asset
            self.position.portfolio.sub(self.position.give_obj, datetime= fill_time)
            
            # Get the desired asset
            self.position.portfolio.add(self.position.get_obj, datetime = fill_time)
            
        elif pos_type == 'Long-Sell':
            print('Execute Long-sell position.')

            # Pay pre-existing asset
            self.position.portfolio.sub(self.position.get_obj, datetime= fill_time)

            # Get the desired asset
            self.position.portfolio.add(self.position.give_obj, datetime = fill_time) 


        elif pos_type == 'Short-Borrow':
            print('Execute Short-Borrow position.')

            # The sub method does not allow overwithdraw. 
            # Thus assume the give_obj is a {debt} object
            
            # here, assume give_obj = cash, get_obj = asset
            
            debt_obj = replace(self.position.get_obj)
            debt_obj.quantity = debt_obj.quantity*-1
            debt_obj.misc = {'debt'}
            
            
            self.position.portfolio.add(self.position.get_obj, datetime= fill_time) #actual asset
            
            
            # sell the asset here
            self.position.portfolio.sub(self.position.get_obj, datetime = fill_time)
            # earn the cash here
            self.position.portfolio.add(self.position.give_obj, datetime = fill_time)
            
            # Issue a debt object for recording the borrowingaction
            self.position.portfolio.add(debt_obj, datetime = fill_time) # debt object

        elif pos_type == 'Short-Buyback':
            print('Execute Short-Buyback position.')

            payback_debt_obj = replace(self.position.get_obj)
            payback_debt_obj.misc = {'debt'}
            
            # normal long
            # subtract the cash here to buy back the asset
            self.position.portfolio.sub(self.position.give_obj, datetime = fill_time)
            # Get the desired asset the set balance out the debt object
            # Buyback the debt object to settle the debt automatically
            self.position.portfolio.add(payback_debt_obj, datetime = fill_time)


        # charge a fee if it exits
        if self.position.fee != None: #or self.position.fee > 0:
            payment_time = fill_time+datetime.timedelta(minutes=5)
            self.position.portfolio.sub(self.position.fee, datetime= payment_time)

        # change the position status and fill time
        self.position.status = PositionStatus.FILLED
        self.position.fill_time = fill_time
        
        return self.position
    
    
    def cancel_pos(self, void_time = datetime.datetime.now()):
        """
        Cancel position method.

        Parameters
        ----------
        void_time : datetime, optional
            The cancelling time. The default is datetime.datetime.now().

        Raises
        ------
        Exception
            If the position is not yet added.

        Returns
        -------
        position object

        """
        # check if the position is Pending
        if self.position.status == PositionStatus.PENDING:
            pass
        else:
            raise Exception("The position can only be cancelled when it is in\
                            the Pending state.")
            
        self.position.status = PositionStatus.VOID
        self.position.void_time = void_time
        return self.position
    