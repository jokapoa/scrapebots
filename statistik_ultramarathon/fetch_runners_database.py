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
import gc
import json
import os
import time
from datetime import datetime
from datetime import timedelta

import aiohttp
import psutil
from aiosocks.connector import ProxyConnector, ProxyClientRequest
from bs4 import BeautifulSoup
from hal.time.profile import print_time_eta, get_time_eta
from pymongo import MongoClient

VALUE_NOT_FOUND = str("DNF")
BASE_URL = "http://statistik.d-u-v.org/"
WEBPAGE_COOKIES = {
    "Language": "EN"
}  # set language
LOG_FILE = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                        "fetch_runners_database-" + str(int(time.time())) + ".log")
MIN_RUNNER_PAGE = 1  # (1) minimum page where to find runner
MAX_RUNNER_PAGE = 1000  # (946958)  # maximum page where to find runner
DATABASE_NAME = "statistik-athletes"


def get_memory_usage():
    """
    :return: float
        MB of memory used by this process
    """

    process = psutil.Process(os.getpid())
    m = process.memory_info().rss
    return m / (1024 * 1024)


def force_garbage_collect():
    """
    :return: void
        Releases memory used
    """

    gc.collect()


def get_url_of_page(p):
    """
    :param p: int
        Number of page to fetch
    :return: str
        Url of selected page
    """

    return BASE_URL + "getresultperson.php?runner=" + str(p)


def remove_all_malformed_unicode(s):
    """
    :param s: str
        Malformed unicode string
    :return: str
        Parsed string without unicode chars
    """

    o = str(s).strip()  # copy
    while o.find("\\") > 0:
        unicode_token = o[o.find("\\"): o.find("\\") + 4]  # find unicode char
        o = o.replace(unicode_token, "")  # replace
    return o.strip()


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


def get_runner_details(raw_html, url=None):
    """
    :param raw_html: str
        Raw HTML page with table with races list
    :param url: str
        Url of this page
    :return: {}
        List of runner details
    """

    soup = BeautifulSoup(str(raw_html), "lxml")  # HTML parser
    rows = soup.find_all("table")[2].find_all("tr")  # rows of table
    details = {}  # output dictionary

    try:
        details["name"] = remove_all_malformed_unicode(
            rows[0].find_all("td")[1].text.replace(",", "")
        )
    except:
        details["name"] = VALUE_NOT_FOUND

    try:
        details["club"] = remove_all_malformed_unicode(
            rows[1].find_all("td")[1].text.replace(",", "")
        )
    except:
        details["club"] = VALUE_NOT_FOUND

    try:
        details["residence"] = remove_all_malformed_unicode(
            rows[2].find_all("td")[1].text.replace(",", "")
        )
    except:
        details["residence"] = VALUE_NOT_FOUND

    try:
        details["birth_year"] = int(
            rows[3].find_all("td")[1].text
        )  # convert to int
    except:
        details["birth_year"] = VALUE_NOT_FOUND

    try:
        details["birth_date"] = datetime.strptime(
            rows[4].find_all("td")[1].text, "%d.%m.%Y"  # parse
        ).strftime("%Y/%m/%d")  # convert to USA format
    except:
        details["birth_date"] = VALUE_NOT_FOUND

    try:
        details["nationality"] = str(rows[5].find_all("td")[1].text).strip()
    except:
        details["nationality"] = VALUE_NOT_FOUND

    try:
        if url is not None:
            details["url"] = str(url).strip()
    except:
        details["url"] = VALUE_NOT_FOUND

    return details


def get_runner_results(raw_html):
    """
    :param raw_html: str
        Raw HTML page with table with races list
    :return: [] of {}
        List of runner results
    """

    soup = BeautifulSoup(str(raw_html), "lxml")  # HTML parser
    rows = soup.find_all("table")[4].find_all("tr")  # rows of table
    rows = [r for r in rows if len(r.find_all("td")) > 2]  # discard jibberish
    if len(rows) % 2 != 0:  # rows should be even
        rows = rows[:-1]  # remove last item
    rows = [BeautifulSoup(str(rows[i]) + str(rows[i + 1]), "lxml") for i in
            range(0, len(rows), 2)]  # merge following rows
    results = []
    for r in rows:
        try:
            race_details = {}  # race details
            columns = r.find_all("td")  # columns in table row

            try:
                race_details["date"] = str(columns[0].text).strip()
            except:
                race_details["date"] = VALUE_NOT_FOUND

            try:
                race_distance = str(columns[2].text).strip()
                if race_distance.find("km") > 0 or race_distance.find("mi") > 0:
                    race_details["distance"] = race_distance
                else:  # this is not a distance
                    race_details["time"] = race_distance
            except:
                race_details["distance"] = VALUE_NOT_FOUND

            try:
                race_time = str(columns[3].text).strip()
                if race_time.find("h") > 0 or race_time.find(":") > 0:
                    race_details["time"] = race_time
                else:  # this is not a time
                    race_details["distance"] = race_time
            except:
                race_details["time"] = VALUE_NOT_FOUND

            try:
                race_details["name"] = str(columns[1].text).strip()
            except:
                race_details["name"] = VALUE_NOT_FOUND

            try:
                race_details["url"] = BASE_URL + str(columns[1].a["href"])[2:-2]
            except:
                race_details["url"] = VALUE_NOT_FOUND

            try:
                race_details["place_overall"] = str(columns[6].text.split(":")[-1]).strip()
            except:
                race_details["place_overall"] = VALUE_NOT_FOUND

            try:
                race_details["place_overall"] = str(columns[7].text.split(":")[-1]).strip()
            except:
                race_details["place_overall"] = VALUE_NOT_FOUND

            try:
                race_details["place_overall"] = str(columns[8].text.split(":")[-1]).strip()
            except:
                race_details["place_overall"] = VALUE_NOT_FOUND

            results.append(race_details)
        except:
            pass

    return results


def get_details_of_runner_in_page(raw_html, url=None):
    """
    :param raw_html: str
        Raw HTML page with table with races list
    :param url: str
        Url of this page
    :return: {}, [] of {}
        List of runner details, list of runner results
    """

    details = get_runner_details(raw_html, url=url)
    try:
        results = get_runner_results(raw_html)
    except:
        results = []

    return details, results


def save_runner_details_to_file(raw_html, out_dir, url=None):
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
        details, results = get_details_of_runner_in_page(raw_html, url=url)  # parse page
        runner_out_dir = os.path.join(out_dir, details["birth_date"], details["nationality"],
                                      details["name"])  # specific folder for race
        if not os.path.exists(runner_out_dir):
            os.makedirs(runner_out_dir)  # prepare output directory

        out_file = os.path.join(runner_out_dir, "details.json")  # output file for details
        with open(out_file, "w", buffering=1) as o:  # use buffer
            json.dump(details, o, indent=4, sort_keys=True)
            o.flush()

        if len(results) > 1:
            out_file = os.path.join(runner_out_dir, "results.csv")  # output file for this runner
            keys = results[0].keys()
            with open(out_file, "w", buffering=1) as o:  # use buffer
                dict_writer = csv.DictWriter(o, keys, quotechar="\"", delimiter=",")
                dict_writer.writeheader()
                dict_writer.writerows(results)
                o.flush()

        print("Output data written to", runner_out_dir.replace(out_dir, ""))
    except Exception as e:
        print("\t!!!\tErrors parsing url", str(url))
        append_to_file(LOG_FILE, "Errors parsing url " + str(url))
        append_to_file(LOG_FILE, "\t" + str(e) + "\n")


def get_runner_details_as_dict(raw_html, url=None):
    """
    :param raw_html: str
        Raw HTML page with table with races list
    :param url: str
        Url of this page
    :return: {}
        Runner details as dict
    """

    try:
        details, results = get_details_of_runner_in_page(raw_html, url=url)  # parse page
        details["results"] = results  # add results to dict
        return details
    except Exception as e:
        print("\t!!!\tErrors getting json from url", str(url))
        append_to_file(LOG_FILE, "Errors getting json from url " + str(url))
        append_to_file(LOG_FILE, "\t" + str(e) + "\n")


def save_runner_details_to_db(raw_html, url=None):
    """
    :param raw_html: str
        Raw HTML page with table with races list
    :param url: str
        Url of this page
    :return: void
        Saves runner details to mongo db database
    """

    try:
        details = get_runner_details_as_dict(raw_html, url=url)  # get details
        db_table = str(details["birth_year"])  # db has tables for each year of runners
        if db[db_table].find(details).count() < 1:  # avoid duplicates
            db[db_table].insert_one(details)
    except Exception as e:
        print("\t!!!\tErrors saving url", str(url), "to db")
        append_to_file(LOG_FILE, "Errors saving url " + str(url) + " to db")
        append_to_file(LOG_FILE, "\t" + str(e) + "\n")


async def try_and_fetch(u, max_attempts=4, time_delay_between_attempts=0.5):
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
        await try_and_fetch(url)


async def fetch_urls(list_of_urls, max_concurrent=1000):
    tasks = []
    sem = asyncio.Semaphore(max_concurrent)
    for u in list_of_urls:
        task = asyncio.ensure_future(bound_fetch(sem, u))
        tasks.append(task)

    responses = asyncio.gather(*tasks)
    await responses


if __name__ == '__main__':
    start_time_overall = time.time()
    start_mem_overall = get_memory_usage()

    urls_list = [get_url_of_page(p) for p in
                 range(MIN_RUNNER_PAGE, MAX_RUNNER_PAGE + 1)]  # get list of urls
    total = len(urls_list)
    raw_sources = []  # list of raw HTML pages to parse

    print("Fetching HTML pages")
    start_time = time.time()
    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(fetch_urls(urls_list))  # fetch sources
    loop.run_until_complete(future)
    loop.close()

    urls_list = None  # free memory

    # initialize mongodb interface
    mongodb_client = MongoClient()  # mongodb client
    mongodb_client.drop_database("statistik-athletes")  # remove all previous data in database
    db = mongodb_client[DATABASE_NAME]  # database to use

    print("Fetched correctly", len(raw_sources), "urls")
    print("Saving databased with athletes details")
    start_time = time.time()
    for i in range(len(raw_sources)):
        page_source = raw_sources[i]["html"]
        save_runner_details_to_db(
            page_source,
            url=raw_sources[i]["url"]
        )
        print_time_eta(
            get_time_eta(
                i + 1,
                total,
                start_time
            )  # get ETA
        )  # debug info

        raw_sources[i] = None  # free memory
        force_garbage_collect()
        print("\tMemory used:", get_memory_usage(), "MB")

    mongodb_client.close()  # close mongodb connection

    end_time_overall = time.time()
    delta_time_overall = end_time_overall - start_time_overall
    end_mem_overall = get_memory_usage()
    delta_mem_overall = end_mem_overall - start_mem_overall

    print(
        "Done fetching", total, "runners details, saving", total,
        "runners data to mongodb database \"" + str(DATABASE_NAME) + "\". Job started at",
        datetime.fromtimestamp(start_time_overall).strftime("%Y-%m-%d %H:%M:%S"), "completed at",
        datetime.fromtimestamp(end_time_overall).strftime("%Y-%m-%d %H:%M:%S"), " and took",
        str(timedelta(seconds=int(delta_time_overall))), "and ~", str(delta_mem_overall), "MB to complete."
    )
