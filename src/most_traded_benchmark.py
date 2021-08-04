# -*- coding: utf-8 -*-
"""
Created on Mon May 31 13:00:25 2021

@author: Antho
"""

from btengine.selectionrules import SelectionRules
from datetime import timedelta, date
from btengine.datamanager import DataManager


class MostTraded(SelectionRules):

    def __init__(self, dm, n = 5, name = "N Most Traded"):
        """
        BE CAREFUL: THIS OBJECT DOES NOT TAKE INTO ACCOUNT NEWLY CREATED ASSETS TO REPRESENT THE MARKET.
        IF YOU NEED TO DO SO, YOU NEED TO REBALANCE YOUR PORTOFOLIO.
        """
        
        super().__init__(dm)
        self.name = name
        self.n = n
        
    def compute_selection(self, selection_date, transactions):
        
        open_positions     = SelectionRules.getOpenPositions(transactions)
        
        # BUY RULES TTD
        # Buy market at the start of the backtest
        for quote in self.data_manager.data["volume"].mean(axis = 0).sort_values().tail(self.n).index.to_list():
            if quote not in open_positions.symbol.to_list():
                transactions   = SelectionRules.openPosition(transactions, quote, selection_date, 1 / self.n)
        
        # SELL RULES TTD
        # None (Market Benchmark)
    
        # Return the daily selection
        return transactions
 

if __name__ == '__main__':
    
    from backtestengine import BacktestEngine
    
    start_date = date(2020,9,1) #Start of the backtest
    end_date   = date.today() - timedelta(1) #date(2020,9,10) #date.today() # End of the backtest

    dm = DataManager()
    be     = BacktestEngine(broker_fees = 0.01)
    strat   = MostTraded(dm, name = "Momentum")
    
    be.addSelectionRules(strat)
    
    be.rebalance(start_date, end_date)
    be.computeReturns(start_date, end_date)