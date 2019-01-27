import mysql.connector

from dbAuthentication import user
from dbAuthentication import password
from dbAuthentication import host
from dbAuthentication import database


def db_connect():
    cnx = mysql.connector.connect(
        user=user, password=password, host=host, database=database
    )
    return cnx
