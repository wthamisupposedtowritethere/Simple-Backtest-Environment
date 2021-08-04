# -*- coding: utf-8 -*-
"""
Created on Sun May 30 19:00:47 2021

This script contains SelectionRules abstract class, used as a framework to 
build simple strategies.

@author:     Anthony
@project:    Systematic strategies in the context of cryptocurrencies trading.
@subproject: Backtesting Engine
@version: 1.0.0

CHANGELOG:
    1.0.0
        - File created with main functions
        
This script requires that `abc`, `tqdm`, `pandas` be installed within 
the Python environment you are running this script in.

This file can also be imported as a module and contains the following
methods:

    * SelectionRules - Save an object in pickle format at the desired path.
    
THIS FILE IS PROTECTED BY GNU General Public License v3.0
ANY INFRINGEMENT TO THE LICENSE MIGHT AND WILL RESULT IN LEGAL ACTIONS.
"""


# imports
from datetime import date, timedelta 
import btengine.financefunctions as financeFunctions
import pandas as pd
from abc import ABC, abstractmethod
from tqdm import tqdm


class SelectionRules(ABC):    
    """Class used to create selection rules for your portfolio. It also contains
    basic functions for computing quantitative data. The general process is the
    following:
        
    (1) Create a class inheriting from this one. ex: class MyStrategy(SelectionRules)
    (2) In the init function, define which variables you want to use in addition
        to those loaded. You can also redefine them by providing a path.
    (3) Design your own selection rules in compute_selection function.

    In your own scripts, the following modules are required:
        from SelectionRules import SelectionRules

    Attributes
    ----------
    data_manager : pd.Dataframe
        Data Manager object to handle inputs/outputs
    name : str
        The name of your strategy

    Methods
    -------
    compute_selection
        Abstract method. Used to compute selection at a given date.
        Must return a Dataframe in the form of [entry_date, Symbol, weight]
    computeSD
        Computes the rolling downside semi-deviation over ndays
    computeVaR
        Computes the rolling VaR over ndays
    computeSTD
        Computes the rolling annualized standard deviation over ndays
    rebalancePosition
        Rebalances a position in a dataframe of transactions.
    openPosition
        Opens a position in a dataframe of transactions.
    closePosition
        Closes a position in a dataframe of transactions.
    getOpenPositions
        Gets a list of open positions from a dataframe of transactions.
    """
    
    def __init__(self, data_manager, name = "Unknown"):
        """
        Parameters
        data_manager : DataManager
            Data Manager object to handle inputs/outputs
        name : str, optional
            Strategy name (Default: default_strategy)
        """
        self.data_manager = data_manager
        self.name         = name
     
        
    @abstractmethod
    def compute_selection(self, selection_date, transactions):
        """Abstract method. Used to compute selection at a given date.
        Must return a Dataframe in the form of [entry_date, Symbol, weight]
        
        Parameters
        ----------
        selection_date : datetime.date
            The rebalancing date
        portfolio_daily : pd.Dataframe([entry_date, ticker, weight])
            The previous portfolio.
        """
        
        return(transactions)
    
    
    def rebalancePosition(self, transactions, transaction_id, timestamp, new_weight):
        """
        Rebalance a position in a dataframe of transactions.

        Parameters
        ----------
        transactions : pd.Dataframe
            List of transactions.
        quote : string
            Quote to open the transaction on.
        timestamp : datetime.date
            The date of opening position.
        new_weight : float
            New weight of the position.

        Returns
        -------
        transactions : pd.Dataframe
            List of transactions (updated).
        """
        
        quote = transaction_id.split("_")[1]
        
        # If partial sellof
        if transactions[transactions.TR_POS == transaction_id].weight.values[0] > new_weight:

            # Closing current transaction
            transaction = [transaction_id, quote, timestamp, 0, 'CLOSE',
                           transactions[transactions.TR_POS == transaction_id].weight.values[0] - new_weight, 
                           "REBALANCE"]
            
            transactions.loc[len(transactions)] = transaction
        
            # Opening a transaction with the new weight
            transaction    = [transaction_id + "Rb", quote, timestamp, new_weight, 'OPEN', 0.0, "REBALANCE"]
            transactions.loc[len(transactions)] = transaction
        
        
        # If reinforcement
        elif transactions[transactions.TR_POS == transaction_id].weight.values[0] < new_weight:

            # Closing current transaction
            transaction = [transaction_id, quote, timestamp, 0, 'CLOSE', 0.0, "REBALANCE"]
            transactions.loc[len(transactions)] = transaction
        
            # Opening a transaction with the new weight
            transaction    = [transaction_id + "Rb", quote, timestamp, 0, 'OPEN', 
                              transactions[transactions.TR_POS == transaction_id].weight.values[0] + new_weight, "REBALANCE"]
            
            transactions.loc[len(transactions)] = transaction      
            
        return transactions

    
    
    def openPosition(transactions, quote, timestamp, weight):
        """
        Opens a position in a dataframe of transactions.

        Parameters
        ----------
        transactions : pd.Dataframe
            List of transactions.
        quote : string
            Quote to open the transaction on.
        timestamp : datetime.date
            The date of opening position.
        weight : float
            Weight of the transaction expressed in % of your capita.

        Returns
        -------
        transactions : pd.Dataframe
            List of transactions (updated).
        """
        
        transaction_id = "TR_" + quote + "_" + timestamp.strftime("%Y%m%d")
        transaction    = [transaction_id, quote, timestamp, weight, 'OPEN', 1.0, "BUY"]
        
        transactions.loc[len(transactions)] = transaction
        
        return transactions
    
    
    def closePosition(transactions, transaction_id, timestamp):
        """
        Closes a position in a dataframe of transactions.

        Parameters
        ----------
        transactions : pd.Dataframe
            List of transactions.
        quote : string
            Quote to open the transaction on.
        timestamp : datetime.date
            The date of opening position.
        weight : float
            Weight of the transaction expressed in % of your capita.

        Returns
        -------
        transactions : pd.Dataframe
            List of transactions (updated).
        """
        
        quote = transaction_id.split("_")[1]
        transaction    = [transaction_id, quote, timestamp, 0, 'CLOSE', 1.0, "SELL"]
        
        transactions.loc[len(transactions)] = transaction
        
        return transactions
    
    
    def getOpenPositions(transactions):
        """Get open positions from a list of transactions

        Parameters
        ----------
        transactions : pd.Dataframe
            List of transactions.

        Returns
        -------
        open_positions : pd.Dataframe
            List of open positions.

        """
        open_positions = transactions.drop_duplicates(subset ="TR_POS", keep = False)
        return open_positions
    
        
    def computeMomentum(self, ndays = 90, start = date.today() - timedelta(365) * 6, end = date.today()):
        """Computes momentum over ndays rolling window.
        
        Parameters
        ----------
        ndays : float, optional
            Size of the rolling window (Default: 90 days)
        start : datetime.date
            Date of the first datapoint.
        end : datetime.date
            Date of the last datapoint.
            
        Raises
        ------
        IncoherentDateRange
            If the start date is superior to the end date. 
        """
                    
        momentums = self.data_manager.getCumulativeReturns(start, end).copy(deep=True)
        
        for ticker in tqdm(momentums.columns):
            momentums[ticker] = momentums[ticker].rolling(ndays).apply(financeFunctions.momentum, raw=False)
        
        momentums.index = pd.to_datetime(momentums.index)
        return momentums
    
    
    def computeSD(self, ndays = 90, start = date.today() - timedelta(365) * 6, end = date.today()):
        """Computes semi deviation (also known as downside risk) over ndays 
        rolling window.
        
        Parameters
        ----------
        ndays : float, optional
            Size of the rolling window (Default: 90 days)
        start : datetime.date
            Date of the first datapoint.
        end : datetime.date
            Date of the last datapoint.
        """
        SD  = self.data_manager.getTimeFrame("returns", start, end).copy(deep=True)
        
        for ticker in tqdm(SD.columns):
            SD[ticker]  = SD[ticker].rolling(ndays).apply(financeFunctions.sd_pos, raw=False)
        
        SD.index = pd.to_datetime(SD.index)
        return SD
    
    
    def computeVaR(self, ndays = 90, start = date.today() - timedelta(365) * 6, end = date.today()):
        """Computes cornish-Fisher VaR (Modified) over ndays rolling window.
        
        Parameters
        ----------
        ndays : float, optional
            Size of the rolling window (Default: 90 days)
        start : datetime.date
            Date of the first datapoint.
        end : datetime.date
            Date of the last datapoint.
            
        """
        VaR  = self.data_manager.getTimeFrame("returns", start, end).copy(deep=True)
        for ticker in tqdm(VaR.columns):
            VaR[ticker]  = VaR[ticker].rolling(ndays).apply(financeFunctions.modVaR, raw=False)

        VaR.index = pd.to_datetime(VaR.index)
        return VaR
    
    
    def computeSTD(self, ndays = 90, start = date.today() - timedelta(365) * 6, end = date.today()):
        """Computes annualized standard deviation over ndays rolling window.
        
        Parameters
        ----------
        ndays : float, optional
            Size of the rolling window (Default: 90 days)
        start : datetime.date
            Date of the first datapoint.
        end : datetime.date
            Date of the last datapoint.
        """
        vol = self.data_manager.getTimeFrame("returns", start, end).copy(deep=True)
        
        for ticker in tqdm(vol.columns):
            vol[ticker] = vol[ticker].rolling(ndays).std()*252**0.5
            
        vol.index = pd.to_datetime(vol.index)   
        return vol