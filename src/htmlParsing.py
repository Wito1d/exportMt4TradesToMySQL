import requests
import re

from bs4 import BeautifulSoup

from webAuthentication import url
from webAuthentication import auth_cookie


def get_html_trade_list(table_type):
    session = requests.Session()

    s = session.get(url, cookies=auth_cookie)
    bs = BeautifulSoup(s.text, "html.parser")

    table = bs.findAll("table", {"class": "responsive-table signal-info-table"})

    if table_type == "closed":
        body = table[1].find("tbody")
    elif table_type == "open":
        body = table[0].find("tbody")
    else:
        print("ERROR: please specify if you want to parse open or closed trades")

    tr_set = body.findAll("tr")
    return tr_set


def parse_open_trade(html_tr):
    time = html_tr.find("td", {"data-label": "Time"}).get_text()
    time = time.replace(".", "-")
    time = re.sub(r"\s+", "", time, flags=re.UNICODE)
    trade_type = html_tr.find("td", {"data-label": "Type"}).get_text()
    trade_type = re.sub("Sell", "sell", trade_type)
    trade_type = re.sub("Buy", "buy", trade_type)
    volume = html_tr.find("td", {"data-label": "Volume"}).get_text()
    symbol = html_tr.find("td", {"data-label": "Symbol"}).get_text()
    price = html_tr.find("td", {"data-label": "Price"}).get_text()
    price = re.sub(r"\s+", "", price, flags=re.UNICODE)
    return time, trade_type, volume, symbol, price


def construct_comparison_string(time, trade_type, volume, symbol, price):
    return time + trade_type + volume + symbol + str(float(price))
