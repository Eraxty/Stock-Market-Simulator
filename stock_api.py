from dotenv import load_dotenv
import os
import requests
from datetime import date, timedelta

load_dotenv()

API_KEY = os.getenv("FINNHUB_API_KEY")
BASE_URL = "https://finnhub.io/api/v1"

def request(endpoint, **params):
    params["token"] = API_KEY
    response = requests.get(f"{BASE_URL}/{endpoint}", params=params)
    return response.json()

def get_quote(symbol):
    return request("quote", symbol=symbol)

def get_price(symbol):
    return get_quote(symbol)["c"]

def get_change(symbol):
    return get_quote(symbol)["d"]

def get_percent_change(symbol):
    return get_quote(symbol)["dp"]

def get_company(symbol):
    return request("stock/profile2", symbol=symbol)

def get_company_name(symbol):
    return get_company(symbol)["name"]

def get_market_cap(symbol):
    return get_company(symbol)["marketCapitalization"]

def get_logo(symbol):
    return get_company(symbol)["logo"]

def get_news(symbol, days=7):
    today = date.today()
    week_ago = today - timedelta(days=days)

    return request(
        "company-news",
        symbol=symbol,
        **{
            "from": week_ago.isoformat(),
            "to": today.isoformat()
        }
    )

def search_company(query):
    return request("search", q=query)

def market_status(exchange="US"):
    return request("stock/market-status", exchange=exchange)

def get_peers(symbol):
    return request("stock/peers", symbol=symbol)

def get_basic_financials(symbol):
    return request(
        "stock/metric",
        symbol=symbol,
        metric="all"
    )