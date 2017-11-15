# -*- coding: utf-8 -*-
"""
Created on Wed Nov 15 10:03:17 2017

@author: Serena
"""

# -*- coding: utf-8 -*-
"""
Created on Fri Oct 27 08:39:57 2017

@author: Serena
"""

import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

path_to_chromedriver = 'C:/Users/Serena/Desktop/Projects/chromedriver.exe'
browser = webdriver.Chrome(executable_path = path_to_chromedriver)
caps = DesiredCapabilities().CHROME
caps["pageLoadStrategy"] = "none"
url = "https://seekingalpha.com/opinion-leaders/long-ideas"
browser.get(url)

# Initial dataframes

authors = get_authors()
tickers = pd.DataFrame(columns = ["TICKER_NAME"])
articles = pd.DataFrame(columns = ["ARTICLE"])
id_tbl = pd.DataFrame(columns = ["AUTHOR_ID","TICKER_ID","ARTICLE_ID"])
calls = pd.DataFrame(columns = ["TICKER_ID","ARTICLE_ID","CALL"])
# Get data
tickers, articles, id_tbl = get_ticker_articles(authors, tickers, articles, id_tbl)
id_tbl, tickers, articles_w_dates, calls = search_article(authors, id_tbl, articles, tickers, calls)

def get_authors():
    links = []
    for link in browser.find_elements_by_css_selector('.ld_page_main a'):
        url_ = link.get_attribute('href')
        if url_ not in links:
            links.append(url_)
    del(url_)
    auth_temp = [author.split("author/") for author in links]
    authors = [auth_temp[i][1] for i in range(len(auth_temp)-1)]
    authors = [x.replace("-", " ") for x in authors]
    authors = [x.upper() for x in authors]
    del(links[-1])
    result = list(zip(authors,links))
    df = pd.DataFrame(result)
    df.columns = ["AUTHOR", "SOURCE"]
    return df

def get_ticker_articles(authors, curr_ticks, curr_arts, ids):
    
    for person in authors.itertuples(index=True, name='Pandas'):

        source = person[2]
        browser.get(source)

        # Get tickers #
        try:
            for ticker in browser.find_elements_by_class_name('ticker-btn'):
                ticker_ = ticker.get_attribute('data-ticker')
                curr_ticks = add_tickers([ticker_], curr_ticks)
        except:
            pass
    # Get articles #

    for person in authors.itertuples(index=True, name='Pandas'):
        browser.get(person[2])
        p_id = person[0]

       # round 1
        for i in range(2, 33):
            j = str(i)
            general_url = '//*[@id="profile-tab-content"]/div[1]/div[' \
                + j + ']/'
            html_url = general_url + 'div[1]/a'
            for article in browser.find_elements_by_xpath(html_url):
                article_ = article.get_attribute('href')
                curr_arts = add_articles([article_], curr_arts)
                a_id = lookup_article(article_, curr_arts)
                ids = append_id_tbl(p_id, a_id, ids)                
        # round 2 #
        for i in range(2, 33):
            j = str(i)
            general_url2 = '//*[@id="profile-tab-content"]/div[2]/div[' \
                + j + ']/'
            html_url2 = general_url2 + 'div[1]/a'
            for article in browser.find_elements_by_xpath(html_url2):
                article_ = article.get_attribute('href')
                curr_arts = add_articles([article_], curr_arts)
                a_id = lookup_article(article_, curr_arts)
                ids = append_id_tbl(p_id, a_id, ids)
    return (curr_ticks, curr_arts, ids)


def append_id_tbl(p_id, a_id, id_tbl):
    
    cols = ["AUTHOR_ID", "ARTICLE_ID"]
    ids = [p_id, a_index]
    s = pd.Series(ids, index = cols)
    id_tbl_ = id_tbl.append(s, ignore_index = True)
    return id_tbl_
    

def lookup_article(article, df):
    
    mask = df[df["ARTICLE"] == article]
    arr = (mask.index.values).tolist()
    return arr

def lookup_ticker(ticker, df):
    mask = df[df["TICKER_NAME"] == ticker]
    arr = (mask.index.values).tolist()
    return arr

def lookup_author_of_article(article_id, ids):
    mask = ids[ids["ARTICLE_ID"] == article_id]
    arr = (mask["AUTHOR_ID"]).tolist()
    return arr

# input list of tickers
# this will add the tickers if they're not yet seen
def add_tickers(to_add, tickers):
    add = pd.DataFrame(to_add)
    add.columns = ["TICKER_NAME"]
    for i in range(len(add)):
        add_ = add["TICKER_NAME"].iloc[i] 
        if lookup_ticker(add_, tickers) == []:
            tickers = tickers.append(add.iloc[i], ignore_index = True)
    return tickers

# input articles
# add articles if not yet seen
    # dataframe not properly constructed???
def add_articles(to_add, articles):
    add = pd.DataFrame(to_add)
    add.columns = ["ARTICLE"]
    for i in range(len(add)):
        add_ = add["ARTICLE"].iloc[i] 
        if lookup_article(add_, articles) == []:
            articles = articles.append(add.iloc[i], ignore_index = True)
    return articles

def search_article(authors, id_tbl, articles, tickers, disclosures):
    
    articles_ =list(articles["ARTICLE"].values)
    
    for article in articles_:
        url = article
        browser.get(url)
        xpath = '//*[@id="a-hd"]/div[1]/span/span[2]/a'
        xpath_date = '//*[@id="a-hd"]/div[1]/span/time'
        src = browser.page_source
        # watch out for infinite loop
        try:
            date_path = browser.find_element_by_xpath(xpath_date)
            date_ = date_path.get_attribute("content").split("T")[0]
            dates.append(date_)
            tick_path = browser.find_element_by_xpath(xpath)
            ticker = tick_path.get_attribute("href")
            ticker = ticker.split("https://seekingalpha.com/symbol/")[1]
        except:
            continue
            browser.execute_script("location.reload()")
            date_path = browser.find_element_by_xpath(xpath_date)
            date_ = date_path.get_attribute("content").split("T")[0]
            dates.append(date_)
            tick_path = browser.find_element_by_xpath(xpath)
            ticker = tick_path.get_attribute("href")
            ticker = ticker.split("https://seekingalpha.com/symbol/")[1]
            
        # Add ticker to tickers if necessary
        tickers = add_tickers([ticker.lower()], tickers)
        # Get ticker ID
        t_id = lookup_ticker(ticker.lower(), tickers)
        # Get artcle ID
        a_id = lookup_article(url, articles)
        p_id = lookup_author_of_article(a_id, id_tbl)
        all_ids = [p_id[0], t_id[0], a_id[0]]
        cols = ["AUTHOR_ID","TICKER_ID","ARTICLE_ID"]
        s = pd.Series(all_ids, index=cols)
        id_tbl = id_tbl.append(s, ignore_index = True)       
      
        articles_w_dates = pd.DataFrame(list(zip(articles_,dates)), columns = ["ARTICLE","DATE"])

        call_src = get_disclosure(src)
        ticker_src = get_ticker_from_source(src)
        url_src = get_url_from_source(src)
        
        ids2 = [t_id[0], a_id[0], call_src]
        cols2 = ["TICKER_ID","ARTICLE_ID","CALL"]
        s2 = pd.Series(ids2, index=cols2)
        disclosures = disclosures.append(s2, ignore_index = True)

    return id_tbl, tickers, articles_w_dates, disclosures
