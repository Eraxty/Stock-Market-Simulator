import sqlite3
import hashlib
import os
from dotenv import load_dotenv
import requests
from pyfiglet import Figlet
from stock_api import *

f = Figlet(font='slant')
print(f.renderText('Stock Market Simulator'))

LINE = "-" * 32


def get_api_key():
    load_dotenv()
    api_key = os.getenv("FINNHUB_API_KEY")

    while True:
        if api_key:
            try: #check if api key is valid
                response = requests.get(
                    "https://finnhub.io/api/v1/quote",
                    params={
                        "symbol": "AAPL",
                        "token": api_key
                    },
                    timeout=5
                )
                data = response.json()
                if "error" not in data:
                    return api_key
                print("API key is invalid.")
            except requests.RequestException:
                print("Couldn't connect to Finnhub.")
                exit()
        api_key = input("Enter your Finnhub API Key: ").strip()
        try:
            response = requests.get(
                "https://finnhub.io/api/v1/quote",
                params={
                    "symbol": "AAPL",
                    "token": api_key
                },
                timeout=5
            )
            data = response.json()
            if "error" in data:
                print("Invalid API key.\n")
                api_key = None
                continue
            with open(".env", "w") as f:
                f.write(f"FINNHUB_API_KEY={api_key}\n")
            load_dotenv(override=True)
            return api_key
        except requests.RequestException:
            print("couldnt connect to finnhub")
            exit()
API_KEY = get_api_key()

# Connect
conn = sqlite3.connect("stock_sim.db")
cur = conn.cursor()
cur.execute("PRAGMA foreign_keys = ON")

def update_prices():
    cur.execute("SELECT id, symbol FROM stocks")
    stocks = cur.fetchall()
    for stock_id, symbol in stocks:
        try:
            price = get_price(symbol)
            cur.execute("UPDATE stocks SET price = ? WHERE id = ?", (price, stock_id))
        except Exception:
            continue
    conn.commit()

update_prices()

logged_in = False
while not logged_in:
    print(LINE)
    print("1. Login")
    print("2. Create Account")
    print(LINE)

    login_choice = input("> ")

    if login_choice == "1":
        while True:
            print(LINE)
            username = input("Enter username: ")
            print(LINE)
            cur.execute("SELECT * FROM users WHERE username = ?",(username,)) #search for username
            user = cur.fetchone()

            if user is None: #username not found
                print(LINE)
                print("User not found")
                print(LINE)
                print("1. Try Again")
                print("2. Back")
                print(LINE)
                choice = input("> ")

                if choice == "1":
                    continue
                else:
                    break

            while True: #username found enter password
                print(LINE)
                password = input("Enter password: ")
                print(LINE)
                pass_hash = hashlib.sha256(password.encode()).hexdigest() #hash the pass bcs storing plain text is bad
                if pass_hash == user[3]: #compare the hashes 
                    print(LINE)
                    print("Login Successful")
                    print(LINE)
                    logged_in = True
                    break
                print(LINE)
                print("Wrong Password")
                print(LINE)
                print("1. Try Again")
                print("2. Back")
                print(LINE)

                choice = input("> ")

                if choice == "1":
                    continue
                else:
                    break

            if logged_in:
                break

    elif login_choice == "2": #user creation

        username = input("Choose username: ")
        cur.execute("SELECT * FROM users WHERE username = ?",(username,))

        if cur.fetchone() != None: #check if user exist
            print(LINE)
            print("Username already exists")
            print(LINE)
            continue

        password = input("Choose password: ")

        pass_hash = hashlib.sha256(password.encode()).hexdigest() #hash the pass
        balance = 100000 #initial balance given
        cur.execute("""INSERT INTO users (username, balance, password) VALUES (?, ?, ?)""",(username, balance ,pass_hash))
        conn.commit()
        print(LINE)
        print("Account Created!") 
        print(LINE)

def get_balance(): #very useful function
    cur.execute("SELECT balance FROM users WHERE username = ?",(user[1],))
    balance = cur.fetchone()
    return balance[0]

def get_net_worth():
    cash = get_balance()
    cur.execute(
        "SELECT symbol, shares FROM portfolio WHERE username = ?",
        (user[1],)
    )
    holdings = cur.fetchall()
    holdings_value = 0
    for symbol, shares in holdings:
        holdings_value += get_price(symbol) * shares
    return cash + holdings_value

def show_market():
    cur.execute("SELECT id, symbol FROM stocks")
    stocks = cur.fetchall()

    print(LINE)
    print("ID  SYMBOL   PRICE")
    print(LINE)

    for stock_id, symbol in stocks:
        try:
            price = get_price(symbol)
            print(f"{stock_id:<3} {symbol:<8} ${price:.2f}")
        except Exception:
            print(f"{stock_id:<3} {symbol:<8} N/A")
    print(LINE)

def show_stock_details(symbol):
    info = get_market_info(symbol)
    print(LINE)
    print("STOCK DETAILS")
    print(LINE)
    print("Company:", info["name"])
    print("Symbol:", info["symbol"])
    print(f"Current Price: ${info['price']:.2f}")
    print(f"Daily Change: ${info['change']:.2f}")
    print(f"Percent Change: {info['percent']:.2f}%")
    print(f"Open: ${info['open']:.2f}")
    print(f"High: ${info['high']:.2f}")
    print(f"Low: ${info['low']:.2f}")
    print("Exchange:", info["exchange"])
    print("Industry:", info["industry"])
    print(f"Market Capitalization: ${info['market_cap']:.2f}M")
    print(LINE)
    print("1. Buy")
    print("2. Back")
    print(LINE)

def buy_stock(stock):
    symbol = stock[1]
    try:
        shares = int(input("Enter Shares: "))
    except ValueError:
        print("Invalid input")
        return
    if shares <= 0:
        print("Invalid share amount")
        return
    price = get_price(symbol)
    cost = price * shares
    balance = get_balance()
    if cost > balance:
        print("Not enough balance")
        return
    new_balance = balance - cost
    print(LINE)
    print("Stock:", symbol)
    print(f"Price: ${price:.2f}")
    print("Shares:", shares)
    print(f"Total Cost: ${cost:.2f}")
    print(f"Balance After: ${new_balance:.2f}")
    print(LINE)
    print("1. Confirm")
    print("2. Cancel")
    print(LINE)

    confirm = input("> ")

    if confirm != "1":
        return

    cur.execute("UPDATE users SET balance = ? WHERE username = ?",(new_balance, user[1]))

    cur.execute("SELECT * FROM portfolio WHERE username = ? AND symbol = ?",(user[1], symbol))
    holding = cur.fetchone()

    cur.execute("INSERT INTO transactions(user_id, stock_id, type, quantity, price) VALUES (?, ?, ?, ?, ?)", (user[0], stock[0], "BUY", shares, price))

    if holding != None:
        new_shares = holding[2] + shares
        cur.execute("UPDATE portfolio SET shares = ? WHERE id = ?",(new_shares, holding[0]))
    else:
        cur.execute("INSERT INTO portfolio(symbol, shares, username)VALUES (?, ?, ?)",(symbol, shares, user[1]))
    conn.commit()
    print("Purchase Complete")

try:
    selected_stock_id = None
    selected_stock_symbol = None
    while True:
        print(LINE) #Main Menu 
        print("Stock Market Simulator")
        print(f"Balance: ${get_balance():.2f}")
        print(LINE)
        print("1.View Market")
        print("2.Buy Stocks")
        print("3.Sell Stocks")
        print("4.Transaction history")
        print("5.Account info")
        print(LINE)

        try:
            menu_choice = int(input("> "))
        except ValueError:
            print("Invalid option")
            continue

        if menu_choice not in (1, 2, 3, 4, 5):
            print("Invalid option")
            continue

        if menu_choice == 1: #shows market
            while True:
                show_market()
                print("Enter Stock ID (0 = Back)")
                try:
                    choice = int(input("> "))
                except ValueError:
                    print("Invalid input")
                    continue

                if choice == 0:
                    break
                cur.execute("SELECT id, symbol FROM stocks WHERE id = ?", (choice,))
                stock = cur.fetchone()
                if stock is None:
                    print("Invalid Stock ID")
                    continue
                while True:
                    show_stock_details(stock[1])
                    try:
                        detail_choice = int(input("> "))
                    except ValueError:
                        print("Invalid option")
                        continue
                    if detail_choice == 1:
                        selected_stock_id = stock[0]
                        selected_stock_symbol = stock[1]
                        buy_stock(stock)
                        selected_stock_id = None
                        selected_stock_symbol = None
                        break
                    if detail_choice == 2:
                        break
                    print("Invalid option")
                if selected_stock_id is not None:
                    break
        

        if menu_choice == 2:
            if selected_stock_id is not None:
                stock_id = selected_stock_id
                symbol = selected_stock_symbol
            else:
                show_market()
                try:
                    stock_id = int(input("Select Stock ID: "))
                except ValueError:
                    print("Invalid input")
                    continue
                cur.execute("SELECT * FROM stocks WHERE id = ?", (stock_id,))
                stock = cur.fetchone()

                if stock is None:
                    print("Invalid Stock ID")
                    continue

                symbol = stock[1]
            cur.execute("SELECT * FROM stocks WHERE id = ?", (stock_id,))
            stock = cur.fetchone()
            if stock is None:
                print("Invalid Stock ID")
                continue
            buy_stock(stock)
            selected_stock_id = None
            selected_stock_symbol = None


        if menu_choice == 3: #sell
            cur.execute("SELECT * FROM portfolio WHERE username = ?",(user[1],))

            holdings = cur.fetchall()

            if len(holdings) == 0:
                print("No holdings found")
                continue

            print(LINE)
            print("YOUR HOLDINGS")
            print(LINE)

            n = 1
            for h in holdings:
                print(f"{n:<3} {h[1]:<8} {h[2]}")
                n = n + 1

            print(LINE)

            try:
                choice = int(input("Sell> "))
            except ValueError:
                print("Invalid option")
                continue
            if choice < 1 or choice > len(holdings):
                print("Invalid choice")
                continue
            hold = holdings[choice - 1]

            try:
                shares = int(input("Number of shares: "))
            except ValueError:
                print("Invalid input")
                continue
            if shares <= 0:
                print("Invalid share amount")
                continue

            if shares > hold[2]: # prevent selling more than owned
                print("Not enough shares")
                continue
            
            symbol = hold[1]
            price = get_price(symbol)
            sale_value = price * shares
            
            #menu for sale
            print(LINE) 
            print("Stock:", symbol)
            print(f"Price: ${price:.2f}")
            print("Shares:", shares)
            print(f"You Receive: ${sale_value:.2f}")
            print(f"Balance After: ${get_balance() + sale_value:.2f}")
            print(LINE)
            print("1. Confirm")
            print("2. Cancel")
            print(LINE)

            confirm = input("> ")

            if confirm != "1":
                continue

            new_balance = get_balance() + sale_value #new balance

            cur.execute("UPDATE users SET balance = ? WHERE username = ?",(new_balance, user[1]))

            remaining = hold[2] - shares # calculate remaining shares after sale

            if remaining == 0:
                cur.execute("DELETE FROM portfolio WHERE id = ?",(hold[0],))

            else: #update remaining shares
                cur.execute("UPDATE portfolio SET shares = ? WHERE id = ?",(remaining, hold[0]))

            cur.execute("SELECT id FROM stocks WHERE symbol = ?", (symbol,))
            stock_id = cur.fetchone()[0]
            cur.execute("INSERT INTO transactions(user_id, stock_id, type, quantity, price) VALUES (?, ?, ?, ?, ?)",(user[0], stock_id, "SELL", shares, price))
            conn.commit()

            print("Successful") #print successfull


        if menu_choice == 4:
            cur.execute("""
                SELECT t.type, s.symbol, t.quantity, t.price, t.timestamp
                FROM transactions t
                JOIN stocks s ON t.stock_id = s.id
                WHERE t.user_id = ?
            """,(user[0],))
            transactions = cur.fetchall()

            print(LINE)
            print("TRANSACTION HISTORY")
            print(LINE)

            for t in transactions:
                total = t[2] * t[3]
                print(t[0], " ", t[1], sep="")
                print("Shares:", t[2])
                print(f"Price: ${t[3]:.2f}")
                print(f"Total: ${total:.2f}")
                print("Time:", t[4])
                print(LINE)
            print(LINE)
            print("1. Go Back")
            try:
                choice = int(input("> "))
            except ValueError:
                print("Invalid input")
                continue
        

        if menu_choice == 5:
            print(LINE)
            print("ACCOUNT INFO")
            print(LINE)

            print("Username:", user[1])
            print(f"Balance: ${get_balance():.2f}")
            print(f"Net Worth: ${get_net_worth():.2f}")

            cur.execute("SELECT SUM(shares) FROM portfolio WHERE username = ?",(user[1],))

            total_shares = cur.fetchone()[0]

            if total_shares is None:
                total_shares = 0

            print("Total Shares:", total_shares)
            print(LINE)
            print("1. Go Back")
            try:
                choice = int(input("> "))
            except ValueError:
                print("Invalid input")
                continue
except KeyboardInterrupt:
    print("\nbyeee.")
finally:
    conn.close()
