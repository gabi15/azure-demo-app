import os
import textwrap
import pyodbc

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


def get_songs():
    with pyodbc.connect(connection_string) as conn:
        with conn.cursor() as cursor:
            results = get_songs_from_db(cursor)
    return results


def get_songs_from_db(cursor):
    results = []
    cursor.execute("SELECT * from [dbo].[Song]")
    columns = [column[0] for column in cursor.description]
    rows = cursor.fetchall()
    for row in rows:
        results.append(dict(zip(columns, row)))
    return results


def add_song(song):
    with pyodbc.connect(connection_string) as conn:
        with conn.cursor() as cursor:
            add_song_to_db(cursor, song)


def add_song_to_db(cursor, song):
    insert_statement = 'INSERT INTO [dbo].[Song] (Name, Artist) VALUES (?, ?)'
    cursor.execute(insert_statement, song['Name'], song['Artist'])
    cursor.commit()


def get_song_by_id(song_id):
    with pyodbc.connect(connection_string) as conn:
        with conn.cursor() as cursor:
            result = get_song_by_id_from_db(cursor, song_id)
    return result


def get_song_by_id_from_db(cursor, song_id):
    results = []
    cursor.execute("SELECT * from [dbo].[Song] song where song.id=?", song_id)
    columns = [column[0] for column in cursor.description]
    rows = cursor.fetchall()
    for row in rows:
        results.append(dict(zip(columns, row)))
    return results


def delete_song_by_id(song_id):
    with pyodbc.connect(connection_string) as conn:
        with conn.cursor() as cursor:
            delete_song_by_id_from_db(cursor, song_id)


def delete_song_by_id_from_db(cursor, song_id):
    delete_statement = 'DELETE FROM [dbo].[Song] WHERE ID=?'
    cursor.execute(delete_statement, song_id)
    cursor.commit()


def update_song_by_id(song, song_id):
    with pyodbc.connect(connection_string) as conn:
        with conn.cursor() as cursor:
            update_song_by_id_to_db(cursor, song, song_id)


def update_song_by_id_to_db(cursor, song, song_id):
    update_statement = 'UPDATE [dbo].[Song] SET Name=?, Artist=? WHERE ID=?'
    cursor.execute(update_statement, song['Name'], song['Artist'], song_id)
    cursor.commit()


