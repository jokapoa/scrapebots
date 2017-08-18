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


""" Scrape IMDB list items """

from bs4 import BeautifulSoup
from hal.internet.web import Webpage

BASE_URL = "http://www.imdb.com/list/"
NULL_VALUE = "dnf"


def get_list_url(list_id):
    """
    :param list_id: str
        List ID
    :return: str
        Url of list
    """

    return "http://www.imdb.com/list/" + str(list_id) + "/"


def get_next_page_list_url(soup):
    """
    :param soup: BeautifulSoup lxml parser
        Raw HTML of page
    :return: str
        Url of next page of list
    """

    try:
        div = soup.find(
            "div", {"class": "see-more"}
        ).find("div", {"class": "pages"})  # div with next/prev pages

        if "next" in div.find("div").text.lower():  # there is a next page
            return str(div.find("div").a["href"])

        return None  # no next page
    except:
        return None  # no next page


def parse_item(soup):
    """
    :param soup: BeautifulSoup lxml parser
        Raw HTML of single item
    :return: {}
        Details info
    """

    out = {}  # parsed output
    try:
        out["listPosition"] = soup.find(
            "div", {"class": "number"}
        ).text.replace(".", "")
    except:
        out["listPosition"] = NULL_VALUE

    try:
        out["Title"] = soup.find("b").a.text.strip()
    except:
        out["Title"] = NULL_VALUE

    try:
        year = soup.find("span", {"class": "year_type"}).text
        out["Year"] = year.replace("(", "").replace(")", "")
    except:
        out["Year"] = NULL_VALUE

    try:
        out["imdbID"] = soup.find("b").a["href"].split("/")[-2]
    except:
        out["imdbID"] = NULL_VALUE

    try:
        soup = soup.find("div", {"class": "info"})
    except:
        pass

    try:
        out["imdbRating"] = soup.find(
            "div", {"class": "rating rating-list"}
        )["title"].split("/")[0].split(" ")[-1]
    except:
        out["imdbRating"] = NULL_VALUE

    try:
        out["imdbVotes"] = soup.find(
            "div", {"class": "rating rating-list"}
        )["title"].split("(")[1].split(" ")[0].replace(",", "")
    except:
        out["imdbVotes"] = NULL_VALUE

    try:
        out["Plot"] = soup.find(
            "div", {"class": "item_description"}
        ).text.split(". (")[0] + "."
    except:
        out["Plot"] = NULL_VALUE

    try:
        out["Runtime"] = soup.find(
            "div", {"class": "item_description"}
        ).text.split(". (")[-1].split(".)")[0]
    except:
        out["Runtime"] = NULL_VALUE

    try:
        out["Director"] = soup.find_all(
            "div", {"class": "secondary"}
        )[0].text.split(":")[1].strip()
    except:
        out["Director"] = NULL_VALUE

    try:
        out["Actors"] = soup.find_all(
            "div", {"class": "secondary"}
        )[-1].text.split(":")[1].strip()
    except:
        out["Actors"] = NULL_VALUE

    return out


def parse_list(soup):
    """
    :param soup: BeautifulSoup lxml parser
        Raw HTML of page
    :return: [] of {}
        List of parsed results of page
    """

    results_table = soup.find("div", {"class": "list detail"})
    results_raw_list = results_table.find_all("div", {
        "class": "list_item"})  # raw HTML divs containing info
    results_list = []  # output list
    for result in results_raw_list:
        results_list.append(
            parse_item(result)  # parse and append to output list
        )

    return results_list


def get_list_items(list_id):
    """
    :param list_id: str
        List ID
    :return: [] of {}
        List of parsed results of list
    """

    list_url = get_list_url(list_id)
    list_items = []  # output list

    url = list_url
    while url:  # while there is a url to fetch
        try:
            soup = BeautifulSoup(Webpage(url).get_html_source(),
                                 "lxml")  # get HTML parser of page
            next_url = get_next_page_list_url(soup)  # get url of next page
            if next_url is not None:
                url = list_url + next_url
            else:
                url = None

            list_items += parse_list(soup)
        except Exception as exception:
            print(str(exception))

    return list_items
