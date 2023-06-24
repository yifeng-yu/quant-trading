import pandas as pd
import finnhub
import time
from datetime import datetime, timedelta

# Setup client
finnhub_client = finnhub.Client(api_key='cib4151r01qvsha5qnc0cib4151r01qvsha5qncg')

# Define a function to get the data
def get_data(symbol):
    # Get company profile 2 for market cap
    profile = finnhub_client.company_profile2(symbol=symbol)
    market_cap = profile['marketCapitalization']

    # Get quote for previous close and open price
    quote = finnhub_client.quote(symbol)
    prev_close = quote['pc']
    open_price = quote['o']

    # Get basic financials for PE ratio and EPS
    financials = finnhub_client.company_basic_financials(symbol, 'all')
    pe_ratio = financials['metric']['peNormalizedAnnual']
    eps = financials['metric']['epsNormalizedAnnual']

    # Get stock candles for average volume calculation over past 10 days
    today = datetime.today()
    ten_days_ago = today - timedelta(days=10)
    res_10_days = finnhub_client.stock_candles(symbol, 'D', int(ten_days_ago.timestamp()), int(today.timestamp()))
    df_10_days = pd.DataFrame(res_10_days)
    average_volume = df_10_days['v'].mean()
    prev_volume = df_10_days['v'].iloc[-2] if len(df_10_days) > 1 else None

    # Get today's volume
    res_today = finnhub_client.stock_candles(symbol, '1', int((today - timedelta(days=1)).timestamp()), int(today.timestamp()))
    df_today = pd.DataFrame(res_today)
    today_volume = df_today['v'].sum() if not df_today.empty else 0

    # Get stock candles for calculating daily returns
    res = finnhub_client.stock_candles(symbol, 'D', int(ten_days_ago.timestamp()), int(today.timestamp()))
    df_candles = pd.DataFrame(res)
    df_candles['t'] = pd.to_datetime(df_candles['t'], unit='s')
    df_candles.set_index('t', inplace=True)
    df_candles['returns'] = df_candles['c'].pct_change()

    # Calculate volatility and Sharpe Ratio
    risk_free_rate = 0.02  # Assuming risk-free rate of 2%
    volatility = df_candles['returns'].std() * (252 ** 0.5)  # Assuming 252 trading days in a year
    sharpe_ratio = (df_candles['returns'].mean() - risk_free_rate) / df_candles['returns'].std() * (252 ** 0.5) if df_candles['returns'].std() != 0 else 0

    return [symbol, prev_close, open_price, prev_volume, today_volume, average_volume, market_cap, pe_ratio, eps, volatility, sharpe_ratio]


if __name__ == '__main__':
	# List of symbols to get data for
	symbols = ['AAPL', 'MSFT', 'GOOG']

	# Fetch the data
	data = [get_data(symbol) for symbol in symbols]

	# Convert to DataFrame and write to CSV
	df = pd.DataFrame(data, columns=['Symbol', 'Previous Close', 'Open Price', 'Prev Day Volume', 'Today Volume', 'Avg Volume (10 days)', 'Market Cap', 'PE Ratio (ttm)', 'EPS (ttm)', 'Volatility', 'Sharpe Ratio'])
	df = df.round(2)
	df.to_csv('stock_data.csv', index=False)
