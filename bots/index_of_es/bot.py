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


""" Scrapes index-of.es web-page """

import urllib.parse

BASE_URL = "http://index-of.es/"


def get_links_in_page(web_page):
    """
    :param web_page: Webpage
        Webpage to scrape
    :return: [] of str
        List of urls to download found in page
    """

    web_page.get_html_source()  # get html page
    table = web_page.soup.find("pre")
    links = table.find_all("a")[4:]  # don't consider labels
    links = [
        str(link.text).strip() for link in links if len(link.text) > 2
        ]  # find only valid links
    links = [
        urllib.parse.urljoin(web_page.url, link.replace(" ", "%20"))
        for link in links
        ]  # add base url

    return links
