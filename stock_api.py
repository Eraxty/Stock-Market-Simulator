from dotenv import load_dotenv
import os
import requests

load_dotenv()

API_KEY = os.getenv("FINNHUB_API_KEY")
BASE_URL = "https://finnhub.io/api/v1"

def api_get(endpoint, **params):
    params["token"] = API_KEY
    response = requests.get(
        f"{BASE_URL}/{endpoint}",
        params=params,
        timeout=5
    )
    response.raise_for_status()
    return response.json()

#quote
def get_quote(symbol):
    return api_get("quote", symbol=symbol)

def get_price(symbol):
    return get_quote(symbol)["c"]

#company
def get_company(symbol):
    return api_get("stock/profile2", symbol=symbol)

#search
def search_company(query):
    return api_get("search", q=query)

#market
def market_status(exchange="US"):
    return api_get(
        "stock/market-status",
        exchange=exchange
    )

#combined
def get_market_info(symbol):
    quote = get_quote(symbol)
    company = get_company(symbol)

    return {
        "symbol": symbol,
        "name": company["name"],
        "price": quote["c"],
        "change": quote["d"],
        "percent": quote["dp"],
        "high": quote["h"],
        "low": quote["l"],
        "open": quote["o"],
        "exchange": company["exchange"],
        "industry": company["finnhubIndustry"],
        "market_cap": company["marketCapitalization"]
    }