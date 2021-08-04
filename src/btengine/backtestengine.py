# -*- coding: utf-8 -*-
"""
Created on Sat May 29 23:58:00 2021

This script contains BacktestEngine class. It is used to perform performance
calculations as well as to call strategies.

@author:     Anthony
@project:    Systematic strategies in the context of cryptocurrencies trading.
@subproject: Backtesting Engine
@version: 1.0.0

CHANGELOG:
    1.0.0
        - File created with main functions
        
This script requires that `datetime`, `tqdm`, `pandas` be installed within 
the Python environment you are running this script in.

This file can also be imported as a module and contains the following
methods:

    * SelectionRules - Save an object in pickle format at the desired path.
    
THIS FILE IS PROTECTED BY GNU General Public License v3.0
ANY INFRINGEMENT TO THE LICENSE MIGHT AND WILL RESULT IN LEGAL ACTIONS.
"""


# Imports
from datetime import timedelta
import pandas as pd
from btengine.selectionrules import SelectionRules
from btengine.visualizer import plotReturns
from pandas.tseries.offsets import BDay
from tqdm import tqdm
import btengine.my_utils as my_utils
import btengine.simulationfunctions as sim


class BacktestEngine():
    """Class used for backtesting. The general process for making backtests is the following:
    (1) Write a strategy as a child class of SelectionRules
    (2) Initialize this class with your own parameters
    (3) Call for BacktestEngine.rebalance to rebalance your portfolio and backtest it.
    (4) Call BacktestEngine.computeReturns to get the returns.

    In your own scripts, the following modules are required:
        from btengine.BacktestEngine import BacktestEngine
        from btengine.SelectionRules import SelectionRules

    Attributes
    ----------
    broker_fees : float
        The fees of your own broker.(default is 0.0)
    selectionRules : SelectionRules
        The selection class designed using an SelectionRules child-class
    transactions : list
        A list of dataframes containing all transactions made by a strategy
    performance_daily: Dataframe
        Dataframe containing daily returns for the strategy and the benchmark
    analyzer: Analyzer
        Analyzer module, initialized after modules computation

    Methods
    -------
    computeReturns(start_date, end_date, plot = True, save = True)
        Computes the portfolio returns between two dates. Requires a rebalancing
        to be run.
    rebalance(start_date, end_date)
        Rebalance the portfolio between two dates. Needs addArtemisSelectionRules
        to be called first.
    addSelectionRules
        Add selection rules for the rebalancing
    forward_backtesting
        Not done yet !
    """
    
    def __init__(self, broker_fees = 0.0, capital = 1, folder = "../out/"):
        """
        Constructor.

        Parameters
        ----------
        broker_fees : float, optional
            The fees of your own broker.(default is 0.0) in % of the transaction (scale 0-1). The default is 0.0.
        capital : float, optional
            Base capital (keep 1 if you only want to see the performance). The default is 1.0.
        folder : string, optional
            Path to the output folder. The default is "../out/".

        Returns
        -------
        None.

        """

        self.broker_fees    = broker_fees
        self.capital        = capital
        self.folder         = folder
        self.selectionRules = []
        self.transactions   = None
        self.returns        = None

    def computeReturns(self, start_date, end_date, plot = True, save = True):
        """Computes the portfolio returns between two dates. Requires a rebalancing
        to be run.

        Parameters
        ----------
        start_date : datetime.date
            The start date
        end_date : datetime.date
            The end date          
        plot : boolean, optional
            Default: True, saves the graph in the script's directory.
            
        save : boolean, optional
            Default: True, saves the performances in a csv format in script's directory.
            
        Raises
        ------
        NotImplementedError
            If the rebalancing has not been done first.
        """
        
        print("[-] Backtest Started...")
        
        if(len(self.transactions) == 0):
            raise NotImplementedError("No rebalancing found. Please call rebalance function first.")
            
        self.returns = pd.DataFrame()
        
        # Look for every transactions from strategies
        for i in range (0, len(self.transactions)):
            
            # Load and save (if option enabled) trades history
            transactions_strat = self.transactions[i]
            if(save):
                transactions_strat.to_csv(self.folder + self.selectionRules[0].name + "_trades" + ".csv")
                    
                
            quotes = transactions_strat.symbol.unique()
            
            # Initialize strategy track record
            track_record = pd.DataFrame(index=self.selectionRules[i].data_manager.data["returns"].index,
                                        columns = self.selectionRules[i].data_manager.data["returns"].columns)
            track_record = track_record[track_record.index.date >= start_date]
            
            # Fetch transactions for every quote
            for quote in quotes:
                
                quote_transactions = transactions_strat[transactions_strat.symbol == quote]
                daily_returns      = self.selectionRules[i].data_manager.data["returns"][quote]
                returns_trans      = []
                
                # Process of each opening transaction.
                for index, quote_transaction in quote_transactions[quote_transactions.action == "OPEN"].iterrows():
                    
                    # Process of each closing transaction.
                    quote_close = quote_transactions[
                        (quote_transactions.action == "CLOSE") & 
                        (quote_transactions.TR_POS == quote_transaction.TR_POS)
                        ]
                    
                    # Work with closed positions
                    if not quote_close.empty:
                        returns_period = daily_returns[
                            (daily_returns.index.date >= quote_transaction.date) & 
                            (daily_returns.index.date < quote_close.date.values[0])
                            ]
                        
                        returns_period[-1] = returns_period[-1] - self.broker_fees *  quote_transaction.fees_coeff
       
                    # Open positions (computing to the last datapoint)
                    else:
                        returns_period = daily_returns[
                            daily_returns.index.date >= quote_transaction.date
                            ]
            
                    # Weight of the transaction in the total capital - broker fees (at open & close)
                    # TODO: REWORK BROKER FEES WITH PRICE
                    if not returns_period.empty:                   
                        returns_period[0]  = returns_period[0]  - self.broker_fees *  quote_transaction.fees_coeff
                         
                    returns_period =  returns_period * quote_transaction.weight
            
                    # Adding the applicable period to the list
                    returns_trans.append(returns_period)
                        
                # Regroupement des daily returns
                quote_returns_pos = pd.concat(returns_trans)
                quote_returns_pos = quote_returns_pos.groupby(quote_returns_pos.index).sum()
            
                track_record[quote] = quote_returns_pos
            
            track_record = track_record.fillna(0)
            track_record_strategy = track_record.sum(axis = 1)
            track_record_strategy = ((1 + track_record.sum(axis = 1)).cumprod()) * self.capital
            track_record_strategy.name = self.selectionRules[i].name  
            
            self.returns = pd.concat([self.returns, track_record_strategy], axis=1)
        
        
        if(plot):
            plotReturns(self.returns, self.selectionRules[0].name)
        
        if(save):
            self.returns.to_csv(self.folder + self.selectionRules[0].name + ".csv")
        
        print("[-] Backtest finished...")
        return self.returns
    
    
    
    def mergeStrategies(self, weights, name = "Portfolio", columns = "all", plot = True, save = True):
        """
        Merge existing strategies into a single strategy

        Parameters
        ----------
        weights : list
            List of weights for the selected strategies.
        name : string, optional
            Name of the macrostrategy created. The default is "Portfolio".
        columns : string or list, optional
            List of strategies to combine. The default is "all".
        plot : Boolean, optional
            Wether the program should plot the results. The default is True.
        save : TYPE, optional
            Wether the program should save the results. The default is True.

        Raises
        ------
        TypeError
            If the columns variable is not a list or 'all'.
        ValueError
            If list of weights differs from the number of columns.

        Returns
        -------
        pd.DataFrame
            Dataframe containing returns for all strategies, including the newly created.

        """
        
        if not (1 + 1e-6 > sum(weights) and 1 - 1e-6 < sum(weights)):
            print("[-] Warning: weights do not sum to 1; meaning you are either leveraged or have non-invested capital")
        
        if isinstance(columns, str):
            if columns == "all":
                # If weights are provided for all strategies
                columns = [x for x in self.returns.columns] 
            else:
                raise TypeError("Variable 'columns' must be either 'all' or a list of existing strategies.")
    
        if len(weights) != len(self.returns.columns):
            raise ValueError("Length of 'weights' list does not correspond to the number of selected strategies.")
                    
            
        self.portfolio_strat      = self.returns[columns]
        for i in range(0, len(columns)):
            self.portfolio_strat[columns[i]] = self.portfolio_strat[columns[i]] * weights[i]
        
        self.portfolio_strat      = self.portfolio_strat.sum(axis = 1)
        self.portfolio_strat.name = name

        self.returns = pd.concat([self.returns, self.portfolio_strat], axis = 1)
                  
        if(plot):
            plotReturns(self.returns, name)
        
        if(save):
            self.returns.to_csv(self.folder + name + ".csv")
            
        return self.returns
            
    
        
    def rebalance(self, start_date, end_date, showstate = True):
        """Rebalance the portfolio between two dates. Needs addSelectionRules
        to be called first.

        Parameters
        ----------
        start_date : datetime.date
            The rebalancing start date
        end_date : datetime.date
            The rebalancing end date
            
        Raises
        ------
        NotImplementedError
            If artemisObject has not been initialized first.
        """
        
        print("[-] Rebalancing started...")
        
        # Check if we can start the backtest
        if(len(self.selectionRules) == 0):
            raise NotImplementedError("[-] No selection method found. Please call addArtemisSelectionRules before calling this function")
        
        # Portfolio & Historical portfolio
        self.transactions = list(pd.DataFrame(columns =['TR_POS', 'symbol', 'date', 'weight', 'action', 'fees_coeff', 'label']) for x in range(0,len(self.selectionRules)))
        
        # Rebalancing
        for selection_date in my_utils.daterange(start_date, end_date + timedelta(1)):
            #print(selection_date)
            for i in range(0, len(self.selectionRules)):
                self.transactions[i] = self.selectionRules[i].compute_selection(selection_date, self.transactions[i].copy())
                if(self.transactions[i].empty):
                    print("Warning: the portfolio has not been updated. Please ensure that your SelectionRules return a dataframe.")

        print("[-] Rebalancing finished.")
        
        
        
    def addSelectionRules(self, selectionObject):
        """Add selection rules for the rebalancing

        Parameters
        ----------
        selectionObject : SelectionRules
            The selection class designed using an SelectionRules child-class

        Raises
        ------
        TypeError
            If selectionObject is not an instance of SelectionRules
        """
        if(isinstance(selectionObject, SelectionRules)):
            self.selectionRules.append(selectionObject)
        else:
            raise TypeError ("[-] Expected an SelectionRules type object, got ", type(selectionObject), "instead.")
            
            
    def forward_backtesting(self, days_to_forecast = 25, simulation_trials = 1000, vol_multiplier = 1,
                            confidence = 0.75):
        
        lower_range = int(simulation_trials * (1 - confidence) / 2)
        upper_range = simulation_trials - lower_range

        # 1. Simulating the data
        self.simulation_per_strat = {}
        
        # Each strategy can have its own data manager, thus the iterations
        for i in range(len(self.selectionRules)):
            returns     = self.selectionRules[i].data_manager.data["prices"]
            indices     = pd.date_range(returns.index[-1] + timedelta(1),
                                        returns.index[-1] + timedelta(days_to_forecast * 2), 
                                        freq=BDay())[:days_to_forecast + 1]
    
            simulations = {}
            for ticker in tqdm(list(returns.columns)):
                y = sim.simulate(returns[ticker], 
                                 days_to_forecast + 1, 
                                 simulation_trials, 
                                 'log', 
                                 vol_multiplier = 1)
                
                y = pd.concat([pd.DataFrame([pd.Series([returns[ticker][-1]] * simulation_trials)]), y], 
                              ignore_index=True)
                
                # TODO DEPLACER CE BLOC PLUS BAS
                y       = (1 + y.pct_change()).cumprod()
                #y       = y * returns[ticker][-1]
                y       = y.iloc[1:]
                y       = y.sort_values(y.last_valid_index(), axis=1)

                y.index = indices
                     
                simulations[ticker] = y
                
            self.simulation_per_strat[self.selectionRules[i].name] = simulations

        # 2. Getting the portfolios performances
        # Better option in newer version of the script
        for i in range(len(self.selectionRules)):
            strat_name  = self.selectionRules[i].name
            positions   = SelectionRules.getOpenPositions(self.transactions[i])

            lb_perfs = []
            ub_perfs = []
            mean_perfs = []

            for index, row in positions.iterrows():
                lb_perfs.append(self.simulation_per_strat[strat_name][row.symbol].iloc[:, [lower_range]] * row.weight)
                ub_perfs.append(self.simulation_per_strat[strat_name][row.symbol].iloc[:, [upper_range]] * row.weight)
                mean_perfs.append(self.simulation_per_strat[strat_name][row.symbol].mean(axis = 1) * row.weight)
                
            lb_perfs   = pd.concat(lb_perfs, axis=1).sum(axis = 1)   * self.returns[self.selectionRules[i].name][-1]
            ub_perfs   = pd.concat(ub_perfs, axis=1).sum(axis = 1)   * self.returns[self.selectionRules[i].name][-1]
            mean_perfs = pd.concat(mean_perfs, axis=1).sum(axis = 1) * self.returns[self.selectionRules[i].name][-1]
            
            lb_perfs.rename("Lower CR  "  + self.selectionRules[i].name, inplace = True)
            ub_perfs.rename("Upper CR  "  + self.selectionRules[i].name, inplace = True)
            mean_perfs.rename("Mean  "  + self.selectionRules[i].name,   inplace = True)
            
            self.returns = pd.merge(self.returns, lb_perfs, how='outer', 
                                   left_index=True, 
                                   right_index = True)
            
            self.returns = pd.merge(self.returns, ub_perfs, how='outer', 
                                   left_index=True, 
                                   right_index = True)
            
            self.returns = pd.merge(self.returns, mean_perfs, how='outer', 
                                   left_index=True, 
                                   right_index = True)
            
        return self.returns
        