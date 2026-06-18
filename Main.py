import sqlite3
import hashlib
import random

# Connect
conn = sqlite3.connect("stock_sim.db")
cur = conn.cursor()

logged_in = False
while not logged_in:
    print("1. Login")
    print("2. Create Account")

    login_choice = input("> ")

    if login_choice == "1":
        while True:
            username = input("Enter username: ")
            cur.execute("SELECT * FROM users WHERE username = ?",(username,))
            user = cur.fetchone()

            if user is None:
                print("User not found")
                print("1. Try Again")
                print("2. Back")
                choice = input("> ")

                if choice == "1":
                    continue
                else:
                    break

            while True:
                password = input("Enter password: ")
                pass_hash = hashlib.sha256(password.encode()).hexdigest()
                if pass_hash == user[3]:
                    print("Login Successful")
                    logged_in = True
                    break

                print("Wrong Password")
                print("1. Try Again")
                print("2. Back")

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
            print("Username already exists")
            continue

        password = input("Choose password: ")

        pass_hash = hashlib.sha256(password.encode()).hexdigest()
        cur.execute("""INSERT INTO users (username, balance, password) VALUES (?, ?, ?)""",(username, 100000 ,pass_hash))
        conn.commit()
        print("Account Created!")


print("Welcome to Stock Market Simulator")
while True:
    print("1.View Market")
    print("2.Buy Stocks")
    print("3.Sell Stocks")
    print("4.Transaction history")
    print("5.Account info")

    menu_choice = int(input("> "))

    if menu_choice == 1:
        while True:
            print("DEBUG: entered market menu")

            cur.execute("SELECT * FROM stocks")
            stocks = cur.fetchall()

            for stock in stocks:
                print(stock[1] + " | $" + str(stock[2]))
            print("1.go back")
            choice = int(input("> "))
            if choice == 1: 
                break

print("less go")