import mysql.connector

def connection():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="170801",
        database="karaoke"
    )
    return conn