# -*- coding: utf-8 -*-
# 20170831
__author__ = "Steven Wang"

"""Compute OmniIndex
Please pay attention for requirement of input of function "get_CSV".

"""

import read_data
import pandas as pd
from functools import reduce


def get_csv(file_path, file_name_list, file_name, sheet_name_list):
    """Get data from csv files

    Input:
        Please include all data a single Microsoft Excel file, with different trading pairs in different sheets.
        Please ensure all in every sheet the columns contain 'Close', 'Open', 'Volume', 'Market Cap'.
        Please ensure all use same time format as index.
        Please ensure the first sheet of data is the one with the most complete set of data points in time.

    Args:
        file_path: system path of the file location
        file_name_list: (for vwap data) assume each file in this list contains data of one cryptocurrency
        file_name: (for OHLC and other data) the name of the excel file that contain different cryptocurrency data in different sheet

    Returns:!
        Returns a list of dataframes containing formatted data.
    """
    df_vwap = read_data.get_vwap(file_path, file_name_list)
    ldf = read_data.get_market_cap(file_path, file_name, sheet_name_list)

    # for _ in ldf:
    #     _ = _.iloc[:753]
    #     _ = _.set_index(_.iloc[:, 0])
    #     _ = _.iloc[:, 1:]
    #     _['supply'] = (_['Market Cap'] / _['Open'])
    #     _['volume_shares'] = (_['Volume'] / _['Open'])
    #     _ = _.iloc[::-1]


    # the following loop is written in this way to avoid modifing the copy instead of the original dataframe.
    for i in range(len(ldf)):
        ldf[i] = ldf[i].iloc[:753]
        ldf[i] = ldf[i].set_index(ldf[i].iloc[:, 0])
        ldf[i] = ldf[i].iloc[:, 1:]
        ldf[i]['supply'] = (ldf[i]['Market Cap'] / ldf[i]['Open'])
        ldf[i]['volume_shares'] = (ldf[i]['Volume'] / ldf[i]['Open'])
        ldf[i] = ldf[i].iloc[::-1]

    # df_list = []
    # for i in range(len(ldf[0])):
    #     df_list.append([ldf[0].iloc[i]])
    # I know it's a piece of time-wasting shit
    # for c in range(1, len(ldf)):
    #     for i in range(len(ldf[c])):
    #         for _ in range(len(df_list)):
    #             if ldf[c].iloc[i].name == df_list[_][0].name:
    #                 df_list[_].append(ldf[c].iloc[i])

    ndf = [ldf[x].copy() for x in range(len(ldf))]
    # create a copy of *ldf* that I can work on with without worrying about the damage to orginal data.

    df_list = []
    for i in range(len(ndf[0])):
        df_list.append([ndf[0].iloc[i]])
        for c in range(1, len(ndf)):
            if ndf[c].iloc[0].name == ndf[0].iloc[i].name:
                df_list[i].append(ndf[c].iloc[0])
                ndf[c].drop(ndf[c].index[0], inplace=True)

    return ldf, df_list


def old_market_cap_index(df, df_list):
    """To calculate the market-cap weighted OmniIndex for any number ot trading pairs
    Args:

    Returns a dataframe of index and indexed by date.
    """
    index_list = [1000]
    for i in range(len(df[0]) - 1):

        # mv: market_value
        my_list = [0]
        my_list.extend(list(range(len(df_list[i]))))
        mv_0 = reduce(lambda x, y: x + df_list[i][y]['Close'] * df_list[i][y]['supply'], my_list)
        mv_01 = reduce(lambda x, y: x + df_list[i][y]['Close'] * df_list[i + 1][y]['supply'], my_list)
        mv_1 = reduce(lambda x, y: x + df_list[i + 1][y]['Close'] * df_list[i + 1][y]['supply'], my_list)

        divisor_0 = (mv_0 / 1000) if (i == 0) else divisor_1
        divisor_1 = divisor_0 * mv_01 / mv_0
        # TODO change the formula to the addition one instead (read S&P docs)

        new_index = mv_1 / divisor_1
        index_list.append(new_index)

    df_index = pd.DataFrame(index_list, columns=["cap_index"], index=df[0].index)

    return df_index


def market_cap_index(df, df_list):
    """To calculate the market-cap weighted OmniIndex for any number ot trading pairs
    Attention!!!:
        For now, this function cannot handle the scenario: add component to the index and remove component from the index at the same time.
        However, it can be easily remedied by adding a new column indicating the name of cryptocurrency to the source dataframe in the read_data module.
    Args:
        mv_0: previous market_value
        mv_1: market_value as of now

    Returns a dataframe of index and indexed by date.
    """
    index_list = [1000]
    my_list = [0]
    my_list.extend(list(range(len(df_list[0]))))
    mv_0 = reduce(lambda x, y: x + df_list[0][y]['Close'] * df_list[0][y]['supply'], my_list)

    for i in range(1, len(df[0])):

        my_list = [0]
        my_list.extend(list(range(len(df_list[i]))))

        # TODO remove try clause
        try:
            cmv = reduce(lambda x, y: x + df_list[i - 1][y]['Close'] * (df_list[i][y]['supply'] - df_list[i - 1][y]['supply']), my_list)
        except IndexError:
            my_list_1 = [0]
            my_list_1.extend(list(range(len(df_list[i - 1]))))
            new_i = len(df_list[i]) - 1
            cmv = reduce(lambda x, y: x + df_list[i - 1][y]['Close'] * (df_list[i][y]['supply'] - df_list[i - 1][y]['supply']), my_list_1) + \
                df_list[i][new_i]['Close'] * df_list[i][new_i]['supply']

        mv_1 = reduce(lambda x, y: x + df_list[i][y]['Close'] * df_list[i][y]['supply'], my_list)

        divisor_0 = (mv_0 / 1000) if (i == 1) else divisor_1
        new_index = 1000 if (i == 1) else new_index
        divisor_1 = divisor_0 + cmv / new_index

        new_index = mv_1 / divisor_1
        index_list.append(new_index)

        mv_0 = mv_1

    df_index = pd.DataFrame(index_list, columns=["cap_index"], index=df[0].index)

    return df_index


def cap_vol_index(df, df_list):

    """To calculate the maret-cap & trading volume weighted OmniIndex
    Args:

    Returns a dataframe of index and indexed by date.
    """
    index_list = [1000]
    my_list = [0]
    my_list.extend(list(range(len(df_list[0]))))

    mv_0 = reduce(lambda x, y: x + df_list[0][y]['Close'] * df_list[0][y]['supply'], my_list)

    for i in range(1, len(df[0])):

        my_list = [0]
        my_list.extend(list(range(len(df_list[i]))))
        trading_volume_list = list(map(lambda c: df_list[i][c]['Close'] * df_list[i][c]['volume_shares'], list(range(len(df_list[i])))))
        entire_trading_volume = sum(trading_volume_list)
        trading_volume_pct_list = [x / entire_trading_volume for x in trading_volume_list]
        multiplier_list = [1 + x * 0.40 for x in trading_volume_pct_list]

        # TODO remove try clause
        try:
            cmv = reduce(lambda x, y: x + df_list[i - 1][y]['Close'] * (df_list[i][y]['supply'] - df_list[i - 1][y]['supply']) * multiplier_list[y], my_list)
        except IndexError:
            my_list_1 = [0]
            my_list_1.extend(list(range(len(df_list[i - 1]))))
            new_i = len(df_list[i]) - 1
            cmv = reduce(lambda x, y: x + df_list[i - 1][y]['Close'] * (df_list[i][y]['supply'] - df_list[i - 1][y]['supply']) * multiplier_list[y], my_list_1) + \
                df_list[i][new_i]['Close'] * df_list[i][new_i]['supply'] * multiplier_list[new_i]

        mv_1 = reduce(lambda x, y: x + df_list[i][y]['Close'] * df_list[i][y]['supply'] * multiplier_list[y], my_list)

        divisor_0 = (mv_0 / 1000) if (i == 1) else divisor_1
        new_index = 1000 if (i == 1) else new_index
        divisor_1 = divisor_0 + cmv / new_index

        new_index = mv_1 / divisor_1
        index_list.append(new_index)

        mv_0 = mv_1

    df_index = pd.DataFrame(index_list, columns=["cap_index"], index=df[0].index)

    return df_index


def old_cap_vol_index(df, df_list):

    """To calculate the maret-cap & trading volume weighted OmniIndex
    Args:

    Returns a dataframe of index and indexed by date.
    """

    index_list = [1000]
    for i in range(len(df[0]) - 1):
        # mv: market value
        my_list = [0]
        my_list.extend(list(range(len(df_list[i]))))
        mv_0 = reduce(lambda x, y: x + df_list[i][y]['Close'] * df_list[i][y]['supply'], my_list)
        mv_01 = reduce(lambda x, y: x + df_list[i][y]['Close'] * df_list[i + 1][y]['supply'], my_list)
        mv_1 = reduce(lambda x, y: x + df_list[i + 1][y]['Close'] * df_list[i + 1][y]['supply'], my_list)
        # tv: trading volume
        tv_0 = reduce(lambda x, y: x + df_list[i][y]['Close'] * df_list[i][y]['volume_shares'], my_list)
        tv_01 = reduce(lambda x, y: x + df_list[i][y]['Close'] * df_list[i + 1][y]['volume_shares'], my_list)
        # is tv_01 necessary?
        tv_1 = reduce(lambda x, y: x + df_list[i + 1][y]['Close'] * df_list[i + 1][y]['volume_shares'], my_list)

        weight_vol = 0.40 / ((tv_0 / (mv_0 + tv_0) + tv_1 / (mv_1 + tv_1)) / 2)

        mvtv_0 = mv_0 + tv_0 * weight_vol
        mvtv_01 = mv_01 + tv_01 * weight_vol
        # is tv_01 necessary?
        mvtv_1 = mv_1 + tv_1 * weight_vol

        divisor_0 = (mvtv_0 / 1000) if (i == 0) else divisor_1
        divisor_1 = divisor_0 * mvtv_01 / mvtv_0
        # TODO change the formula to the addition one instead (read S&P docs)

        new_index = mvtv_1 / divisor_1
        index_list.append(new_index)

    df_index = pd.DataFrame(index_list, columns=["cap_vol_index"], index=df[0].index)

    return df_index
