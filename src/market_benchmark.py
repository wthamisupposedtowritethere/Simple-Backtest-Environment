# -*- coding: utf-8 -*-
"""
Created on Sun May 30 00:17:28 2021

@author: Antho
"""


from btengine.selectionrules import SelectionRules
from datetime import timedelta, date
from btengine.datamanager import DataManager


class MarketBenchmark(SelectionRules):

    def __init__(self, dm, name = "Market"):
        """
        BE CAREFUL: THIS OBJECT DOES NOT TAKE INTO ACCOUNT NEWLY CREATED ASSETS TO REPRESENT THE MARKET.
        IF YOU NEED TO DO SO, YOU NEED TO REBALANCE YOUR PORTOFOLIO.
        """
        
        super().__init__(dm)
        self.name = name
       
        
    def compute_selection(self, selection_date, transactions):
        
        open_positions     = SelectionRules.getOpenPositions(transactions)
        
        # BUY RULES TTD
        # Buy market at the start of the backtest
        for quote in self.data_manager.data["returns"].columns:
            if quote not in open_positions.symbol.to_list():
                transactions   = SelectionRules.openPosition(transactions, quote, selection_date, 1 / len(self.data_manager.data["returns"].columns))
        
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
    strat   = MarketBenchmark(dm, name = "Momentum")
    
    be.addSelectionRules(strat)
    
    be.rebalance(start_date, end_date)
    be.computeReturns(start_date, end_date)