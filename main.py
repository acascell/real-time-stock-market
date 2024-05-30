import threading
import requests
import time
from queue import Queue
import numpy as np
from typing import List


class StockMarketDataProcessor:
    """A class to fetch and process stock market data using Alpha Vantage API."""

    def __init__(self, api_key: str, stocks: List[str], interval: str = "1min"):
        """Initialize the data processor with API key, stock list, and data fetch interval."""

        self.api_key: str = api_key
        self.stocks: List[str] = stocks
        self.interval: str = interval
        self.base_url: str = "https://www.alphavantage.co/query"
        self.data_queue: Queue = Queue()
        self.queue_lock: threading.Lock = (
            threading.Lock()
        )  # Lock for thread-safe queue access
        self.fetch_threads: List[threading.Thread] = []
        self.process_thread = None

    def fetch_stock_data(self, stock: str) -> None:
        """Fetch stock data continuously every minute and add to the queue.
        :param stock: The stock symbol to fetch data for
        """

        while True:
            params = {
                "function": "TIME_SERIES_INTRADAY",
                "symbol": stock,
                "interval": self.interval,
                "apikey": self.api_key,
            }
            response = requests.get(self.base_url, params=params)
            if response.status_code == 200:
                with self.queue_lock:  # Synchronize access to the queue
                    self.data_queue.put((stock, response.json()))
            time.sleep(60)  # Wait a minute before the next fetch

    def process_stock_data(self) -> None:
        """Process fetched stock data from the queue, calculate SMA and EMA."""

        def calculate_sma(data: List[float], window: int) -> np.ndarray:
            """Calculate simple moving average (SMA).

            :param data: The list of closing prices
            :param window:  the window size
            :return:  the SMA values
            """

            return np.convolve(data, np.ones(window), "valid") / window

        def calculate_ema(data: List[float], window: int) -> List[float]:
            """Calculate exponential moving average (EMA).

            :param data: The list of closing prices
            :param window: the window size
            :return: the EMA values
            """

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
                        print(f"SMA: {sma[-5:]}")  # Print the last 5 values of SMA
                        print(f"EMA: {ema[-5:]}")  # Print the last 5 values of EMA

                    except KeyError as e:
                        print(f"Error processing data for {stock}: {e}")

                    self.data_queue.task_done()
                else:
                    time.sleep(1)  # Sleep if the queue is empty

    def start(self) -> None:
        """Start threads for fetching and processing data."""

        for stock in self.stocks:
            thread = threading.Thread(target=self.fetch_stock_data, args=(stock,))
            thread.start()
            self.fetch_threads.append(thread)

        # Create and start a thread for processing data
        self.process_thread = threading.Thread(target=self.process_stock_data)
        self.process_thread.start()

    def join(self) -> None:
        """Wait for all threads to complete."""

        for thread in self.fetch_threads:
            thread.join()
        self.process_thread.join()


if __name__ == "__main__":

    API_KEY = "**API_KEY**"
    STOCKS = ["STOCK_1", "STOCK_2", "STOCK_3", "STOCK_4"]

    # Instantiate and start the data processor
    data_processor = StockMarketDataProcessor(API_KEY, STOCKS)
    data_processor.start()
    data_processor.join()
