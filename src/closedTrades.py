import datetime
import mysql.connector
import re
import requests
import string

from bs4 import BeautifulSoup

from htmlParsing import get_html_trade_list
from htmlParsing import parse_open_trade
from htmlParsing import construct_comparison_string
from db import db_connect


cnx = db_connect()
cursor = cnx.cursor()

query = (
    "SELECT open_time, type, volume, symbol, open_price, id FROM journal "
    "WHERE close_price is NULL OR close_price=0"
)

cursor.execute(query, ())
list_to_check = list()

i = 0
for (col1, col2, col3, col4, col5, col6) in cursor:
    # 	print (col1, col2, col3, col4, col5 )
    trade_string = (
        col1.isoformat() + str(col2) + str(col3) + str(col4) + str(float(col5))
    )
    trade_string = re.sub("(-[0-9][0-9])T([0-9][0-9]:)", r"\1\2", trade_string)
    trade_string = re.sub("([0-9][0-9]:[0-9][0-9]):00", r"\1", trade_string)
    # 	print( trade_string )
    list_to_check.append((col6, trade_string))
    i = i + 1

print("list to check before filtering")
for item in list_to_check:
    print(item)

# removed trades that are still open from the list
tr_set_open = get_html_trade_list("open")
for tr in tr_set_open:
    try:
        open_time, open_trade_type, open_volume, open_symbol, open_price = parse_open_trade(
            tr
        )
        open_current_trade = construct_comparison_string(
            open_time, open_trade_type, open_volume, open_symbol, open_price
        )
        print(open_current_trade)
        for index, found_trade in list_to_check:
            print(found_trade)
            if open_current_trade == found_trade:
                list_to_check.remove((index, found_trade))
    except AttributeError as e:
        break

print("list to check after filtering")
for item in list_to_check:
    print(item)

tr_set_closed = get_html_trade_list("closed")
for tr in tr_set_closed:
    try:
        time_open = tr.find("td", {"data-label": "Time"}).get_text()
        time_open = time_open.replace(".", "-")
        time_close = tr.findAll("td", {"data-label": "Time"})[1].get_text()
        time_close = time_close.replace(".", "-")
        trade_type = tr.find("td", {"data-label": "Type"}).get_text()

        volume = tr.find("td", {"data-label": "Volume"}).get_text()
        symbol = tr.find("td", {"data-label": "Symbol"}).get_text()
        price_open = tr.find("td", {"data-label": "Price"}).get_text()

        price_close = tr.findAll("td", {"data-label": "Price"})[1].get_text()
        swap_text = tr.find("td", {"data-label": "Swap"}).get_text()
        swap_text = re.sub(r"\s+", "", swap_text, flags=re.UNICODE)
        try:
            swap = float(swap_text)
        except ValueError as e:
            swap = 0
            # print( 'Swap error: ' + swap_text )
        profit_text = tr.find("td", {"data-label": "Profit"}).get_text()
        profit_text = re.sub(r"\s+", "", profit_text, flags=re.UNICODE)
        try:
            profit = float(profit_text)
        except ValueError as e:
            profit = 0
            # print( 'Profit error: ' + profit_text )

        time_open = re.sub(r"\s+", "", time_open, flags=re.UNICODE)
        trade_type = re.sub(r"\s+", "", trade_type, flags=re.UNICODE)
        trade_type = re.sub("Sell", "sell", trade_type)
        trade_type = re.sub("Buy", "buy", trade_type)
        volume = re.sub(r"\s+", "", volume, flags=re.UNICODE)
        symbol = re.sub(r"\s+", "", symbol, flags=re.UNICODE)
        price_open = re.sub(r"\s+", "", price_open, flags=re.UNICODE)
        current_trade = (
            time_open + trade_type + volume + symbol + str(float(price_open))
        )

        for index, found_trade in list_to_check:
            if current_trade == found_trade:
                print("updating DB")
                print(current_trade)
                update_trade = (
                    "UPDATE journal"
                    " SET close_time=%s, close_price=%s, profit=%s"
                    " WHERE id=%s"
                )
                update_string = (time_close, price_close, profit, index)
                cursor.execute(update_trade, update_string)
                list_to_check.remove((index, found_trade))
                cnx.commit()

    except AttributeError as e:
        print("AttributeError in for loop")
        break

cursor.close()
cnx.close()
