# -*- coding: utf-8 -*-
"""
Created on Sun May 30 00:05:15 2021

@author: Antho
"""

# Imports
from datetime import timedelta
import numpy as np


def daterange(start_date, end_date):
    """
    Create a list day by day from start_date to end_date.

    Parameters
    ----------
    start_date : datetime.date
        Start date of the daterange
    end_date : datetime.date
        End date of the daterange (excluded)
    """
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)
        
        
def getLaggedReturns_fromPrice(x, lag):
    """
    Get lagged log returns for an x pandas Serie.

    Parameters
    ----------
    x : pd.Series
        Data serie
    lag : int
        Number of periods to be lagged
    """
    price          = x
    weekly_price   = price.rolling(lag).mean()
    weekly_returns = np.log(weekly_price).diff(lag)
    weekly_returns = np.exp(weekly_returns)-1
    return weekly_returns

        
def getLaggedReturns_fromReturns(x, lag):
    """
    Get lagged log returns for an x pandas Serie.

    Parameters
    ----------
    x : pd.Series
        Data serie
    lag : int
        Number of periods to be lagged
    """
    weekly_price   = x.rolling(lag).sum()
    weekly_returns = weekly_price.diff(lag)
    return weekly_returns