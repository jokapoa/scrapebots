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


from datetime import datetime, timedelta

from bs4 import BeautifulSoup

VALUE_NOT_FOUND = str("DNF")  # value to put when data cannot be found (or some errors occur)


def get_url_of_page(y, base_url="http://www.letour.fr/HISTO/us/TDF/"):
    """
    :param y: int
        Year of tour to fetch
    :param base_url: str
        Root url of links
    :return: str
        Url of selected page
    """

    return base_url + str(y) + "/etapes.html"


def get_stage_details_from_url(u):
    """
    :param u: str
        Url of stage to parse
    :return: {}
        Details of stage
    """

    tokens = str(u.strip()).split("/")

    try:
        stage_id = str(int(tokens[-2]) / 100).strip()
    except Exception as e:
        print(str(e))
        stage_id = VALUE_NOT_FOUND

    return {
        "year": str(tokens[-3]).strip(),
        "id": stage_id
    }


def get_list_of_stages(raw_html, base_url="http://www.letour.fr"):
    """
    :param raw_html: str
        Raw HTML page with table with races list
    :param base_url: str
        Root url of links
    :return: [] of {}
        List of stages urls and names
    """

    soup = BeautifulSoup(str(raw_html), "lxml")  # HTML parser
    table = soup.find_all("table", {"class": "liste"})[0]
    rows = table.find_all("tr")[1:]  # discard header
    urls = [r.find("td").a["href"] for r in rows]  # raw urls
    return [str(base_url + u) for u in urls]  # add root urls


def get_standings_of_stage(raw_html):
    """
    :param raw_html: str
        Raw HTML page with table with races list
    :return: [] of {}
        Standings of stage: each dict has values: position, id, name, time
    """

    standings = []
    soup = BeautifulSoup(str(raw_html), "lxml")  # HTML parser
    table = soup.find_all("table", {"class": "liste"})[-1]
    rows = table.find_all("tr")

    if "etape" in rows[1].find("td").text.lower():
        rows = rows[2:]  # discard header
        non_stage_rows = [r for r in rows if "tr class=\"strong\"" in str(r)]  # rows that do not have stage standings
        try:
            end_rows = rows.index(non_stage_rows[0])  # data rows ends at this index
            rows = rows[:end_rows]
            winner_time = timedelta(days=1)  # time of winner (all races lasted < 1 day)

            for r in rows:
                try:
                    columns = r.find_all("td")
                    columns = [str(c.text.replace("\\\'", "'").replace("\\t", "").replace("\\n", "").strip()) for c in
                               columns]  # parse
                    athlete_time = columns[3]  # TODO
                    if athlete_time.startswith("+"):
                        try:
                            athlete_time = datetime.strptime(athlete_time, '+ %M\' %S"')
                            athlete_time = timedelta(
                                hours=athlete_time.hour,
                                minutes=athlete_time.minute,
                                seconds=athlete_time.second
                            )
                        except Exception as e:
                            print(str(e))
                            athlete_time = VALUE_NOT_FOUND
                    else:  # this is the winner time
                        try:
                            athlete_time = datetime.strptime(athlete_time, '%Hh %M\' %S\"')
                            athlete_time = timedelta(
                                hours=athlete_time.hour,
                                minutes=athlete_time.minute,
                                seconds=athlete_time.second
                            )
                            if athlete_time < winner_time:
                                winner_time = athlete_time
                        except Exception as e:
                            print(str(e))
                            athlete_time = VALUE_NOT_FOUND

                    standings.append(
                        {
                            "position": columns[0],
                            "id": columns[1],
                            "name": columns[2],
                            "time": str(athlete_time)  # to string
                        }
                    )  # add to result list
                except Exception as e:
                    print(str(e))
                    pass
        except Exception as e:
            print(str(e))  # parse all rows
            pass
    else:  # this is not the stage standings
        return []
