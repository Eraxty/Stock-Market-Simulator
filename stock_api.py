from dotenv import load_dotenv
import os
import requests

load_dotenv()

API_KEY = os.getenv("FINNHUB_API_KEY")

def get_quote(symbol):
    response = requests.get(
        "https://finnhub.io/api/v1/quote",
        params={
            "symbol": symbol,
            "token": API_KEY
        }
    )
    return response.json()

def get_price(symbol):
    return get_quote(symbol)["c"]