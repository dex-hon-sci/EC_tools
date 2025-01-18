#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 28 16:11:10 2024

@author: dexter
"""
from dataclasses import dataclass, field

@dataclass
class Asset:
    """
    A class that solely define the attribute of a Asset object.
    # We can abnadon this and just use a dict for asset
    
    """
    name: str  # note that future countract should be written in the CLM24 format
    quantity: int or float
    unit: str
    asset_type:str 
    misc: dict[str] = field(default_factory=dict)