from flask import Flask, g, render_template, request, redirect, url_for
from datetime import datetime
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

#executes a query and returns either all results or 1 result
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
    
    sql_subjects = """
        SELECT Subjects.SubjectID, Subjects.SubjectName, Subjects.SubjectColor, 
               COUNT(Tasks.TaskID) AS TaskCount
        FROM Subjects
        LEFT JOIN Tasks ON Subjects.SubjectID = Tasks.SubjectID
        GROUP BY Subjects.SubjectID;
    """
    subjects = query_db(sql_subjects)

    sql = """
        SELECT Tasks.TaskID, Tasks.TaskName, Tasks.DueDate,
        Subjects.SubjectName, Status.StatusName, Subjects.SubjectColor, Status.StatusColor
        FROM Tasks
        LEFT JOIN Subjects ON Tasks.SubjectID = Subjects.SubjectID
        LEFT JOIN Status ON Tasks.StatusID = Status.StatusID
        """
    tasks = query_db(sql)

    #display due dates correctly
    formatted_list = []

    for task in tasks:
        task_list = list(task)
        
        if task_list[2]:
            try:
                date_obj = datetime.strptime(task_list[2], '%Y-%m-%d')
                task_list[2] = date_obj.strftime('%d %b %Y')
            except ValueError:
                pass
            
        formatted_list.append(task_list)

    tasks = formatted_list
    
    return render_template("index.html", tasks=tasks, subjects=subjects)


#home page subject section
@app.route('/add-subject', methods=['POST'])
def add_subject():
    if request.method == 'POST':
        subject_name = request.form.get('subject_name')
        subject_color = request.form.get('subject_color') 

        db = get_db()
        
        sql = "INSERT INTO Subjects (SubjectName, SubjectColor) VALUES (?, ?)"
        db.execute(sql, (subject_name, subject_color))
        db.commit()
        
        return redirect(url_for('home'))
    
#delete tasks
@app.route('/delete-task/<int:task_id>')
def delete_task(task_id):
    db = get_db()
    db.execute("DELETE FROM Tasks WHERE TaskID = ?", (task_id,))
    db.commit()
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True)