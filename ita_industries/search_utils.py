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

from search_engines import PagineGialleSearchBot

PATH_TO_CHROMEDRIVER = "/home/stefano/Coding/misc/chromedriver"  # path to web-driver to use with selenium
VALUE_NOT_FOUND = "DNF"  # value to use when data error or not found
VALUE_NULL = ""  # value to use when data is null
BOT = PagineGialleSearchBot(PATH_TO_CHROMEDRIVER)


def parse_address(query):
    """
    :param query: str
        Query
    :return: str
        Address of industry in query
    """

    try:
        if len(str(query["CAP"])) > 3:
            return str(int(query["CAP"]))[0].strip()
        elif len(str(query["CITTA"]).strip()) > 1:
            return str(query["CITTA"])
        elif len(str(query["VIA"]).strip()) > 1:
            return str(query["VIA"])
        else:
            return VALUE_NULL
    except:
        return VALUE_NULL


def parse_name(query):
    """
    :param query: str
        Query
    :return: str
        Address of industry in query
    """

    try:
        name_tokens = str(query["DENOMINAZIONE"]).lower().strip().split(" ")
        while name_tokens[0].strip()[0].isdigit():  # remove digits
            name_tokens = name_tokens[1:]

        if len(name_tokens) >= 8:
            return " ".join(name_tokens[2:])
        else:
            return " ".join(name_tokens)
    except:
        return str(query["DENOMINAZIONE"])


def search_telephone_number(query):
    """
    :param query: str
        Query
    :return: [] of str
        List of possible telephone numbers of query found on the Internet
    """

    if len(str(query["TELEFONO"])) > 4:  # already has telephone
        return [str(query["TELEFONO"]).strip()]

    try:
        address = parse_address(query)
        ind_name = parse_name(query)
        print("Searching", ind_name, "in", address)

        search_results = BOT.get_search_results(
            ind_name,
            address
        )[:3]  # get only top 3 results
        return [
            s["telephone"] for s in search_results
            ]  # get all telephones
    except:
        return [VALUE_NOT_FOUND]


def search_email(query):
    """
    :param query: str
        Query
    :return: [] of str
        List of possible telephone emails of query found on the Internet
    """

    return [VALUE_NOT_FOUND]  # TODO


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
