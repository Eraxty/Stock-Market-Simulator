import sqlite3
import hashlib
import random
import time
# Connect
conn = sqlite3.connect("stock_sim.db")
cur = conn.cursor()

logged_in = False
while not logged_in:
    print("--------------------------------")
    print("1. Login")
    print("2. Create Account")
    print("--------------------------------")

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
        cur.execute("""INSERT INTO users (username, balance, password) VALUES (?, ?, ?)""",(username, 100000 ,pass_hash))
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
        print(i[1], "\t$", i[2])

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
    print("Balance: $", user[2])
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