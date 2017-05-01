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
import os
import time
from datetime import datetime
from datetime import timedelta

import aiohttp
from aiosocks.connector import ProxyConnector, ProxyClientRequest
from hal.profile.mem import get_memory_usage, force_garbage_collect
from hal.time.profile import print_time_eta, get_time_eta
from parsers import get_runner_details_as_dict
from pymongo import MongoClient
from utils import append_to_file

BASE_URL = "http://statistik.d-u-v.org/"  # url of web-page
WEBPAGE_COOKIES = {
    "Language": "EN"
}  # set language
LOG_FILE = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                        "fetch_runners_database-" + str(int(time.time())) + ".log")  # path to log file
MIN_RUNNER_PAGE = 450000  # (1) minimum page where to find runner
MAX_RUNNER_PAGE = 600000  # (946958)  # maximum page where to find runner

DATABASE_NAME = "statistik-athletes"  # name of database to use
COLLECTIONS_KEY = "birth_year"
mongodb_client = MongoClient()  # mongodb client
# mongodb_client.drop_database(DATABASE_NAME)  # remove all previous data in database
db = mongodb_client[DATABASE_NAME]  # database to use
for c in db.collection_names():
    db[c].create_index("url", unique=True)  # set primary key


def get_url_of_page(p):
    """
    :param p: int
        Number of page to fetch
    :return: str
        Url of selected page
    """

    return BASE_URL + "getresultperson.php?runner=" + str(p)


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
                        ),  # get ETA
                        note="Got HTML"
                    )  # debug info
                    return body
        except:
            time.sleep(time_delay_between_attempts)
            append_to_file(LOG_FILE, "Cannot get url " + str(u))
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


if __name__ == "__main__":
    start_time_overall = time.time()

    urls_list = [get_url_of_page(p) for p in
                 range(MIN_RUNNER_PAGE, MAX_RUNNER_PAGE + 1)]  # get list of urls
    total = len(urls_list)
    raw_sources = []  # list of raw HTML pages to parse

    print("\tFetching HTML pages")
    start_time = time.time()
    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(fetch_urls(urls_list))  # fetch sources
    loop.run_until_complete(future)
    loop.close()

    print("\tGarbage-collecting useless stuff")
    urls_list = None  # free memory
    force_garbage_collect()
    total = len(raw_sources)

    print("\tParsing HTML pages")
    start_time = time.time()
    for i in range(len(raw_sources)):
        d = get_runner_details_as_dict(
            raw_sources[i]["html"],
            url=raw_sources[i]["url"],
            log_file=LOG_FILE
        )  # get details

        if d is not None:
            try:
                db[str(d[COLLECTIONS_KEY])].insert_one(d)
                raw_sources[i] = None  # release memory
            except Exception as e:
                if "duplicate key error" not in str(e):
                    append_to_file(LOG_FILE, str(e))

        print_time_eta(
            get_time_eta(
                i + 1,
                total,
                start_time
            ),  # get ETA
            note="Saved to database"
        )  # debug info

    mongodb_client.close()  # close mongodb connection

    end_time_overall = time.time()
    delta_time_overall = end_time_overall - start_time_overall
    delta_mem_overall = get_memory_usage()

    print(
        "Done fetching and saving data to mongodb database \"" + str(DATABASE_NAME) + "\". Job started at",
        datetime.fromtimestamp(start_time_overall).strftime("%Y-%m-%d %H:%M:%S"), "completed at",
        datetime.fromtimestamp(end_time_overall).strftime("%Y-%m-%d %H:%M:%S"), ", took",
        str(timedelta(seconds=int(delta_time_overall))), "and ~", str(delta_mem_overall), "MB to complete."
    )  # debug info
