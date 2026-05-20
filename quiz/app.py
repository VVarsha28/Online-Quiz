from flask import Flask, render_template, request, session
import mysql.connector

app = Flask(__name__)
app.secret_key = "quiz_secret_key"

# -----------------------------------
# MYSQL CONNECTION
# -----------------------------------
try:
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Varsha@28",
        database="quiz_system"
    )

    cursor = db.cursor()
    db_connected = True

except:
    print("MySQL connection failed")
    db_connected = False


# -----------------------------------
# LOGIN PAGE
# -----------------------------------
@app.route('/', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        username = request.form['name']

        session['username'] = username

        return render_template('subjects.html')

    return render_template('login.html')


# -----------------------------------
# QUIZ PAGE
# -----------------------------------
@app.route('/quiz/<subject>')
def quiz(subject):

    if not db_connected:
        return """
        <h2>Database not connected</h2>
        <p>Online deployment cannot access localhost MySQL.</p>
        """

    cursor.execute(
        "SELECT * FROM questions WHERE subject=%s ORDER BY RAND() LIMIT 5",
        (subject,)
    )

    quiz_questions = cursor.fetchall()

    return render_template(
        'quiz.html',
        questions=quiz_questions,
        subject=subject
    )


# -----------------------------------
# SUBMIT QUIZ
# -----------------------------------
@app.route('/submit', methods=['POST'])
def submit():

    if not db_connected:
        return """
        <h2>Database not connected</h2>
        """

    username = session.get('username')

    subject = request.form.get('subject')

    cursor.execute(
        "SELECT * FROM questions WHERE subject=%s LIMIT 5",
        (subject,)
    )

    quiz_questions = cursor.fetchall()

    score = 0

    for i, q in enumerate(quiz_questions):

        user_answer = request.form.get(f"q{i+1}")

        correct_answer = q[4]

        if user_answer == correct_answer:
            score += 1

    total_questions = len(quiz_questions)

    percentage = (score / total_questions) * 100

    status = "Pass ✅" if percentage >= 50 else "Fail ❌"

    # SAVE RESULT
    cursor.execute(
        "INSERT INTO results(name, score, subject) VALUES(%s, %s, %s)",
        (username, score, subject)
    )

    db.commit()

    return render_template(
        'result.html',
        username=username,
        score=score,
        percentage=percentage,
        status=status,
        subject=subject
    )


# -----------------------------------
# LEADERBOARD
# -----------------------------------
@app.route('/leaderboard/<subject>')
def leaderboard(subject):

    if not db_connected:
        return "<h2>Database not connected</h2>"

    cursor.execute(
        "SELECT * FROM results WHERE subject=%s ORDER BY score DESC",
        (subject,)
    )

    data = cursor.fetchall()

    return render_template(
        'leaderboard.html',
        data=data,
        subject=subject
    )


# -----------------------------------
# LOGOUT
# -----------------------------------
@app.route('/logout')
def logout():

    session.clear()

    return render_template('login.html')


# -----------------------------------
# RUN APP
# -----------------------------------
if __name__ == '__main__':
    app.run(debug=True)
