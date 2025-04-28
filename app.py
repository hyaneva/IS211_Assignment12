from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3

app = Flask(__name__)
app.secret_key = 'secretkey'

DATABASE = 'hw13.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def home():
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'password':
            session['logged_in'] = True
            return redirect('/dashboard')
        else:
            error = 'Invalid Credentials. Please try again.'
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect('/login')

def login_required(f):
    def wrapper(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect('/login')
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

@app.route('/dashboard')
@login_required
def dashboard():
    db = get_db()
    students = db.execute('SELECT * FROM students').fetchall()
    quizzes = db.execute('SELECT * FROM quizzes').fetchall()
    return render_template('dashboard.html', students=students, quizzes=quizzes)

@app.route('/student/add', methods=['GET', 'POST'])
@login_required
def add_student():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        db = get_db()
        db.execute('INSERT INTO students (first_name, last_name) VALUES (?, ?)', (first_name, last_name))
        db.commit()
        return redirect('/dashboard')
    return render_template('add_student.html')

@app.route('/quiz/add', methods=['GET', 'POST'])
@login_required
def add_quiz():
    if request.method == 'POST':
        subject = request.form['subject']
        num_questions = request.form['num_questions']
        quiz_date = request.form['quiz_date']
        db = get_db()
        db.execute('INSERT INTO quizzes (subject, num_questions, quiz_date) VALUES (?, ?, ?)', (subject, num_questions, quiz_date))
        db.commit()
        return redirect('/dashboard')
    return render_template('add_quiz.html')

@app.route('/results/add', methods=['GET', 'POST'])
@login_required
def add_result():
    db = get_db()
    students = db.execute('SELECT * FROM students').fetchall()
    quizzes = db.execute('SELECT * FROM quizzes').fetchall()
    if request.method == 'POST':
        student_id = request.form['student_id']
        quiz_id = request.form['quiz_id']
        score = request.form['score']
        db.execute('INSERT INTO results (student_id, quiz_id, score) VALUES (?, ?, ?)', (student_id, quiz_id, score))
        db.commit()
        return redirect('/dashboard')
    return render_template('add_result.html', students=students, quizzes=quizzes)

@app.route('/student/<int:student_id>')
@login_required
def student_results(student_id):
    db = get_db()
    student = db.execute('SELECT * FROM students WHERE id = ?', (student_id,)).fetchone()
    results = db.execute('''
        SELECT results.score, quizzes.subject, quizzes.quiz_date
        FROM results
        JOIN quizzes ON results.quiz_id = quizzes.id
        WHERE results.student_id = ?
    ''', (student_id,)).fetchall()
    return render_template('student_results.html', student=student, results=results)

@app.route('/quiz/<int:quiz_id>/results/')
def quiz_results(quiz_id):
    db = get_db()
    quiz = db.execute('SELECT * FROM quizzes WHERE id = ?', (quiz_id,)).fetchone()
    results = db.execute('''
        SELECT students.id AS student_id, results.score
        FROM results
        JOIN students ON results.student_id = students.id
        WHERE results.quiz_id = ?
    ''', (quiz_id,)).fetchall()

    show_names = False
    if session.get('logged_in'):
        show_names = True
        results = db.execute('''
            SELECT students.first_name, students.last_name, results.score
            FROM results
            JOIN students ON results.student_id = students.id
            WHERE results.quiz_id = ?
        ''', (quiz_id,)).fetchall()
    
    return render_template('quiz_results.html', quiz=quiz, results=results, show_names=show_names)

@app.route('/student/<int:id>/delete')
@login_required
def delete_student(id):
    db = get_db()
    db.execute('DELETE FROM students WHERE id = ?', (id,))
    db.commit()
    return redirect('/dashboard')

@app.route('/quiz/<int:id>/delete')
@login_required
def delete_quiz(id):
    db = get_db()
    db.execute('DELETE FROM quizzes WHERE id = ?', (id,))
    db.commit()
    return redirect('/dashboard')

@app.route('/result/<int:id>/delete')
@login_required
def delete_result(id):
    db = get_db()
    db.execute('DELETE FROM results WHERE id = ?', (id,))
    db.commit()
    return redirect('/dashboard')

if __name__ == '__main__':
    app.run(debug=True)
