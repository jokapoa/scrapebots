# !/usr/bin/python3
# coding: utf-8

# Copyright {yyyy} Stefano Fogarollo
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


""" Search and download torrent files """

import os
from subprocess import call

from hal.wrappers.methods import handle_exceptions
from pytorrents.search import engines

QUERY_LIST_FILE = "/home/stefano/tmp/westerns"  # file containing query to search torrents (one for each line)
DOWNLOAD_DIR = "/home/stefano/Downloads/chrome/"  # where to download torrent files
SEARCH_ENGINE = engines.TorrentFunk()  # search engine of torrents


def download_torrent(query, download_dir=DOWNLOAD_DIR):
    """
    :param query: str
        Query to search torrents
    :param download_dir: str
        Path to download folder
    :return: void
        Downloads first torrent file matching query to download folder
    """

    results = SEARCH_ENGINE.search(query, "peers", 1, False)

    if len(results) > 0:
        result = results[0]
        download_link = result.download_link
        download_name = query.replace(" ", "_")
        download_file = os.path.join(download_dir, download_name + ".torrent")
        download_command = "wget -O \"" + download_file + "\" \"" + download_link + "\""

        print("Downloading:", download_name)
        call([download_command], shell=True)
    else:
        print("No results for:", query)


def get_list_of_queries():
    """
    :return: [] of str
        List of queries to be made
    """

    query_list = open(QUERY_LIST_FILE, "r").readlines()
    query_list = [l.strip() for l in query_list]
    return query_list


@handle_exceptions
def main():
    """
    :return: void
        Main driver
    """

    query_list = get_list_of_queries()
    for query in query_list:
        try:
            download_torrent(query)
        except Exception as e:
            print(str(e))
            print("Cannot download", query)


if __name__ == '__main__':
    main()
