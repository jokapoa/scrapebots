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

import pandas as pd
from hal.files.models import Document

VALUE_NOT_FOUND = "DNF"


def create_args():
    """
    :return: ArgumentParser
        Parser that handles cmd arguments.
    """

    parser = argparse.ArgumentParser(usage="-of <path to file to parse>")
    parser.add_argument("-f", dest="path_file", help="path to file", required=True)
    return parser


def parse_args(parser):
    """
    :param parser: ArgumentParser
        Object that holds cmd arguments.
    :return: tuple
        Values of arguments.
    """

    args = parser.parse_args()
    return str(args.path_file)


def check_args(path_file):
    """
    :param path_file: str
        File to parse
    :return: bool
        True iff args are correct
    """

    assert os.path.exists(path_file)
    return True


def get_tokens(l):
    """
    :param l: str
        Line of file to parse
    :return: [] of str
        Tokens of line
    """

    tokens = l.strip().split(" ")
    tokens = [t.strip() for t in tokens if len(t) > 0]
    return tokens


def fix_line(l):
    """
    :param l: [] of str
        Tokens of line
    :return: [] of str
        Tokens of line
    """

    for i in range(len(l)):
        if l[i].find(" ") > 0 and l[i][0].isdigit():  # there is some number jammed up with some words
            tokens = l[i].split(" ")
            n = tokens[0].strip()  # number
            t = " ".join(tokens[1:]).strip()  # words
            l[i] = n
            l.insert(i + 1, t)
    return l


def fix_headers(h):
    """
    :param h: [] of str
        Tokens of headers
    :return: [] of str
        Tokens of headers
    """

    headers = []
    for x in h:
        headers += x.split(" ")
    return headers


def parse_file(path_file):
    """
    :param path_file: str
        File to parse
    :return: [] of str, [] of [] of str
        Column names, matrix of data in file
    """

    with open(path_file, "r") as i:  # read all lines in file
        lines = i.readlines()

    if len(lines) > 0:
        lines = [get_tokens(l) for l in lines if len(l) > 2]  # parse each line
        headers = fix_headers(lines[0])

        lines = lines[1:]
        lines = [l for l in lines if len(l) > 4 and (l[-2].find(":") > 0 or l[-1].find(":") > 0)]

        return headers, lines
    else:
        return None, None


def parse_and_save_file(path_file):
    """
    :param path_file: str
        File to parse
    :return: void
        Parses raw file, then saves results
    """

    h, d = parse_file(path_file)
    if h is not None and d is not None:
        file_name_tokens = Document(path_file).name.split("-")
        file_name = file_name_tokens[0] + "_" + file_name_tokens[1].split(".")[0] + ".csv"
        out_file = os.path.join(os.path.dirname(path_file), file_name)

        for i in range(len(d)):
            if len(h) == len(d[i]) - 1:
                d[i][2] += d[i][3]
                del d[i][3]

            if len(h) == len(d[i]) and d[i][-1].find(":") > 0:  # it's a time
                d[i][2] += d[i][3]
                del d[i][3]

            if len(d[i]) < len(h):
                d[i].insert(4, VALUE_NOT_FOUND)

            while len(d[i]) > len(h) and len(d[i]) > 4:
                del d[i][4]

            if len(h) != len(d[i]):
                print(h, len(h))
                print(d[i], len(d[i]))

        df = pd.DataFrame(d)
        df.to_csv(out_file, quotechar="\"", index=False, header=h)
        print("Data saved to", out_file)
    else:
        print("Empty file", path_file)


def main():
    path_file = parse_args(create_args())
    if check_args(path_file):
        for f in os.listdir(path_file):
            if True:
                parse_and_save_file(os.path.join(path_file, f))
    else:
        print("Error while parsing args.")


if __name__ == '__main__':
    main()
