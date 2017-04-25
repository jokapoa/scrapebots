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
import os
import time

import aiohttp
from aiosocks.connector import ProxyConnector, ProxyClientRequest
from models import StreamsBot, AthletePerformance
from utils import get_time_eta, print_item_info, print_time_eta, print_debug_info


def create_args():
    """
    :return: ArgumentParser
        Parser that handles cmd arguments.
    """

    parser = argparse.ArgumentParser(usage="-f <path to input file>")
    parser.add_argument("-f", dest="file_path", help="e.g /home/awesome/data/data.csv", required=True)
    return parser


def parse_args(parser):
    """
    :param parser: ArgumentParser
        Object that holds cmd arguments.
    :return: tuple
        Values of arguments.
    """

    args = parser.parse_args()
    return str(args.file_path)


def check_args(file_path):
    """
    :param file_path: str
        File to use as output
    :return: bool
        True iff args are correct
    """

    assert os.path.exists(file_path)

    return True


async def fetch(u):
    try:
        conn = ProxyConnector(remote_resolve=True)
        async with aiohttp.ClientSession(connector=conn, request_class=ProxyClientRequest) as session:
            async with session.get(u, proxy="socks5://127.0.0.1:9150") as response:
                print_time_eta(
                    get_time_eta(
                        len(raw_sources),
                        total,
                        start_time
                    )  # get ETA
                )  # debug info

                body = await response.text()
                raw_sources.append(body)

                if response.status != 200:
                    print_debug_info([response.status, u])
                return body
    except Exception as e:
        print_debug_info([str(e), u])
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
    file_path = parse_args(create_args())
    if check_args(file_path):
        urls = StreamsBot(file_path).read_results_url_from_csv()  # parse file to get urls of results
        total = len(urls)
        start_time = int(time.time())  # get ms of day

        print("Fetching HTML pages")
        raw_sources = []  # list of raw HTML page sources
        loop = asyncio.get_event_loop()
        future = asyncio.ensure_future(fetch_urls(urls))  # fetch sources
        loop.run_until_complete(future)
        loop.close()

        print("Parsing HTML pages")
        print(len(raw_sources))
        details = []  # list of details
        start_time = int(time.time())  # get ms of day
        for r in raw_sources:
            athletic_performance = AthletePerformance(raw_html=r)
            athletic_performance.parse_details()
            d = athletic_performance.to_dict()
            details.append(d)  # add to list

            print_item_info(d)
            print_time_eta(
                get_time_eta(
                    len(details),
                    total,
                    start_time
                )  # get ETA
            )  # debug info

        out_path = os.path.join(os.path.dirname(file_path), "out-" + str(int(time.time())) + ".csv")
        StreamsBot(out_path).write_dicts_to_csv(details)  # save to output file
    else:
        print("Error while parsing args.")
