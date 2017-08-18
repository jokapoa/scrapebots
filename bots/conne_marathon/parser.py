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


""" Tools to parse Conne marathon webpage """

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
    parser.add_argument("-f", dest="path_file", help="path to file",
                        required=True)
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


def get_tokens(line):
    """
    :param line: str
        Line of file to parse
    :return: [] of str
        Tokens of line
    """

    tokens = line.strip().split(" ")
    tokens = [t.strip() for t in tokens if len(t) > 0]
    return tokens


def fix_line(line):
    """
    :param line: [] of str
        Tokens of line
    :return: [] of str
        Tokens of line
    """

    for i, value in enumerate(line):
        if value.find(" ") > 0 and value[0].isdigit():
            tokens = value.split(" ")
            number = tokens[0].strip()  # number
            words = " ".join(tokens[1:]).strip()  # words
            line[i] = number
            line.insert(i + 1, words)
    return line


def fix_headers(bad_headers):
    """
    :param bad_headers: [] of str
        Tokens of headers
    :return: [] of str
        Tokens of headers
    """

    headers = []
    for header in bad_headers:
        headers += header.split(" ")
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

    if lines:
        lines = [get_tokens(l) for l in lines if len(l) > 2]  # parse each line
        headers = fix_headers(lines[0])

        lines = lines[1:]
        lines = [
            l for l in lines
            if len(l) > 4 and (l[-2].find(":") > 0 or l[-1].find(":") > 0)
            ]

        return headers, lines

    return None, None


def parse_and_save_file(path_file):
    """
    :param path_file: str
        File to parse
    :return: void
        Parses raw file, then saves results
    """

    headers, data = parse_file(path_file)
    if headers is not None and data is not None:
        file_name_tokens = Document(path_file).name.split("-")
        file_name = file_name_tokens[0] + "_"
        file_name += file_name_tokens[1].split(".")[0] + ".csv"
        out_file = os.path.join(os.path.dirname(path_file), file_name)

        for i, value in enumerate(data):
            if len(headers) == len(value) - 1:
                data[i][2] += data[i][3]
                del data[i][3]

            if len(headers) == len(value) and data[i][-1].find(":") > 0:
                data[i][2] += data[i][3]
                del data[i][3]

            if len(data[i]) < len(headers):
                data[i].insert(4, VALUE_NOT_FOUND)

            while len(value) > len(headers) and len(value) > 4:
                del data[i][4]

            if len(headers) != len(data[i]):
                print(headers, len(headers))
                print(data[i], len(data[i]))

        data_frame = pd.DataFrame(data)
        data_frame.to_csv(out_file, quotechar="\"", index=False,
                          header=headers)
        print("Data saved to", out_file)
    else:
        print("Empty file", path_file)


def main():
    """
    :return: void
        Parses raw file, then saves results
    """

    path_file = parse_args(create_args())
    if check_args(path_file):
        for file in os.listdir(path_file):
            parse_and_save_file(os.path.join(path_file, file))
    else:
        print("Error while parsing args.")


if __name__ == '__main__':
    main()
