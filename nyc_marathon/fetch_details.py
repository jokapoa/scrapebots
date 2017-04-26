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
import time

from models import NYCMarathonBot, NYCMarathonParser, StreamsBot


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

    bot = NYCMarathonBot()  # build bot to scrape data
    data_tables = bot.get_data_tables_of_year(year)  # fetch data

    data = []
    for t in data_tables:  # parse data
        data_table = NYCMarathonParser(t)
        results = data_table.get_results()
        data += results

    csv_details = [d.to_dict() for d in data]  # convert to dict
    out_file = os.path.join(
        out_path,
        str(year) + "_" + str(int(time.time())) + ".csv"
    )
    StreamsBot(out_file).write_dicts_to_csv(csv_details)  # save to output file
    print("Results saved to", out_file)


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
