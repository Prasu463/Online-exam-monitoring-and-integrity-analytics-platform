import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), "examguard.db")
connection = sqlite3.connect(db_path)
cursor = connection.cursor()

cursor.execute("SELECT id, question FROM questions")

rows = cursor.fetchall()

for row in rows:
    print(row)

connection.close()