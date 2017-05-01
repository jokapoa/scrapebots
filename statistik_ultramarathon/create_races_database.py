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


import json
import os
import time

from hal.files.models import Directory
from hal.time.profile import print_time_eta, get_time_eta
from pymongo import MongoClient
from utils import get_dicts_from_csv

PATH_TO_DATA_FOLDER = "/home/stefano/Coding/Data/projects/galore/running/ultramarathon/races/statistik-races/races_details/"
VALUE_NOT_FOUND = str("DNF")  # value to put when data cannot be found (or some errors occur)
BASE_URL = "http://statistik.d-u-v.org/"  # url of web-page
WEBPAGE_COOKIES = {
    "Language": "EN"
}  # set language
LOG_FILE = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                        str(os.path.basename(__file__)) + str(int(time.time())) + ".log")
DATABASE_NAME = "statistik-races"  # name of database to use
mongodb_client = MongoClient()  # mongodb client
# mongodb_client.drop_database(DATABASE_NAME)  # remove all previous data in database
db = mongodb_client[DATABASE_NAME]  # database to use
for c in db.collection_names():
    db[c].create_index("url", unique=True)  # set primary key
db_table = "races"  # database table (i.e collection) to use


def get_race_dict_from_files(details_file, results_file):
    """
    :param details_file: str
        Path to file with race details
    :param results_file: str
        Path to file with race results
    :return: {}
        Dict with race
    """

    race_dict = json.loads(open(details_file, "r").read())
    results_list = get_dicts_from_csv(results_file)
    for i in range(len(results_list)):
        bson_compatible_dict = {}
        for k in results_list[i].keys():  # edit name of all keys with a dot (not officially accepted by bson)
            bson_compatible_dict[str(k).replace(".", "")] = results_list[i][k]
        results_list[i] = bson_compatible_dict

    race_dict["results"] = results_list
    return race_dict


def get_dict_in_folder(dir_path):
    """
    :param dir_path: str
        Path to folder
    :return: {}
        Dictionary with data about race in path
    """

    content_dir = Directory.ls(dir_path, recurse=False)  # get content of folder
    files_in_folder = [f for f in content_dir if os.path.isfile(f)]
    if len(files_in_folder) == 2:
        return get_race_dict_from_files(
            os.path.join(dir_path, "details.json"),
            os.path.join(dir_path, "results.csv")
        )
    else:
        return None


if __name__ == '__main__':
    paths = Directory.ls(PATH_TO_DATA_FOLDER, recurse=True)  # get list of files and folders to edit
    paths = [p for p in paths if os.path.isdir(p)]
    start_time = time.time()
    total = len(paths)
    total_done = 0

    for p in paths:
        d = get_dict_in_folder(p)
        if d is not None:
            try:
                db[db_table].insert_one(d)
            except Exception as e:
                if "duplicate key" not in str(e):
                    print(str(e))

        total_done += 1
        print_time_eta(
            get_time_eta(
                total_done,
                total,
                start_time
            )  # get ETA
        )  # debug info
