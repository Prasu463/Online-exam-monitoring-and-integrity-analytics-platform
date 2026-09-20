import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), "examguard.db")
connection = sqlite3.connect(db_path)
cursor = connection.cursor()

cursor.execute("DELETE FROM questions")
connection.commit()

print("All questions deleted.")

connection.close()