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


from urllib.parse import urlencode

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


class GoogleSearchBot(object):
    """ Selenium bot to search Google data """

    BROWSER_WAIT_TIMEOUT_SECONDS = 1

    def __init__(self, chromedriver_path):
        """
        :param chromedriver_path: str
            Path to Chrome driver to use as browser
        """

        object.__init__(self)
        self.browser = webdriver.Chrome(chromedriver_path)

    @staticmethod
    def _get_search_url(query, page=0, per_page=10, lang="it"):
        # note: num per page might not be supported by google anymore (because of google instant)

        params = {
            "nl": lang,
            "q": query.encode("utf8"),
            "start": page * per_page,
            "num": per_page
        }
        params = urlencode(params)
        return u"http://www.google.com/search?" + params

    @staticmethod
    def _get_name(li):
        """Return the name of a google search."""

        a = li.find("a")
        # return a.text.encode("utf-8").strip()
        if a is not None:
            return a.text.strip()
        return None

    @staticmethod
    def _get_link(li):
        """Return external link from a search."""

        a = li.find("a")
        # return a.text.encode("utf-8").strip()
        if a is not None:
            return a["href"].strip()
        return None

    @staticmethod
    def _get_description(li):
        """Return the description of a google search.
        TODO: There are some text encoding problems to resolve."""

        sdiv = li.find("div", attrs={"class": "s"})
        if sdiv:
            stspan = sdiv.find("span", attrs={"class": "st"})
            if stspan is not None:
                return stspan.text.strip()
        else:
            return None

    def parse_page_results(self, html):
        """
        :return: [] of {}
            Each dict is a result of the query browser has just made
        """

        results = []
        soup = BeautifulSoup(html, "html.parser")
        soup = soup.find_all("div", {"class": "_NId"})[-1]
        divs = soup.findAll("div", attrs={"class": "rc"})
        for d in divs:
            name = self._get_name(d)
            link = self._get_link(d)
            description = self._get_description(d)
            results.append(
                {
                    "name": name,
                    "link": link,
                    "description": description
                }
            )
        return results

    def get_search_results(self, query):
        """
        :param query: str
            Words to search
        :return: void
            Browser navigates to Google page, search query and returns list of results
        """

        try:
            self.browser.get(
                self._get_search_url(query)
            )
            results = self.parse_page_results(self.browser.page_source)
        except:
            results = []
            print("Errors while searching for \"", query, "\"")

        return results


class DuckDuckGoSearchBot(object):
    """ Selenium bot to search Google data """

    BROWSER_WAIT_TIMEOUT_SECONDS = 3

    def __init__(self, chromedriver_path):
        """
        :param chromedriver_path: str
            Path to Chrome driver to use as browser
        """

        object.__init__(self)
        self.browser = webdriver.Chrome(chromedriver_path)

    @staticmethod
    def _get_search_url(query, page=0, per_page=10, lang="it"):
        # note: num per page might not be supported by google anymore (because of google instant)

        params = {
            "q": query.encode("utf8"),
            "t": "hd",
            "ia": "web"
        }
        return u"https://duckduckgo.com/html/?" + urlencode(params)

    @staticmethod
    def _get_name(li):
        """Return the name of a google search."""

        a = li.find_all("h2", {"class": "result__title"})[0].find_all("a", {
            "class": "result__a"})
        if a is not None:
            return a.text.strip()
        return None

    @staticmethod
    def _get_link(li):
        """Return external link from a search."""

        a = li.find_all("h2", {"class": "result__title"})[0].find_all("a", {
            "class": "result__a"})
        if len(a) > 0:
            return a[0]["href"]
        return None

    @staticmethod
    def _get_description(li):
        """Return the description of a google search.
        TODO: There are some text encoding problems to resolve."""

        a = li.find_all("div", {"class": "result__snippet"})
        if len(a) > 0:
            return a[0].text.strip()
        else:
            return None

    def parse_page_results(self, html, top=10):
        """
        :return: [] of {}
            Each dict is a result of the query browser has just made
        """

        WebDriverWait(self.browser, self.BROWSER_WAIT_TIMEOUT_SECONDS).until(
            EC.presence_of_element_located((By.ID, "links"))
        )  # wait until fully loaded
        results = []
        soup = BeautifulSoup(html, "lxml")
        divs = soup.find_all("div", {"id": "links"})[0].find_all("div", {
            "data-nir": "1"})[:top]
        divs = [d.find_all("div", {"class": "result__body"})[0] for d in divs]
        for d in divs:
            name = self._get_name(d)
            link = self._get_link(d)
            description = self._get_description(d)
            results.append(
                {
                    "name": name,
                    "link": link,
                    "description": description
                }
            )
        return results

    def get_search_results(self, query):
        """
        :param query: str
            Words to search
        :return: void
            Browser navigates to Google page, search query and returns list of results
        """

        try:
            self.browser.get(
                self._get_search_url(query)
            )
            results = self.parse_page_results(self.browser.page_source)
        except:
            results = []
            print("Errors while searching for \"", query, "\"")

        return results


class PagineGialleSearchBot(object):
    """ Selenium bot to search Google data """

    BROWSER_WAIT_TIMEOUT_SECONDS = 3

    def __init__(self, chromedriver_path):
        """
        :param chromedriver_path: str
            Path to Chrome driver to use as browser
        """

        object.__init__(self)
        self.browser = webdriver.Chrome(chromedriver_path)

    @staticmethod
    def _get_search_url(query, address):
        """
        :param query: str
            Words to search
        :param address: str
            Address of stuff to search
        :return: str
            Url of search page
        """

        return u"https://www.paginegialle.it/ricerca/" \
               + str(query).strip().replace(" ", "%20") + "/" + str(
            address).strip()

    @staticmethod
    def get_name(d):
        """ Return the name of a Pagine Gialle """

        try:
            data = d.find_all("div", {"class": "table"})[0].find_all("div", {
                "class": "elementRowL"})[0]  # table
            data = data.find_all("div", {"class": "elementTop"})[0]  # title
            data = data.find_all("span", {"class": "elementTitle"})[0]
            return data.text.strip()
        except:
            return None

    @staticmethod
    def get_address(d):
        """Return external link from a search."""

        try:
            data = d.find_all("div", {"class": "table"})[0].find_all("div", {
                "class": "elementRowL"})[0]  # table
            data = data.find_all("div", {"class": "elementBody"})[0]  # body
            data = \
                data.find_all("div", {"class": "elementAddress"})[0].find_all(
                    "div", {"itemprop": "address"})[0]
            return data.text.strip()
        except:
            return None

    @staticmethod
    def get_phone(d):
        """Return the description of a google search.
        TODO: There are some text encoding problems to resolve."""

        try:
            data = d.find_all("div", {"class": "table"})[0].find_all("div", {
                "class": "elementRowL"})[0]  # table
            data = data.find_all("div", {"class": "elementBody"})[0]  # body
            data = \
                data.find_all("div", {"class": "elementPhoneCont"})[
                    0].find_all(
                    "div", {"class": "elementPhone"})[0]
            return data.text.strip()
        except:
            return None

    @staticmethod
    def parse_page_results(html):
        """
        :return: [] of {}
            Each dict is a result of the query browser has just made
        """

        results = []
        soup = BeautifulSoup(html, "lxml")
        results_div = soup.find_all("div",
                                    {"class": "listElementsInnerWrapper"})
        if len(results_div) > 0:
            results_div = results_div[0]
            divs = results_div.find_all("div", {"class": "vcard"})
            for d in divs:
                results.append(
                    {
                        "name": PagineGialleSearchBot.get_name(d),
                        "address": PagineGialleSearchBot.get_address(d),
                        "telephone": PagineGialleSearchBot.get_phone(d)
                    }
                )

        return results

    def get_search_results(self, query, address):
        """
        :param query: str
            Words to search
        :param address: str
            Address of stuff to search
        :return: void
            Browser navigates to Google page, search query and returns list of results
        """

        try:
            self.browser.get(
                self._get_search_url(query, address)
            )
            WebDriverWait(self.browser,
                          self.BROWSER_WAIT_TIMEOUT_SECONDS).until(
                EC.presence_of_element_located((By.ID, "headSearchBar"))
            )  # wait until fully loaded
            results = self.parse_page_results(self.browser.page_source)
        except:
            results = []
            print("Errors while searching for \"", query, "\"")

        return results
