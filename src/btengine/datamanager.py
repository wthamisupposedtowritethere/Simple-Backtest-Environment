# -*- coding: utf-8 -*-
"""
Created on Sat May 29 19:28:41 2021

This script contains DataManager class, used as a pipeline for loading as well
as downloading from Yahoo Finance financial data.

@author:     Anthony
@project:    Systematic strategies in the context of cryptocurrencies trading.
@subproject: Backtesting Engine
@version: 1.0.0

CHANGELOG:
    1.0.0
        - File created with main functions
        
This script requires that `yfinance`, `tqdm`, `pandas` be installed within 
the Python environment you are running this script in.

This file can also be imported as a module and contains the following
methods:

    * DataManager - Builds an environment to use data.
    
THIS FILE IS PROTECTED BY GNU General Public License v3.0
ANY INFRINGEMENT TO THE LICENSE MIGHT AND WILL RESULT IN LEGAL ACTIONS.
"""

# Imports
import pandas as pd
from datetime import date, timedelta 
from pandas_datareader import data as pdr
import yfinance as yf
from tqdm import tqdm
import sys
from btengine.custom_errors import IncoherentDateRange, MissingColumn

# Override pandas datareader for compatibility issues
yf.pdr_override()


params = {"SymbolColumn" : "Symbol"}


class DataManager():
    """Framework for using data downloaded from Yahoo Finance.
    
    Attributes
    ----------
    quotes : list
        List of strings corresponding to Tickers
        
    data : dict(DataFrame)
        Dictionnary containing dataframes of financial data
        
    Returns
    -------
    quotes.Symbol.to_list() : list[string]
        List of Symbols to feed to the Yahoo Finance API.
    
    Raises
    ------
    MissingColumn
        If the column "Symbol" is missing.
    """
    def __init__(self,
                 quotes_file    = "../data/named/quotes.csv",
                 update_data    = False,
                 feed_start     = date.today() - timedelta(365) * 10,
                 feed_end       = date.today(),
                 returns_folder = "../data/financial/",
                 verbose        = True
                 ):
        
        self.quotes = self.getQuotes(quotes_file)
        
        # Updating Data        
        if update_data:
            for quote in self.quotes:
                self.getData(quote, feed_start, feed_end)

        self.data   = self.load(self.quotes, returns_folder)
        
    def getQuotes(self, file = "../data/named/quotes.csv"):
        """Get tickers from a csv file.
        
        Parameters
        ----------
        file : string
            Path to the csv file. The file must contain a column named 'Symbol'
            
        Returns
        -------
        quotes.Symbol.to_list() : list[string]
            List of Symbols to feed to the Yahoo Finance API.
        
        Raises
        ------
        MissingColumn
            If the column "Symbol" is missing.
        """
        
        quotes = pd.read_csv(file)
        
        if not params["SymbolColumn"] in quotes.columns:
            raise MissingColumn("Symbol")
            
        return quotes.Symbol.to_list()    



    def getData(self, quote, start = date.today(), end = date.today(), folder = "../data/financial/"):
        """Write a csv file corresponding to the pricing for a given quote over a
        one year time period.
        
        Parameters
        ----------
        quote : string
            The quote as it appears on Yahoo Finance
        start : datetime.date
            Date of the first datapoint.
        end : datetime.date
            Date of the last datapoint.
        folder : string
            Folder inwhich all returns files are contained.
            
        Raises
        ------
        IncoherentDateRange
            If the start date is superior to the end date.
        Generic Error
            In any error happened during the process. Failed downloads are not
            considered as errors.
        """
            
        if start > end:
            raise IncoherentDateRange(start, end)
        
        try:
            data = pdr.get_data_yahoo(quote, start = start, end = end)
            data.to_csv(folder + quote + ".csv")
        except:
            print("Unexpected error for quote" , quote, ":", sys.exc_info()[0])
            raise
        
        
        
    def load(self, quotes, folder = "../data/financial/", verbose = False):
        """Load return files; drop NAs, remove duplicated rows, set Date as the index
        and converts it to percent change.
        /!\ Keep in mind: Those are day-to-day percent change, NOT CUMULATIVE RETURNS.
        
        Parameters
        ----------
        quotes : string
            The list of quotes
        folder : string
            Folder inwhich all returns files are contained.
        verbose : boolean
            Errors printing (T/F).
            
        Returns
        -------
        data : dict(Dataframe[Date.datetime, float])
            Dictionnary of dataframes containing financial datapoints.
        """
        
        data = {'returns' : pd.DataFrame(), 'volume' : pd.DataFrame(), 'prices' : pd.DataFrame()}
        
        for quote in tqdm(quotes):
            
            try:
                x = pd.read_csv(folder + quote.strip() + ".csv")
                x = x.dropna()
                x = x[~x.index.duplicated(keep='last')]
                x.index = x.Date
                
                # Volume
                volume         = x['Volume']
                volume.name    = quote
                data['volume'] = pd.merge(data['volume'], volume, how='outer', 
                       left_index=True, 
                       right_index = True)
                            
                        
                # Prices
                price_close      = x["Adj Close"]
                price_close.name = quote
                data['prices'] = pd.merge(data['prices'], price_close, how='outer', 
                                   left_index=True, 
                                   right_index = True)
                
                # Returns
                close           = x["Adj Close"].pct_change()
                close.name      = quote
                data['returns'] = pd.merge(data['returns'], close, how='outer', 
                                   left_index=True, 
                                   right_index = True)
                
                data['returns'][quote].iloc[0] = 0.0
                
            except:
                if verbose:
                    print("[-] Error for", quote, "the table will not be loaded.")
                pass
        
        data['returns'].fillna(0, inplace=True)
        data['volume'].fillna(0, inplace=True)
        data['prices'].fillna(method="backfill")
        
        data['returns'].index = pd.to_datetime(data['returns'].index)  
        data['volume'].index = pd.to_datetime(data['volume'].index)
        data['prices'].index = pd.to_datetime(data['prices'].index)
        
        return data


    def getTimeFrame(self, column, start, end = date.today()):
        """Computes cumulative returns between two dates (both start and end are
        included).
        
        Parameters
        ----------
        column : string
            String indicating which data dictionnary entry to work with.
        start : datetime.date
            Date of the first datapoint.
        end : datetime.date
            Date of the last datapoint.
            
        Raises
        ------
        IncoherentDateRange
            If the start date is superior to the end date.  
        MissingColumn
            If the column entered in parameters is missing.
        """
        
        if start > end:
            raise IncoherentDateRange(start, end)

        if not column in self.data.keys():
            raise MissingColumn(column)
            
        x = self.data[column]
        
        return x[(x.index.date >= start) & (x.index.date <= end)]
    
    
    def getCumulativeReturns(self, start, end = date.today()):
        """Computes cumulative returns between two dates (both start and end are
        included).
        
        Parameters
        ----------
        returns : pd.DataFrame
            Dataframe containing returns
        start : datetime.date
            Date of the first datapoint.
        end : datetime.date
            Date of the last datapoint.
            
        Raises
        ------
        IncoherentDateRange
            If the start date is superior to the end date.    
        """
        
        if start > end:
            raise IncoherentDateRange(start, end)
        
        return self.getTimeFrame("returns", start, end).apply(lambda x: (1 + x).cumprod())
        

    
    
# Use example
if __name__ == "__main__":
    dm = DataManager()
    dm.getCumulativeReturns(date.today() - timedelta(365) * 2, date.today())