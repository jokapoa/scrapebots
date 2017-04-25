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


import time


def get_time_eta(total_done, total, start_time):
    """
    :param total_done: int
        Item processed
    :param total: int
        Total number of items to process
    :param start_time: time
        Time of start processing items
    :return: time
        Time to go
    """

    time_done = int(time.time()) - start_time
    try:
        speed = total_done / time_done
    except:
        speed = 0

    if time_done > 0 and speed > 0:
        total_to_go = total - total_done
        time_to_go = total_to_go / speed
        m, s = divmod(time_to_go, 60)  # get hours, seconds and minutes
        h, m = divmod(m, 60)

        return {
            "h": int(h),
            "m": int(m),
            "s": int(s)
        }
    else:
        return {
            "h": 0,
            "m": 0,
            "s": 0
        }


def print_item_info(details):
    """
    :param details: {}
        Details of AthletePerformance
    :return: void
        Prints debug info to screen
    """

    print(
        "{:20.19}".format(details["name"]),
        "{:20.19}".format(details["finish_time"])
    )  # debug info


def print_time_eta(time_to_go):
    """
    :param time_to_go: {}
        Result of a call get_time_eta(...)
    :return: void
        Prints debug info to screen
    """

    print(
        "ETA: {:20.19}".format(
            str(time_to_go["h"]) + "h " + str(time_to_go["m"]) + "\" " + str(time_to_go["s"]) + "'"
        )
    )


def print_debug_info(infos):
    out = ""
    for i in infos:
        out += "{:20.19}".format(str(i))
    print(out)
