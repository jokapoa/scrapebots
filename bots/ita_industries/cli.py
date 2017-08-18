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


""" Main driver of bot """

from args_utils import create_args, parse_args, check_args
from data_utils import get_data_from_csv, get_list_queries, save_dicts_to_csv
from search_utils import search_query


def main():
    path_in, path_out = parse_args(create_args())
    if check_args(path_in, path_out):
        queries = get_list_queries(
            get_data_from_csv(path_in))  # get input data
        search_results = []  # output of queries
        for q in queries:
            r = search_query(q)  # search result
            r["name"] = q["DENOMINAZIONE"]  # add field
            r["email"] = ",".join(
                [str(x) for x in r["email"]])  # to list of string
            r["telephone"] = ",".join(
                [str(x) for x in r["telephone"]])  # to list of string

            search_results.append(r)  # add to results
        save_dicts_to_csv(search_results, path_out)  # save to output


if __name__ == '__main__':
    main()
