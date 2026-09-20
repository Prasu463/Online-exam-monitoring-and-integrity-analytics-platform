import sqlite3
import os

# Create database folder if it doesn't exist
os.makedirs("database", exist_ok=True)

connection = sqlite3.connect("database/examguard.db")
cursor = connection.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS candidates(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fullname TEXT,
    email TEXT,
    password TEXT,
    phone TEXT,
    college TEXT,
    rollnumber TEXT,
    department TEXT,
    photo TEXT
)
""")

connection.commit()
connection.close()

print("Database and candidates table created successfully!")