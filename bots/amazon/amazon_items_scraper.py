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


""" Parse items in classic amazon web-age """


def get_title_of_item(item):
    """
    :param item: BeautifulSoup
        Raw HTML item
    :return: str
        Titles of item
    """

    col_right = item.find_all("div", {
        "class": "a-fixed-left-grid-col a-col-right"})  # right column of item
    title = col_right[0].find_all("div", {
        "class": "a-row a-spacing-none"})  # divs containing title
    return title[0].a["title"]  # get title


def get_items_of_page(soup):
    """
    :param soup: BeautifulSoup
        Raw HTML page
    :return: [] of str
        List of items in page
    """

    return soup.find_all("div", {"class": "s-item-container"})


def get_titles_of_items_in_page(soup):
    """
    :param soup: BeautifulSoup
        Raw HTML page
    :return: [] of str
        List of titles of items in page
    """

    items = get_items_of_page(soup)
    for i in items:
        yield get_title_of_item(i)
