# -*- coding: utf-8 -*-
# 20170828

__author__ = "Steven Wang"

"""To get historical rates from GDAX
For API reference:  https://docs.gdax.com/#market-data

Problems:
    GDAX public API seems to be too crowded.
    Every time I run this script, the data is not the same.

Args:
    link_*: created link
    trading_pair: trading product
    start_unix: start unix time
    end_unix: end unix time
    granularity: use second as unit
Returns:
    It will create plain text files containing price data.

"""

from urllib.request import Request, urlopen
import json
import datetime
import time


def get_data(trading_pair, start, end, granularity, end_unix, number_per_request):
    """get data from GDAX and return a dictionary.
    Args:
        link_*: crrated link.
        trading_pair_list: list of trading products.
        start: start time.
        end: end time.
        granularity: use second as unit.
        end_unix: used to check if this is the last use of get_data.

    Returns:
        It creates a text file and writes data to the file.
    """

    link_p = "https://api.gdax.com/products/" + trading_pair + "/candles?start=" + start + "&end=" + end + "&granularity=" + granularity
    with urlopen(link_p) as url:
        j = url.read().decode('utf8')
        s = json.loads(j)

    n = 0
    while (len(s) != number_per_request) and (end != end_unix) and (n <= 5):
        print('trying...', n)
        time.sleep(2)
        n = n + 1
        with urlopen(link_p) as url:
            j = url.read().decode('utf8')
            s = json.loads(j)

    file_name = trading_pair + "_data.txt"
    with open(file_name, 'a') as file_obj:
        for _ in reversed(s):
            file_obj.write(','.join(map(str, _)) + '\n')
    return s


def get_all_data(trading_pair_list, start_unix, end_unix, granularity, number_per_request, time_range_per_request):
    """get all the data in one function
    Args:
        trading_pair_list: list of trading products
        start_unix: start unix time
        end_unix: end unix time
        granularity: use second as unit

    Returns:
        Text files with data.
    """
    for _ in trading_pair_list:
        trading_pair = _
        unix_epoch_time = start_unix
        while unix_epoch_time <= end_unix:

            start = datetime.datetime.utcfromtimestamp(unix_epoch_time).isoformat()
            if end_unix - unix_epoch_time >= time_range_per_request:
                end = datetime.datetime.utcfromtimestamp(unix_epoch_time + time_range_per_request).isoformat()
            else:
                end = datetime.datetime.utcfromtimestamp(end_unix).isoformat()

            s = get_data(trading_pair, start, end, granularity, end_unix, number_per_request)
            unix_epoch_time = unix_epoch_time + time_range_per_request
            time.sleep(1)

    return 0

trading_pair_list = ['BTC-USD',
                     'ETH-USD',
                     'LTC-USD']


start_unix = 1451606400 - 1
# 20160101
end_unix = 1503878400 + 1
granularity = "3600"
number_per_request = 192
time_range_per_request = 691200

print(trading_pair_list, start_unix, end_unix, granularity, number_per_request, time_range_per_request)
get_all_data(trading_pair_list, start_unix, end_unix, granularity, number_per_request, time_range_per_request)

"""
#############################################################
# Ethereum
link_quantity = 'https://etherchain.org/api/supply'
# nor working
link_quantity_2 = 'https://api.etherscan.io/api?module=stats&action=ethsupply&apikey=YourApiKeyToken'
req = Request(link_quantity, headers={'User-Agent': 'Mozilla/5.0'})
j = urlopen(req).read().decode('utf8')
s = json.loads(j)
int(s['result'])/1000000000000000000
# watch out for the digit when it reaches over 100 million
"""
