# Guru Ratings

# Part 1: How good is a guru? A sort of thought experiment

# Motivation

There are so many stock gurus nowadays, whether that’s someone with a following on the order of O(10) or O(10000) people. It’s easy to make a blog post or write an article stating a long or short position on a given stock, and it’s easy for a reader, or thousands of readers, to take said position without a grain of salt. How do we know these gurus are right?

I propose a project where we check the accuracy of so-called guru forecasts. The idea is as follows. For a given guru, get all the forecasts s/he has made over the entire history of their forecasting career. Get the historical prices of the stocks in question. Check if their predictions were correct. Easy enough, right? Actually, not really.

There are some difficulties in doing this. First, getting the data is a challenge. How does one have access to all the forecasts a guru has made? How much would this access cost? Once we have identified an online source, can we scrape it and actually get the data? Second, there is a question of whether this is even useful or not. One would think that any “guru” with event a hint of predictive know how would already be working in hedge fund or another financial institution- why would someone just post forecasts online, for free, and not capitalize on their own knowledge? To this I say, there’s a lot of people who have hobbies (in this case, stock market forecasting) who have other jobs, but might just like to make posts and share their knowledge with the world. They could be in it for the fun of it, not for the money.

The programming part of this project is actually quite simple. The most difficult parts are outlined above- where/how to get the data, and if it’s even worth the time in the first place.

# Description of the Code

Since this is just a prototype, I manually got stock calls from some websites for several arbitrary pundits for several arbitrary stocks, and saved the data in a csv on my computer. The csv containing the stock data has the columns Guru_Name, Stock_Name, Call, and Date. The calls can be Buy, Sell, Hold, Positive, or Negative. I decided to treat Buy and Positive as one, i.e. the pundit is saying the price of the stock will go up. Similarly, I treat Sell and Negative the same. I use the function Read_data to (surprise, surprise) read in this data into a Pandas dataframe.

I realized it wouldn’t make sense to keep on downloading data to save it on my computer, so I decided to write a function to fetch historical daily close prices for a given stock that a guru has talked about. I called this function Google_finance, which returns a dataframe of the historical daily close price of a given stock that a guru has discussed, start_lag days before the first guru call. For example, with start_lag = 5 and first_guru_call = ‘01/20/2015’, then the first entry in the returned dataframe will correspond to January 15, 2015.

Now that I have the stock calls for a given guru, and the prices for the given stock for the appropriate time frame, it’s time to write the function that actually checks if the guru was correct in their prediction. I sloppily named this function Get_predictions_spy, with the “spy” part coming from the fact that I want to compare the change in a particular stock with the overall change in the market. I use the S&P 500 index as a marker of overall market change. I compute the n-day moving average of the stock prices, with the n specified by my parameter “ma.” I check if the n-day moving average of the stock price is greater (lower) than pct, if the guru made a buy (sell) call, else for a hold. A question that comes up is how long term these predictions are- for that I included a “lag” parameter. This way I can easily check if a guru is correct 5 days after they make a call, 30 days, or 100 days, etc.

Get_predictions_spy(guru, spy, stock_price, ma, lag, pct): output the number of correct predictions compared to the overall increase in the market (SP500 data frame), and the total number of predictions. Stock_price is obtained from google_finance. Take the “ma”-day moving average of the stock prices lag days after a guru call. Check if the value is greater or lower than pct.

Finally I have a simple function called Total_acc that just lets me get the total accuracy of a given guru’s calls, for multiple stocks.

# Example

As an example, let’s look at Kevin O’Leary’s track record on Apple. I only have 2 sample points. This is pretty horrible, and as someone with two math degrees I should probably be ashamed of myself. However, I think this is enough to show the point of this exercise. Let’s say we use a 10 day moving average, a lag of 10, and a required percent change pct of 5%. The code below does this.

stock_name = "AAPL"
index = "NASDAQ"
stock_w_index = stock_name +":"+index
oleary_AAPL = read_data("OLeary", stock_name)
aapl, spy = google_finance(stock_w_index, oleary_AAPL, 10)
plot(oleary_AAPL,aapl,stock_w_index)
num, tot = get_predictions_spy(oleary_AAPL, spy, aapl, 10, 10, 5)

The output is:

Buy signal with requirement of 5% change.
Stock change: 5.67899526001
Market change: 0.645022847189
Buy signal with requirement of 5% change.
Stock change: -0.810814531338
Market change: -0.576555858982

So O’Leary was correct the for his first call, but not the second, so O’Leary gets 50%, given the parameters we chose. You can see by just glancing at the chart below that changing the lag would definitely change O’Leary’s score.


Price of AAPL overlaid with two buy signals made by Kevin O'Leary.
Future Work

I think it’s pretty clear that future work, if I wasn’t treating this as anything more than a slightly extensive thought experiment, would involve cleaning up my code and improving my output figures. Future work would also involve scaling and an automated way to obtain data- I talk about this in part 2 below. It’d be interesting to extend this to not just what people actually said about stocks, but how they felt, i.e. use sentiment analysis. We have these powerful computing tools available, why not use them to see if something interesting comes up? Overall this could be a very valuable project, one worth putting in time for.

# Part 2: Automation and scaling

# Tools: Python, Selenium Webdriver, SQL

The scraping part of this project consists of fetching data from any website where individuals make stock forecasts. This would require scraping and saving the data in an automated way. I use Selenium WebDriver which allows you to scrape a website, while it thinks you’re a regular internet surfing user, rather than a web scraping program. I use SQL to manage the data. The advantage of SQL is, admittedly, mainly that I know how to use SQL and Python together. Compared to NoSQL, SQL just works. It’s simple, clear, and you know what you’ll get when you make a query. Scalability is of course an issue with SQL, but if you know how much data you’ll have, or can control that, it’s not a problem. In addition, if you know that your project will never be getting infinite data, then it’s fine to use SQL. In my case, I can control how much data I get, and I can say that my project won’t be infinite. If it expands, then I can revisit this, but for now, go SQL!

# The 5 SQL Tables

There are 5 tables that I’ll make to contain the data, listed below.

1. tblAuthors contains the nickname of the author, and the source (website). We’ll create this table and populate it with two authors.

CREATE TABLE [dbo].[tblAuthors](
[id] [int] IDENTITY(1,1) NOT NULL,
[nickname] [varchar](250) NULL,
[source] [varchar](500) NULL
) ON [PRIMARY]

id nickname source
1 Cramer TheStreet
2 Bradford Moneyweek

2. tblArticles contains the article URL, and the date of the article. Let’s populate it with 4 articles.

CREATE TABLE [dbo].[tblArticles](
[id] [int] IDENTITY(1,1) NOT NULL,
[articleURL] [varchar](250) NULL,
[articleDate] [datetime] NULL
) ON [PRIMARY]

id articleURL articleDate
1 test 2017-01-01 00:00:00.000
2 test1 2017-01-04 00:00:00.000
3 test2 2017-01-11 00:00:00.000
4 test4 2017-01-12 00:00:00.000

3. tblTickers contains the tickers of all the stocks mentioned in the entire scope of the project. Let’s consider 3 different stocks for this example.

CREATE TABLE [dbo].[tblTickers](
[id] [int] IDENTITY(1,1) NOT NULL,
[tickername] [varchar](250) NULL
) ON [PRIMARY]

id tickername
1 AAPL
2 GOOG
3 IBM

4. tblCall has a ticker ID, article ID, and a call- buy, sell, etc. There will be 4 rows, one for each article.

CREATE TABLE [dbo].[tblCall](
[id] [int] IDENTITY(1,1) NOT NULL,
[tickerId] [int] NULL,
[articleId] [int] NULL,
[call] [varchar](4) NULL
) ON [PRIMARY]

id tickerId articleId call
1 1 1 buy
2 2 2 buy
3 3 3 buy
4 1 4 sell

5. tblId is how we join all the previous tables together. In my code, every author is iterated over. For each author, every article is considered, and the stock discussed in it is noted.

CREATE TABLE [dbo].[tblId](
[id] [int] IDENTITY(1,1) NOT NULL,
[tickerId] [int] NULL,
[articleId] [int] NULL,
[authorId] [int] NULL
) ON [PRIMARY]

id tickerId articleId authorId
1 1 1 1
2 2 2 3
3 3 3 4
4 2 4 1

Now let’s consider an example. Let’s say we want to get all the calls that the author Cramer made, about AAPL. The required query is:

select * from tblID
LEFT JOIN tblAuthors ON tblAuthors.id = tblID.authorId
LEFT JOIN tblTickers ON tblTickers.Id = tblId.tickerId
LEFT JOIN tblArticles ON tblArticles.id = tblId.articleId
LEFT JOIN tblCall ON tblCall.articleId = tblArticles.id
where nickname = 'cramer' AND tickername = 'AAPL'

And it returns:

id tickerId articleId authorId id nickname source id tickername id articleURL articleDate id tickerId articleId call
1 1 1 1 1 Cramer TheStreet 1 AAPL 1 test 2017-01-01 00:00:00.000 1 1 1 buy
4 1 4 1 1 Cramer TheStreet 1 AAPL 4 test4 2017-01-12 00:00:00.000 4 1 4 sell
