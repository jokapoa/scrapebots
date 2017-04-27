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
import pandas as pd
from aiosocks.connector import ProxyConnector, ProxyClientRequest
from bs4 import BeautifulSoup
from hal.time.profile import print_time_eta, get_time_eta

VALUE_NOT_FOUND = "DNF"
BASE_URL = "http://statistik.d-u-v.org/"
WEBPAGE_COOKIES = {
    "Language": "EN"
}  # set language
LOG_FILE = os.path.join(os.path.dirname(os.path.realpath(__file__)), str(int(time.time())) + ".log")


def append_to_file(f, s):
    """
    :param f: str
        Path to file to append stuff to
    :param s: str
        Stuff to append
    :return: void
        Appends stuff to file
    """

    try:
        with open(f, "a") as o:
            o.write(str(s))
            o.write("\n")
    except Exception as e:
        print("Cannot append", str(s), "to", str(f))
        print(str(e))


def create_args():
    """
    :return: ArgumentParser
        Parser that handles cmd arguments.
    """

    parser = argparse.ArgumentParser(usage="-of <path to file with races urls>")
    parser.add_argument("-f", dest="path_file", help="path to input file", required=True)
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

    assert os.path.exists(path_file)
    return True


def get_races_from_file(path_file):
    """
    :param path_file: str
        File to parse
    :return: [] of {}
        List of races details in file
    """

    d = pd.read_csv(path_file).T.to_dict()
    return list(d.values())


def get_details_of_race_in_page(p):
    """
    :param p: str
        Raw HTML page with table with races list
    :return: {}, [] of {}
        List of race details, list of race results
    """

    soup = BeautifulSoup(str(p), "lxml")  # HTML parser
    rows = soup.find_all("table")[4].find_all("tr")  # rows of table
    headers = rows[0].find_all("th")  # column names
    headers = [str(h.text).strip() for h in headers]
    rows = rows[1:]  # discard header
    race_results = []
    for r in rows:
        d = {}  # values of row
        columns = r.find_all("td")
        for i in range(len(headers)):
            try:
                d[headers[i]] = str(columns[i].text).strip()
            except:
                d[headers[i]] = VALUE_NOT_FOUND
        race_results.append(d)

    rows = soup.find_all("table")[3].find_all("tr")  # rows with race details
    try:
        race_date = str(rows[0].find_all("td")[1].text).strip()
    except:
        race_date = VALUE_NOT_FOUND

    try:
        race_name = str(rows[1].find_all("td")[1].text).strip()
    except:
        race_name = VALUE_NOT_FOUND

    try:
        race_distance = str(rows[2].find_all("td")[1].text).strip()
    except:
        race_distance = VALUE_NOT_FOUND

    race_details = {
        "date": race_date,
        "name": race_name,
        "distance": race_distance
    }
    return race_details, race_results


async def fetch(u):
    try:
        conn = ProxyConnector(remote_resolve=True)
        async with aiohttp.ClientSession(connector=conn, request_class=ProxyClientRequest,
                                         cookies=WEBPAGE_COOKIES) as session:
            async with session.get(u, proxy="socks5://127.0.0.1:9150") as response:
                print_time_eta(
                    get_time_eta(
                        len(raw_sources),
                        total,
                        start_time
                    )  # get ETA
                )  # debug info

                body = await response.text()
                raw_sources.append(str(body))  # add url and page source

                if response.status != 200:
                    print(response.status, u)
                return body
    except Exception as e:
        print("\t!!!\tErrors with url", str(u))
        print(str(e))
        append_to_file(LOG_FILE, str(u))
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
    path_in = parse_args(create_args())
    if check_args(path_in):
        races_list = get_races_from_file(path_in)
        total = len(races_list)
        raw_sources = []  # list of raw HTML pages to parse
        pages_to_fetch = [r["url"] for r in races_list]  # urls of pages to fetch
        start_time = time.time()

        print("Fetching HTML pages")
        loop = asyncio.get_event_loop()
        future = asyncio.ensure_future(fetch_urls(pages_to_fetch))  # fetch sources
        loop.run_until_complete(future)
        loop.close()

        print("Parsing HTML pages")
        out_dir = os.path.join(os.path.dirname(path_in), "out-" + str(int(time.time())))
        os.makedirs(out_dir)  # prepare output directory
        for p in raw_sources:
            try:
                details, results = get_details_of_race_in_page(p)  # parse page
                file_name = details["date"] + "_" + details["name"] + "_" + details["distance"] + "_" + str(
                    int(time.time()))
                out_file = os.path.join(out_dir, file_name + ".csv")  # output file for this race
                keys = results[0].keys()
                with open(out_file, "w") as output_file:
                    dict_writer = csv.DictWriter(output_file, keys, quotechar="\"", delimiter=",")
                    dict_writer.writeheader()
                    dict_writer.writerows(results)
                print("Output data written to", out_file)
            except Exception as e:
                print("\t!!!\tErrors with page at index", str(raw_sources.index(p)))
                append_to_file(LOG_FILE, str(raw_sources.index(p)))
                print(str(e))
    else:
        print("Error while parsing args.")
