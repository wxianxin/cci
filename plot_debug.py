# -*- coding: utf-8 -*-
"""This is a script for testing and plotting cryptocurrency index with necessary variables.
"""
__author__ = "Steven Wang"
__date__ = "20170906"

import matplotlib.pyplot as plt
import cci


file_path = "/home/steven/Dropbox/data/"
file_name_list = ['vwapHourlyBTCUSD.csv', 'vwapHourlyETHUSD.csv', 'vwapHourlyLTCUSD.csv']
file_name = "marketcap.xlsx"
sheet_name_list = ["BTC", "BCC", "LTC", "ETH"]
# sheet_name_list = ["BTC", "BCC", "ETH", "LTC"]

df, df_list = cci.get_csv(file_path, file_name_list, file_name, sheet_name_list)
cap_index = cci.market_cap_index(df, df_list)
cap_vol_index = cci.cap_vol_index(df, df_list)
old_cap_index = cci.old_market_cap_index(df, df_list)
old_cap_vol_index = cci.old_cap_vol_index(df, df_list)

plt.style.use('ggplot')
plt.plot(cap_index, label="cap-weighted index")
plt.plot(cap_vol_index, label="cap&vol-weighted index")
plt.plot(old_cap_index, label="old cap-weighted index")
# plt.plot(old_cap_vol_index, label="old cap&vol-weighted index")
plt.legend(["cap-weighted index", "cap&vol-weighted index", "old cap-weighted index", "old cap&vol-weighted index"])

plt.show()
