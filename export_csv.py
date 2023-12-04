import mysql
import pandas as pd
from sqlalchemy import create_engine
def export_csv():
    db_config = {
        'host': 'localhost',
        'user': 'root',
        'password': '170801',
        'database': 'karaoke'
    }
    engine = create_engine(
        f"mysql+mysqlconnector://{db_config['user']}:{db_config['password']}@{db_config['host']}/{db_config['database']}")

    query = """
                Select * from customer
            """
    df = pd.read_sql(query, engine)
    engine.dispose()

    csv_filename = 'E:\\python-tkinter-karaoke\\Visualization\\csv files\\data2.csv'
    df.to_csv(csv_filename, index=False)

export_csv()