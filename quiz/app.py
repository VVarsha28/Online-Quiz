from flask import Flask, render_template, request, session

app = Flask(__name__)
app.secret_key = "quiz_secret_key"


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

    # Dummy questions for deployment demo
    quiz_questions = [
        (1, "What is Python?", "Programming Language", "Snake", "1"),
        (2, "What is DBMS?", "Database Management System", "Operating System", "1"),
        (3, "HTML stands for?", "Hyper Text Markup Language", "High Text Machine Language", "1"),
        (4, "Which is immutable?", "Tuple", "List", "1"),
        (5, "Which keyword defines function?", "def", "func", "1")
    ]

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

    username = session.get('username')

    score = 0

    # Dummy answers
    correct_answers = ['1', '1', '1', '1', '1']

    for i in range(5):

        user_answer = request.form.get(f"q{i+1}")

        if user_answer == correct_answers[i]:
            score += 1

    percentage = (score / 5) * 100

    status = "Pass ✅" if percentage >= 50 else "Fail ❌"

    return render_template(
        'result.html',
        username=username,
        score=score,
        percentage=percentage,
        status=status
    )


# -----------------------------------
# LEADERBOARD
# -----------------------------------
@app.route('/leaderboard/<subject>')
def leaderboard(subject):

    # Dummy leaderboard data
    data = [
        (1, "Varsha", 5),
        (2, "Student1", 4),
        (3, "Student2", 3)
    ]

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
