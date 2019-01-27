import re
import requests
import mysql.connector

from bs4 import BeautifulSoup

from htmlParsing import get_html_trade_list
from htmlParsing import parse_open_trade
from htmlParsing import construct_comparison_string
from db import db_connect


tr_set = get_html_trade_list("open")

cnx = db_connect()
cursor = cnx.cursor()

add_trade = (
    "INSERT INTO journal "
    "( open_time, type, volume, symbol, open_price )"
    "VALUES (%s, %s, %s, %s, %s )"
)

query = (
    "SELECT open_time, type, volume, symbol, open_price FROM journal "
    "WHERE DATE(open_time) = %s AND type = %s AND volume = %s AND symbol = %s AND open_price = %s"
)

prev_trade = ""

for tr in tr_set:
    try:
        print(
            "###########################################################################"
        )
        time, trade_type, volume, symbol, price = parse_open_trade(tr)
        # print(query, time[:-5], trade_type, volume, symbol, str(float(price)))
        cursor.execute(
            query, (time[:-5], trade_type, volume, symbol, str(float(price)))
        )

        i = 0
        # checking number of returned DB rows was not working
        # becasue of this there is this hacky solution here
        for (col1, col2, col3, col4, col5) in cursor:
            # print (col1, col2, col3, col4)
            i = i + 1

        current_trade = construct_comparison_string(
            time, trade_type, volume, symbol, price
        )

        if i == 1 and current_trade == prev_trade or i == 0:
            trade_string = (time, trade_type, volume, symbol, price)
            cursor.execute(add_trade, trade_string)
            print("trade added")
            print(trade_string)

        prev_trade = current_trade
        cnx.commit()

    except AttributeError as e:
        break

cursor.close()
cnx.close()
