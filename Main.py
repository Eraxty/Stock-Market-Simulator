import sqlite3
import hashlib
import random
import time
# Connect
conn = sqlite3.connect("stock_sim.db")
cur = conn.cursor()

logged_in = False
def get_balance():

    cur.execute("SELECT balance FROM users WHERE username = ?",(user[1],))
    balance = cur.fetchone()
    return balance[0]

while not logged_in:
    print("--------------------------------")
    print("1. Login")
    print("2. Create Account")
    print("----------------u----------------")

    login_choice = input("> ")

    if login_choice == "1":
        while True:
            print("--------------------------------")
            username = input("Enter username: ")
            print("--------------------------------")
            cur.execute("SELECT * FROM users WHERE username = ?",(username,))
            user = cur.fetchone()

            if user is None:
                print("--------------------------------")
                print("User not found")
                print("--------------------------------")
                print("1. Try Again")
                print("2. Back")
                print("--------------------------------")
                choice = input("> ")

                if choice == "1":
                    continue
                else:
                    break

            while True:
                print("--------------------------------")
                password = input("Enter password: ")
                print("--------------------------------")
                pass_hash = hashlib.sha256(password.encode()).hexdigest()
                if pass_hash == user[3]:
                    print("--------------------------------")
                    print("Login Successful")
                    print("--------------------------------")
                    logged_in = True
                    break
                print("--------------------------------")
                print("Wrong Password")
                print("--------------------------------")
                print("1. Try Again")
                print("2. Back")
                print("--------------------------------")

                choice = input("> ")

                if choice == "1":
                    continue
                else:
                    break

            if logged_in:
                break

    elif login_choice == "2":

        username = input("Choose username: ")
        cur.execute("SELECT * FROM users WHERE username = ?",(username,))

        if cur.fetchone():
            print("--------------------------------")
            print("Username already exists")
            print("--------------------------------")
            continue

        password = input("Choose password: ")

        pass_hash = hashlib.sha256(password.encode()).hexdigest()
        balance = 100000
        cur.execute("""INSERT INTO users (username, balance, password) VALUES (?, ?, ?)""",(username, balance ,pass_hash))
        conn.commit()
        print("--------------------------------")
        print("Account Created!") 
        print("--------------------------------")


def show_market():

    cur.execute("SELECT * FROM stocks")
    stocks = cur.fetchall()

    print("--------------------------------")
    print("SYMBOL\tPRICE")
    print("--------------------------------")
 
    for i in stocks:
        print(f"{i[0]:<3} {i[1]:<8} ${i[2]:.2f}")
    print("--------------------------------")

def crash():
    return random.uniform(-20, -10)

def boom():
    return random.uniform(10, 20)

def bear():
    return random.uniform(-8, -3)

def bull():
    return random.uniform(3, 8)

def stable():
    return random.uniform(-1, 1)

def little_up():
    return random.uniform(1, 3)

def little_down():
    return random.uniform(-3, -1)

def update_market():
    cur.execute("SELECT * FROM stocks")
    stocks = cur.fetchall()
    event = random.choices([crash, boom, bear, bull, stable, little_up, little_down],
    weights=[2, 2, 10, 10, 50, 13, 13])[0]

    for stock in stocks:
        change = event()
        new_price = stock[2] * (1 + change / 100)

        if new_price < 1:
            new_price = 1

        cur.execute("UPDATE stocks SET price = ? WHERE id = ?",(round(new_price, 2), stock[0]))
    conn.commit()

last_update = time.time()

while True:
    current_time = time.time()

    if current_time - last_update >= 30:
        update_market()
        print("Market Updated!")
        last_update = current_time

    print("--------------------------------")
    print("Stock Market Simulator")
    print("Balance: $", round(get_balance()))
    print("--------------------------------")
    print("1.View Market")
    print("2.Buy Stocks")
    print("3.Sell Stocks")
    print("4.Transaction history")
    print("5.Account info")
    print("--------------------------------")

    menu_choice = int(input("> "))
    if menu_choice == 1:
        while True:
            show_market()
            print("1. Go Back")
            choice = int(input("> "))

            if choice == 1:
                break
    
    if menu_choice == 2:
        show_market()
        stock_id = int(input("Select Stock ID: "))
        cur.execute(
        "SELECT * FROM stocks WHERE id = ?",(stock_id,))
        stock = cur.fetchone()
        if stock is None:
            print("Invalid Stock ID")
            continue
        shares = int(input("Enter Shares: "))
        cost = stock[2] * shares
        balance = get_balance() - cost
        print("--------------------------------")
        print("Stock:", stock[1])
        print("Price: $", stock[2])
        print("Shares:", shares)
        print("Total Cost: $", round(cost, 2))
        print("Balance After $",balance)
        print("--------------------------------")
        print("1. Confirm")
        print("2. Cancel")
        print("--------------------------------")

        confirm = input("> ")

        if confirm != "1":
            continue

        if cost > get_balance():
            print("Not enough balance")
            continue

        cur.execute("UPDATE users SET balance = ? WHERE username = ?",(balance, user[1]))
        cur.execute("SELECT * FROM portfolio WHERE username = ? AND symbol = ?",(user[1], stock[1]))
        holding = cur.fetchone()
        cur.execute("INSERT INTO transactions(user_id, stock_id, type, quantity, price) VALUES (?, ?, ?, ?, ?)", (user[0], stock[0], "BUY", shares, stock[2]))
        

        if holding != None:
            new_shares = holding[2] + shares
            cur.execute("UPDATE portfolio SET shares = ? WHERE id = ?",(new_shares, holding[0]))
            
        else:
            cur.execute("INSERT INTO portfolio(symbol, shares, username)VALUES (?, ?, ?)",(stock[1], shares, user[1]))
        conn.commit()
    
    if menu_choice == 4:
        cur.execute("SELECT * FROM transactions WHERE user_id = ?",(user[0],))
        transactions = cur.fetchall()

        print("--------------------------------")
        print("TRANSACTION HISTORY")
        print("--------------------------------")

        for t in transactions:
            total = t[4] * t[5]
            print(t[3],"Stock ID:", t[2],"Shares:", t[4],"Price:$", round(t[5], 2), "Total:$", round(total, 2))
        print("--------------------------------")
        print("--------------------------------")
        print("1. Go Back")
        choice = input("> ") #pressing down button on elevator when u wanna go up 
    
    if menu_choice == 5:

        print("--------------------------------")
        print("ACCOUNT INFO")
        print("--------------------------------")

        print("Username:", user[1])
        print("Balance: $", round(get_balance(), 2))

        cur.execute("SELECT SUM(shares) FROM portfolio WHERE username = ?",(user[1],))

        total_shares = cur.fetchone()[0]

        if total_shares is None:
            total_shares = 0

        print("Total Shares:", total_shares)
        print("--------------------------------")
        print("1. Go Back")
        choice = input("> ")  # elevator again 