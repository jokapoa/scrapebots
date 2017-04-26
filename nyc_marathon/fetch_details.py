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

from models import download_year_results


def create_args():
    """
    :return: ArgumentParser
        Parser that handles cmd arguments.
    """

    parser = argparse.ArgumentParser(usage="-c <path to chromedriver> -o <path to output file>")
    parser.add_argument("-c", dest="path_chromedriver", help="path to chromedriver to use", required=True)
    parser.add_argument("-o", dest="path_out", help="path to output file", required=True)
    return parser


def parse_args(parser):
    """
    :param parser: ArgumentParser
        Object that holds cmd arguments.
    :return: tuple
        Values of arguments.
    """

    args = parser.parse_args()
    return str(args.path_chromedriver), str(args.path_out)


def check_args(path_chromedriver, path_out):
    """
    :param path_chromedriver: str
        Path to chromedriver
    :param path_out: str
        File to use as output
    :return: bool
        True iff args are correct
    """

    assert os.path.exists(path_chromedriver)

    out_dir = os.path.dirname(path_out)
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)  # create necessary dir for output file

    return True


def main():
    path_chromedriver, path_out = parse_args(create_args())
    if check_args(path_chromedriver, path_out):
        download_year_results(1970, path_chromedriver, path_out)
    else:
        print("Error while parsing args.")


if __name__ == '__main__':
    main()
