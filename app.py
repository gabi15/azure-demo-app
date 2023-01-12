from flask import Flask, render_template, request, flash, redirect, url_for
import pyodbc
import textwrap
import os
import logging


app = Flask(__name__)
app.config['SECRET_KEY'] = 'bigosik'
logging.basicConfig(level=logging.INFO)


server = 'tcp:relativity-project-db-server.database.windows.net,1433'
database = 'project-db'
username = os.environ["DB_USER"]
password = os.environ["DB_PASSWORD"]
driver = '{ODBC Driver 18 for SQL Server}'

connection_string = textwrap.dedent('''
    Driver={driver};
    Server={server};
    Database={database};
    Uid={username};
    Pwd={password};
    Encrypt=yes;
    TrustServerCertificate=no;
    Connection Timeout=30;
    '''.format(
    driver=driver,
    server=server,
    database=database,
    username=username,
    password=password
))


@app.route('/')
def hello_world():
    app.logger.info("Info log information")
    return "Hello world"


@app.route('/songs')
def get_songs():
    results = []
    with pyodbc.connect(connection_string) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * from [dbo].[Song]")
            columns = [column[0] for column in cursor.description]
            rows = cursor.fetchall()
            print(rows)
            for row in rows:
                results.append(dict(zip(columns, row)))
            print(results)

    return render_template('index.html', songs=results)


@app.route('/create', methods=['POST', 'GET'])
def create_song():
    if request.method == 'POST':
        title = request.form['title']
        artist = request.form['artist']

        if not title:
            flash('Title is required!')
        elif not artist:
            flash('Artist is required!')
        else:
            add_song({"Name": title, "Artist": artist})
            return redirect(url_for('get_songs'))
    return render_template('create.html', title='Add a new song')


@app.route('/song/<int:song_id>')
def get_song(song_id):
    results=[]
    with pyodbc.connect(connection_string) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * from [dbo].[Song] song where song.id=?", song_id)
            columns = [column[0] for column in cursor.description]
            rows = cursor.fetchall()
            print(rows)
            for row in rows:
                results.append(dict(zip(columns, row)))
            print(results)

    return render_template('song.html', songs=results)





@app.route('/song/<int:song_id>', methods=['POST'])
def delete_song(song_id):
    delete_statement = 'DELETE FROM [dbo].[Song] WHERE ID=?'
    with pyodbc.connect(connection_string) as conn:
        with conn.cursor() as cursor:
            cursor.execute(delete_statement, song_id)
            cursor.commit()
    return redirect(url_for('get_songs'))


@app.route('/song/<int:song_id>/update', methods=['POST', 'GET'])
def update_song(song_id):
    if request.method == 'POST':
        title = request.form['title']
        artist = request.form['artist']
        if not title:
            flash('Title is required!')
        elif not artist:
            flash('Artist is required!')
        else:
            update_song_by_id({"Name": title, "Artist": artist}, song_id)
            return redirect(url_for('get_songs'))
    return render_template('create.html', title='Update a song')


def add_song(song):
    insert_statement = 'INSERT INTO [dbo].[Song] (Name, Artist) VALUES (?, ?)'
    with pyodbc.connect(connection_string) as conn:
        with conn.cursor() as cursor:
            cursor.execute(insert_statement, song['Name'], song['Artist'])
            cursor.commit()


def update_song_by_id(song, id):
    update_statement = 'UPDATE [dbo].[Song] SET Name=?, Artist=? WHERE ID=?'
    with pyodbc.connect(connection_string) as conn:
        with conn.cursor() as cursor:
            cursor.execute(update_statement, song['Name'], song['Artist'], id)
            cursor.commit()


# main driver function
if __name__ == '__main__':
    app.run()
