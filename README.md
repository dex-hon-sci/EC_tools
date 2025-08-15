# *EC_tools*: A utility package for building Trading Strategies 


## Overview
`EC_tools` (Euler Capital tools) is a utility package that provides useful tools 
to build your trading strategies. 

It serves as a baseline for building an
analytical ETL data processing pipelines that:
1. Process raw market data,
2. Generate trading signals,
3. Backtest trading strategy based on signals, and
4. Evaluate/Plot portfolio performances

## Module Reviews
`EC_tools` contains the following modules:
| Module | Description |
|-----------|-------------|
| `backtest` |Contains the core backtesting functions. The backtesting<br>process is optimised by running time-series segementation<br>based of the informations supplied by the `Signal` objects<br>(the output from `Strategy`) and vector operation on the<br>raw market data. In other words, the backtest engine only<br>looks at the relevant portion of historical data based on<br>your strategy. |
| `base` | Contains file-reading and data extraction types of functions. |
| `features` | Contains functions that derive additional *features* given<br>raw market data. |
| `order` | Contains `Order` data class that are used in the backtesting<br>engine. The `Portfolio` objects rely on the mecahnsim in this<br>module to modify their states. |
| `plot` | Contains plotting scripts. Intraday price action and Profolio PNL<br>are uses functions in this module. |
| `portfolio` | Contains data container `Portfolio` class. Backtesting engine<br>operate on the `Portfolio` object. It modifying its state and<br>add/subtract items in it. It also contains handy methods for<br>logging trades and calculating portfolio metrics. |
| `signal` | Contains `Signal` data class object that serve as a universal<br>format for the output of any `Strategy` class objects.<br>All user-defined strategies must conform to this protocol and<br>produce `Signal`objects before supplying them to the backtesting<br>engine. `Signal` objects contains the effective period of the<br>signal and a list of `Order` objects associated with the<br>intended orders to be sent to the backtest engine. |
| `strategy` | Contains `Strategy` Protocol class and the signal<br>generation logic, as well as the looping mechanism for<br>the signal generation process. |
| `trade` | Contains different trade logic and methods of calculating<br>trade returns. |
| `utility` | Contains the basic mathmatical or format related utility<br>functions. |

## Usage
In this example, I will demonstrate the entire cycle of generating trading signals
and backtesting a strategy using `EC_tools`.

### Feature Extraction
```python
import pandas as pd

```
### Signal Generation

Defining a strategy object
### `simple_strat.py`
```python
from datetime import datetime
from EC_tools.strategy.base import Strategy
from EC_tools.strategy_2.signal import Signal, SignalType, SignalSide, SignalStatus
from EC_tools.order.cqg_enums import OrderSide, OrderType
from EC_tools.order.cqg_order import CQGOrder # In this example, we use CQG orders for demonstration

# First, you need to define a Strategy object that contains the signal generation logic.
class SimpleStrategy(Strategy): # Inherit by the `Strategy` Protocol class
    """
    This simple strategy does xxx
    """
    def __init__(data1: pd.DataFrame, data2: pd.DataFrame):
        pass
        
    def gen_data():
        return
         
    def make_signals(up_threshold: float, down_threshold: float):
        diff = data1 - data2
        if diff > up_threshold:
            # Target-Entry Order
            action_TEO_SHORT = CQGOrder(asset_name,
                                        OrderSide.SIDE_SELL,
                                        OrderType.ORDER_TYPE_MKT,
                                        QTY, open_=True, close_=False,
                                        kwargs={'MKT_time': TE_time,
                                                'MKT_price':TE_price})
            # Target-Exit Order
            action_TPO_SHORT = CQGOrder(asset_name,
                                        OrderSide.SIDE_BUY,
                                        OrderType.ORDER_TYPE_LMT,
                                        QTY,  open_=False, close_=True,
                                        kwargs={'LMT_price': TP_price})  
                                                       
            actions = [action_TEO_SHORT, action_TPO_SHORT, 
                       action_SLO_SHORT, action_MCO_SHORT]
            
            S = Signal(SignalType.SELL, # Signal type
                       SignalSide.SELL, # Signal Side
                       SignalStatus.INACTIVE, # Signal status
                       TE_time, # start_time
                       CO_time, # end_time
                       actions) # Orders

        elif diff < down_threshold:
            pass
        
        return 
        
    def apply():
        return
    
# Second, you need to provide the looping
# mechanism in running this strategy
def loop_signal(df1: pd.DataFrame, df2: pd.DataFrame, 
                unique_dates: list[datetime], # A list of unique trading date
                asset_name_1: str, asset_name_2: str, 
                qty: int,
                open_hr: str, close_hr: str,
                **kwargs)-> pd.DataFrame:
                
    master_signal_df = pd.DataFrame()
    for i, date in enumerate(unique_dates):
        signal_df = SimpleStrategy(...).apply()
        # Updating the master signal dataframe
        master_signal_df = pd.concat([master_signal_df, signal_df])
        
    master_signal_df = master_signal_df.sort_values(by=["signal_datetime"], 
                                                    ascending=True)
    return master_signal_df
    
```

Now make a run method for the signal generation process.
### `run_sig_gen_SimpleStrat.py`
```python
from EC_tools.strategy.simple_strategy import loop_signal

def run_gen_signals(daily_minute_data_pkl: dict[pd.DataFrame], 
                    start_date: datetime, 
                    end_date: datetime, 
                    symbol_list: list[str],
                    **kwargs):    
    master_dict  = dict()
    for symbol in symbol_list:
        # Load Historical data
        HISTORY_MINUTE_PKL = load_source_data_bt([daily_minute_data_pkl[symbol]])
        HISTORY_MINUTE_PKL[symbol] = reindex_dt(HISTORY_MINUTE_PKL[symbol])
        
        # Select for the range of dates
        new_df = new_df[(new_df['Datetime'] >= start_date) & 
                        (new_df['Datetime'] <= end_date)]
        
        # Define unique trading date for the script to loop through        
        unique_dates = util.get_trading_date(start_date,end_date,
                                             exchange=EXCHANGE[symbol])
        open_hr, close_hr = kwargs['open_hr_dict'][symbol], kwargs['close_hr_dict'][symbol]
        ######### Feature Extraction Layer #################################    
        # Calculate VWAP, save it in the dataframe as a new column.
        new_df = add_VWAP2df(new_df, unique_dates, open_hr, close_hr)
        new_df = add_ATR(new_df)
       
        filename = kwargs['save_filenames_loc'][symbol]
        @util.pickle_save("{}".format(filename), save_or_not=kwargs['save_or_not'])
        def run_gen_MR_indi():
            master_signal_df = loop_signal(new_df, 
                                           unique_dates, 
                                           asset_name, QTY, 
                                           open_hr, close_hr,
                                           **kwargs)
            return master_signal_df
        master_dict[symbol] = run_gen_MR_indi()
    return master_dict

```

### Backtesting

Define backtest engine and run method.
### `run_backtest_SimpleStrat.py`
```python
from EC_tools.strategy.signal import SignalStatus, SignalType, Signal
from EC_tools.trade.onetradeperseg import OneTradePerSeg
from EC_tools.trade import Trade # Trsde protocol class for type hints
import EC_tools.base.read as read
from EC_tools.portoflio.base import Portfolio
from EC_tools.backtest import activate_signal_1atatime # Activate signal one-at-a-time. Only allow one active signal before a trade is completed.

# To define a backtest engine
def backtest_engine(trade_method: Trade,
                    portfo: Portfolio,
                    signals: pd.DataFrame,
                    histroy_data: pd.DataFrame):
    # Loop through the signal list,  
    # Only test for the ACTIVE signals
    signal_datetime = signals['signal_datetime'].to_list()
    signal_list = signals['signal'].to_list()
    
    # Initiate latest_dateime
    latest_datetime = datetime(2020,12,31,0,0,0)
    active_signals = pd.DataFrame()
    # Loop through a list of time-ordered signals.
    # This method assumes signals Independent backtest (Signals 
    # does not interact with each other)
    for i, signal in enumerate(signal_list):
        #### Signal activation Layer
        # First check and control if this is an active signal
        # Turn on ACTIVE signal if the signal start after 7:30 UTC for enough Volume. 
        if signal.start_time.time() > datetime.time(hour=7,minute=30):
            print("Signal comes after 7:30. Try to activate Signal.")
            # Only turn on the signal if the last signal is already resolved
            signal = activate_signal_1atatime(signal, latest_datetime)

        #### Trading layer
        # Check if the signal is active
        if signal.status == SignalStatus.ACTIVE:
            # Segmentation: isolate price data segment
            seg_start_dt, seg_end_dt = signal.start_time, signal.end_time
            sub_history_data = histroy_data[(histroy_data['Datetime']>=seg_start_dt) &
                                            (histroy_data['Datetime']<=seg_end_dt)]
            # Run_trade
            T = trade_method(portfo, signal, sub_history_data, i)
            T.run_trade()
            # Update the latest_datetime based on the closing trade 
            # of the Trade object for this signal
            if np.nan not in T.close_pt:
                latest_datetime = T.close_pt[0]
                active_signals = pd.concat([active_signals, 
                                            pd.DataFrame([active_signal_row])])
    return portfo, active_signals
    
# Now define the run backtest function to handle input related operationa before
# running the backtest engine.
def run_backtest(TradeMethod, 
                 signals, 
                 daily_minute_data_pkl, 
                 start_date: str, 
                 end_date: str, **kwargs):
    start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')

    # Run backtest control the range of datetime and signal selections
    # Initialise Portfolio
    P1 = Portfolio()
    # Add 10,000,000 USD into the Portfolio First
    USD_initial = {'name':"USD", 'quantity': 10_000_000, 'unit':"dollars", 
                   'asset_type': "Cash", 'misc':{}} # initial fund
    P1.add(USD_initial, datetime=datetime(2020,12,31))
    
    symbol_list = ['CLc1']
    for symbol in symbol_list:
        # Load Historical data
        HISTORY_MINUTE_PKL = load_source_data_bt([daily_minute_data_pkl[symbol]])
        # reindexing with time
        histroy_data = reindex_dt(HISTORY_MINUTE_PKL[symbol])
        histroy_data = histroy_data[(histroy_data['Datetime'] >=start_date) &
                                    (histroy_data['Datetime'] <=end_date)]
        
        signals = signals[(signals['signal_datetime'] >=start_date) &
                          (signals['signal_datetime'] <=end_date)]
        
        P1, active_signals = backtest_engine(TradeMethod, P1, signals, histroy_data)
        if kwargs['save_or_not']: # save pkl portfolio
            file = open(kwargs['master_pnl_filename'], 'wb')
            file2 = open(kwargs['active_signal_filename'], 'wb')
            pickle.dump(P1, file)  # Save the portfolio in pickle format
            pickle.dump(active_signals, file2) # Save the active signals
    return P1, active_signals
    
```

Note that the signal generation and backtesting engine are completely separated.
This is to maintain the modular nature of our system and allow user to switch 
to different strategies while using the same backtest engine. Naturally, specific
backtest engine can be made using the framework provided by this package to include
additional conditions.

### Plotting/Evaluation script
### `main.py`
```python
# To define a backtest engine

```

### Main ETL pipeline

An typical ETL pipeline will look like the following:
```python
from run_sig_gen_SimpleStrat import run_gen_signals
from run_backtest_SimpleStrat import run_backtest

def main():
    run_gen_signals()
    run_backtest()
    
    
```
Example plots

Example Porfolio Metrics



 


