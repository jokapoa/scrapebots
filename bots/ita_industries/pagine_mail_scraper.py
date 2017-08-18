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


""" Scrape www.paginemail.it data """

import asyncio
import os
import time

import aiohttp
from aiosocks.connector import ProxyConnector, ProxyClientRequest
from bs4 import BeautifulSoup
from hal.internet.web import Webpage
from hal.time.profile import print_time_eta, get_time_eta

SCRIPT_FOLDER = os.path.dirname(os.path.realpath(__file__))
SCRIPT_NAME = str(os.path.basename(__file__)).split(".")[0]
LOG_FILE = os.path.join(
    SCRIPT_FOLDER,
    SCRIPT_NAME + "-" + str(int(time.time())) + ".log"
)
OUTPUT_FILE = os.path.join(
    SCRIPT_FOLDER,
    SCRIPT_NAME + "-OUTPUT-" + str(int(time.time())) + ".csv"
)
INPUT_FILE = os.path.join(
    SCRIPT_FOLDER,
    "errors.csv"
)
START_PAGE = "https://www.paginemail.it/dir/r/veneto/20/treviso"  # url where to start scrape
BASE_URL = "https://www.paginemail.it"


async def try_and_fetch(u, max_attempts=8, time_delay_between_attempts=1):
    """
    :param u: str
        Url to fetch
    :param max_attempts: int
        Max number of attempts to get page
    :param time_delay_between_attempts: float
        Number of seconds to wait between 2 consecutive attempts
    :return: str
        Body of page with url or null
    """

    for _ in range(max_attempts):
        try:
            conn = ProxyConnector(remote_resolve=True)
            async with aiohttp.ClientSession(
                    connector=conn, request_class=ProxyClientRequest
            ) as session:
                async with session.get(
                        u, proxy="socks5://127.0.0.1:9150"
                ) as response:  # use tor
                    body = await response.text()  # encoding='latin-1'
                    raw_sources.append(body)  # add url and page source
                    print_time_eta(
                        get_time_eta(
                            len(raw_sources),
                            total,
                            start_time
                        ),  # get ETA
                        note="Fetched url"
                    )  # debug info
                    return body
        except Exception as e:
            time.sleep(time_delay_between_attempts)
            print("Cannot get url " + str(u))
            print(str(e))
    return None


async def bound_fetch(sem, url):
    async with sem:
        await try_and_fetch(url, max_attempts=3, time_delay_between_attempts=2)


async def async_fetch_urls(list_of_urls, max_concurrent=200):
    tasks = []
    sem = asyncio.Semaphore(max_concurrent)
    for u in list_of_urls:
        task = asyncio.ensure_future(bound_fetch(sem, u))
        tasks.append(task)

    responses = asyncio.gather(*tasks)
    await responses


def fetch_urls(list_of_urls):
    """
    :param list_of_urls: [] of str
        List of urls to fetch
    :return: void
        Append to list HTML content of each url
    """

    total = len(list_of_urls)
    start_time = time.time()
    for u in urls_list:
        raw_sources.append(
            Webpage(u).get_html_source(tor=True)
        )

        print_time_eta(
            get_time_eta(
                len(raw_sources),
                total,
                start_time
            ),  # get ETA
            note="Fetched url"
        )  # debug info


def get_urls_in_page(html):
    """
    :param html: str
        HTML content of page with <ul> element of class "clearfix" to scrape
    :return: [] of str
        List of urls found
    """

    soup = BeautifulSoup(html, "lxml")

    try:
        items_list = soup.find_all("table", {"id": "item"})[0]
        items = items_list.find_all("div", {"class": "leftSide"})
    except:
        try:
            items_list = soup.find_all("ul", {"class": "clearfix"})[0]
            items = items_list.find_all("li")
        except:
            return []

    try:
        urls = []
        for i in items:
            try:
                urls.append(
                    str(i.find_all("a")[0]["href"]).strip().replace("\\n", "")
                )
            except Exception as e:
                print("Cannot find url of div", str(i))
        return [
            str(BASE_URL + u) for u in urls
            ]  # add base url
    except:
        return []


def get_next_pages(html):
    """
    :param html: str
        HTML content of page with <ul> element of class "clearfix" to scrape
    :return: [] of str
        List of next pages urls
    """

    soup = BeautifulSoup(html, "lxml")
    try:
        pages_div = soup.find_all("div", {"class": "pagination"})[0]
        return [
            str(a["href"]).strip() for a in pages_div.find_all("a")
            ]
    except:
        return []


def write_list_to_csv(l, f):
    """
    :param l: []
        List
    :param f: str
        Path to output file
    :return: void
        Saves list data to output file (one for each line)
    """

    with open(f, "w") as o:
        o.write(
            "\n".join([str(x) for x in l])  # add new line at end of each line
        )


if __name__ == "__main__":
    start_page_html = Webpage(START_PAGE).get_html_source()  # get HTML content
    raw_sources = []  # list of scraped HTML pages content
    ind_urls_list = []  # list of urls of industries found
    urls_list = [str(l).strip() for l in
                 open(INPUT_FILE,
                      "r").readlines()]  # get_urls_in_page(start_page_html)  # first list of url to scrape

    total = len(urls_list)
    start_time = time.time()
    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(
        async_fetch_urls(urls_list))  # fetch sources
    loop.run_until_complete(future)
    urls_list = []  # empty urls list (all found)

    for h in raw_sources:
        ind_urls_list += get_urls_in_page(h)  # find items
        urls_list += get_next_pages(h)  # find next pages (if there are)

    raw_sources = []  # empty HTMLs list (all scraped)
    total = len(urls_list)
    start_time = time.time()
    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(
        async_fetch_urls(urls_list))  # fetch sources
    loop.run_until_complete(future)

    for h in raw_sources:
        ind_urls_list += get_urls_in_page(h)  # find items

    write_list_to_csv(ind_urls_list, OUTPUT_FILE + "-all.csv")
    write_list_to_csv(urls_list, OUTPUT_FILE + "-urls.csv")
