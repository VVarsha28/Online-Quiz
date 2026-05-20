from flask import Flask, render_template, request
import sqlite3
import random

app = Flask(__name__)

# -------------------------------
# DATABASE CONNECTION
# -------------------------------
def get_db_connection():
    conn = sqlite3.connect('quiz.db')
    conn.row_factory = sqlite3.Row
    return conn


# -------------------------------
# CREATE TABLES
# -------------------------------
conn = get_db_connection()
cursor = conn.cursor()

# Questions Table
cursor.execute('''
CREATE TABLE IF NOT EXISTS questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question TEXT NOT NULL,
    option1 TEXT NOT NULL,
    option2 TEXT NOT NULL,
    option3 TEXT NOT NULL,
    option4 TEXT NOT NULL,
    answer TEXT NOT NULL
)
''')

# Results Table
cursor.execute('''
CREATE TABLE IF NOT EXISTS results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    score INTEGER NOT NULL
)
''')

conn.commit()

# -------------------------------
# INSERT SAMPLE QUESTIONS
# -------------------------------
cursor.execute("SELECT COUNT(*) FROM questions")
count = cursor.fetchone()[0]

if count == 0:
    sample_questions = [
        (
            "What is the capital of India?",
            "Delhi",
            "Mumbai",
            "Chennai",
            "Kolkata",
            "Delhi"
        ),
        (
            "Which language is used for Flask?",
            "Java",
            "Python",
            "C++",
            "PHP",
            "Python"
        ),
        (
            "Who developed Python?",
            "Dennis Ritchie",
            "James Gosling",
            "Guido van Rossum",
            "Bjarne Stroustrup",
            "Guido van Rossum"
        ),
        (
            "HTML stands for?",
            "Hyper Text Markup Language",
            "High Text Machine Language",
            "Hyper Tool Multi Language",
            "None",
            "Hyper Text Markup Language"
        ),
        (
            "Which database is lightweight?",
            "Oracle",
            "MySQL",
            "SQLite",
            "MongoDB",
            "SQLite"
        )
    ]

    cursor.executemany('''
    INSERT INTO questions
    (question, option1, option2, option3, option4, answer)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', sample_questions)

    conn.commit()

conn.close()

# -------------------------------
# LOGIN PAGE
# -------------------------------
@app.route('/', methods=['GET', 'POST'])
def login():
    global username, quiz_questions

    if request.method == 'POST':
        username = request.form['name']

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM questions")
        all_questions = cursor.fetchall()

        quiz_questions = random.sample(list(all_questions), min(5, len(all_questions)))

        conn.close()

        return render_template('quiz.html', questions=quiz_questions)

    return render_template('login.html')


# -------------------------------
# SUBMIT QUIZ
# -------------------------------
@app.route('/submit', methods=['POST'])
def submit():
    global username, quiz_questions

    score = 0
    user_answers = {}
    correct_answers = {}

    for i, q in enumerate(quiz_questions):
        question_id = f"q{i+1}"

        user_answer = request.form.get(question_id)

        correct_answer = q['answer']

        user_answers[question_id] = user_answer
        correct_answers[question_id] = correct_answer

        if user_answer == correct_answer:
            score += 1

    total_questions = len(quiz_questions)

    percentage = (score / total_questions) * 100

    status = "Pass ✅" if percentage >= 50 else "Fail ❌"

    # Save Result
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO results (name, score) VALUES (?, ?)",
        (username, score)
    )

    conn.commit()
    conn.close()

    return render_template(
        "result.html",
        username=username,
        score=score,
        percentage=percentage,
        status=status,
        answers=correct_answers,
        user_answers=user_answers
    )


# -------------------------------
# LEADERBOARD
# -------------------------------
@app.route('/leaderboard')
def leaderboard():

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM results ORDER BY score DESC")

    data = cursor.fetchall()

    conn.close()

    return render_template('leaderboard.html', data=data)


# -------------------------------
# RUN APP
# -------------------------------
if __name__ == '__main__':
    app.run(debug=True)
