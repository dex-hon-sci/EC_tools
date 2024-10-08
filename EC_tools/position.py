"""
Created on Wed May 29 23:49:08 2024

@author: dexter


Position Module.

"""
# python import
from dataclasses import dataclass, field, replace
from typing import Protocol, Union
from enum import Enum, auto
import datetime as datetime
from attrs import setters

# EC_tools import
from EC_tools.portfolio import Portfolio
import EC_tools.utility as util  
    

__all__=['PositionStatus', 'PositionType', 'Position', 'ExecutePosition']
__author__="Dexter S.-H. Hon"

class PositionStatus(Enum):
    """
    A set of possible status for positions.
    
    """
    PENDING = "Pending" # When the position is added but not filled
    FILLED = "Filled" # When the position is executed
    VOID = "Cancelled" # When the position is cancelled

    
class PositionType(Enum):
    """
    A set of possible types of positions
    """
    LONG_BUY = 'Long-Buy'
    LONG_SELL = 'Long-Sell'
    SHORT_BORROW = 'Short-Borrow'
    SHORT_BUYBACK = 'Short-Buyback'
    CALL_BUY = 'Call-Buy'
    CALL_SELL = 'Call-Sell'
    PUT_BUY = 'Put-Buy'
    PUT_SELL = 'Put-Sell'
    
    
@dataclass
class Position(object):
    """
    Position class that create and manage position objects.
    
    The position objects tracks the give and get objects and the 
    
    """
    # key attributes
    give_obj: dict # Asset
    get_obj: dict # Asset
    _price: float
    status: PositionStatus = PositionStatus.PENDING
    portfolio: Portfolio = None
    
    # optional asset control
    size: float = 1
    fee: dict = None
    pos_type: str = 'Long-Buy'
    
    # position attribute adjustable
    open_time: datetime = datetime.datetime.now() 
    fill_time: datetime = None
    void_time: datetime = None
    auto_adjust: bool = True
    pos_id: str = util.random_string()  
    #misc: dict = field(default_factory={'None'})
    
    def __post_init__(self, 
                      void_time: datetime = datetime.datetime.now(), 
                      epi: float = 1e-8):
        """
        The post init function that checks if the input price is correct.
        If it is not. the position is voided.
        
        """
        # check if the quantity of both assets are 
        #correct_ratio = self.give_obj.quantity / (self.get_obj.quantity*self.size)
        # reminder: give is cash, get is asset (usually)
        correct_ratio =  self.give_obj['quantity'] / (self.get_obj['quantity']*self.size)

        #print('correction_ratio', correct_ratio, self.price)
        
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
        self._fix_quantity = self.get_obj['quantity']
        
    @property
    def fix_quantity(self) -> None:
        """
        This is a speical attribute for each position object. It defines which 
        quantity to be fixed for an exchange to be executed when the price is 
        not exactly as stated in the position object. It can either be 
        self.give_obj.quantity or self.get_obj.quantity.

        """
        return self._fix_quantity
    
    @fix_quantity.setter
    def fix_quantity(self, value: Union[int, float]) -> int | float:
        """
        Setter method to change the value of fix_quantity.

        Parameters
        ----------
        value : int or float
            The new fix value.

        Returns
        -------
        int or float
            DESCRIPTION.

        """
        self._fix_quantity = value
        return self._fix_quantity
    
    @property
    def price(self) -> float:
        """
        Getter method for calling position's price.

        Returns
        -------
        float
            The price of this exchanges.

        """
        return self._price
    
    @price.setter
    def price(self, value: Union[int, float]) -> None:
        """
        Setter method for calling position's price.

        """
        # check if the new price is the same 
        if value != self.give_obj['quantity'] / (self.get_obj['quantity']*self.size):
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
        if self.fix_quantity == self.give_obj['quantity']:
            self.get_obj['quantity'] = self.give_obj['quantity']  / (self._price*self.size)
            
        elif self.fix_quantity == self.get_obj['quantity']:
            self.give_obj['quantity'] = self.get_obj['quantity']*(self._price*self.size)
            
class ExecutePosition(object):
    """
    A class that execute the position.
    
    """
    
    def __init__(self,  Position: Position):
        self.position = Position
        
        #check if there is a Portfolio attached to the position.
        if not isinstance(self.position.portfolio, Portfolio):
            raise Exception("The position does not belong to a valid \
                            Portfolio.")
    def fill_pos(self, 
                 fill_time: datetime = datetime.datetime.now(), 
                 pos_type: str ='Long-Buy') -> None:
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
            
        # define a delay time so that each entry would not be simultaneous.
        # simultaneous entry results in fault calculation in the Portfolio method 
        delay_time = datetime.timedelta(seconds=0.1) 

        if pos_type == 'Long-Buy':
            #print('Execute Long-buy position.')
            
            # Pay pre-existing asset
            self.position.portfolio.sub(self.position.give_obj, 
                                        datetime= fill_time)
            
            #print(self.position.give_obj)
            
            # Get the desired asset
            self.position.portfolio.add(self.position.get_obj, 
                                        datetime = fill_time + delay_time)
            #print(self.position.get_obj)

            
        elif pos_type == 'Long-Sell':
            #print('Execute Long-sell position.')

            # Pay pre-existing asset
            self.position.portfolio.sub(self.position.get_obj, 
                                        datetime= fill_time)
            #print(self.position.get_obj)

            # Get the desired asset
            self.position.portfolio.add(self.position.give_obj, 
                                        datetime = fill_time + delay_time) 

            #print(self.position.give_obj)

        elif pos_type == 'Short-Borrow':
            #print('Execute Short-Borrow position.')

            # The sub method does not allow overwithdraw. 
            # Thus assume the give_obj is a {debt} object
            
            # Here, assume give_obj = cash, get_obj = asset
            # Set up the debt object
            debt_obj = self.position.get_obj.copy() #replace(self.position.get_obj)
            debt_obj['quantity'] = debt_obj['quantity']*-1
            debt_obj['misc'] = {'debt'}
            
            # The "Borrow" action
            self.position.portfolio.add(self.position.get_obj, 
                                        datetime= fill_time) #actual asset
            
            # sell the asset here
            self.position.portfolio.sub(self.position.get_obj,
                                        datetime = fill_time + delay_time)
            # earn the cash here
            self.position.portfolio.add(self.position.give_obj, 
                                        datetime = fill_time + delay_time*2)
            
            # Issue a debt object for recording the borrowingaction
            self.position.portfolio.add(debt_obj, datetime = 
                                        fill_time + delay_time*3) # debt object

        elif pos_type == 'Short-Buyback':
            #print('Execute Short-Buyback position.')

            payback_debt_obj = self.position.get_obj.copy() #replace(self.position.get_obj)
            payback_debt_obj['misc'] = {'debt'}
            
            # normal long
            # subtract the cash here to buy back the asset
            self.position.portfolio.sub(self.position.give_obj, 
                                        datetime = fill_time)
            # Get the desired asset the set balance out the debt object
            # Buyback the debt object to settle the debt automatically
            self.position.portfolio.add(payback_debt_obj, 
                                        datetime = fill_time + delay_time)


        # charge a fee if it exits
        if self.position.fee != None: #or self.position.fee > 0:
            payment_time = fill_time+ delay_time*10
            # Fees are calculated per contracts                                
            self.position.portfolio.sub(self.position.fee, 
                                        datetime= payment_time)

        # change the position status and fill time
        self.position.status = PositionStatus.FILLED
        self.position.fill_time = fill_time
        
    
    def cancel_pos(self, void_time: datetime = datetime.datetime.now()) -> None:
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
