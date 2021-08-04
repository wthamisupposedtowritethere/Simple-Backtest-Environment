# Simple-Backtest-Environment
Simple backtesting environment in Python.

## Table of contents
* [General info](#general-info)
* [Technologies](#technologies)



## General info
This project aims at proposing a simple backtesting solution for any strategy dealing with an asset class without defined expiration (i.e. equities, cryptocurrencies, indices).

The code considers each element as a strategy object. Therefore, elements like the benchmark must be defined as a strategy. This can be done by implementing the rules for selecting the benchmark as a strategy, or by making a buy transaction on the strategy (if it is listed on an exchange, i.e. ^GSPC) at the start date of the backtest.

It is also possible to perform forward backtesting using simulations (Monte Carlo); although the feature is not fully implemented.
	
## Technologies
Project is created with:
* Python 3.5

It requires the following modules:
* pandas
* datetime
* tqdm
* yfinance
* numpy
* scipy
* statsmodels
* abc
* matplotlib
