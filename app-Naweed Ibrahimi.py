import time
import threading
import pandas as pd
from datetime import datetime
from flask import Flask, render_template, jsonify, request
import requests

api_key = '2L85V79WS6K0WR64'  # Replace with your Alpha Vantage API key


def fetch_stock_data(symbol):
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=1min&apikey={api_key}'
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if 'Error Message' in data:
            raise ValueError(
                f"Error fetching data for symbol {symbol}: {data['Error Message']}")

        time_series = data.get('Time Series (1min)', {})
        processed_data = [
            {
                'time': key,
                'open': float(value['1. open']),
                'high': float(value['2. high']),
                'low': float(value['3. low']),
                'close': float(value['4. close']),
                'volume': int(value['5. volume'])
            }
            for key, value in time_series.items()
        ]
        return processed_data

    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        return None
    except ValueError as ve:
        print(ve)
        return None


app = Flask(__name__)
symbols = ['AAPL', 'GOOGL', 'MSFT', 'AMZN']
stock_data = {symbol: [] for symbol in symbols}


def update_data():
    global stock_data
    while True:
        for symbol in symbols:
            data = fetch_stock_data(symbol)
            if data:
                stock_data[symbol] = data
        time.sleep(60)


@app.route('/')
def index():
    return render_template('index.html', symbols=symbols)


@app.route('/update-data')
def update_data_route():
    symbol = request.args.get('symbol', 'AAPL')
    return jsonify(stock_data.get(symbol, []))


if __name__ == '__main__':
    thread = threading.Thread(target=update_data)
    thread.daemon = True
    thread.start()
    app.run(debug=True)
