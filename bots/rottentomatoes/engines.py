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


import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from hal.internet.engines import SearchEngine, SearchEngineResult


class RottenTomatoesSearchResult(SearchEngineResult):
    def __init__(self, title, link, category, year, artists, tmeter):
        SearchEngineResult.__init__(self, title, link)

        self.category = category
        self.year = year
        self.artists = artists
        self.tmeter = tmeter


class RottenTomatoes(SearchEngine):
    def __init__(self):
        SearchEngine.__init__(self, "https://www.rottentomatoes.com/search/?search=",
                              blank_replace="%20")  # create search engine with url

    @staticmethod
    def _has_results(search_page):
        """
        :param search_page: soup
            HTML page to parse
        :return: bool
            True iff search page got any results
        """

        return "No results, you didn't search for anything!" not in search_page

    def _parse_result(self, item, category):
        """
        :param item: soup
            Raw item
        :param category: str
            Category to search
        :return: RottenTomatoesSearchResult
            Parsed item
        """

        if category == "Movies":
            try:
                title = item.find_all("a")[1].text.strip()  # title
            except:
                title = "No title found"

            try:
                link = urljoin(self.domain, item.find_all("a")[1]["href"].strip())  # link
            except:
                link = "No link found"

            try:
                year = int(re.sub("\D", "", item.find_all("span", {"class": "movie_year"})[0].text))  # year
            except:
                year = -1

            try:
                artists = [x.text.strip().title() for x in
                           item.find_all("a", {"class": "unstyled articleLink"})[1:]]  # artists
            except:
                artists = []

            try:
                tmeter = int(re.sub("\D", "", item.find_all("span", {"class": "tMeterScore"})[0].text))  # tmeter
            except:
                tmeter = -1

            return RottenTomatoesSearchResult(title, link, category, year, artists, tmeter)
        elif category == "TV":
            try:
                title = item.find_all("a")[1].text.strip()  # title
            except:
                title = "No title found"

            try:
                link = urljoin(self.domain, item.find_all("a")[1]["href"].strip())  # link
            except:
                link = "No link found"

            try:
                year = item.find_all("span")[-1].text  # year
            except:
                year = -1

            try:
                tmeter = int(item.find_all("span", {"class": "tMeterScore"})[0].text.replace("%", ""))  # tmeter
            except:
                tmeter = -1

            return RottenTomatoesSearchResult(title, link, category, year, [], tmeter)
        elif category == "Celebrities" or category == "Critics" or category == "Franchise":
            try:
                title = item.find_all("a")[1].text.strip()  # title
            except:
                title = "No title found"

            try:
                link = urljoin(self.domain, item.find_all("a")[1]["href"].strip())  # link
            except:
                link = "No link found"

            return RottenTomatoesSearchResult(title, link, category, -1, [], -1)

    def _get_results(self, soup, category):
        """
        :param soup: BeautifulSoup
            bs4 object from raw HTML search page.
        :param category: string
            Name of category to search.
        :return: array which yields RottenTomatoesSearchResult
            Results of query in this search engine.
        """

        if self._has_results(soup):
            categories = soup.find_all("div", {"id": "main_container"}) \
                [0].find_all("h2", {"class": "bottom_divider"})
            categories = [x.text for x in categories]  # list of categories

            items = soup.find_all("div", {"id": "main_container"}) \
                [0].find_all("ul", {"class": "results_ul"})  # list of results

            r = []

            for i in range(len(categories)):  # get DOM elements of category
                c = categories[i]  # name of category
                items_c = []

                if c == "Movies" or c == "TV":
                    items_c = items[i].find_all("li", {"class": "bottom_divider clearfix"})  # items of category
                elif c == "Celebrities" or c == "Critics" or c == "Franchise":
                    items_c = items[i].find_all("li", {"class": "media bottom_divider"})

                if category == "All" or c == category:  # select only items with given category
                    for item in items_c:
                        r.append(self._parse_result(item, c))
        else:
            r = []  # soup has no results

        return r

    def search(self, query, category="all"):
        """
        :param query: string
            Search engine for query.
        :param category: string
            Category to search on.
        :return: array which yields RottenTomatoesSearchResult
            Results of query in this search engine.
        """

        search_page = self.get_search_page(query)  # get html source page of results of query
        return self._get_results(BeautifulSoup(search_page, "lxml"), category)
