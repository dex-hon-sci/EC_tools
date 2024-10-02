# Welcome to EC_tools Documentation

For full documentation visit [mkdocs.org](https://www.mkdocs.org).

## Code annotation Examples

## Codeblocks

```py

import EC_tools.read as read

```

## Project layout

    mkdocs.yml    # The configuration file.
    main.py       # The main function that generates signal and backtest
    crudeoil_future_const.py  # Global variables related to Crude-oil Futures
    docs/
        index.md  # The documentation homepage.
        ...       # Other markdown pages, images and other files.
    app/          # Application scripts
        argus_latest_meta.csv # Meta-data used to download APC from Argus Server
        __init__.py
        run_apc_price_study.py  # Run studies on APC performance
        run_backtest.py  # Backtesting Application
        run_comparison_plot.py  # Run comparison between signals generations
        run_daily_instruction.py  # Generation of daily XLS trader template 
        run_data_management.py  #
        run_gen_monthly_MR_dir.py  # Trading signal generation for monthly MR strategy
        run_gen_MR_dir.py  # Trading signal generation for daily MR strategy
        run_plot_heatamp.py # Plot Heatmap for backtest results under different settings
        run_PNL_plot.py  # Plot PNL for different strategies
        run_preprocess.py  # Convert the raw data into usable formats
        run_update_db.py  # Automatically download the latest data
    ext_codes/    # External codes
    EC_tools/     # The essential tools and modlues
        __init__.py
        __version__.py
        backtest.py  # Backtesting functions and loop class
        bookkeep.py  # Bookkeeping formatting class
        features.py
        math_func.py  # General Mathematics Functions
        plot.py #  Plot Pricing chart
        portfolio.py  # Portfolio class, the Log, and the Metrics
        position.py  # Position classes for Trade
        read.py  # Read, sorting, and reformat functions
        simple_trade.py  # Simple Trade functions
        trade.py  # Trade classes
        utility.py  # General utility functions
    tests/       # Unit tests
        test_ArgusMRStrategy.py
        test_ArgusMRStrategyMode.py
        test_bidirectionaltrade.py
        test_func_speed.py
        test_math_func.py
        test_onetradeperday.py
        test_onetradeperday_2.py
        test_plot.py
        test_portfolio.py
        test_position.py
        test_strategy.py
