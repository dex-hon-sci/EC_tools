#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 28 16:11:10 2024

@author: dexter
"""
from dataclasses import dataclass, field, replace
from typing import Protocol
import datetime

@dataclass
class Asset(Protocol):
    """
    A class that solely define the attribute of a Asset object.
    # We can abnadon this and just use a dict for asset
    
    Base class for all assets.
    
    """
    name: str ="" # note that future countract should be written in the CLM24 format
    qty: int or float = 0
    misc: dict[str] = field(default_factory=dict)
   
@dataclass
class Security(Asset):
    name: str = ""
    unit: str = ""
    value: float = 0
    numeriare: str = "USD"

@dataclass
class Derivative(Asset):
    name: str = ""
    unit: str = "Contract"
    value: float = 0
    numeriare: str = "USD"
    underlying: Security = field(default_factory = Security(name=name, 
                                                            qty=0,
                                                            value = 0))

@dataclass
class CallOption(Derivative):
    asset_type:str = "Call-Option"
    strike: float = 0 
    premium: float = 0
    exp: datetime.datetime = None
    def __post_init__(self):
        if self.underlying.value > self.strike:
            self.payoff = self.underlying.value - self.premium
        elif self.underlying.value  <= self.strike:
            self.payoff = - self.premium

@dataclass
class PutOption(Derivative):
    #name: str = ""
    asset_type:str = "Put-Option"
    strike: float = 0 
    premium: float = 0
    exp: datetime.datetime = None # expiration datetime
    def __post_init__(self):
        if self.underlying.value < self.strike:
            self.payoff = self.underlying.value - self.premium
        elif self.underlying.value  >= self.strike:
            self.payoff = - self.premium

@dataclass  
class Future(Derivative):
    #name: str = ""
    asset_type:str = "Future"
    exp: datetime.datetime = None # expiration datetime

    def __post_init__(self):\
        self.payoff = self.underlying.value
        
    
# =============================================================================
# Example
# S = Security(name = "CLM25", qty = 10, unit='lot')
# S.value = 100
# C = CallOption(name = S.name , strike = 10, premium =8, exp= datetime.datetime.now(), underlying = S)
# C.name
# S.name
# C.value
# S.value
# C.payoff
# S.value = 40
# C= replace(C,underlying=S)
# C.payoff
# =============================================================================
