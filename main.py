import threading
import requests
import time
from queue import Queue
import numpy as np


class StockMarketDataProcessor:
    def __init__(self, api_key, stocks, interval="1min"):
        self.api_key = api_key
        self.stocks = stocks
        self.interval = interval
        self.base_url = "https://www.alphavantage.co/query"
        self.data_queue = Queue()
        self.queue_lock = threading.Lock()  # Lock for accessing the queue
        self.fetch_threads = []
        self.process_thread = None

    def fetch_stock_data(self, stock):
        while True:
            params = {
                "function": "TIME_SERIES_INTRADAY",
                "symbol": stock,
                "interval": self.interval,
                "apikey": self.api_key,
            }
            response = requests.get(self.base_url, params=params)
            if response.status_code == 200:
                with self.queue_lock:  # Ensure thread-safe access to the queue
                    self.data_queue.put((stock, response.json()))
            time.sleep(60)  # Fetch data every minute

    def process_stock_data(self):
        def calculate_sma(data, window):
            return np.convolve(data, np.ones(window), "valid") / window

        def calculate_ema(data, window):
            ema = [sum(data[:window]) / window]
            multiplier = 2 / (window + 1)
            for price in data[window:]:
                ema.append((price - ema[-1]) * multiplier + ema[-1])
            return ema

        while True:
            with self.queue_lock:  # Ensure thread-safe access to the queue
                if not self.data_queue.empty():
                    stock, raw_data = self.data_queue.get()
                    try:
                        time_series = raw_data["Time Series (1min)"]
                        closing_prices = [
                            float(data["4. close"])
                            for timestamp, data in time_series.items()
                        ]
                        closing_prices.reverse()  # Ensure correct order

                        # Calculate SMA and EMA
                        sma = calculate_sma(closing_prices, window=20)
                        ema = calculate_ema(closing_prices, window=20)

                        print(f"Processing data for {stock}")
                        print(f"SMA: {sma[-5:]}")  # Print last 5 values of SMA
                        print(f"EMA: {ema[-5:]}")  # Print last 5 values of EMA

                    except KeyError as e:
                        print(f"Error processing data for {stock}: {e}")

                    self.data_queue.task_done()
                else:
                    time.sleep(1)  # Sleep for a bit if the queue is empty

    def start(self):
        # Create and start threads for fetching data
        for stock in self.stocks:
            thread = threading.Thread(target=self.fetch_stock_data, args=(stock,))
            thread.start()
            self.fetch_threads.append(thread)

        # Create and start a thread for processing data
        self.process_thread = threading.Thread(target=self.process_stock_data)
        self.process_thread.start()

    def join(self):
        # Join threads
        for thread in self.fetch_threads:
            thread.join()
        self.process_thread.join()


if __name__ == "__main__":

    # Configuration
    API_KEY = "**API_KEY**"
    STOCKS = ["STOCK_1", "STOCK_2", "STOCK_3", "STOCK_4"]

    # Instantiate and start the data processor
    data_processor = StockMarketDataProcessor(API_KEY, STOCKS)
    data_processor.start()
    data_processor.join()
