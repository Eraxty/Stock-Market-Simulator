import sqlite3
import random

# Connect 
conn = sqlite3.connect("stock_sim.db")

#Send commands to Sql
cur = conn.cursor()

username = input("Enter your username: ")
password = input("Enter your password: ")
cur.execute(
    "INSERT INTO users (username, balance) VALUES (?, ?)",
    (username, 100000)
)




#Save
conn.commit()
#Close
conn.close()