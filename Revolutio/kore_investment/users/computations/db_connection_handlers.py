import logging
import urllib

import oracledb
import psycopg2
from sqlalchemy import create_engine
from turbodbc import connect


def sqlAlchemy_engine_generator(connection_details):
    return create_engine(connection_details)


def turbodbc_engine_generator(connection_details):
    turbodbc_con = connect(
        driver=connection_details["driver"],
        server=connection_details["server"],
        database=connection_details["database"],
        uid=connection_details["uid"],
        pwd=connection_details["pwd"],
        turbodbc_options=connection_details["turbodbc_options"],
    )
    return turbodbc_con


def postgreSQL_engine_generator(connection_details):
    sql_engine = psycopg2.connect(
        dbname=connection_details["dbname"],
        user=connection_details["user"],
        password=connection_details["password"],
        host=connection_details["host"],
        port=connection_details["port"],
    )
    return sql_engine


def mssql_engine_generator(connection_details, fast_executemany=False):
    user_quoted = urllib.parse.quote_plus(
        "driver={ODBC Driver 18 for SQL Server};"
        + "server="
        + connection_details["server"]
        + ","
        + connection_details["port"]
        + ";database="
        + connection_details["db_name"]
        + ";Uid="
        + connection_details["username"]
        + ";Pwd="
        + connection_details["password"]
        + ";Encrypt=yes;TrustServerCertificate=yes;Connection Timeout=30;"
    )
    db_engine = create_engine(
        f"mssql+pyodbc:///?odbc_connect={user_quoted}", fast_executemany=fast_executemany
    )
    return db_engine


def oracle_engine_generator(connection_details):
    if connection_details.get("db_connection_mode") == "thick":
        oracledb.init_oracle_client()
        thick_mode = True
    else:
        thick_mode = False
    db_engine = create_engine(
        "oracle+oracledb://:@",
        thick_mode=thick_mode,
        connect_args={
            "user": connection_details["username"],
            "password": connection_details["password"],
            "host": connection_details["server"],
            "port": connection_details["port"],
            "service_name": connection_details["service_name"],
        },
    )
    return db_engine


def db_connection_generator(connection_details, con_type="TurbODBC"):
    if con_type == "SQLAlchemy":
        return sqlAlchemy_engine_generator(connection_details)
    elif con_type == "TurbODBC":
        return turbodbc_engine_generator(connection_details)
    else:
        return None
