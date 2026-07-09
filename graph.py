import yfinance as yf
import plotext as plt


def get_history(symbol, period="1mo"):
    stock = yf.Ticker(symbol)
    return stock.history(period=period)


def plot_history(symbol, period="1mo"):
    history = get_history(symbol, period)
    if history.empty:
        print("No historical data found.")
        return
    prices = history["Close"].tolist()
    plt.clear_figure()
    plt.title(f"{symbol} - Last Month")
    plt.xlabel("Trading Days")
    plt.ylabel("Price ($)")
    plt.plot(prices)
    plt.show()