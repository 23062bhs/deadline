from flask import Flask, g, render_template, request, redirect, url_for, session, flash
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import sqlite3

DATABASE = "deadline.db"

# initialise app and secret key
app = Flask(__name__)
app.secret_key = 'deadlinesecretkey'

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

# user needs to be logged in to access the app
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session: # redirects to login page if not logged in
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# home page
@app.route('/', methods=['GET', 'POST'])
@login_required
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
                sql_insert = "INSERT INTO Tasks (TaskName, DueDate, SubjectID, StatusID, UserID) VALUES (?, ?, ?, ?, ?)"
                db.execute(sql_insert, (task_name, due_date_str, subject_id, status_id, session['user_id'],))
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
        WHERE Tasks.UserID = ?
        """
    tasks = query_db(sql, (session['user_id'],))
    
    sql_subjects = """
        SELECT Subjects.SubjectID, Subjects.SubjectName, Subjects.SubjectColor, 
               COUNT(Tasks.TaskID) AS TaskCount
        FROM Subjects
        LEFT JOIN Tasks ON Subjects.SubjectID = Tasks.SubjectID
        WHERE Subjects.UserID = ?    
        GROUP BY Subjects.SubjectID;
    """
    subjects = query_db(sql_subjects, (session['user_id'],))

    # display due dates correctly (day, month, year)
    formatted_list = []
    for task in tasks:
        task_list = list(task) 
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

    total = len(tasks)
    completed = sum(1 for t in tasks if t[8] == 1)
    overdue = sum(1 for t in tasks if t[8] == 4)   
    incomplete = total - completed - overdue
    
    return render_template("index.html", tasks=tasks, subjects=subjects, today_date=today.isoformat(), total=total, completed=completed, incomplete=incomplete, overdue=overdue)

# home page subject section
@app.route('/add-subject', methods=['POST'])
@login_required
def add_subject():
    if request.method == 'POST':
        subject_name = request.form.get('subject_name')
        subject_color = request.form.get('subject_color') 

        db = get_db()
        
        sql = "INSERT INTO Subjects (SubjectName, SubjectColor, UserID) VALUES (?, ?, ?)"
        db.execute(sql, (subject_name, subject_color, session['user_id'],))
        db.commit()
        
        return redirect(url_for('home'))
    
# delete tasks
@app.route('/delete-task/<int:task_id>')
@login_required
def delete_task(task_id):
    db = get_db()
    db.execute("DELETE FROM Tasks WHERE TaskID = ? AND UserID = ?", (task_id, session['user_id'],))
    db.commit()
    return redirect(request.referrer or url_for('home'))

# edit tasks
@app.route('/edit-task/<int:task_id>', methods=['POST'])
@login_required
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
            WHERE TaskID = ? AND UserID = ?
        """
        db.execute(sql, (task_name, subject_id, due_date, status_id, task_id, session['user_id'],))
        db.commit()
        
    return redirect(request.referrer or url_for('home'))

# subjects page
@app.route('/subjects')
@login_required
def subjects_page():
    db = get_db()
    
    sql_subjects = """
        SELECT Subjects.SubjectID, Subjects.SubjectName, Subjects.SubjectColor, 
        COUNT(Tasks.TaskID) AS TaskCount
        FROM Subjects
        LEFT JOIN Tasks ON Subjects.SubjectID = Tasks.SubjectID
        WHERE Subjects.UserID = ?
        GROUP BY Subjects.SubjectID
    """
    subjects = query_db(sql_subjects, (session['user_id'],))
    
    return render_template("subjects.html", subjects=subjects)

# edit subjects
@app.route('/edit-subject/<int:subject_id>', methods=['POST'])
@login_required
def edit_subject(subject_id):
    if request.method == 'POST':
        subject_name = request.form.get('subject_name')
        subject_id = request.form.get('subject_id')
        subject_color = request.form.get('subject_color')
        
        db = get_db()
        #update the subject row that matches the subject id
        sql = """
            UPDATE Subjects
            SET SubjectName = ?, SubjectColor = ?
            WHERE SubjectID = ? AND UserID = ?
        """
        db.execute(sql, (subject_name, subject_color, subject_id, session['user_id']))
        db.commit()
        
    return redirect(request.referrer or url_for('home'))

# delete subjects
@app.route('/delete-subject/<int:subject_id>')
@login_required
def delete_subject(subject_id):
    db = get_db()
    db.execute("DELETE FROM Subjects WHERE SubjectID = ? AND UserID = ?", (subject_id, session['user_id'],))
    db.commit()
    return redirect(request.referrer or url_for('subjects_page'))

# tasks page
@app.route('/tasks')
@login_required
def tasks_page():
    today = datetime.now().date() # used to set the minimum selectable date in forms 
    subjects = query_db("SELECT SubjectID, SubjectName, SubjectColor FROM Subjects WHERE UserID = ?", (session['user_id'],))

    # truncate long subject names in the dropdown
    subjects = [
        (s[0], s[1][:17] + '...' if len(s[1]) > 20 else s[1], s[2])
        for s in subjects
    ]

    subject_filter = request.args.get('subject') # gets the subject filter from the URL query string
    status_filter = request.args.get('status') # gets the status filter from the URL query string
    sort = request.args.get('sort') # gets the sort option from the URL

    conditions = ["Tasks.UserID = ?"]
    args = [session['user_id']]

    #subject filter
    if subject_filter:
        conditions.append("Tasks.SubjectID = ?")
        args.append(subject_filter)

    if status_filter:
        conditions.append("Tasks.StatusID = ?")
        args.append(status_filter)

    where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""

    # sort button
    if sort == 'due_soonest':
        order_clause = "ORDER BY Tasks.DueDate ASC"
    elif sort == 'due_latest':
        order_clause = "ORDER BY Tasks.DueDate DESC"
    elif sort == 'name':
        order_clause = "ORDER BY Tasks.TaskName ASC"
    else:
        order_clause = ""

    sql = f"""
        SELECT Tasks.TaskID, Tasks.TaskName, Tasks.DueDate,
        Subjects.SubjectName, Status.StatusName, Subjects.SubjectColor, Status.StatusColor,
        Tasks.SubjectID, Tasks.StatusID
        FROM Tasks
        LEFT JOIN Subjects ON Tasks.SubjectID = Subjects.SubjectID
        LEFT JOIN Status ON Tasks.StatusID = Status.StatusID
        {where_clause}
        {order_clause}
    """
    tasks = query_db(sql, args)

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
    return render_template("tasks.html", tasks=tasks, subjects=subjects, today_date=today.isoformat(), selected_subject=subject_filter, selected_status=status_filter, selected_sort=sort)

# checkbox
@app.route('/delete-selected', methods=['POST'])
@login_required
def delete_selected():
    selected_tasks = request.form.get('selected_tasks') # gets the selected task IDs
    if selected_tasks:
        task_ids = selected_tasks.split(',') # splits the comma separated IDs into a list
        db = get_db()
        for task_id in task_ids:
            db.execute("DELETE FROM Tasks WHERE TaskID = ? AND UserID = ?", (task_id, session['user_id'],)) # deletes each selected task
        db.commit()
    return redirect(request.referrer or url_for('tasks_page'))

# signup page
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # username and password requirements
        existing_user = query_db("SELECT * FROM Users WHERE Username = ?", (username,), one=True)
        if existing_user:
            flash('Username already taken')
            session['form_username'] = username
            return redirect(url_for('signup'))
        if len(username) < 5:
            flash('Username must be at least 5 characters')
            session['form_username'] = username
            return redirect(url_for('signup'))  
        if len(username) > 20:
            flash('Username must be less than 20 characters')
            session['form_username'] = username
            return redirect(url_for('signup'))
        if ' ' in username:
            flash('Username cannot contain spaces')
            session['form_username'] = username
            return redirect(url_for('signup'))
        if len(password) < 8:
            flash('Password must be more than 8 characters')
            session['form_username'] = username
            return redirect(url_for('signup'))
        if request.form['password'] != request.form['confirm_password']:
            flash('Passwords do not match')
            session['form_username'] = username
            return redirect(url_for('signup'))

        # hash the password, get the join date and insert the new user
        hashed_password = generate_password_hash(password)
        join_date = datetime.now().strftime('%d-%m-%Y')
        db = get_db()
        db.execute("INSERT INTO Users (Username, Password, JoinDate) VALUES (?, ?, ?)", (username, hashed_password, join_date))
        db.commit()

        return redirect(url_for('login'))

    return render_template('signup.html')

# login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # check if user exists and password is correct
        user = query_db("SELECT * FROM Users WHERE Username = ?", (username,), one=True)
        if user and check_password_hash(user[2], password):
            session['user_id'] = user[0] # stores user ID in session
            session['username'] = user[1] # stores username in session
            return redirect(url_for('home'))

        flash('Invalid username or password')
        session['form_username'] = username
        return redirect(url_for('login'))

    return render_template('login.html')

# logout
@app.route('/logout')
def logout():
    session.clear() # clears the session
    return redirect(url_for('login'))

# profile page
@app.route('/profile')
@login_required
def profile():
    user = query_db("SELECT * FROM Users WHERE UserID = ?", (session['user_id'],), one=True)
    join_date = user[3] if len(user) > 3 else 'Unknown'

    # get task counts
    total = query_db("SELECT COUNT(*) FROM Tasks WHERE UserID = ?", (session['user_id'],), one=True)[0]
    completed = query_db("SELECT COUNT(*) FROM Tasks WHERE UserID = ? AND StatusID = 1", (session['user_id'],), one=True)[0]
    overdue = query_db("SELECT COUNT(*) FROM Tasks WHERE UserID = ? AND StatusID = 4", (session['user_id'],), one=True)[0]
    incomplete = total - completed - overdue

    # get subjects with task counts
    subjects = query_db("""
        SELECT Subjects.SubjectID, Subjects.SubjectName, Subjects.SubjectColor,
        COUNT(Tasks.TaskID) AS TaskCount
        FROM Subjects
        LEFT JOIN Tasks ON Subjects.SubjectID = Tasks.SubjectID
        WHERE Subjects.UserID = ?
        GROUP BY Subjects.SubjectID
        ORDER BY TaskCount DESC
    """, (session['user_id'],))

    subject_count = len(subjects)

    return render_template("profile.html", join_date=join_date, total=total, completed=completed, incomplete=incomplete, overdue=overdue, subjects=subjects, subject_count=subject_count)

# edit profile
@app.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        new_username = request.form.get('username')
        new_password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        db = get_db()

        # only check username rules if it's actually being changed
        if new_username != session['username']:
            existing_user = query_db("SELECT * FROM Users WHERE Username = ?", (new_username,), one=True)
            if existing_user:
                flash('Username already taken')
                return redirect(url_for('edit_profile'))
            if len(new_username) < 5:
                flash('Username must be at least 5 characters')
                return redirect(url_for('edit_profile'))
            if len(new_username) > 20:
                flash('Username must be less than 20 characters')
                return redirect(url_for('edit_profile'))
            if ' ' in new_username:
                flash('Username cannot contain spaces')
                return redirect(url_for('edit_profile'))

        # only update password if the user typed one
        if new_password:
            if len(new_password) < 8:
                flash('Password must be more than 8 characters')
                return redirect(url_for('edit_profile'))
            if new_password != confirm_password:
                flash('Passwords do not match')
                return redirect(url_for('edit_profile'))
            hashed_password = generate_password_hash(new_password)
            db.execute("UPDATE Users SET Username = ?, Password = ? WHERE UserID = ?", (new_username, hashed_password, session['user_id']))
        else:
            db.execute("UPDATE Users SET Username = ? WHERE UserID = ?", (new_username, session['user_id']))

        db.commit()
        session['username'] = new_username  # keep session in sync
        flash('Profile updated successfully')
        return redirect(url_for('edit_profile'))

    return render_template('edit_profile.html')

# error 404 handler
@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

# runs the app directly 
if __name__ == "__main__":
    app.run(debug=True)