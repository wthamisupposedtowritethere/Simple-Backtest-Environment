# -*- coding: utf-8 -*-
"""
Created on Sun May 30 00:15:56 2021

This script contains visual clues for interpreting backtests performance

@author:     Anthony
@project:    Systematic strategies in the context of cryptocurrencies trading.
@subproject: Backtesting Engine

This script requires that `datetime` and `numpy` be installed within 
the Python environment you are running this script in.

This file can also be imported as a module and contains the following
methods:

    * plotReturns        - Plots returns from multiple strategies.

THIS FILE IS PROTECTED BY GNU General Public License v3.0
ANY INFRINGEMENT TO THE LICENSE MIGHT AND WILL RESULT IN LEGAL ACTIONS.
"""

# Imports
from datetime import timedelta
import matplotlib.pyplot as plt  


def plotReturns(returns,
                subtext = "Data source: Yahoo Finance"    
                          "\nAuthor: Anthony Woznica"    
                          "\nNote: Backtests are limited due to Data time range. The benchmark used is the most traded cryptocurrencies.",
                folder = "../out/",
                name   = "Strategies Plot"):
    """
    Plots returns from multiple strategies.

    Parameters
    ----------
    returns : pd.Dataframe
        Dataframe containing the daily returns
    name : str
        Strategy name(s) to be plotted.
    subtext : str
        Text to be displayed below the graph.
    folder: str
        Folder where the image should be exported.
    name: str
        Name of the graph.
    """
    
    data = returns
    
    # Colors list
    colors = [(0, 0, 0), (31, 119, 180), (174, 199, 232), (255, 127, 14), (255, 187, 120),    
             (44, 160, 44), (152, 223, 138), (214, 39, 40), (255, 152, 150),    
             (148, 103, 189), (197, 176, 213), (140, 86, 75), (196, 156, 148),    
             (227, 119, 194), (247, 182, 210), (127, 127, 127), (199, 199, 199),    
             (188, 189, 34), (219, 219, 141), (23, 190, 207), (158, 218, 229)]
    colors = colors[:len(data.columns)]
    
    # Scale the RGB values to the [0, 1] range   
    for i in range(len(colors)):    
        r, g, b = colors[i]    
        colors[i] = (r / 255., g / 255., b / 255.)  
        
    # Figure size   
    plt.figure(figsize=(20, 9))
    
    # Define a style for the graph 
    ax = plt.subplot(111)    
    ax.spines["top"].set_visible(False)     
    ax.spines["right"].set_visible(False)    
    ax.spines["left"].set_visible(False)
    
    plt.ylim(min(data.min()) - 0.05, max(data.max()) + 0.05)
    plt.grid()
    
    names = data.columns.tolist() 
  
    # Plotting text
    for rank, column in enumerate(names):     
        plt.plot(data.index.values,    
                data[column.replace("\n", " ")].values,    
                lw=2.5, color=colors[rank])    
  
        y_pos = data[column][-1] 

        plt.text(max(data.index) + timedelta(5), y_pos, column, fontsize=12, color=colors[rank])    
    
    # Title and Subtext
    plt.text(data.index[int(len(data.index)/2)], max(data.max()) + 0.1, name, fontsize=17, ha="center")    
    plt.text(min(data.index), min(data.min()) - 0.15, subtext, fontsize=10)    
    
    # Saving file.
    plt.savefig(folder + name + ".png", bbox_inches="tight", dpi=300)