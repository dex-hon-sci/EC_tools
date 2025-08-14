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
    - `backtest`: Contains the core backtesting functions. The backtesting 
                  process is optimised by running time-series segementation 
                  based of the informations supplied by the `Signal` objects 
                  (the output from `Strategy`) and vector operation on the 
                  raw market data. In other words, the backtest engine only 
                  looks at the relevant portion of historical data based on 
                  your strategy.
    - `base`: Contains file-reading and data extraction types of functions.
    - `features`: Contains functions that derive additional *features* given 
                  raw market data.
    - `order`: Contains `Order` data class that are used in the backtesting 
               engine. The `Portfolio` objects rely on the mecahnsim in this 
               module to modify their states.
    - `plot`: Contains plotting scripts. Intraday price action and Profolio PNL 
              are uses functions in this module.
    - `portfolio`: Contains data container `Portfolio` class. Backtesting engine 
                   operate on the `Portfolio` object. It modifying its state and
                   add/subtract items in it. It also contains handy methods for 
                   logging trades and calculating portfolio metrics.
    - `signal`: Contains `Signal` data class object that serve as a universal 
                format for the output of any `Strategy` class objects. 
                All user-defined strategies must conform to this protocol and 
                produce `Signal`objects before supplying them to the backtesting 
                engine. `Signal` objects contains the effective period of the 
                signal and a list of `Order` objects associate
    - `strategy`: Contains `Strategy` Protocol class and the signal 
                  generation logic, as well as the looping mechanism for 
                  the signal generation process.
    - `trade`: Contains different trade logic and methods of calculating trade returns.
    - `utility`: Contains the basic mathmatical or format related utility functions

## Usage
In this example, I will demonstrate the entire cycle of making and backtesting  
a trading strategy using `EC_tools`.

### Feature Extraction
```python

```
### Signal Generation
Defining a strategy
```python

```
Run signal generation script 
```python
```

### Backtesting
```python

```

### Plotting/Evaluation script


### Main ETL pipeline
An typical ETL pipeline will look like the following:
```python
```
Example plots

Example Porfolio Metrics



 


