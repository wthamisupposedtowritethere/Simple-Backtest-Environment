# -*- coding: utf-8 -*-
"""
Created on Sun May 30 23:10:49 2021

@author: Antho
"""

from btengine.backtestengine import BacktestEngine
from btengine.datamanager import DataManager
from strategy_example import Momentum
from market_benchmark import MarketBenchmark
from most_traded_benchmark import MostTraded
from datetime import timedelta, date


start_date = date(2020,1,1) #Start of the backtest
end_date   = date.today() - timedelta(1) #date(2020,9,10) #date.today() # End of the backtest

dm = DataManager()

be     = BacktestEngine(broker_fees = 0.0, capital = 800)

#market   = MarketBenchmark(dm, name = "Market")
mt       = MostTraded(dm)
mmt      = Momentum(dm, momentum_days = 3, max_stocks = 25, name = "Momentum")

be.addSelectionRules(mmt)
#be.addSelectionRules(market)
be.addSelectionRules(mt)



be.rebalance(start_date, end_date)
be.computeReturns(start_date, end_date)

#be.mergeStrategies(weights = [0.6, 0.1, 0.3], columns = "all")
v = be.forward_backtesting()