# -*- coding: utf-8 -*-
"""
Created on Wed Nov 15 09:40:29 2017

@author: Serena
"""
import requests
import json
import time
import datetime
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.style as style
import numpy as np
import itertools

'''
Read in and format the data according to who the guru is
Input: guru (name of guru), stock (name of stock)
Output: Pandas dataframe with the calls (buy, sell, etc) made by a given guru for a given stock
'''    

def read_data(guru, stock):
    guru_ = guru.lower()
    txt = guru_ + "_" + stock + ".txt"
    if guru_ == "cramer":       
        data = pd.read_csv(txt, delimiter = "\t", 
                           names = ["Company",	"Date",	"Segment",	"Call","Price",	"Portfolio"])           
        data.index = data["Date"]
        data.index = pd.to_datetime(data.index, format = '%m/%d/%y').strftime('%b %d, %Y')
        data.drop("Segment",axis =1, inplace = True)
        data.drop("Price",axis =1, inplace = True)
        data.drop("Portfolio",axis =1, inplace = True)
        data.drop("Date",axis =1, inplace = True)
        data.drop("Company",axis =1, inplace = True)
        cramer_mapping = {
                1:"sell",
                2:"neg",
                3:"hold",
                4:"pos",
                5:"buy"        
                }
        data['Call'] = data['Call'].map(cramer_mapping)
        data = data.iloc[::-1] # chronological
    else:
        data = pd.read_csv(txt, delimiter = "\t",
                           names = ["Company",	"Date",	"Call"])
        data["Date"] = pd.to_datetime(data["Date"], format = '%m/%d/%y')
        data.sort_values(by = "Date", inplace = True)
        data.index = data["Date"]
        data.index = (data.index).strftime('%b %d, %Y')
        data.drop("Company",axis =1, inplace = True)
        data.drop("Date",axis =1, inplace = True)
    return data

'''
Get finance data via Google Finance for a single stock
    Outputs data with time range from start_lag days before first guru call
    to end date (default is time_now of computer) 
Input: ticker (stock ticker)
    guru_call (dataframe of call's by guru)
    start_lag (days before first call we want)
'''

def google_finance(ticker, guru_call, start_lag): 
    time_now = datetime.now()
    first_guru_date = pd.to_datetime(guru_call.index[0], format ='%b %d, %Y')
    start_date = first_guru_date - pd.Timedelta(days=start_lag) 
    data_source = "google"
    ticker_ = [ticker]
    panel_data = data.DataReader(ticker_, data_source, start_date, time_now)
    close = panel_data.ix['Close'] #adj close? check later
    all_weekdays = pd.date_range(start=start_date, end=time_now, freq='B')
    close = close.reindex(all_weekdays)
    close.index = pd.to_datetime(close.index, format = '%Y-%m-%d').strftime('%b %d, %Y')
    # Get SPY
    panel_data_spy = data.DataReader("SPY", data_source, start_date, time_now)
    #close_spy = panel_data_spy.ix['Close'] #adj close? check later
    close_spy = panel_data_spy.reindex(all_weekdays)
    close_spy.index = pd.to_datetime(close_spy.index, format = '%Y-%m-%d').strftime('%b %d, %Y')   
    close_spy = pd.DataFrame(close_spy["Close"])
    return close, close_spy

'''
Plot the data
Input: guru (calls made by a guru)
    stock_price (stock price obtained from google_finance function)
    stock_name (for chart title)
Output: Historical close price for the given stock, with the guru's calls overlayed on top of the price chart
'''

def plot(guru, stock_price, stock_name):
    data = stock_price.join(guru, how = "left")
    calls = data.dropna(axis = 0)
    buy = calls[calls["Call"] == "buy"]
    buy_s = pd.Series(data = buy[stock_name].values,
                                   index = buy.index)
    buy_df = stock_price.join(pd.DataFrame(buy_s), how = "left")
    buy_plt = pd.Series(data = buy_df[0], index = buy_df.index)
    
    pos = calls[calls["Call"] == "sell"]
    pos_s = pd.Series(data = pos[stock_name].values,
                                   index = pos.index)
    pos_df = stock_price.join(pd.DataFrame(pos_s), how = "left")
    pos_plt = pd.Series(data = pos_df[0], index = pos_df.index)

    
    hold = calls[calls["Call"] == "hold"]
    hold_s = pd.Series(data = hold[stock_name].values,
                                   index = hold.index)
    hold_df = stock_price.join(pd.DataFrame(hold_s), how = "left")
    hold_plt = pd.Series(data = hold_df[0], index = hold_df.index)

    neg = calls[calls["Call"] == "neg"]
    neg_s = pd.Series(data = neg[stock_name].values,
                                   index = neg.index)
    neg_df = stock_price.join(pd.DataFrame(neg_s), how = "left")
    neg_plt = pd.Series(data = neg_df[0], index = neg_df.index)
    
    sell = calls[calls["Call"] == "sell"]
    sell_s = pd.Series(data = sell[stock_name].values,
                                   index = sell.index)
    sell_df = stock_price.join(pd.DataFrame(sell_s), how = "left")
    sell_plt = pd.Series(data = sell_df[0], index = sell_df.index)

    style.use('fivethirtyeight')
    stock_price.interpolate().plot(color = "grey", title = stock_name, linewidth = 5)
    buy_plt.plot(linestyle='none', marker = 'o',color = "green", label = "Buy", markersize = 15)
    pos_plt.plot(linestyle='none', marker = 'o',color = "cyan", label = "Pos", markersize = 15)
    hold_plt.plot(linestyle='none', marker = 'o',color = "blue", label = "Sell", markersize = 15)
    neg_plt.plot(linestyle='none', marker = 'o',color = "orange", label = "Neg", markersize = 15)
    sell_plt.plot(linestyle='none', marker = 'o',color = "red", label = "Sell", markersize = 15)
    plt.ylabel("Price (USD)")
    plt.legend()
    
'''
Check if the guru's predictions are correct. 
    Calc the n-day moving average for the stock price.
    Compare the change in this moving average, x days after the initial call, to the overall market change (S&P 500).
    Done by checking if the moving average has changed within a certain percent, pct.
Input: guru (dataframe of guru's calls)
    stock_price (stock price obtained from google_finance function)
    ma (specifies the n for the n-day moving average)
    lag (specifies the x days after the initial call, i.e. when to check)
    pct (specifies the percent change we require
         e.g. if the guru made a buy call and if pct = 5, then we require the moving average to have increased by 5 percent
         after x days in order to say the buy call was correct)
Output: number of correct predictions (compared to overall S&P 500 change) and total predictions made by a guru
'''
    
def get_predictions_spy(guru, spy, stock_price, ma, lag, pct):
    data = stock_price.join(guru, how = "left")
    num_predictions = 0
    total_predictions = len(guru)
    if (ma != 0):
        filled = stock_price.fillna(method='ffill')
        filled_spy = spy.fillna(method='ffill')
        ma_price = pd.Series(filled.ix[:,0].rolling(window = ma, center = True).mean())
        ma_spy = pd.Series(filled_spy.ix[:,0].rolling(window = ma, center = True).mean())
    else:
        ma_price = stock_price
        ma_spy = spy["Close"]
    call = data["Call"]
    max_ = max(lag,ma)
    for i in range(len(data)-max_):
        call_= str(call[i])
        past_price = ma_price.iloc[i]
        future_price = ma_price.iloc[i+lag]
        change = ((future_price-past_price)/past_price)*100
        past_spy = ma_spy.iloc[i]
        future_spy = ma_spy.iloc[i+lag]
        change_spy = ((future_spy-past_spy)/past_spy)*100
        if not np.isnan(change):
            if (call_ == "buy") or (call_ == "pos"):
                print("Buy signal with requirement of " + str(pct) + "% change.")
                print("Stock change: "+ str(change))
                print("Market change: "+ str(change_spy))
                if (change > pct) and (change > change_spy):
                    num_predictions += 1
            if (call_ =="neg") or (call_ =="sell"):
                if (change < -pct) and (change < change_spy):
                    num_predictions += 1
            if (call_ == "hold"):
                if (change < pct) and (change > -pct) and (change < change_spy) and (change > change_spy):
                    num_predictions += 1
            else: 
                pass
    return num_predictions, total_predictions      

'''
Get the total accuracy for a guru for all the stocks
Input: guru_name (name of guru)
    stocks (list of names of all the stocks they discussed)
    indicies (list of the corresponding indices of the stocks above)
    pct (required percent change)
Output: guru's call accuracy
'''

def total_acc(guru_name, stocks, indices, pct):
    num = 0
    tot = 0
    for (stock_name, index) in zip(stocks, indices):
        stock_w_index = stock_name +":"+index
        guru_call = read_data(guru_name, stock_name)
        stock_price, spy = google_finance(stock_w_index, guru_call, 10)
        num_, tot_ = get_predictions_spy(guru_call, spy, stock_price, 10, 30, pct)
        num += num_
        tot += tot_
    acc = num/tot
    print("Correct predictions: " + str(num))
    print("Total predictions: " + str(tot))
    print("Accuracy: " + str(acc*100) +"%")
    return acc

# Testing: use 10 day moving average, lag of 10, required percent change of 5% for Kevin O'Leary's calls on Apple.
stock_name  = "AAPL"
index = "NASDAQ"
stock_w_index = stock_name +":"+index
oleary_AAPL = read_data("OLeary", stock_name)
aapl, spy = google_finance(stock_w_index, oleary_AAPL, 10)
plot(oleary_AAPL,aapl,stock_w_index)
num, tot = get_predictions_spy(oleary_AAPL, spy, aapl, 10, 10, 5)

