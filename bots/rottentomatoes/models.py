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


import html
from datetime import datetime

from bs4 import BeautifulSoup
from hal.internet.web import Webpage


class RottenTomatoesSpider(object):
    """ Scrape RottenTomatoes website to fetch content about various models """

    def __init__(self, url, category):
        """
        :param url: url of given RT item to scrape
        :param category: category (one of franchise, m, tv, celebrity, critic)
        """

        object.__init__(self)

        assert (category in ["franchise", "m", "tv", "celebrity", "critic"])

        self.url = url
        self.code = self.url[url.index("/" + category + "/") + len(
            "/" + category + "/"):]
        self.web_page = Webpage(self.url)
        self.domain = self.web_page.get_domain()
        self.page_source = str(html.unescape(self.web_page.get_html_source())) \
            .replace("\n", "").replace("\\n", "").replace("\\", "").strip()
        self.soup = BeautifulSoup(self.page_source, "lxml")


class RottenTomatoesFranchise(RottenTomatoesSpider):
    """ Following features to scrape from website:
        best rated movie
        info
        best movies """

    def __init__(self, url):
        RottenTomatoesSpider.__init__(self, url, "franchise")


class RottenTomatoesMovies(RottenTomatoesSpider):
    """ Following features to scrape from website:
        tomatometer
        critics
        audience
        info """

    def __init__(self, url):
        RottenTomatoesSpider.__init__(self, url, "m")

        self.title = self.soup.find_all("h1", {"id": "movie-title"})[
            0].text.strip()  # parse source to get title
        self.tmeter_info = {
            "score": "Not found.",
            "avg_rating": "Not found.",
            "reviews": "Not found."
        }  # critics
        self.audience_meter_info = {
            "score": "Not found.",
            "avg_rating": "Not found.",
            "reviews": "Not found."
        }  # audience
        self.critics_review = ""  # short review shared by all critics
        self.movie_info = {
            "plot": "",
            "r": "",
            "genre": [],
            "directed_by": "",
            "written_by": "",
            "in_theaters": "",
            "box_office": "",
            "wide_on_dvd": "",
            "runtime": "",
            "studio": "",
            "cast": []
        }  # general info

        self.is_updated = [False, False, False]  # mark as updated general info

    def get_score(self):
        """ Return tomatometer and audience ratings """
        if not self.is_updated[0]:
            try:
                tmeter_info = {
                    "score": int(self.soup.find_all("span", {
                        "class": "meter-value superPageFontColor"})
                                 [0].text.replace("%", "").strip()),
                    "avg_rating": float(self.soup.find_all("div", {
                        "class": "superPageFontColor"})
                                        [0].text.replace("Average Rating: ",
                                                         "").strip().replace(
                        "/10", "").strip()),
                    "reviews": int(self.soup.find_all("div", {
                        "class": "superPageFontColor"})
                                   [1].text.replace("Reviews Counted: ",
                                                    "").strip())
                }  # critics
            except:
                tmeter_info = {
                    "score": "Not found.",
                    "avg_rating": "Not found.",
                    "reviews": "Not found."
                }

            try:
                audience_meter_info = {
                    "score": int(
                        self.soup.find_all("span",
                                           {"class": "superPageFontColor",
                                            "style": "vertical-align:top"})
                        [0].text.replace("%", "").strip()),
                    "avg_rating": float(
                        self.soup.find_all("div", {
                            "class": "audience-info hidden-xs superPageFontColor"})
                        [0].find_all("div")
                        [0].text.replace("Average Rating:",
                                         "").strip().replace("/5",
                                                             "").strip()),
                    "reviews": int(self.soup.find_all("div", {
                        "class": "audience-info hidden-xs superPageFontColor"})
                                   [0].find_all("div")
                                   [1].text.replace("User Ratings:",
                                                    "").replace(",",
                                                                "").strip())
                }  # audience
            except:
                audience_meter_info = {
                    "score": "Not found.",
                    "avg_rating": "Not found.",
                    "reviews": "Not found."
                }

            self.tmeter_info = tmeter_info  # save new findings
            self.audience_meter_info = audience_meter_info
            self.is_updated[0] = True  # mark as updated

        return self.tmeter_info, self.audience_meter_info

    def get_critics_review(self):
        """ Return short review shared by all critics """
        if not self.is_updated[1]:
            try:
                critics_review = str(self.soup.find_all("p", {
                    "class": "critic_consensus superPageFontColor"})
                                     [0].text.replace("Critics Consensus:",
                                                      "").strip())
            except:
                critics_review = "Not found."

            self.critics_review = critics_review  # save new findings
            self.is_updated[1] = True  # mark as updated

        return self.critics_review

    def get_movie_info(self):
        """ Return general info about movie """

        def get_panel_info(key, soup):
            """ Scrape movie panel info to get specific info matching key """

            assert (
                key in ["Rating", "Genre", "Directed By", "Written By",
                        "On DVD",
                        "In Theaters", "Box Office",
                        "Runtime", "Studio"])

            panel = soup.find_all("div", {"class": "info"})[0].find_all("div")
            try:
                index = panel.index([x for x in panel if key in x.text][
                                        0]) + 1  # get index of value

                if key == "On DVD" or key == "In Theaters":
                    value = datetime.strptime(panel[index].text
                                              .replace("&nbsp;Wide", "")
                                              .replace("&nbsp;wide", "")
                                              .replace("wide", "").strip(),
                                              "%b %d, %Y")
                elif key == "Box Office" or key == "Runtime":
                    value = panel[index].text.strip().replace("$", "").replace(
                        ",", "").replace(" minutes", "")
                    if key == "Box Office":  # value is a price
                        value = value[
                                :value.index(".")]  # remove decimal points
                    value = int(value)
                else:  # rating, genre, directed by, written by, studio
                    value = [x.strip() for x in
                             panel[index].text.strip().split(",")]
            except:
                value = "Not found."

            return value

        if not self.is_updated[2]:
            movie_info = {
                "plot": self.soup.find_all("div", {"id": "movieSynopsis"})[
                    0].text.strip(),
                "r": get_panel_info("Rating", self.soup),
                "genre": get_panel_info("Genre", self.soup),
                "directed_by": get_panel_info("Directed By", self.soup),
                "written_by": get_panel_info("Written By", self.soup),
                "in_theaters": get_panel_info("In Theaters", self.soup),
                "box_office": get_panel_info("Box Office", self.soup),
                "wide_on_dvd": get_panel_info("On DVD", self.soup),
                "runtime": get_panel_info("Runtime", self.soup),
                "studio": get_panel_info("Studio", self.soup),
                "cast": [x.text.strip() for x in
                         self.soup.find_all("div", {
                             "class": "cast-item media inlineBlock "})] +
                        [x.text.strip() for x in
                         self.soup.find_all("div", {
                             "class": "cast-item media inlineBlock  castRemaining"})]
            }

            self.movie_info = movie_info  # save new findings
            self.is_updated[2] = True  # mark as updated

        return self.movie_info

    def get_info(self):
        tmeter_info, audience_meter_info = self.get_score()
        critics_review = self.get_critics_review()
        movie_info = self.get_movie_info()
        return tmeter_info, audience_meter_info, critics_review, movie_info


class RottenTomatoesTV(RottenTomatoesSpider):
    """ Following features to scrape from website:
        tomatometer
        audience
        info """

    def __init__(self, url):
        RottenTomatoesSpider.__init__(self, url, "tv")

        self.title = ""
        self.score = {
            "tmeter": "",
            "audience": ""
        }  # meter-value superPageFontColor
        self.tv_info = {
            "plot": "",
            "network": "",
            "premiere": "",
            "date": "",
            "executive": [],
            "producers": [],
            "cast": []
        }

        self.is_updated = [False, False]  # mark as updated general info

    def get_score(self):
        """ Return tomatometer and audience ratings """
        if not self.is_updated[0]:
            try:
                score = {  # TODO: try something
                    "tmeter": "",
                    "audience": ""
                }
            except:
                score = {
                    "tmeter": "Not found.",
                    "audience": "Not found."
                }

            self.score = score
            self.is_updated[0] = True

        return self.score

    def get_tv_info(self):
        """ Return general info about tv serie"""
        if not self.is_updated[1]:
            try:
                tv_info = {  # TODO: try something
                    "plot": "",
                    "network": "",
                    "premiere": "",
                    "date": "",
                    "executive": [],
                    "producers": [],
                    "cast": []
                }
            except:
                tv_info = {  # TODO: try something
                    "plot": "Not found.",
                    "network": "Not found.",
                    "premiere": "Not found.",
                    "date": "Not found.",
                    "executive": [],
                    "producers": [],
                    "cast": []
                }

            self.tv_info = tv_info
            self.is_updated[1] = True

        return self.tv_info

    def get_info(self):
        score = self.get_score()
        tv_info = self.get_tv_info()
        return score, tv_info


class RottenTomatoesCelebrities(RottenTomatoesSpider):
    """ Following features to scrape from website:
        name
        high rated
        low rated
        list of films
        info
            birtday
            birthplace
            bio
        trivia
            trivia
            quotes """

    def __init__(self, url):
        RottenTomatoesSpider.__init__(self, url, "celebrity")


class RottenTomatoesCritics(RottenTomatoesSpider):
    """ Following features to scrape from website:
        info
        publications
        nr reviews
        list of movies
        best movie
        worst movie """

    def __init__(self, url):
        RottenTomatoesSpider.__init__(self, url, "critic")
