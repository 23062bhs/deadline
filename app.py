from flask import Flask, g, render_template, request, redirect, url_for
from datetime import datetime
import sqlite3

DATABASE = "deadline.db"

# initialise app
app = Flask(__name__)

#connect to .db file
def get_db():
    db = getattr(g, '_database', None) # check if a connection already exists in g
    if db is None:
        db = g._database = sqlite3.connect(DATABASE) # creates a new connection if not
    return db

# automatically closes database after every request (prevents memory leaks and file locks)
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close() # only close if a connection was opened

# executes a query and returns either all results or 1 result
def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

# home page
@app.route('/', methods=['GET', 'POST'])
def home(): 
    db = get_db()
    today = datetime.now().date() # used to set the minimum selectable date in forms    

    if request.method == 'POST':
        #get form values
        task_name = request.form.get('task_name')
        due_date_str = request.form.get('due_date')
        subject_id = request.form.get('subject_id')
        status_id = request.form.get('status')

        #insert dates
        if due_date_str: 
            try:
                sql_insert = "INSERT INTO Tasks (TaskName, DueDate, SubjectID, StatusID) VALUES (?, ?, ?, ?)"
                db.execute(sql_insert, (task_name, due_date_str, subject_id, status_id))
                db.commit()
                return redirect(url_for('home'))
            
            except ValueError:
                return "Invalid date format", 400

    sql = """
        SELECT Tasks.TaskID, Tasks.TaskName, Tasks.DueDate,
        Subjects.SubjectName, Status.StatusName, Subjects.SubjectColor, Status.StatusColor, 
        Tasks.SubjectID, Tasks.StatusID
        FROM Tasks
        LEFT JOIN Subjects ON Tasks.SubjectID = Subjects.SubjectID
        LEFT JOIN Status ON Tasks.StatusID = Status.StatusID
        """
    tasks = query_db(sql)
    
    sql_subjects = """
        SELECT Subjects.SubjectID, Subjects.SubjectName, Subjects.SubjectColor, 
               COUNT(Tasks.TaskID) AS TaskCount
        FROM Subjects
        LEFT JOIN Tasks ON Subjects.SubjectID = Tasks.SubjectID
        GROUP BY Subjects.SubjectID;
    """
    subjects = query_db(sql_subjects)

    # display due dates correctly (day, month, year)
    formatted_list = []
    for task in tasks:
        task_list = list(task) # convert to list 
        raw_date = task_list[2] # store original date 
        
        if task_list[2]:
            try:
                date_obj = datetime.strptime(task_list[2], '%Y-%m-%d')
                task_list[2] = date_obj.strftime('%d %b %Y') # reformat the date
            except ValueError:
                pass # leaves date unchanged if it cant be fixed

        task_list.append(raw_date) 
        formatted_list.append(task_list)

    tasks = formatted_list
    
    return render_template("index.html", tasks=tasks, subjects=subjects, today_date=today.isoformat())

# home page subject section
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
    
# delete tasks
@app.route('/delete-task/<int:task_id>')
def delete_task(task_id):
    db = get_db()
    db.execute("DELETE FROM Tasks WHERE TaskID = ?", (task_id,))
    db.commit()
    return redirect(url_for('home'))

# edit tasks
@app.route('/edit-task/<int:task_id>', methods=['POST'])
def edit_task(task_id):
    if request.method == 'POST':
        # gets updated values from edit form 
        task_name = request.form.get('task_name')
        subject_id = request.form.get('subject_id')
        due_date = request.form.get('due_date')
        status_id = request.form.get('status')
        
        db = get_db()
        #updates task row that matches task id
        sql = """
            UPDATE Tasks 
            SET TaskName = ?, SubjectID = ?, DueDate = ?, StatusID = ? 
            WHERE TaskID = ?
        """
        db.execute(sql, (task_name, subject_id, due_date, status_id, task_id))
        db.commit()
        
    return redirect(url_for('home'))

# subjects page
@app.route('/subjects')
def subjects_page():
    db = get_db()
    
    sql_subjects = """
        SELECT Subjects.SubjectID, Subjects.SubjectName, Subjects.SubjectColor, 
        COUNT(Tasks.TaskID) AS TaskCount
        FROM Subjects
        LEFT JOIN Tasks ON Subjects.SubjectID = Tasks.SubjectID
        GROUP BY Subjects.SubjectID
    """
    subjects = query_db(sql_subjects)
    
    return render_template("subjects.html", subjects=subjects)

# edit subjects
@app.route('/edit-subject/<int:subject_id>', methods=['POST'])
def edit_subject(subject_id):
    if request.method == 'POST':
        subject_name = request.form.get('subject_name')
        subject_id = request.form.get('subject_id')
        subject_color = request.form.get('subject_color')
        
        db = get_db()
        #update the subject row that matches the subject id
        sql = """
            UPDATE Subjects
            SET SubjectName = ?, SubjectID = ?, SubjectColor = ?
            WHERE SubjectID = ?
        """
        db.execute(sql, (subject_name, subject_id, subject_color))
        db.commit()
        
    return redirect(url_for('home'))

# delete subjects
@app.route('/delete-subject/<int:subject_id>')
def delete_subject(subject_id):
    db = get_db()
    db.execute("DELETE FROM Subjects WHERE SubjectID = ?", (subject_id,))
    db.commit()
    return redirect(url_for('subjects_page'))

# tasks page
@app.route('/tasks')
def tasks_page():
    today = datetime.now().date() # used to set the minimum selectable date in forms 
    subjects = query_db("SELECT SubjectID, SubjectName, SubjectColor FROM Subjects")
    sql = """ 
        SELECT Tasks.TaskID, Tasks.TaskName, Tasks.DueDate,
        Subjects.SubjectName, Status.StatusName, Subjects.SubjectColor, Status.StatusColor,
        Tasks.SubjectID, Tasks.StatusID
        FROM Tasks
        LEFT JOIN Subjects ON Tasks.SubjectID = Subjects.SubjectID
        LEFT JOIN Status ON Tasks.StatusID = Status.StatusID
    """
    tasks = query_db(sql)

    formatted_list = []
    for task in tasks:
        task_list = list(task) # convert to list 
        raw_date = task_list[2] # store original date 
        
        if task_list[2]:
            try:
                date_obj = datetime.strptime(task_list[2], '%Y-%m-%d')
                task_list[2] = date_obj.strftime('%d %b %Y') # reformat the date
            except ValueError:
                pass # leaves date unchanged if it cant be fixed

        task_list.append(raw_date) 
        formatted_list.append(task_list)

    task = formatted_list
    
    return render_template("tasks.html", tasks=tasks, subjects=subjects, today_date=today.isoformat())

# error 404 handler
@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

# runs the app directly 
if __name__ == "__main__":
    app.run(debug=True)