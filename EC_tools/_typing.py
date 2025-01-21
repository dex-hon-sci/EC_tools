import numpy as np
import pandas as pd
from pandas import Series, DataFrame as Frame, Index
from typing import *
from datetime import datetime, timedelta, tzinfo


# Generic types
Typ = TypeVar("T")
Func = TypeVar("F", bound=Callable[..., Any])

# Config

# Arrays
Array = np.ndarray  # ready to be used for n-dim data
Array1D = np.ndarray
Array2D = np.ndarray
Array3D = np.ndarray
Record = np.void
RecordArray = np.ndarray

# Trade functions

# Strategy functions

# Strategy signal

# backtest