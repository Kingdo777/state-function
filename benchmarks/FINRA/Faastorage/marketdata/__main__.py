import pickle

import requests
import yfinance as yf
import time
import datafunction as df


def timestamp(response, event, execute_start_time, execute_end_time, transport_start_time, transport_end_time):
    stamp_begin = 1000 * time.time()
    prior_execute_time = event['executeTime'] if 'executeTime' in event else 0
    response['executeTime'] = prior_execute_time + execute_end_time - execute_start_time

    prior_interaction_time = event['interactionTime'] if 'interactionTime' in event else 0
    response['interactionTime'] = prior_interaction_time + transport_end_time - transport_start_time

    prior_cost = event['timeStampCost'] if 'timeStampCost' in event else 0
    response['timeStampCost'] = prior_cost - (stamp_begin - 1000 * time.time())
    return response


def main(event):
    startTime = 1000 * time.time()
    index = event['index']
    portfolioType = event['body']['portfolioType']

    tickersForPortfolioTypes = {'S&P': ['GOOG', 'AMZN', 'MSFT']}
    tickers = tickersForPortfolioTypes[portfolioType]
    prices = {}

    # for ticker in tickers:
    # Get last closing price

    ####### this get an 403
    # tickerObj = yf.Ticker(ticker)
    # data = tickerObj.history(period="1d", proxy="http://127.0.0.1:7890")
    # price = data['Close'].unique()[0]

    ####### let us get it by hand
    # data = requests.get(
    #     url="https://query1.finance.yahoo.com/v8/finance/chart/{}?range=1&interval=1d&includePrePost=False&events=div%2Csplits".
    #     format(ticker),
    #     proxies={"https": "http://222.20.68.145:7890"},
    #     headers={
    #         'User-Agent': 'Mozilla/5.0'
    #     }
    # ).json()
    # price = data['chart']['result'][0]['indicators']['quote'][0]['close'][0]
    #
    # prices[ticker] = price

    prices = {'GOOG': 1732.38, 'AMZN': 3185.27, 'MSFT': 221.02}

    bucket = df.get_bucket("kingdo-finra")
    body_data = pickle.dumps({'marketData': prices})
    response = {'statusCode': 200}
    endTime = 1000 * time.time()

    transport_start_time = endTime
    bucket_ = df.create_bucket("kingdo-finra-marketdata-{}".format(index), 1024 * 4)
    bucket.set("marketdata_body_{}".format(index), body_data)
    transport_end_time = 1000 * time.time()
    bucket_.destroy()

    return timestamp(response, event, startTime, endTime, transport_start_time, transport_end_time)


if __name__ == "__main__":
    print(main({'body': {'portfolioType': 'S&P'}}))
