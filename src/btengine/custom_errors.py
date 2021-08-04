# -*- coding: utf-8 -*-
"""
Created on Sat May 29 19:39:14 2021

This script contains IncoherentDateRange and MissingColumn Exceptions classes.

@author:     Anthony
@project:    Systematic strategies in the context of cryptocurrencies trading.
@subproject: Backtesting Engine
@version: 1.0.0

CHANGELOG:
    1.0.0
        - File created with main functions
        
This file can also be imported as a module and contains the following
methods:

    * IncoherentDateRange - Exception raised for dates (start date < end date).
    * MissingColumn - Exception raised for the absence of a specific column in 
                      a dataframe.
        
THIS FILE IS PROTECTED BY GNU General Public License v3.0
ANY INFRINGEMENT TO THE LICENSE MIGHT AND WILL RESULT IN LEGAL ACTIONS.
"""


class IncoherentDateRange(Exception):
    """Exception raised for dates.

    Parameters
    ----------
        start : string
            The ticker as it appears on Yahoo Finance
        end : datetime.date
            Date of the first datapoint.
        message : datetime.date
            Message sent back to the console by default.
    """

    def __init__(self, start, end, message="Start date must be lower or equal to End date."):
        self.start   = str(start)
        self.end     = str(end)
        self.message = message
        super().__init__(self.message)
        
    def __str__(self):
        return f'{self.start} > {self.end}: {self.message}'
    
    
    
class MissingColumn(Exception):
    """Exception raised for the absence of a specific column in a dataframe.

    Parameters
    ----------
        name : string
            Name of the column
        message : datetime.date
            Message sent back to the console by default.
    """

    def __init__(self, name, message="Please make sure your dataframe has the beforementionned column. The symbols must be compatible with Yahoo Finance tickers."):
        self.name   = str(name)
        self.message = message
        super().__init__(self.message)
        
    def __str__(self):
        return f'{self.name}: {self.message}'