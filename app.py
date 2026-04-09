from flask import Flask, g, render_template, request, redirect, url_for
import sqlite3

DATABASE = "deadline.db"

#initialise app
app = Flask(__name__)

#connect to .db file
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE) 
    return db


#automatically closes database after every request (prevents memory leaks and file locks)
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

#
def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

#home page
@app.route('/', methods=['GET', 'POST'])
def home(): 
    db = get_db()

    if request.method == 'POST':
        task_name = request.form.get('task_name')
        subject_id = request.form.get('subject_id')
        due_date = request.form.get('due_date')
        status_id = request.form.get('status')
        
        sql_insert = """
            INSERT INTO Tasks (TaskName, SubjectID, DueDate, StatusID)
            VALUES (?, ?, ?, ?)
        """
        db.execute(sql_insert, (task_name, subject_id, due_date, status_id))
        db.commit()
        
        return redirect(url_for('home'))

    sql = """
        SELECT Tasks.TaskID, Tasks.TaskName, Tasks.DueDate,
        Subjects.SubjectName, Status.StatusName
        FROM Tasks
        JOIN Subjects ON Tasks.SubjectID = Subjects.SubjectID
        JOIN Status ON Tasks.StatusID = Status.StatusID
        """
    tasks = query_db(sql)
    return render_template("index.html",tasks=tasks)

if __name__ == "__main__":
    app.run(debug=True)