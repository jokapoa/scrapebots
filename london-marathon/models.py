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
import time

import pandas
import socks
from bs4 import BeautifulSoup
from hal.internet.web import Webpage

VALUE_NOT_FOUND = "DNF"


def get_time_to_go(total_done, total, start_time):
    """
    :param total_done: int
        Item processed
    :param total: int
        Total number of items to process
    :param start_time: time
        Time of start processing items
    :return: time
        Time to go
    """

    time_done = int(time.time()) - start_time
    speed = total_done / time_done
    total_to_go = total - total_done
    return total_to_go / speed


class AthletePerformance(object):
    """ Models a performance in the marathon of an athlete """

    def __init__(self, url=None, raw_html=None):
        object.__init__(self)

        self.url = url
        self.raw_html = raw_html

        self.event_id = str(VALUE_NOT_FOUND)  # event and runner details
        self.surname_name = str(VALUE_NOT_FOUND)
        self.nationality = str(VALUE_NOT_FOUND)
        self.club = str(VALUE_NOT_FOUND)
        self.category = str(VALUE_NOT_FOUND)
        self.bib = str(VALUE_NOT_FOUND)

        self.place_mv = str(VALUE_NOT_FOUND)  # standings
        self.place_ac = str(VALUE_NOT_FOUND)
        self.place_overall = str(VALUE_NOT_FOUND)
        self.finish_time = str(VALUE_NOT_FOUND)

        self.race_finished = str(VALUE_NOT_FOUND)  # finish time
        self.last_split = str(VALUE_NOT_FOUND)
        self.start_time = str(VALUE_NOT_FOUND)

        self.split_5K = str(VALUE_NOT_FOUND)  # splits details
        self.split_10K = str(VALUE_NOT_FOUND)
        self.split_15K = str(VALUE_NOT_FOUND)
        self.split_20K = str(VALUE_NOT_FOUND)
        self.split_HALF = str(VALUE_NOT_FOUND)
        self.split_25K = str(VALUE_NOT_FOUND)
        self.split_30K = str(VALUE_NOT_FOUND)
        self.split_35K = str(VALUE_NOT_FOUND)
        self.split_40K = str(VALUE_NOT_FOUND)
        self.split_MARATHON = str(VALUE_NOT_FOUND)

    def get_raw_html(self):
        """
        :return: void
            Fetches raw HTML source of page of performance
        """

        if self.raw_html is None:
            self.raw_html = Webpage(self.url).get_html_source(tor=True)  # get html source of url

    def parse_details(self):
        """
        :return: void
           Parses webpage at url and saves details
        """

        if self.url is None:
            self.event_id = str(VALUE_NOT_FOUND)
        else:
            self.event_id = self.url.split("&search_event=")[-1]

        self.get_raw_html()  # get HTML page source

        soup = BeautifulSoup(self.raw_html, "lxml")  # HTML parser
        details_tables = soup.find_all("table", {"class": "list-table names"})  # tables with details about competition

        try:
            self.parse_runner_details(details_tables[0])
        except:
            pass
        try:
            self.parse_standings_details(details_tables[1])
        except:
            pass

        try:
            self.parse_race_details(details_tables[2])
        except:
            pass

        try:
            self.parse_splits_details(details_tables[3])
        except:
            pass

    def parse_runner_details(self, raw_html):
        """
        :param raw_html: HTML soup
            HTML with table to parse
        :return: void
            Saves details
        """

        try:
            rows = raw_html.find_all("tr")  # table rows
        except:
            rows = []

        try:
            raw_name = rows[0].find_all("td")[-1].text
            surname_name = raw_name.split("(")[0].strip().replace(",", "")  # remove middle , to separate surname name
            nationality = raw_name.split("(")[-1].strip().replace(")", "")  # remove trailing )
            self.surname_name = str(surname_name).strip()
            self.nationality = str(nationality).strip()
        except:
            self.surname_name = str(VALUE_NOT_FOUND)
            self.nationality = str(VALUE_NOT_FOUND)

        try:
            self.club = str(rows[1].find_all("td")[-1].text).strip()
        except:
            self.club = str(VALUE_NOT_FOUND)

        try:
            self.category = str(rows[2].find_all("td")[-1].text).strip()
        except:
            self.category = str(VALUE_NOT_FOUND)

        try:
            self.bib = str(rows[3].find_all("td")[-1].text).strip()
        except:
            self.bib = str(VALUE_NOT_FOUND)

    def parse_standings_details(self, raw_html):
        """
        :param raw_html: HTML soup
            HTML with table to parse
        :return: void
            Saves details
        """

        try:
            rows = raw_html.find_all("tr")  # table rows
        except:
            rows = []

        try:
            self.place_mv = str(rows[0].find_all("td")[-1].text).strip()
        except:
            self.place_mv = str(VALUE_NOT_FOUND)

        try:
            self.place_ac = str(rows[1].find_all("td")[-1].text).strip()
        except:
            self.place_ac = str(VALUE_NOT_FOUND)

        try:
            self.place_overall = str(rows[2].find_all("td")[-1].text).strip()
        except:
            self.place_overall = str(VALUE_NOT_FOUND)

        try:
            self.finish_time = str(rows[3].find_all("td")[-1].text).strip()
        except:
            self.finish_time = str(VALUE_NOT_FOUND)

    def parse_race_details(self, raw_html):
        """
        :param raw_html: HTML soup
            HTML with table to parse
        :return: void
            Saves details
        """

        try:
            rows = raw_html.find_all("tr")  # table rows
        except:
            rows = []

        try:
            self.race_finished = str("Finished" == str(rows[0].find_all("td")[-1].text)).strip()
        except:
            self.place_mv = str(VALUE_NOT_FOUND)

        try:
            self.last_split = str(rows[1].find_all("td")[-1].text).strip()
        except:
            self.last_split = str(VALUE_NOT_FOUND)

        try:
            self.start_time = str(rows[2].find_all("td")[-1].text).strip()
        except:
            self.start_time = str(VALUE_NOT_FOUND)

    def parse_splits_details(self, raw_html):
        """
        :param raw_html: HTML soup
            HTML with table to parse
        :return: void
            Saves details
        """

        try:
            rows = raw_html.find_all("tr")  # table rows
        except:
            rows = []

        try:
            self.split_5K = str(rows[0].find_all("td")[2].text).strip()
        except:
            self.split_5K = str(VALUE_NOT_FOUND)

        try:
            self.split_10K = str(rows[1].find_all("td")[2].text).strip()
        except:
            self.split_10K = str(VALUE_NOT_FOUND)

        try:
            self.split_15K = str(rows[2].find_all("td")[2].text).strip()

        except:
            self.split_15K = str(VALUE_NOT_FOUND)

        try:
            self.split_20K = str(rows[3].find_all("td")[2].text).strip()
        except:
            self.split_20K = str(VALUE_NOT_FOUND)

        try:
            self.split_HALF = str(rows[4].find_all("td")[2].text).strip()
        except:
            self.split_HALF = str(VALUE_NOT_FOUND)

        try:
            self.split_25K = str(rows[5].find_all("td")[2].text).strip()
        except:
            self.split_25K = str(VALUE_NOT_FOUND)

        try:
            self.split_30K = str(rows[6].find_all("td")[2].text).strip()
        except:
            self.split_30K = str(VALUE_NOT_FOUND)

        try:
            self.split_35K = str(rows[7].find_all("td")[2].text).strip()
        except:
            self.split_35K = str(VALUE_NOT_FOUND)

        try:
            self.split_40K = str(rows[8].find_all("td")[2].text).strip()
        except:
            self.split_40K = str(VALUE_NOT_FOUND)

        try:
            self.split_MARATHON = str(rows[9].find_all("td")[2].text).strip()
        except:
            self.split_MARATHON = str(VALUE_NOT_FOUND)

    def to_dict(self):
        """
        :return: dict
            Dictionary with keys (obj fields) and values (obj values)
        """

        return {
            "event": self.event_id,  # event and runner details
            "name": self.surname_name,
            "nationality": self.nationality,
            "club": self.club,
            "category": self.category,
            "bib": self.bib,
            "place_mv": self.place_mv,  # standings
            "place_ac": self.place_ac,
            "place_overall": self.place_overall,
            "finish_time": self.finish_time,
            "race_finished": self.race_finished,  # finish time
            "last_split": self.last_split,
            "start_time": self.start_time,
            "split_5K": self.split_5K,  # splits details
            "split_10K": self.split_10K,
            "split_15K": self.split_15K,
            "split_20K": self.split_20K,
            "split_HALF": self.split_HALF,
            "split_25K": self.split_25K,
            "split_30K": self.split_30K,
            "split_35K": self.split_35K,
            "split_40K": self.split_40K,
            "split_MARATHON": self.split_MARATHON
        }


class LondonMarathonBot(object):
    """ Scraper of London Marathon data"""

    EVENTS = {
        "ELIT": "Elite",
        "MAS": "Club, Charity and Ballot",
        "VLMW": "VMLM Wheelchair (T53/T54)",
        "IPC": "World Para Athletics Marathon World Cup in association with the Virgin Money London Marathon",
        "IPCW": "World Para Athletics Marathon World Cup in association with the Virgin Money London Marathon (Wheelchair)"
    }

    def __init__(self):
        object.__init__(self)

    @staticmethod
    def get_url_of_year(year):
        """
        :param year: int
            Year
        :return: str
            Url with year data
        """

        return "http://results-" + str(year) + ".virginmoneylondonmarathon.com/" + str(year)

    @staticmethod
    def get_result_urls_from_page_source(page_source):
        """
        :param page_source: str
            Raw HTML source of results page
        :return: [] of str
            List of url of performances
        """

        results = []
        try:
            soup = BeautifulSoup(page_source, "lxml")  # HTML parser
            table = soup.find_all("div", {"class": "list"})[0]  # table with results
            table = table.find_all("table", {"class": "list-table"})[0]  # discard jibberish
            table_rows = table.find_all("tr")[1:]  # find rows of table (discard header)
            for row in table_rows:
                url = row.find_all("td")[3].a["href"]  # find url of result
                results.append(url)  # add url to results
        except:
            results = []

        return results

    def get_url_of_event_in_year(self, year, event_id, page=1):
        """
        :param page: int
            Page of results
        :param year: int
            Year
         :param event_id: str
            Event id (one of the keys of EVENTS)
        :return: str
            Url for data of specific event in that year
        """

        url = self.get_url_of_year(year)
        url += "?page=" + str(page)  # specify page
        url += "&event=" + str(event_id)  # specify event
        url += "&pid=search"  # search mode
        return url

    def get_urls_of_year(self, year):
        """
        :param year: int
            Year to get data of
        :return: [] of str
            List of url of results of year
        """

        data = []
        for e in self.EVENTS.keys():
            page = 1
            keep_getting_data = True  # flag for when to stop
            while keep_getting_data:
                base_url = self.get_url_of_year(year)
                url = self.get_url_of_event_in_year(year, e, page=page)  # url to scrape data
                page_source = Webpage(url).get_html_source()  # get raw HTML
                results = self.get_result_urls_from_page_source(page_source)
                results = [base_url + str(r).strip() for r in results]  # add base url (to relative result)
                data += results  # add results
                keep_getting_data = (len(results) > 0)  # go to next page if there is data on this page
                page += 1

                print(str(len(results)), "results from", str(e), str(year), "event (page",
                      str(page - 1) + ")")  # debug info

        return data

    def get_urls_of_years(self, years):
        """
        :param years: [] of int
            Years to get data of
        :return: {} of [] of str
            Each key of the dictionary has the year, each value has the results of that year
        """

        db_years = {}
        for year in years:
            db_years[str(year)] = self.get_urls_of_year(year)  # add data of year
        return db_years

    @staticmethod
    def get_performances_details(urls):
        """
        :param urls: [] of str
            List of url of results of year
        :return: [] of {}
            Parses performances and returns list of details
        """

        o = []
        for u in urls:
            result = AthletePerformance(u)
            result.parse_details()  # parse
            o.append(
                result.to_dict()
            )  # add to dict
            print("Parsed", len(o), "/", len(urls))  # debug info
        return o

    @staticmethod
    def async_get_performance_details(urls):
        """
        :return: [] of {}
            List of each athlete performance
        """

        results = []
        start_time = int(time.time())  # get ms of day
        total = len(urls)
        socks.setdefaultproxy(proxy_type=socks.PROXY_TYPE_SOCKS5, addr="127.0.0.1", port=9050)  # force TOR way

        @asyncio.coroutine
        def async_get_performance_details_from_url(u):
            result = AthletePerformance(url=u)
            result.parse_details()  # get details
            results.append(result.to_dict())  # add to list of results

            time_now = int(time.time())
            time_to_go = get_time_to_go(
                len(results),
                total,
                start_time
            )
            print("Got", str(len(results)), "athletes at", str(time_now), "ETA (h):",
                  str(time_to_go / (60 * 60)))  # debug info

        loop = asyncio.get_event_loop()
        task = asyncio.ensure_future(
            asyncio.gather(
                *(async_get_performance_details_from_url(u) for u in urls)
            )
        )
        loop.run_until_complete(task)
        loop.close()

        return results


class StreamsBot(object):
    """ I/O on (generally) files with data about the London Marathon"""

    def __init__(self, file_path):
        object.__init__(self)

        self.file_path = file_path

    def write_dict_to_csv(self, d):
        """
        :param d: {}
            Dict to write to csv
        :return: void
            Writes dict to csv
        """

        df = pandas.DataFrame.from_dict(d)
        df.to_csv(self.file_path, sep=",", quotechar="\"")

    def read_results_url_from_csv(self):
        """
        :return: [] of str
            Reads from .csv file and returns list of url of results of year
        """

        d = pandas.DataFrame.from_csv(self.file_path, sep=",").to_dict()  # turn file into dict
        big_dict = list(d.values())[0]  # get raw values (big dataframe dictionary <i, value>
        values = [str(v).strip() for v in big_dict.values()]  # get real value
        return values

    def write_dicts_to_csv(self, dicts):
        """
        :param dicts: [] of {}
            Dictionaries with same values
        :return: void
            Saves .csv file with posts data
        """

        csv_headers = dicts[0].keys()
        with open(self.file_path, "w") as o:  # write to file
            dict_writer = csv.DictWriter(o, csv_headers, delimiter=",", quotechar="\"")
            dict_writer.writeheader()
            dict_writer.writerows(dicts)
