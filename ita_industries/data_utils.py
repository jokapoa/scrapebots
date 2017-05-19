# !/usr/bin/python3
# coding: utf-8

# Copyright 2017 Stefano Fogarollo
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


""" Parse, fix and save data """

import pandas as pd


def get_list_queries(df):
    """
    :param df:pandas.DataFrame
        Content of .csv file
    :return: [] of {}
        List of queries with attributes in input data
    """

    return list(df.T.to_dict().values())  # to list


def get_data_from_csv(path_in):
    """
    :param path_in:str
        File to use as input
    :return: pandas.DataFrame
        Content of .csv file
    """

    return pd.read_csv(path_in)
