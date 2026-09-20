import os
import sqlite3

# Connect to the database
db_path = os.path.join(os.path.dirname(__file__), "examguard.db")
connection = sqlite3.connect(db_path)
cursor = connection.cursor()

questions = [
    (
        "Which language is widely used for Artificial Intelligence?",
        "Python",
        "HTML",
        "CSS",
        "MS Word",
        "Python"
    ),
    (
        "Which keyword is used to define a function in Python?",
        "function",
        "define",
        "def",
        "fun",
        "def"
    ),
    (
        "Which database are we using in this project?",
        "MySQL",
        "SQLite",
        "Oracle",
        "MongoDB",
        "SQLite"
    ),
    (
        "Which company developed Python?",
        "Microsoft",
        "Google",
        "Python Software Foundation",
        "Apple",
        "Python Software Foundation"
    ),
    (
        "Which symbol is used for comments in Python?",
        "//",
        "#",
        "<!-- -->",
        "/* */",
        "#"
    )
]

cursor.executemany("""
INSERT INTO questions
(question, option1, option2, option3, option4, correct_answer)
VALUES (?, ?, ?, ?, ?, ?)
""", questions)

connection.commit()
connection.close()

print("Questions inserted successfully!")