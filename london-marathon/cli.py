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

from models import StreamsBot, LondonMarathonBot


def create_args():
    """
    :return: ArgumentParser
        Parser that handles cmd arguments.
    """

    parser = argparse.ArgumentParser(usage="-y <years to fetch> -o <path to output file>")
    parser.add_argument("-y", dest="years", help="e.g '2017', '2014-2017', '2014,2016,2017'", required=False)
    parser.add_argument("-f", dest="file_path", help="e.g /home/awesome/data/out.csv", required=True)
    return parser


def parse_args(parser):
    """
    :param parser: ArgumentParser
        Object that holds cmd arguments.
    :return: tuple
        Values of arguments.
    """

    args = parser.parse_args()

    try:
        years = args.years
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

    return years, str(args.file_path)


def check_args(years, file_path):
    """
    :param years: [] of int
        List of years to fetch
    :param file_path: str
        File to use as output
    :return: bool
        True iff args are correct
    """

    if years is not None:
        assert (len(years) > 0)

    out_dir = os.path.dirname(file_path)
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)  # create necessary dir for output file

    return True


def main():
    years, file_path = parse_args(create_args())
    if check_args(years, file_path):
        if years is not None:
            bot = LondonMarathonBot()
            urls = bot.get_urls_of_years(years)
            bot = StreamsBot(file_path)
            bot.write_dict_to_csv(urls)
        else:
            urls = StreamsBot(file_path).read_results_url_from_csv()  # parse file to get urls of results
            details = LondonMarathonBot.get_performance_details(urls)  # get details of performances
            out_path = os.path.join(os.path.dirname(file_path),
                                    "out-" + str(int(time.time())) + ".csv")  # unique out file
            StreamsBot(out_path).write_dicts_to_csv(details)  # save to output file
    else:
        print("Error while parsing args.")


if __name__ == '__main__':
    main()
