# -*- coding: utf-8 -*-
"""
Created on Sun May 30 00:17:28 2021

@author: Antho
"""

from btengine.backtestengine import BacktestEngine
from btengine.selectionrules import SelectionRules
import pandas as pd
from datetime import timedelta, date
import os
from btengine.datamanager import DataManager

class Momentum(SelectionRules):

    def __init__(self, dm, momentum_days = 90, max_stocks = 8, name = "Momentum-90D"):
        super().__init__(dm)
        self.name       = name
        self.md         = momentum_days
        self.max_stocks = max_stocks
        
        # Loading precomputed data
        if os.path.isfile("../data/precalculated/momentum_" + str(momentum_days) + ".pkl"):
            self.momentums = pd.read_pickle("../data/precalculated/momentum_" + str(momentum_days) + ".pkl")
        else:
            self.momentums  = self.computeMomentum(momentum_days)
            self.momentums.to_pickle("../data/precalculated/momentum_" + str(momentum_days) + ".pkl")
        
        
    def compute_selection(self, selection_date, transactions):
        
        # Sums Momentums
        momentum_scores_daily  = self.momentums[self.momentums.index.date == selection_date - timedelta(1)].dropna(1, how="any")

        i = 2
        while (momentum_scores_daily.empty) and (selection_date - timedelta(i) > self.momentums.index[0].date()):
            momentum_scores_daily  = self.momentums [self.momentums.index.date  == selection_date - timedelta(i)].dropna(1, how="any")
            i += 1

        if not momentum_scores_daily.empty:
            
            investible = self.data_manager.data["returns"][self.data_manager.data["returns"].index.date == selection_date - timedelta(1)].dropna(axis=1, how='all')
            
            
            momentum_scores_daily = momentum_scores_daily[investible.columns.to_list()].dropna(1)
            momentum_scores_daily = momentum_scores_daily.loc[:, momentum_scores_daily.ge(0.001).all()].T

            momentum_scores_daily["f1"] = momentum_scores_daily[momentum_scores_daily.columns[0]]

            #Sorting
            momentum_scores_daily = momentum_scores_daily.sort_values(by = "f1", axis=0, ascending = False)
            
            # Note that selection is already sorted by momentum
            selection = momentum_scores_daily.head(2).index.to_list()
            
            # BUY & SELL RULES TTD
            # Buy at most 2 stocks with highest momentum
            open_positions     = SelectionRules.getOpenPositions(transactions)
            
            # If more than 8 positions at the same time: we need to sell one
            for quote in selection:
                
                if len(open_positions) >= self.max_stocks:
                    
                    open_positions_scores = open_positions.join(momentum_scores_daily[momentum_scores_daily.index.isin(open_positions.symbol)], on = "symbol")

                    # If higher momentum: we sell the stock in selection with lowest momentum
                    sell = open_positions_scores[open_positions_scores.f1 < momentum_scores_daily[momentum_scores_daily.index == quote].f1.values[0]]
                    
                    if len(sell) > 0:
                        sell = sell.sort_values(by = "f1", ascending = True)                        
                        transactions   = SelectionRules.closePosition(transactions, sell.head(1).TR_POS.values[0], selection_date)
                        transactions   = SelectionRules.openPosition(transactions, quote, selection_date, 1 / self.max_stocks)
                        open_positions = SelectionRules.getOpenPositions(transactions)
                        
                else:
                        transactions   = SelectionRules.openPosition(transactions, quote, selection_date, 1 / self.max_stocks)
                        open_positions = SelectionRules.getOpenPositions(transactions)
               
                        
               
            # If the momentum for an asset turns out to be negative, we close the position immediately
            open_positions     = SelectionRules.getOpenPositions(transactions)
            
            for index, row in open_positions.iterrows():
                if momentum_scores_daily[momentum_scores_daily.index == row["symbol"]].empty and row["symbol"] in investible.columns.to_list():                    
                    transactions   = SelectionRules.closePosition(transactions, row.TR_POS, selection_date)
                
                
        # Return the daily selection
        return transactions
 

if __name__ == '__main__':
    
    start_date = date(2020,9,1) #Start of the backtest
    end_date   = date.today() - timedelta(1) #date(2020,9,10) #date.today() # End of the backtest

    dm = DataManager()
    be     = BacktestEngine(broker_fees = 0.00)
    strat   = Momentum(dm, momentum_days = 3, max_stocks = 25, name = "Momentum")
    
    be.addSelectionRules(strat)
    
    be.rebalance(start_date, end_date)
    be.computeReturns(start_date, end_date)