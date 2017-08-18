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
from pymongo import MongoClient

from .parsers import get_url_of_page, get_list_of_stages, get_standings_of_stage, get_stage_details_from_url

LOG_FILE = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                        str(os.path.basename(__file__)).split(".")[0] + "-" + str(int(time.time())) + ".log")
MIN_YEAR_PAGE = 1903  # minimum year of tour
MAX_YEAR_PAGE = 2016  # maximum year of tour

DATABASE_NAME = "letour-stages"  # name of mongodb database to use
mongodb_client = MongoClient()  # mongodb client
# mongodb_client.drop_database(DATABASE_NAME)  # remove all previous data in database
db = mongodb_client[DATABASE_NAME]  # database to use (will have a coll for each year, each coll will have stages list)
for c in db.collection_names():
    db[c].create_index("num", unique=True)  # set primary key


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
            async with aiohttp.ClientSession(connector=conn, request_class=ProxyClientRequest) as session:
                async with session.get(u, proxy="socks5://127.0.0.1:9150") as response:  # use tor
                    body = await response.text(encoding='latin-1')
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
        except Exception as e:
            time.sleep(time_delay_between_attempts)
            import traceback
            traceback.print_exc()
            print("Cannot get url " + str(u))
            print(str(e))
    return None


async def bound_fetch(sem, url):
    async with sem:
        await try_and_fetch(url, max_attempts=1, time_delay_between_attempts=0)


async def fetch_urls(list_of_urls, max_concurrent=200):
    tasks = []
    sem = asyncio.Semaphore(max_concurrent)
    for u in list_of_urls:
        task = asyncio.ensure_future(bound_fetch(sem, u))
        tasks.append(task)

    responses = asyncio.gather(*tasks)
    await responses


if __name__ == "__main__":
    start_time_overall = time.time()

    print("\t0 - Getting URLs list")
    urls_list = [get_url_of_page(y) for y in
                 range(MIN_YEAR_PAGE, MAX_YEAR_PAGE + 1)]  # get list of urls
    total = len(urls_list)
    raw_sources = []  # list of raw HTML pages to parse

    print("\t1 - Downloading years pages")
    start_time = time.time()
    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(fetch_urls(urls_list))  # fetch sources
    loop.run_until_complete(future)

    print("\t2 - Getting list of all stages")
    start_time = time.time()
    urls_list = []
    total = len(raw_sources)
    for i in range(len(raw_sources)):
        urls_list += get_list_of_stages(
            raw_sources[i]["html"]
        )  # get list of stages in page
        print_time_eta(
            get_time_eta(
                i + 1,
                total,
                start_time
            ),  # get ETA
            note="Got stage list"
        )  # debug info

    print("\t3 - Downloading stages pages")
    raw_sources = []  # list of raw HTML pages to parse
    total = len(urls_list)

    start_time = time.time()
    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(fetch_urls(urls_list))  # fetch sources
    loop.run_until_complete(future)
    loop.close()

    print("\t4 - Garbage-collecting useless stuff")
    urls_list = None
    force_garbage_collect()

    print("\t5- Parsing stages pages")
    total = len(raw_sources)
    start_time = time.time()
    for i in range(len(raw_sources)):
        stage_standings = get_standings_of_stage(
            raw_sources[i]["html"]
        )
        stage_details = get_stage_details_from_url(raw_sources[i]["url"])
        d = {
            "num": stage_details["id"],
            "standings": stage_standings
        }

        try:
            db[str(stage_details["year"])].insert_one(d)
            raw_sources[i] = None  # release memory
        except Exception as e:
            print(str(e))

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
        "Done downloading and saving data to mongodb database \"" + str(DATABASE_NAME) + "\". Job started at",
        datetime.fromtimestamp(start_time_overall).strftime("%Y-%m-%d %H:%M:%S"), "completed at",
        datetime.fromtimestamp(end_time_overall).strftime("%Y-%m-%d %H:%M:%S"), ", took",
        str(timedelta(seconds=int(delta_time_overall))), "and ~", str(delta_mem_overall), "MB to complete."
    )  # debug info
