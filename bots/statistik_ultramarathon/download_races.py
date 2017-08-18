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


import asyncio
import csv
import json
import os
import time

import aiohttp
from aiosocks.connector import ProxyConnector, ProxyClientRequest
from hal.time.profile import print_time_eta, get_time_eta
from parsers import get_details_of_race_in_page
from utils import append_to_file

VALUE_NOT_FOUND = str("DNF")
BASE_URL = "http://statistik.d-u-v.org/"
WEBPAGE_COOKIES = {
    "Language": "EN"
}  # set language
LOG_FILE = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                        str(os.path.basename(__file__)) + str(int(time.time())) + ".log")


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
        race_out_dir = os.path.join(out_dir, details["name"], details["distance"],
                                    details["date"].replace("/", "-"))  # specific folder for race
        if not os.path.exists(race_out_dir):
            os.makedirs(race_out_dir)  # prepare output directory

        out_file = os.path.join(race_out_dir, "results.csv")  # output file for this race
        if len(results) > 1:
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
        print(str(e))
        append_to_file(LOG_FILE, "Errors parsing url " + str(url))


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
            async with aiohttp.ClientSession(connector=conn, request_class=ProxyClientRequest,
                                             cookies=WEBPAGE_COOKIES) as session:
                async with session.get(u, proxy="socks5://127.0.0.1:9150") as response:
                    body = await response.text()
                    raw_sources.append({
                        "url": str(u),
                        "html": str(body)
                    })  # add url and page source

                    print_time_eta(
                        get_time_eta(
                            len(raw_sources),
                            total,
                            start_time
                        )  # get ETA
                    )  # debug info
                    return body
        except:
            time.sleep(time_delay_between_attempts)
    return None


async def bound_fetch(sem, url):
    async with sem:
        await try_and_fetch(url, max_attempts=1, time_delay_between_attempts=0)


async def fetch_urls(list_of_urls, max_concurrent=1000):
    tasks = []
    sem = asyncio.Semaphore(max_concurrent)
    for u in list_of_urls:
        task = asyncio.ensure_future(bound_fetch(sem, u))
        tasks.append(task)

    responses = asyncio.gather(*tasks)
    await responses


if __name__ == '__main__':
    output_dir = "/home/stefano/Coding/Data/projects/galore/running/ultramarathon/races/statistik-races/races_details"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    pages_to_fetch = []  # [r["url"] for r in races_list]  # urls of pages to fetch
    list_of_urls_file = "/home/stefano/Coding/Python/projects/scrapebots/statistik_ultramarathon/errors_races.log"
    with open(list_of_urls_file, "r") as i:
        lines = i.readlines()
        lines = [str(l).strip() for l in lines]
        pages_to_fetch = lines
    raw_sources = []  # list of raw HTML pages to parse

    print("Fetching HTML pages")
    start_time = time.time()
    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(fetch_urls(pages_to_fetch))  # fetch sources
    loop.run_until_complete(future)
    loop.close()

    print("Saving races results")
    start_time = time.time()
    saved_races = 0  # counter of how many races have been saved
    total = len(raw_sources)
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
