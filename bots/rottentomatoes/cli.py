#!/usr/bin/env python3
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


""" Command line tool """

import argparse
import sys

from pyrottentomatoes import engines
from pyrottentomatoes import models


def parse_args():
    """ raise errors if args do not match parameters """
    parser = argparse.ArgumentParser(usage="-q query\n-h for full usage")
    parser.add_argument("-q", dest="query",
                        help="query, keywords to crawl RottenTomatoes about",
                        required=True)
    parser.add_argument("-c", dest="category",
                        help="category in [all, Franchise, Movies, TV, Celebrities, Critics]",
                        required=False)
    parser.add_argument("-y", dest="year",
                        help="consider results only in given year",
                        required=False)
    parser.add_argument("-after", dest="after",
                        help="consider results only that are produced after given year",
                        required=False)
    parser.add_argument("-before", dest="before",
                        help="consider results only that are produced before given year",
                        required=False)
    parser.add_argument("-m", dest="max_results",
                        help="max number of results to display",
                        required=False)
    args = parser.parse_args()

    assert (isinstance(args.query, type("string")))

    if not args.category:
        args.category = "all"
    assert (
        args.category in ["all", "Franchise", "Movies", "TV", "Celebrities",
                          "Critics"])

    if args.after:
        args.after = int(args.after)

    if args.before:
        args.before = int(args.before)

        if args.after:
            assert (
                args.before >= args.after)  # this way we have intersection of results

    if args.year:
        args.year = int(args.year)

        if args.after:
            assert (args.year >= args.after)

        if args.before:
            assert (args.year <= args.before)

    if not args.max_results:
        args.max_results = 100
    args.max_results = int(args.max_results)
    assert (args.max_results > 0)

    return args.query, args.category, args.year, args.after, args.before, args.max_results


def parse_results(results, year, after, before):
    """ refine search results with more parameters """

    r = []
    if year is not None:
        for x in results:
            try:
                if int(x.year) == int(year):
                    r.append(x)
            except:
                r.append(x)

    if after is not None:
        for x in results:
            try:
                if int(x.year) >= int(year):
                    r.append(x)
            except:
                r.append(x)
    else:
        r = results

    if before is not None:
        for x in results:
            try:
                if int(x.year) <= int(year):
                    r.append(x)
            except:
                r.append(x)

    return sorted(r, key=lambda k: k.tmeter, reverse=True)


def print_rt_info(result, category):
    assert (
        category in ["all", "Franchise", "Movies", "TV", "Celebrities",
                     "Critics"])

    url = result.link
    print("\nInfo about \"" + str(result.title) + "\":")

    if category == "Franchise":
        model = models.RottenTomatoesFranchise(url)
        print("No info found.")
    elif category == "Movies":
        model = models.RottenTomatoesMovies(url)
        tmeter_info, audience_meter_info, critics_review, movie_info = model.get_info()

        print("- Tomatometer:")
        print("\tScore:", str(tmeter_info["score"]), "%")
        print("\tAverage rating:", str(tmeter_info["avg_rating"]), "/10")
        print("- Audience:")
        print("\tLiked it:", str(audience_meter_info["score"]), "%")
        print("\tAverage rating:", str(audience_meter_info["avg_rating"]),
              "/5")
        print("- Critics review:", critics_review)
        print("- Plot:", str(movie_info["plot"]))
        print("- R:", str(movie_info["r"]))
        print("- Genre:", str(movie_info["genre"]))
        print("- Directed by:", str(movie_info["directed_by"]))
        print("- Written by:", str(movie_info["written_by"]))
        print("- In theaters (yyyy-mm-dd):", str(movie_info["in_theaters"]))
        print("- Box office:", str(movie_info["box_office"]), "$")
        print("- Wide on dvd (yyyy-mm-dd):", str(movie_info["wide_on_dvd"]))
        print("- Runtime:", str(movie_info["runtime"]), " minutes")
        print("- Studios:", str(movie_info["studio"]))
        print("- Cast:", str(movie_info["cast"]))
    elif category == "TV":
        model = models.RottenTomatoesTV(url)
        score, tv_info = model.get_info()

        print("- Rating:")
        print("\tTomatometer:", str(score["tmeter"]), "%")
        print("\tLiked it:", str(score["audience"]), "%")
        print("- Plot:", str(tv_info["plot"]))
        print("- Network:", str(tv_info["network"]))
        print("- Premiere (yyyy-mm-dd):", str(tv_info["premiere"]))
        print("- Date (yyyy-mm-dd):", str(tv_info["date"]))
        print("- Executive:", str(tv_info["executive"]))
        print("- Producers:", str(tv_info["producers"]))
        print("- Cast:", str(tv_info["cast"]))
    elif category == "Celebrities":
        model = models.RottenTomatoesCelebrities(url)
        print("No info found.")
    elif category == "Critics":
        model = models.RottenTomatoesCritics(url)
        print("No info found.")


def main():
    query, category, year, after, before, max_results = parse_args()
    search_engine = engines.RottenTomatoes()
    results = search_engine.search(query, category=category)
    results = parse_results(results, year, after, before)[:max_results]

    if len(results) > 0:
        print("\n\n".join([
                              str(results.index(
                                  x) + 1) + " - Title: " + x.title +
                              "\nLink: " + x.link +
                              "\nCategory: " + x.category +
                              "\nYear: " + str(x.year) +
                              "\nArtists: " + str(x.artists) +
                              "\nTomatometer : " + str(x.tmeter) + "%"
                              for x in results]))

        user_answer = input(
            "More info about result " + str([i + 1 for i in range(
                len(results))]) + "? or any other key to quit: ")
        try:
            user_answer = int(user_answer)
            print_rt_info(results[user_answer - 1],
                          results[user_answer - 1].category)
        except:  # answer is not a integer -> exit
            return

    else:
        print("Sorry, no results found.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\r[!] User requesting exit...\n%s" % sys.exc_info()[1])
        sys.exit(0)
    except Exception:
        print("\r[!] Unhandled exception occured...\n%s" % sys.exc_info()[1])
