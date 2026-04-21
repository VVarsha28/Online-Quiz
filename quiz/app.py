from flask import Flask, render_template, request
import mysql.connector

app = Flask(__name__)

# MySQL Connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Varsha@28",
    database="quiz_system"
)

cursor = db.cursor()

# -------------------------------
# LOGIN PAGE
# -------------------------------
@app.route('/', methods=['GET', 'POST'])
def login():
    global username, quiz_questions

    if request.method == 'POST':
        username = request.form['name']

        # 🔥 Fetch random questions
        cursor.execute("SELECT * FROM questions ORDER BY RAND() LIMIT 5")
        quiz_questions = cursor.fetchall()

        # 🔍 Debug (check in terminal)
        print("Fetched Questions:", quiz_questions)

        # ❗ Handle empty database
        if not quiz_questions:
            return "<h2>No questions found in database!</h2>"

        return render_template('quiz.html', questions=quiz_questions)

    return render_template('login.html')


# -------------------------------
# SUBMIT QUIZ (DYNAMIC VERSION)
# -------------------------------
@app.route('/submit', methods=['POST'])
def submit():
    global username, quiz_questions

    score = 0
    user_answers = {}
    correct_answers = {}

    # 🔥 Loop through dynamic questions
    for i, q in enumerate(quiz_questions):
        question_id = f"q{i+1}"
        user_answer = request.form.get(question_id)
        correct_answer = q[4]

        user_answers[question_id] = user_answer
        correct_answers[question_id] = correct_answer

        if user_answer == correct_answer:
            score += 1

    total_questions = len(quiz_questions)

    # Avoid division error
    if total_questions == 0:
        return "<h2>Error: No questions available</h2>"

    percentage = (score / total_questions) * 100

    status = "Pass ✅" if percentage >= 50 else "Fail ❌"

    # Save to DB
    cursor.execute(
        "INSERT INTO results (name, score) VALUES (%s, %s)",
        (username, score)
    )
    db.commit()

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
    cursor.execute("SELECT * FROM results ORDER BY score DESC")
    data = cursor.fetchall()
    return render_template('leaderboard.html', data=data)


# -------------------------------
# RUN APP
# -------------------------------
if __name__ == '__main__':
    app.run(debug=True)