# Data loader
# Loads data from MySQL database

import sqlalchemy
import pandas as pd


def load_from_sql():
    """

    :return:
    """
    # Create SQL engine and establish a connection
    sql_engine = sqlalchemy.create_engine('mysql+pymysql://root:Eregion12!@127.0.0.1', pool_recycle=3600)

    db_connection = sql_engine.connect()

    # Put data into Pandas data frame
    results = pd.read_sql("select * from football_ressults.football_results", db_connection);
    pd.set_option('display.expand_frame_repr', False)

    # Set date to datetime format
    results['date'] = pd.to_datetime(results['date'])

    # Put countries info into Pandas data frame
    countries_info = pd.read_sql("select * from football_ressults.country_useful", db_connection);
    pd.set_option('display.expand_frame_repr', False)

    # Load the final data tables
    final_data = pd.read_sql("select * from football_ressults.final_data", db_connection);
    pd.set_option('display.expand_frame_repr', False)

    db_connection.close()

    return results, countries_info, final_data


def save_to_sql(data, table_name):
    """

    :param data:
    :param table_name:
    :return:
    """
    # Create SQL engine and establish a connection
    sql_engine = sqlalchemy.create_engine('mysql+pymysql://root:Eregion12!@127.0.0.1/football_ressults', pool_recycle=3600)

    db_connection = sql_engine.connect()

    data.to_sql(con=db_connection, name=table_name, if_exists='replace')

    db_connection.close()