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


from datetime import datetime

from bs4 import BeautifulSoup
from hal.time.utils import get_seconds
from utils import append_to_file, VALUE_NOT_FOUND


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
    try:
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
                    time_performance = datetime.strptime(d["Performance"],
                                                         "%H:%M:%S h")
                    time_hours = get_seconds(
                        time_performance.strftime("%H:%M:%S")) / (
                                     60 * 60)  # hours of performance
                    speed_performance = float(d["Avg.Speed km/h"])
                    distance_performance = speed_performance * time_hours  # compute distance

                    d["Performance"] = time_performance.strftime("%H:%M:%S")
                    race_distance_km = "{0:.2f}".format(distance_performance)
                except:
                    pass

                race_results.append(d)
    except:
        pass

    rows = soup.find_all("table")[3].find_all("tr")  # rows with race details
    try:  # try parse race date
        race_date = str(rows[0].find_all("td")[1].text).strip()
        dates = race_date.split("-")  # in case of multiple dates
        if len(dates) > 1 and len(dates[0]) < len(dates[1]) - 2:
            race_date = dates[1]
        else:
            race_date = dates[0]
        race_date = datetime.strptime(race_date, "%d.%m.%Y").strftime(
            "%Y/%m/%d")
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


def get_runner_results(raw_html, base_url="http://statistik.d-u-v.org/"):
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
                if race_distance.find("km") > 0 or race_distance.find(
                        "mi") > 0:
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
                race_details["url"] = base_url + str(columns[1].a["href"])[
                                                 2:-2]
            except:
                race_details["url"] = VALUE_NOT_FOUND

            try:
                race_details["place_overall"] = str(
                    columns[6].text.split(":")[-1]).strip()
            except:
                race_details["place_overall"] = VALUE_NOT_FOUND

            try:
                race_details["place_overall"] = str(
                    columns[7].text.split(":")[-1]).strip()
            except:
                race_details["place_overall"] = VALUE_NOT_FOUND

            try:
                race_details["place_overall"] = str(
                    columns[8].text.split(":")[-1]).strip()
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


def get_runner_details_as_dict(raw_html, url=None, log_file=None):
    """
    :param raw_html: str
        Raw HTML page with table with races list
    :param url: str
        Url of this page
    :param log_file: str
        Path to log file
    :return: {}
        Runner details as dict
    """

    try:
        details, results = get_details_of_runner_in_page(raw_html,
                                                         url=url)  # parse page
        details["results"] = results  # add results to dict
        return details
    except:
        print("\t!!!\tErrors getting dict from url", str(url))
        if log_file is not None:
            append_to_file(log_file,
                           "Errors getting dict from url " + str(url))
        return None
