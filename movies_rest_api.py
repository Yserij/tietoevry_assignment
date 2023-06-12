from flask import Flask, request
import sqlite3
import os.path

app = Flask(__name__)

def open_db_connection(db):
    global conn, cur
    conn = sqlite3.connect(db, check_same_thread=False)
    cur = conn.cursor()

def close_db_connection():
    global conn
    conn.close()

def create_table():
    global conn, cur
    open_db_connection('movies.db')
    cur.execute("""CREATE TABLE movies (
                        id INTEGER PRIMARY KEY,
                        title TEXT NOT NULL,
                        description TEXT,
                        release_year INTEGER NOT NULL
                        )""")
    conn.commit()
    close_db_connection()

def insert_testing_data():
    global conn, cur
    open_db_connection('movies.db')
    cur.execute("INSERT INTO movies (title, description, release_year) VALUES (?,?,?)", ('The Matrix','The Matrix is computer-generated dream world ...',1999))
    cur.execute("INSERT INTO movies (title, description, release_year) VALUES (?,?,?)", ('The Matrix Reloaded','Continuation of the cult clasic The Matrix ...',2003))
    cur.execute("INSERT INTO movies (title, release_year) VALUES (?,?)", ('Ender\'s Game',2013))
    conn.commit()
    close_db_connection()

def process_request_attributes():
    try:
        title = request.json['title']
        release_year = request.json['release_year']
        status_code = 200
    except KeyError:
        return 400, 'Bad request'

    try:
        description = request.json['description']
    except KeyError:
        description = None
    
    return status_code, (title, description, release_year)

@app.route('/')
def hello():
    return 'Hello World!'

@app.route('/movies')
def get_movies():
    global conn, cur
    open_db_connection('movies.db')
    cur.execute("SELECT * FROM movies")
    movies = cur.fetchall()

    output = []
    for movie in movies:
        data = {'id': movie[0], 'title': movie[1], 'description': movie[2], 'release_year': movie[3]}
        output.append(data)

    close_db_connection()
    return output

@app.route('/movies/<int:id>')
def get_movie(id):
    global conn, cur
    open_db_connection('movies.db')
    cur.execute("SELECT * FROM movies WHERE id=(?)",(id,))
    movie = cur.fetchone()
    if (movie is None):
        resp = 'Record not found', 404
    else:
        resp = {'id': movie[0], 'title': movie[1], 'description': movie[2], 'release_year': movie[3]}
    close_db_connection()
    return resp

@app.route('/movies',methods=['POST'])
def insert_movie():
    global conn, cur
    status_code, data = process_request_attributes()

    if status_code is 400:
        return data, status_code

    open_db_connection('movies.db')
    cur.execute("""INSERT INTO movies (title, description, release_year) VALUES (?,?,?)""", (data[0], data[1], data[2]))
    conn.commit()

    cur.execute("SELECT * FROM movies WHERE id=(?)",(cur.lastrowid,))
    movie = cur.fetchone()
    resp = {'id': movie[0], 'title': movie[1], 'description': movie[2], 'release_year': movie[3]}
    close_db_connection()
    
    return resp

@app.route('/movies/<int:id>', methods=['PUT'])
def update_movie(id):
    global conn, cur
    status_code, data = process_request_attributes()

    if status_code is 400:
        return data, status_code
    
    open_db_connection('movies.db')
    if (data[1] is None):
        cur.execute("UPDATE movies SET title = (?), release_year = (?) WHERE id = (?)", (data[0], data[2], id))
    else:
        cur.execute("UPDATE movies SET title = (?), description = (?), release_year = (?) WHERE id = (?)", 
                    (data[0], data[1], data[2], id))
    conn.commit()

    cur.execute("SELECT * FROM movies WHERE id=(?)",(id,))
    movie = cur.fetchone()
    resp = {'id': movie[0], 'title': movie[1], 'description': movie[2], 'release_year': movie[3]}
    close_db_connection()
    return resp

if not os.path.isfile('movies.db'):
    create_table()
    insert_testing_data()


if __name__ == '__main__':
    app.run()