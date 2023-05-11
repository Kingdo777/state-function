import requests
import yfinance as yf
from utils import *


def main(event):
    startTime = 1000 * time.time()
    portfolioType = event['body']['portfolioType']

    tickersForPortfolioTypes = {'S&P': ['GOOG', 'AMZN', 'MSFT']}
    tickers = tickersForPortfolioTypes[portfolioType]
    prices = {}

    # for ticker in tickers:
    #     # Get last closing price
    #
    #     ####### this get an 403
    #     # tickerObj = yf.Ticker(ticker)
    #     # data = tickerObj.history(period="1d", proxy="http://127.0.0.1:7890")
    #     # price = data['Close'].unique()[0]
    #
    #     ###### let us get it by hand
    #     data = requests.get(
    #         url="https://query1.finance.yahoo.com/v8/finance/chart/{}?range=1&interval=1d&includePrePost=False&events=div%2Csplits".
    #         format(ticker),
    #         proxies={"https": "http://222.20.68.145:7890"},
    #         headers={
    #             'User-Agent': 'Mozilla/5.0'
    #         }
    #     ).json()
    #     price = data['chart']['result'][0]['indicators']['quote'][0]['close'][0]
    #
    #     prices[ticker] = price

    prices = {'GOOG': 1732.38, 'AMZN': 3185.27, 'MSFT': 221.02}

    response = {
        'statusCode': 200,
        'body': {'marketData': prices}
    }
    endTime = 1000 * time.time()
    return timestamp(response, event, startTime, endTime)


if __name__ == "__main__":
    print(main({'body': {'portfolioType': 'S&P'}}))
