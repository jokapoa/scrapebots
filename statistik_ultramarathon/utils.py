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


import pandas as pd

VALUE_NOT_FOUND = str("DNF")  # value to put when data cannot be found (or some errors occur)


def append_to_file(f, s):
    """
    :param f: str
        Path to file to append stuff to
    :param s: str
        Stuff to append
    :return: void
        Appends stuff to file
    """

    try:
        with open(f, "a") as o:
            o.write(str(s))
            o.write("\n")
    except Exception as e:
        print("Cannot append", str(s), "to", str(f))
        print(str(e))


def get_dicts_from_csv(path_file):
    """
    :param path_file: str
        File to parse
    :return: [] of {}
        List of data details in file
    """

    d = pd.read_csv(path_file).T.to_dict()
    return list(d.values())
