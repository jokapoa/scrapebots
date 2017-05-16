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


from collections import Counter
from urllib.parse import urlencode

from selenium import webdriver


def tops(lst):
    return Counter(lst)


def get_tops(lst, key, top=3):
    """
    :param lst: [] of {}
        List of dicts
    :param key: str
        Key to filter on
    :param top: int
        How many top elements to get
    :return: []
        List of top values
    """

    try:
        candidates = []
        for c in lst:
            candidates += c[key]
        top_list = tops(candidates).most_common(top)
        return [t[0] for t in top_list]
    except:
        return candidates


class ContactsScrapeBot(object):
    """ Selenium bot to scrape contacts data """

    def __init__(self, chromedriver_path):
        """
        :param chromedriver_path: str
            Path to chrome driver to use as browser
        """

        object.__init__(self)
        self.browser = webdriver.Chrome(chromedriver_path)

    @staticmethod
    def _get_search_url(query, page=0, per_page=10, lang="en"):
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

    def parse_page_infos(self, html):
        """
        :param html: str
            Raw HTML page source to scrape
        :return: {} of [] of str
            Each value is all phones (and emails) numbers found in page
        """

        return {
            "tel": None,
            "email": None
        }  # TODO

    def get_possible_info_pages(self, html):
        """
        :param html: str
            Raw HTML page source to scrape
        :return: [] of str
            List of other urls where to scrape infos
        """

        return []  # TODO

    def get_contacts(self, url):
        """
        :param url: str
            Url of page to scrape
        :return: void
            Browser navigates to page, searches info
        """

        try:
            self.browser.get(url)
            possible_info_pages = self.get_possible_info_pages(
                self.browser.page_source)  # list of other urls where to scrape infos
            possible_info_pages.append(url)
            results = []
            for u in possible_info_pages:
                try:
                    self.browser.get(u)
                    result = self.parse_page_infos(self.browser.page_source)
                    if result:
                        results.append(result)
                except:
                    pass

            return {
                "tel": get_tops(results, "tel", 2),
                "email": get_tops(results, "email", 2)
            }  # return only most probable items
        except:
            results = []
            print("Errors while scraping \"", url, "\"")

        return results
