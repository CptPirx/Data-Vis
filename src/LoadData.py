# Data loader
# Loads data from MySQL database

import sqlalchemy
import pandas as pd
import time


def load_from_sql():
    # Create SQL engine and establish a connection
    sql_engine = sqlalchemy.create_engine('mysql+pymysql://root:Eregion12!@127.0.0.1', pool_recycle=3600)

    db_connection = sql_engine.connect()

    # Put data into Pandas data frame
    frame = pd.read_sql("select * from football_ressults.football_results", db_connection);
    pd.set_option('display.expand_frame_repr', False)

    frame['date'] = pd.to_datetime(frame['date'])

    return frame

    db_connection.close()