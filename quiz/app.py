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
    subject TEXT,
    question TEXT,
    option1 TEXT,
    option2 TEXT,
    option3 TEXT,
    option4 TEXT,
    answer TEXT
)
''')

# Results Table
cursor.execute('''
CREATE TABLE IF NOT EXISTS results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    subject TEXT,
    score INTEGER
)
''')

conn.commit()

# -------------------------------
# INSERT SAMPLE QUESTIONS
# -------------------------------
cursor.execute("SELECT COUNT(*) FROM questions")
count = cursor.fetchone()[0]

if count == 0:

    questions_data = [

        # Python
        (
            "Python",
            "Which keyword is used to define a function?",
            "func",
            "define",
            "def",
            "function",
            "def"
        ),

        (
            "Python",
            "Which symbol is used for comments in Python?",
            "//",
            "#",
            "/*",
            "%",
            "#"
        ),

        (
            "Python",
            "Python is developed by?",
            "James Gosling",
            "Dennis Ritchie",
            "Guido van Rossum",
            "Bjarne Stroustrup",
            "Guido van Rossum"
        ),

        # DBMS
        (
            "DBMS",
            "What does DBMS stand for?",
            "Data Base Management System",
            "Data Backup Management System",
            "Database Memory System",
            "None",
            "Data Base Management System"
        ),

        (
            "DBMS",
            "Which language is used in MySQL?",
            "SQL",
            "Python",
            "Java",
            "HTML",
            "SQL"
        ),

        (
            "DBMS",
            "Primary key uniquely identifies?",
            "Column",
            "Row",
            "Table",
            "Database",
            "Row"
        )
    ]

    cursor.executemany('''
    INSERT INTO questions
    (subject, question, option1, option2, option3, option4, answer)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', questions_data)

    conn.commit()

conn.close()

# -------------------------------
# LOGIN PAGE
# -------------------------------
@app.route('/', methods=['GET', 'POST'])
def login():

    global username
    global selected_subject
    global quiz_questions

    if request.method == 'POST':

        username = request.form['name']
        selected_subject = request.form['subject']

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM questions WHERE subject=?",
            (selected_subject,)
        )

        all_questions = cursor.fetchall()

        if len(all_questions) == 0:
            return "<h2>No questions found for this subject!</h2>"

        quiz_questions = random.sample(
            list(all_questions),
            min(5, len(all_questions))
        )

        conn.close()

        return render_template(
            'quiz.html',
            questions=quiz_questions,
            subject=selected_subject
        )

    return render_template('login.html')


# -------------------------------
# SUBMIT QUIZ
# -------------------------------
@app.route('/submit', methods=['POST'])
def submit():

    global username
    global selected_subject
    global quiz_questions

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
        "INSERT INTO results (name, subject, score) VALUES (?, ?, ?)",
        (username, selected_subject, score)
    )

    conn.commit()
    conn.close()

    return render_template(
        "result.html",
        username=username,
        subject=selected_subject,
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

    cursor.execute(
        "SELECT * FROM results ORDER BY score DESC"
    )

    data = cursor.fetchall()

    conn.close()

    return render_template(
        'leaderboard.html',
        data=data
    )


# -------------------------------
# RUN APP
# -------------------------------
if __name__ == '__main__':
    app.run(debug=True)
