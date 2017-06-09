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


from colorama import init, Fore, Style
from models import GithubUser

code_lang_colors = {
    "": Fore.WHITE,
    "python": Fore.CYAN,
    "c": Fore.LIGHTBLUE_EX,
    "c++": Fore.YELLOW,
    "java": Fore.RED,
    "haskell": Fore.GREEN,
    "go": Fore.BLUE,
    "ruby": Fore.RED,
    "mathematica": Fore.RED,
    "matlab": Fore.MAGENTA,
    "tex": Fore.GREEN
}


def print_repos_details(repos_list, lang=""):
    """
    :param repos_list: [] of GithubUserRepo
        List of repos to print to stdout
    :param lang: str
        Coding language (only for prettify purposes)
    :return: void
        Prints details to stdout
    """

    init(autoreset=True)  # colorful output
    lang_color = code_lang_colors[lang] if lang in code_lang_colors else ""  # color output for this language
    url_color = Fore.BLUE + Style.BRIGHT

    for r in repos_list:
        if not (r["name"] is None and r["description"] is None):  # valid repository
            print(lang_color + str(r["name"]) + " " + str(r["language"]))
            print(str(r["description"]))
            print(str(r["stargazers_count"]), "***", " ", str(r["forks_count"]), "|-", " ", str(r["subscribers_count"]),
                  "-.-")
            print("Created", str(r["created_at"]), " ", "Last update", str(r["pushed_at"]))
            print(url_color + str(r["html_url"]), "\n")


def show_trends_for_user(user, langs, include_already_starred=True):
    """
    :param user: str
        Username of Github user
    :param langs: list
        List of languages to get trends for
    :param include_already_starred: bool
        True iff want to print out also already starred repositories
    :return: void
        Prints trending repositories of user
    """

    u = GithubUser(user)
    stars = []

    if not include_already_starred:
        print("Fetching", user + "'s stars")
        stars = u.get_starred_repos()

    for l in langs:
        print("Fetching trending", l.title(), "repositories for", user)
        trends = u.get_trending_daily_except(avoid=stars, lang=l)
        print("Found", str(len(trends)), "repositories:", end="\n")
        print_repos_details(trends, lang=l)


if __name__ == '__main__':
    show_trends_for_user(
        "sirfoga",
        ["", "python", "c", "c++", "java", "haskell", "go", "ruby", "mathematica", "matlab", "tex"]
    )  # example of usage
