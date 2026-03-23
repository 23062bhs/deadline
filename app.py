from flask import Flask, g, render_template, request, redirect
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


def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

#home page
@app.route('/')
def home(): 
    sql = """
        SELECT Tasks.TaskID, Tasks.TaskName, Tasks.DueDate,
        Subjects.SubjectName, Status.StatusName
        FROM Tasks
        JOIN Subjects ON Tasks.SubjectID = Subjects.SubjectID
        JOIN Status ON Tasks.StatusID = Status.StatusID
        """
    tasks = query_db(sql)
    return render_template("index.html",tasks=tasks)\
    


if __name__ == "__main__":
    app.run(debug=True)