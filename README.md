# real-time-stock-market
Use multithreading to spawn threads and get updates about stock exchanges

## 🚀 Overview
The application implements multiple threads to actually
pull data using https://www.alphavantage.co/ API and display stock prices it in real time. 
Implement 'requests' library to interact with the remote interface
and place the data in a threading queue in the form of json response.
Multiple threads are being created iteratively to get the data based on a list
of stock using the API key. Use a context manager implementing 'locking'
feature to ensure thread-safe access to the queue when the processing is
occurring. Implements 'numpy' library to actually perform the
 Simple Moving Averages (SMA) and Exponential Moving Averages (EMA) calculation
and display the results in real time.

## 🔎 TODO
- Extend the processing function to calculate financial indicators.
- Implement visualization using Matplotlib or Plotly and update the charts in real-time.
- Add a GUI using Tkinter or PyQt to display the visualizations and alerts.
- Optimize and test the application to ensure smooth real-time performance.