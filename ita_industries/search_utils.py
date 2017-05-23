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


""" Search queries from various search engines in Internet """

PATH_TO_CHROMEDRIVER = "/home/stefano/Coding/misc/chromedriver"  # path to web-driver to use with selenium
VALUE_NOT_FOUND = "DNF"  # value to use when data error or not found


def search_telephone_number(query):
    """
    :param query: str
        Query
    :return: [] of str
        List of possible telephone numbers of query found on the Internet
    """

    if len(str(query["TELEFONO"])) > 4:  # already has telephone
        return [str(query["TELEFONO"]).strip()]

    return []  # TODO


def search_email(query):
    """
    :param query: str
        Query
    :return: [] of str
        List of possible telephone emails of query found on the Internet
    """

    return []  # TODO


def search_query(query):
    """
    :param query: str
        Query
    :return: {}
        List of attributes of query found on the Internet
    """

    return {
        "telephone": search_telephone_number(query),
        "email": search_email(query)
    }
