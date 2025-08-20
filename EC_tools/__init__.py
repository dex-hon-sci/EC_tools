#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 11 16:33:24 2025

@author: dexter
"""

"""
A tool for finacial analytics.

A tool made to mainpulate pricing data from various sources, 
to generate trading signals, backtest trading strategies, and 
execute trades through third-party API. 

A procedural interface is provided by the companion pyplot module,
which may be imported directly, e.g.::

    import EC_tools.strategy as strategy

or using ipython::

    ipython

at your terminal, followed by::

    In [1]: %EC_tools
    In [2]: import EC_tools.strategy as strategy

at the ipython shell prompt.

Modules include:

:mod: 'read'
"""
#__all__ = []

__pdoc__ = {}

# Import version
from ._version import __version__ as _version

__version__ = _version

from EC_tools.backtest import *
from EC_tools.backtest_2 import *
from EC_tools.base import *
from EC_tools.ext import *
from EC_tools.feature import *
from EC_tools.order import *
from EC_tools.plot import *
from EC_tools.portfolio import *
from EC_tools.portfolio_2 import *
from EC_tools.signal import *
from EC_tools.strategy import *
from EC_tools.strategy_2 import *
from EC_tools.trade import *
from EC_tools.trade_2 import *
from EC_tools.utility import *

__pdoc__['_settings'] = True