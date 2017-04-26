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


import csv
import string
import time

import pandas
from bs4 import BeautifulSoup
from selenium import webdriver
from utils import get_time_eta, print_time_eta, print_debug_info

VALUE_NOT_FOUND = str("DNF")
TOTAL_RUNNERS_IN_ONE_EVENT = 50000


def get_text_or_dnf(raw_html):
    """
    :param raw_html: str
        Raw HTML snippet to parse
    :return: str
        .text field or DNF value
    """

    try:
        return str(raw_html.text).strip()
    except:
        return VALUE_NOT_FOUND


class AthletePerformance(object):
    """ Models a performance in the marathon of an athlete """

    def __init__(self, raw_html):
        object.__init__(self)

        self.raw_html = raw_html

        self.first_name = VALUE_NOT_FOUND  # runner details
        self.last_name = VALUE_NOT_FOUND
        self.sex = VALUE_NOT_FOUND
        self.age = VALUE_NOT_FOUND
        self.nationality = VALUE_NOT_FOUND
        self.team = VALUE_NOT_FOUND
        self.state = VALUE_NOT_FOUND
        self.bib = VALUE_NOT_FOUND

        self.place = VALUE_NOT_FOUND  # standings
        self.place_gender = VALUE_NOT_FOUND
        self.place_age = VALUE_NOT_FOUND

        self.gun_time = VALUE_NOT_FOUND  # splits details
        self.net_time = VALUE_NOT_FOUND
        self.split_5K = VALUE_NOT_FOUND
        self.split_10K = VALUE_NOT_FOUND
        self.split_15K = VALUE_NOT_FOUND
        self.split_20K = VALUE_NOT_FOUND
        self.split_HALF = VALUE_NOT_FOUND
        self.split_25K = VALUE_NOT_FOUND
        self.split_30K = VALUE_NOT_FOUND
        self.split_35K = VALUE_NOT_FOUND
        self.split_40K = VALUE_NOT_FOUND

        self.age_graded_time = VALUE_NOT_FOUND  # performance
        self.age_graded_performance = VALUE_NOT_FOUND

    def parse_details(self, headers):
        """
        :param headers: [] of str
            Column names
        :return: void
           Parses webpage at url and saves details
        """

        soup = BeautifulSoup(self.raw_html, "lxml")  # HTML parser
        columns = soup.find_all("td")

        self.parse_runner_details(columns, headers)
        self.parse_standings_details(columns, headers)
        self.parse_splits_details(columns, headers)
        self.parse_performance_details(columns, headers)

    def parse_runner_details(self, columns, headers):
        """
        :param columns: [] of str
            List of raw HTML table columns with data
        :param headers: [] of str
            Column names
        :return: void
            Sets obj fields
        """

        try:
            self.first_name = get_text_or_dnf(columns[headers.index("First Name")])
        except:
            pass

        try:
            self.last_name = get_text_or_dnf(columns[headers.index("Last Name")])
        except:
            pass

        try:
            sex_age = str(columns[headers.index("Sex/Age")].text).strip()
            self.sex = sex_age[0]
            self.age = sex_age[1:]
        except:
            self.sex = VALUE_NOT_FOUND
            self.age = VALUE_NOT_FOUND

        try:
            self.bib = get_text_or_dnf(columns[headers.index("Bib")])
        except:
            pass

        try:
            self.team = get_text_or_dnf(columns[headers.index("Team")])
        except:
            pass

        try:
            self.state = get_text_or_dnf(columns[headers.index("State")])
        except:
            pass

        try:
            self.nationality = get_text_or_dnf(columns[headers.index("Citizenship")])
        except:
            pass

    def parse_standings_details(self, columns, headers):
        """
        :param columns: [] of str
            List of raw HTML table columns with data
        :param headers: [] of str
            Column names
        :return: void
            Sets obj fields
        """

        try:
            self.place = get_text_or_dnf(columns[headers.index("Place")])
        except:
            pass

        try:
            self.place_gender = get_text_or_dnf(columns[headers.index("GenderPlace")])
        except:
            pass

        try:
            self.place_age = get_text_or_dnf(columns[headers.index("AgePlace")])
        except:
            pass

    def parse_splits_details(self, columns, headers):
        """
        :param columns: [] of str
            List of raw HTML table columns with data
        :param headers: [] of str
            Column names
        :return: void
            Sets obj fields
        """

        try:
            self.gun_time = get_text_or_dnf(columns[headers.index("GunTime")])
        except:
            pass

        try:
            self.net_time = get_text_or_dnf(columns[headers.index("NetTime")])
        except:
            pass

        try:
            self.split_5K = get_text_or_dnf(columns[headers.index("5 km")])
        except:
            pass

        try:
            self.split_10K = get_text_or_dnf(columns[headers.index("10 km")])
        except:
            pass

        try:
            self.split_15K = get_text_or_dnf(columns[headers.index("15 km")])
        except:
            pass

        try:
            self.split_20K = get_text_or_dnf(columns[headers.index("20 km")])
        except:
            pass

        try:
            self.split_HALF = get_text_or_dnf(columns[headers.index("13.1 mi")])
        except:
            pass

        try:
            self.split_25K = get_text_or_dnf(columns[headers.index("25 km")])
        except:
            pass

        try:
            self.split_30K = get_text_or_dnf(columns[headers.index("30 km")])
        except:
            pass

        try:
            self.split_35K = get_text_or_dnf(columns[headers.index("35 km")])
        except:
            pass

        try:
            self.split_40K = get_text_or_dnf(columns[headers.index("40 km")])
        except:
            pass

    def parse_performance_details(self, columns, headers):
        """
        :param columns: [] of str
            List of raw HTML table columns with data
        :param headers: [] of str
            Column names
        :return: void
            Sets obj fields
        """

        try:
            self.age_graded_time = get_text_or_dnf(columns[headers.index("Age-GradedTime")])
        except:
            pass

        try:
            self.age_graded_performance = get_text_or_dnf(columns[headers.index("Age-GradedPerformance %")])
        except:
            pass

    def to_dict(self):
        """
        :return: dict
            Dictionary with keys (obj fields) and values (obj values)
        """

        return {
            "first_name": self.first_name,  # runner details
            "last_name": self.last_name,
            "sex": self.sex,
            "age": self.age,
            "nationality": self.nationality,
            "team": self.team,
            "state": self.state,
            "bib": self.bib,
            "place": self.place,  # standings
            "place_gender": self.place_gender,
            "place_age": self.place_age,
            "gun_time": self.gun_time,  # splits
            "net_time": self.net_time,
            "split_5K": self.split_5K,
            "split_10K": self.split_10K,
            "split_15K": self.split_15K,
            "split_20K": self.split_20K,
            "split_HALF": self.split_HALF,
            "split_25K": self.split_25K,
            "split_30K": self.split_30K,
            "split_35K": self.split_35K,
            "split_40K": self.split_40K,
            "age_graded_time": self.age_graded_time,  # performance
            "age_graded_performance": self.age_graded_performance,
        }


class NYCMarathonBot(object):
    """ Selenium bot for NYC Marathon website data """

    ARCHIVE_SEARCH_FORM_URL = "http://web2.nyrrc.org/cgi-bin/start.cgi/mar-programs/archive/archive_search.html"
    BROWSER_WAIT_TIMEOUT_SECONDS = 1

    def __init__(self):
        """
        :param chromedriver_path: str
            Path to Chrome driver to use as browser
        """

        object.__init__(self)
        self.browser = webdriver.Firefox()
        self.browser.set_page_load_timeout(self.BROWSER_WAIT_TIMEOUT_SECONDS)  # seconds

    def go_to_archive_search_form(self):
        """
        :return: void
            Browser navigates to form to choose parameters of search
        """

        try:
            self.browser.get(self.ARCHIVE_SEARCH_FORM_URL)
            time.sleep(self.BROWSER_WAIT_TIMEOUT_SECONDS)
        except:
            pass

    def go_to_first_page_of_archive(self, year):
        """
        :param year: int
            Year of marathon to get data about
        :return: void
            Browser navigates to first page of archive
        """

        self.go_to_archive_search_form()
        self.browser.execute_script(
            "document.getElementsByName(\"input.searchyear\")[0].value = \"" + str(year) + "\"")  # choose year

        self.browser.execute_script("document.getElementsByTagName(\"input\")[9].checked = true")  # check age method
        self.browser.execute_script("document.getElementsByName(\"input.f.age\")[0].value = \"0\"")  # choose min age
        self.browser.execute_script("document.getElementsByName(\"input.t.age\")[0].value = \"99\"")  # choose max age

        self.browser.execute_script("document.getElementsByTagName(\"form\")[0].submit()")  # submit form
        time.sleep(self.BROWSER_WAIT_TIMEOUT_SECONDS)

    def get_raw_data(self):
        """
        :return: str, int
            Raw HTML table in page with results, number of rows in table
        """

        try:
            page_source = str(self.browser.page_source)
            soup = BeautifulSoup(page_source, "lxml")  # html parser
            table = soup.find_all("table")[0]
            rows = table.find_all("tr")[1:]
            return str(table), len(rows)
        except:
            return "", 0

    def go_to_next_page_of_archive(self):
        """
        :return: bool
            True iff browser navigates correctly to next page of archive
        """

        try:
            has_next_page = self.browser.execute_script(
                "l = document.getElementsByName(\"submit\"); s = l[l.length - 1]; return s.value.includes(\"Next\")")
            if has_next_page:
                self.browser.execute_script(
                    "l = document.getElementsByName(\"submit\"); s = l[l.length - 1]; s.click()")  # go to next page
                time.sleep(self.BROWSER_WAIT_TIMEOUT_SECONDS)
                return True
            else:
                return False
        except:
            return False

    def get_data_tables_of_year(self, year):
        """
        :param year: int
            Year of marathon to get data about
        :return: [] of str
            List of raw HTML tablesof archive of year
        """

        list_tables = []  # list of raw table data of archive
        keep_going = True
        fetched_data_counter = 0  # counter of how many fetched pages
        self.go_to_first_page_of_archive(year)  # get first page of archive
        start_time = time.time()

        while keep_going:
            try:
                table_data, rows_counter = self.get_raw_data()
                list_tables.append(table_data)
                fetched_data_counter += rows_counter
                has_next_page = self.go_to_next_page_of_archive()
                keep_going = (rows_counter > 0 and has_next_page)

                print_time_eta(
                    get_time_eta(
                        fetched_data_counter, TOTAL_RUNNERS_IN_ONE_EVENT, start_time
                    )
                )  # debug info
            except Exception as e:
                print_debug_info(["\n\t!!!!!!!!!!!!!!!!!!!!\n\t", str(e), "\n\t!!!!!!!!!!!!!!!!!!!!\n\t\n"])
                keep_going = False

        self.browser.close()  # close browser
        self.browser.stop_client()
        self.browser.quit()

        return list_tables


class NYCMarathonParser(object):
    """ Parses raw NYC Marathon data """

    def __init__(self, data_table):
        """
        :param data_table: str
            Raw HTML table with results
        """

        object.__init__(self)
        self.data_table = data_table

    def get_results(self):
        """
        :return: [] of AthletePerformance
            Parses raw data and returns list of results
        """

        soup = BeautifulSoup(self.data_table, "lxml")  # html parser
        rows = soup.find_all("tr")[1:]  # discard headers
        headers = [h.text for h in soup.find_all("table")[0].find_all("tr")[0].find_all("td")]  # column names
        headers = [
            "".join(c for c in h if c in string.printable) for h in headers
            ]  # convert to unicode utf-8
        headers.insert(headers.index("Country ofResidence/Citizenship") + 1,
                       "Citizenship")  # add citizenship missing header

        results = []
        for r in rows:
            a = AthletePerformance(str(r))
            a.parse_details(headers)
            results.append(a)
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
