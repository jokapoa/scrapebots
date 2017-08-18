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


import argparse
import asyncio
import csv
import os
import time

import aiohttp
from aiosocks.connector import ProxyConnector, ProxyClientRequest
from bs4 import BeautifulSoup
from hal.time.profile import print_time_eta, get_time_eta

VALUE_NOT_FOUND = "DNF"
BASE_URL = "http://statistik.d-u-v.org/"


def get_url_of_page(p):
    """
    :param p: int
        Number of page to fetch
    :return: str
        Url of selected page
    """

    return BASE_URL + "geteventlist.php?year=all&dist=all&country=all&page=" + str(
        p)


def create_args():
    """
    :return: ArgumentParser
        Parser that handles cmd arguments.
    """

    parser = argparse.ArgumentParser(
        usage="-of <path to file to dump data to>")
    parser.add_argument("-f", dest="path_file", help="path to output file",
                        required=True)
    return parser


def parse_args(parser):
    """
    :param parser: ArgumentParser
        Object that holds cmd arguments.
    :return: tuple
        Values of arguments.
    """

    args = parser.parse_args()
    return str(args.path_file)


def check_args(path_file):
    """
    :param path_file: str
        File to parse
    :return: bool
        True iff args are correct
    """

    d = os.path.dirname(path_file)
    if not os.path.exists(d):  # create folders if necessary
        os.makedirs(d)

    return True


def get_list_of_races_in_page(p):
    """
    :param p: str
        Raw HTML page with table with races list
    :return: [] of {}
        List of races details in page
    """

    soup = BeautifulSoup(str(p), "lxml")  # HTML parser
    rows = soup.find_all("table")[4].find_all("tr")  # rows of table
    rows = [r for r in rows if len(r.find_all("td")) > 2]  # discard headers
    details = [
        {
            "date": str(r.find_all("td")[0].text).strip(),
            "url": BASE_URL + r.find_all("td")[1].a["href"],
            "distance": str(r.find_all("td")[2].text).strip(),
            "finishers": str(r.find_all("td")[3].text).strip()
        } for r in rows
        ]
    return details


def get_list_of_races(list_of_pages):
    """
    :param list_of_pages: [] of str
        List of raw HTML pages
    :return: [] of {}
        List of races details in page
    """

    details = []
    for p in list_of_pages:
        details += get_list_of_races_in_page(p)
    return details


async def fetch(u):
    try:
        conn = ProxyConnector(remote_resolve=True)
        async with aiohttp.ClientSession(connector=conn,
                                         request_class=ProxyClientRequest) as session:
            async with session.get(u,
                                   proxy="socks5://127.0.0.1:9150") as response:
                print_time_eta(
                    get_time_eta(
                        len(raw_sources),
                        total_pages,
                        start_time
                    )  # get ETA
                )  # debug info

                body = await response.text()
                raw_sources.append(str(body))  # add url and page source

                if response.status != 200:
                    print(response.status, u)
                return body
    except Exception as e:
        print(str(e))
        return ""


async def bound_fetch(sem, url):
    async with sem:
        await fetch(url)


async def fetch_urls(list_of_urls, max_concurrent=1000):
    tasks = []
    sem = asyncio.Semaphore(max_concurrent)
    for u in list_of_urls:
        task = asyncio.ensure_future(bound_fetch(sem, u))
        tasks.append(task)

    responses = asyncio.gather(*tasks)
    await responses


if __name__ == '__main__':
    path_out = parse_args(create_args())
    if check_args(path_out):
        raw_sources = []  # list of raw HTML pages to parse
        total_pages = 38
        pages_to_fetch = [get_url_of_page(p) for p in
                          range(1, total_pages + 1)]  # urls of pages to fetch
        start_time = time.time()

        print("Fetching HTML pages")
        loop = asyncio.get_event_loop()
        future = asyncio.ensure_future(
            fetch_urls(pages_to_fetch))  # fetch sources
        loop.run_until_complete(future)
        loop.close()

        print("Parsing HTML pages")
        details = get_list_of_races(raw_sources)

        keys = details[0].keys()
        with open(path_out, "w") as output_file:
            dict_writer = csv.DictWriter(output_file, keys, quotechar="\"",
                                         delimiter=",")
            dict_writer.writeheader()
            dict_writer.writerows(details)
        print("Output data written to", path_out)
    else:
        print("Error while parsing args.")
