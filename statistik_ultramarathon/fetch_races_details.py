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
import json
import os
import time
from datetime import datetime

import aiohttp
import pandas as pd
from aiosocks.connector import ProxyConnector, ProxyClientRequest
from bs4 import BeautifulSoup
from hal.time.profile import print_time_eta, get_time_eta
from hal.time.utils import get_seconds

VALUE_NOT_FOUND = str("DNF")
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


def get_details_of_race_in_page(raw_html, url=None):
    """
    :param raw_html: str
        Raw HTML page with table with races list
    :param url: str
        Url of this page
    :return: {}, [] of {}
        List of race details, list of race results
    """

    race_results = []
    race_distance_km = VALUE_NOT_FOUND  # distance of race in km
    soup = BeautifulSoup(str(raw_html), "lxml")  # HTML parser
    rows = soup.find_all("table")[4].find_all("tr")  # rows of table
    headers = rows[0].find_all("th")  # column names
    headers = [str(h.text).strip() for h in headers]
    if len(rows) > 1:
        rows = rows[1:]  # discard header
        for r in rows:
            d = {}  # values of row
            columns = r.find_all("td")
            for i in range(len(headers)):
                try:
                    d[headers[i]] = str(columns[i].text).strip()
                except:
                    d[headers[i]] = VALUE_NOT_FOUND

            try:  # try parse performance time and compute distance
                time_performance = datetime.strptime(d["Performance"], "%H:%M:%S h")
                time_hours = get_seconds(time_performance.strftime("%H:%M:%S")) / (60 * 60)  # hours of performance
                speed_performance = float(d["Avg.Speed km/h"])
                distance_performance = speed_performance * time_hours  # compute distance

                d["Performance"] = time_performance.strftime("%H:%M:%S")
                race_distance_km = "{0:.2f}".format(distance_performance)
            except:
                pass

            race_results.append(d)

    rows = soup.find_all("table")[3].find_all("tr")  # rows with race details
    try:  # try parse race date
        race_date = str(rows[0].find_all("td")[1].text).strip()
        dates = race_date.split("-")  # in case of multiple dates
        if len(dates) > 1 and len(dates[0]) < len(dates[1]) - 2:
            race_date = dates[1]
        else:
            race_date = dates[0]
        race_date = datetime.strptime(race_date, "%d.%m.%Y").strftime("%Y/%m/%d")
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

    if url is None:
        race_url = VALUE_NOT_FOUND
    else:
        try:
            race_url = str(url).strip()
        except:
            race_url = VALUE_NOT_FOUND

    race_details = {
        "date": race_date,
        "name": race_name,
        "distance": race_distance,
        "km": race_distance_km,
        "url": race_url
    }
    return race_details, race_results


def save_race_details_to_file(raw_html, out_dir, url=None):
    """
    :param raw_html: str
        Raw HTML page with race details
    :param out_dir: str
        Path to output folder
    :param url: str
        Url of this page
    :return: void
        Parses race details from HTML page, then saves results to folder
    """

    try:
        details, results = get_details_of_race_in_page(raw_html, url=url)  # parse page
        race_out_dir = os.path.join(out_dir, details["name"], details["distance"])  # specific folder for race
        if not os.path.exists(race_out_dir):
            os.makedirs(race_out_dir)  # prepare output directory

        out_file = os.path.join(race_out_dir, details["date"].replace("/", "-") + ".csv")  # output file for this race
        keys = results[0].keys()
        with open(out_file, "w") as output_file:  # write race results (standings)
            dict_writer = csv.DictWriter(output_file, keys, quotechar="\"", delimiter=",")
            dict_writer.writeheader()
            dict_writer.writerows(results)

        out_file_details = os.path.join(race_out_dir, "details.json")  # output file for details
        with open(out_file_details, "w") as o:  # write race details
            json.dump(details, o, indent=4, sort_keys=True)

        print("Output data written to", out_file)
    except Exception as e:
        print("\t!!!\tErrors parsing url", str(url))
        append_to_file(LOG_FILE, "Errors parsing url " + str(url))
        append_to_file(LOG_FILE, "\t" + str(e) + "\n")


async def fetch(u):
    try:
        conn = ProxyConnector(remote_resolve=True)
        async with aiohttp.ClientSession(connector=conn, request_class=ProxyClientRequest,
                                         cookies=WEBPAGE_COOKIES) as session:
            async with session.get(u, proxy="socks5://127.0.0.1:9150") as response:
                body = await response.text()
                raw_sources.append({
                    "url": str(u),
                    "html": str(body)
                })  # add url and page source

                if response.status != 200:
                    print(response.status, u)

                print_time_eta(
                    get_time_eta(
                        len(raw_sources),
                        total,
                        start_time
                    )  # get ETA
                )  # debug info
                return body
    except Exception as e:
        print("\t!!!\tErrors fetching url", str(u))
        append_to_file(LOG_FILE, "Errors fetching url " + str(u))
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
        output_dir = os.path.join(os.path.dirname(path_in), "out-" + str(int(time.time())))  # output directory
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)  # prepare output directory

        races_list = get_races_from_file(path_in)  # get list of races from input file
        total = len(races_list)
        raw_sources = []  # list of raw HTML pages to parse
        pages_to_fetch = [r["url"] for r in races_list]  # urls of pages to fetch

        print("Fetching HTML pages")
        start_time = time.time()
        loop = asyncio.get_event_loop()
        future = asyncio.ensure_future(fetch_urls(pages_to_fetch))  # fetch sources
        loop.run_until_complete(future)
        loop.close()

        print("Saving races results")
        start_time = time.time()
        saved_races = 0  # counter of how many races have been saved
        for k in raw_sources:
            page_source = k["html"]
            save_race_details_to_file(page_source, output_dir, url=k["url"])
            saved_races += 1
            print_time_eta(
                get_time_eta(
                    saved_races,
                    total,
                    start_time
                )  # get ETA
            )  # debug info
    else:
        print("Error while parsing args.")
