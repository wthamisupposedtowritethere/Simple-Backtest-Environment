# -*- coding: utf-8 -*-
"""
Created on Sun May 30 20:10:11 2021

This script contains functions used to perform the simulation.

@author:     Anthony
@project:    Systematic strategies in the context of cryptocurrencies trading.
@subproject: Backtesting Engine
@version: 1.0.0

CHANGELOG:
    1.0.0
        - File created with main functions
        
This script requires that `pandas`, `numpy`, `scipy.stats` be installed within 
the Python environment you are running this script in.

This file can also be imported as a module and contains the following
methods:

    * SelectionRules - Save an object in pickle format at the desired path.
    
THIS FILE IS PROTECTED BY GNU General Public License v3.0
ANY INFRINGEMENT TO THE LICENSE MIGHT AND WILL RESULT IN LEGAL ACTIONS.
"""

import numpy as np
import pandas as pd
from scipy.stats import norm


def get_drift(data, return_type='log'):

    
    if return_type=='log':
        lr = np.log(1+data.pct_change())
    elif return_type=='simple':
        lr = (data/data.shift(1))-1
    else:
        raise NotImplementedError("[-] The type " + return_type + " has not been implemented yet.")
    

    # Mu - Var / 2    
    drift = lr.mean() - lr.var() / 2
    
    try:
        return drift.values
    except:
        return drift


def daily_returns(data, days, iterations, return_type='log', vol_multiplier = 1):
    ft = get_drift(data, return_type)
    
    # Computes volatility
    if return_type == 'log':
        try:
            stv =  np.log(1+data.pct_change()).std().values * vol_multiplier
        except:
            stv =  np.log(1+data.pct_change()).std() * vol_multiplier
    elif return_type=='simple':
        try:
            stv = ((data/data.shift(1))-1).std().values * vol_multiplier
        except:
            stv = ((data/data.shift(1))-1).std() * vol_multiplier
            
    # Drifted normal distribution / Cauchy distribution
    dr = np.exp(ft + stv * norm.ppf(np.random.rand(days, iterations)))
    
    return dr


def simulate(data, days, iterations, return_type='log', vol_multiplier = 1):
    """
    Simulates
    """
    
    # Generate daily returns
    returns = daily_returns(data, days, iterations, return_type, vol_multiplier)
    
    # Create empty matrix
    price_list = np.zeros_like(returns)
    
    # Put the last actual price in the first row of matrix. 
    price_list[0] = data.iloc[-1]
    
    # Calculate the price of each day
    for t in range(1, days):
        price_list[t] = price_list[t-1] * returns[t]
          
    return pd.DataFrame(price_list)


"""
def monte_carlo(tickers, data, days_forecast, iterations, start_date = '2000-1-1', return_type = 'log', vol_multiplier = 1):

    simulations = {}
    indices     = pd.date_range(returns.index[-1] + timedelta(1), returns.index[-1] + timedelta(days_to_forecast * 2), freq=BDay())[:days_to_forecast + 1]
    
    for t in tqdm(range(len(tickers))):
        y = simulate(data.iloc[:,t], (days_forecast+1), iterations, return_type, vol_multiplier = 1)

        y.index = indices
        simulations[tickers[t]] = y
        
    return simulations

    
ret_sim_df = monte_carlo(returns.columns, returns, days_forecast= days_to_forecast, iterations=simulation_trials, start_date=start)
"""