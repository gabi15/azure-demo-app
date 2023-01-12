from flask import Flask, jsonify
import pyodbc
import textwrap
import os
import logging


app = Flask(__name__)


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

logging.basicConfig(level=logging.INFO)
@app.route('/')
def hello_world():
    app.logger.info("Info log information")
    return "Hello world"


@app.route('/songs')
def get_songs():
    results = []
    app.logger.info("db user: ", username)
    app.logger.info("db password: ", password)
    with pyodbc.connect(connection_string) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * from [dbo].[Song]")
            columns = [column[0] for column in cursor.description]
            rows = cursor.fetchall()
            for row in rows:
                results.append(dict(zip(columns, row)))

    return jsonify({'data': results})


# main driver function
if __name__ == '__main__':
    app.run()
