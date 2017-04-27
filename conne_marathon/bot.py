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
import os

from bs4 import BeautifulSoup
from hal.internet.web import Webpage, download_pdf_to_file

RESULTS_PAGE_URL = "http://www.connemarathon.com/results/"
MIN_YEAR = 2002


def create_args():
    """
    :return: ArgumentParser
        Parser that handles cmd arguments.
    """

    parser = argparse.ArgumentParser(usage="-y <years to fetch> -o <path to output folder>")
    parser.add_argument("-y", dest="years", help="e.g '2017', '2014-2017', '2014,2016,2017'", required=True)
    parser.add_argument("-o", dest="path_out", help="path to output folder", required=True)
    return parser


def parse_args(parser):
    """
    :param parser: ArgumentParser
        Object that holds cmd arguments.
    :return: tuple
        Values of arguments.
    """

    args = parser.parse_args()

    years = args.years
    try:
        if years.find(",") > 0:  # multiple years
            years = years.split(",")  # tokenize
            years = [str(y).strip() for y in years if len(y) >= 4]  # strip and discard null values
            years = [int(y) for y in years]  # parse
        elif years.find("-") > 0:  # years range
            min_year = int(years.split("-")[0])
            max_year = int(years.split("-")[-1])
            years = list(range(min_year, max_year + 1))
        else:
            years = [int(str(years).strip())]
    except:
        years = None

    return years, str(args.path_out)


def check_args(years, path_out):
    """
    :param years: [] of int
        List of years to fetch
    :param path_out: str
        File to use as output
    :return: bool
        True iff args are correct
    """

    assert (years is not None)
    assert (len(years) > 0)

    out_dir = os.path.dirname(path_out)
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)  # create necessary dir for output file

    return True


def download_year_results(year, out_path):
    """
    :param year: int
        Year of marathon to get data about
    :param out_path: str
        Path where save data to
    :return: void
        Saves data to file
    """

    w = Webpage(RESULTS_PAGE_URL)
    soup = BeautifulSoup(w.get_html_source(), "lxml")
    table = soup.find_all("table")[0]
    rows = table.find_all("tr")[1:]  # discard header
    rows.reverse()  # start from min year to present
    row_of_year = rows[year - MIN_YEAR]  # row where to find results of given year
    columns = row_of_year.find_all("td")
    for c in columns:
        try:
            link = c.a["href"]
            file_name = link.split("/")[-1]
            out_file = os.path.join(out_path, file_name)
            download_pdf_to_file(link, out_file)  # download
        except Exception as e:  # column has no link
            print(str(e))


def download_years_results(years, out_path):
    """
    :param years: [] of int
        Years of marathon to get data about
    :param out_path: str
        Path where save data to
    :return: void
        Saves data to file
    """

    for y in years:
        download_year_results(y, out_path)


def download_results_in_range(min_y, max_y, out_path):
    """
    :param min_y: int
        Min year of marathon to get data about
    :param max_y: int
        Min year of marathon to get data about
    :param out_path: str
        Path where save data to
    :return: void
        Saves data to file
    """

    for y in range(min_y, max_y + 1):
        download_year_results(y, out_path)


def main():
    years, path_out = parse_args(create_args())
    if check_args(years, path_out):
        download_years_results(years, path_out)
    else:
        print("Error while parsing args.")


if __name__ == '__main__':
    main()
