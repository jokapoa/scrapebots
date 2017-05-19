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


""" Create, parse and check command line arguments and options """

import argparse
import os


def create_args():
    """
    :return: ArgumentParser
        Parser that handles cmd arguments.
    """

    parser = argparse.ArgumentParser(usage="-i <path to input .csv file> -o <path to output folder>")
    parser.add_argument("-i", dest="path_in", help="path to input .csv file", required=True)
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
    return str(args.path_in), str(args.path_out)


def check_args(path_in, path_out):
    """
    :param path_in: str
        File to use as input
    :param path_out: str
        Folder to use as output
    :return: bool
        True iff args are correct
    """

    assert (os.path.exists(path_in))
    assert (path_in.endswith(".csv"))

    out_dir = os.path.dirname(path_out)
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)  # create necessary dir for output file

    return True
