# -*- coding: utf-8 -*-
# 20170830

__author__ = "Steven Wang"

import pandas as pd


def get_vwap(file_path, file_name_list):
    """Get vwap data of all currencies in file_name_list

    Args:
        file_path: system path of the file location
        file_name_list: assume each file in this list contains data of one cryptocurrency

    Returns:!
        df: A dataframe containing formatted data.

    """

    df = []
    for i in range(len(file_name_list)):
        df.append(pd.read_csv(file_path + file_name_list[i]))

    df = pd.concat(df, axis=1)
    df = df.iloc[:12930]
    df = df.drop('Date', axis=1)

    # testing for correctness after concatenation of dataframes
    # if only returns 0, then all good
    result_1 = df.iloc[:, 0] - df.iloc[:, 3]
    result_2 = df.iloc[:, 0] - df.iloc[:, 6]
    if not (result_1.sum() == 0 and result_2.sum() == 0):
        print("error!!!")

    df.set_index(df.iloc[:, 0], inplace=True)
    df = df.drop('Timestamp', axis=1)

    df.columns = ['Vwap_BTCUSD', 'Volume_BTCUSD', 'Vwap_ETHUSD', 'Volume_ETHUSD', 'Vwap_LTCUSD', 'Volume_LTCUSD']
    return(df)


def get_market_cap(file_path, file_name, sheet_name_list):
    """Get market capitalization data of all currencies in sheet_name_list

    Args:
        file_path: system path of the file location
        file_name: The name of the excel file that contain different cryptocurrency data in different sheet

    Returns:!
        df: A list of dataframes.

    """

    link = file_path + file_name
    df_list = []
    for _ in sheet_name_list:
        df = pd.read_excel(link, sheetname=_)
        df['coin_name'] = _
        df_list.append(df)

    return df_list
