# -*- coding: utf-8 -*-
"""
Created on Wed Oct  7 23:12:15 2020

@author: Antho
"""

import numpy as np
import statsmodels.api as sm
from statsmodels import regression
from scipy.stats import linregress
from scipy.stats import norm

def skewness(r):
    '''
        ARGS:
            Series or Dataframe
        RETURNS: 
            Float or a series data with the calculated skewness
    '''
    
    # Calculate the demeaned returns 
    demeaned_r = r - r.mean()
    
    # Use the population standard deviation, ddof=0
    sigma_r = r.std(ddof=0)
    
    # Calculate the expectation of the demeaned returns raised to the third power
    exp = (demeaned_r**3).mean()
    
    # Calcualte the skew
    if(sigma_r != 0):
        skew = exp/sigma_r**3
        return skew
    return exp

# Make a kurtosis function 
def kurtosis(r):
    '''
        ARGS:
            Series or Dataframe
        RETURNS: 
            Float or a series data with the calculated kurtosis
    '''
    
    # Calculate the demeaned returns 
    demeaned_r = r - r.mean()
    
    # Use the population standard deviation, ddof=0
    sigma_r = r.std(ddof=0)
    
    # Calculate the expectation of the demeaned returns raised to the fourth power
    exp = (demeaned_r**4).mean()
    
    # Calcualte the skew
    if(sigma_r != 0):
        kurt = exp/sigma_r**4
        return kurt
    else:
        return exp
    
def modVaR(returns):
    k = kurtosis(returns)
    s = skewness(returns)
    z = norm.ppf(0.05)
    
    z = (z + (z**2 - 1)*s/6 + (z**3 - 3*z)*(k-3)/24 - (2 * z**3 - 5*z)*(s**2)/36)
    
    mcf_var = - (returns.mean() + z * returns.std(ddof=0))
    return(mcf_var)
    
def sd_pos(returns):
    average = returns.mean()
    returns_negative = returns[returns < average]
    if(len(returns_negative) > 0):
        return np.sqrt( (1/len(returns_negative)) * np.power((average - returns_negative), 2).sum() )
    else:
        return np.sqrt( (1) * np.power(average, 2).sum() )
        
def momentum(closes):
    # MAJOR UPDATE: RETURNS ARE NOW IN THE FILE
    returns = np.log(closes)
    x = np.arange(len(returns))
    slope, _, rvalue, _, _ = linregress(x, returns)
    return ((1 + slope) ** 252) * (rvalue ** 2)  # annualize slope and multiply by R^2

def alpha_beta(x, y):
    """
    list(float)*2 ->  float, float
    
    Performs a linear regression y = alpha + beta * x and returns its coefficients.
    """
    # Fit regression model

    x = sm.add_constant(x)
    model = regression.linear_model.OLS(x, y).fit()
    
    x = x[:, 1]
    
    # Returns alpha, beta
    return model.params[0][0], model.params[0][1]
    
def information_coefficient(returns, benchmark_returns):
    if(returns.isnull().mean() > 0.1):
        return np.NaN
    
    returns = returns[~returns.isnull()]
    benchmark_returns = benchmark_returns.loc[returns.index]
    
    exces_rendement = (returns - benchmark_returns)
    
    _, coeff_correlation = alpha_beta(list(exces_rendement)[:-7], list(exces_rendement.shift(-7))[:-7])
    
    IC = (coeff_correlation * exces_rendement.std() * (exces_rendement -  exces_rendement.mean())/exces_rendement.std())
    return IC.sum()