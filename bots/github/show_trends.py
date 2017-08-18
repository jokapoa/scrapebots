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


""" Prints trending repositories for user """


from colorama import init, Fore, Style

from hal.internet.github import GithubUser

LANGUAGES_COLORS = {
    "": Fore.WHITE + Style.BRIGHT,
    "python": Fore.CYAN + Style.BRIGHT,
    "c": Fore.LIGHTBLUE_EX + Style.BRIGHT,
    "c++": Fore.YELLOW + Style.BRIGHT,
    "java": Fore.RED + Style.BRIGHT,
    "haskell": Fore.GREEN + Style.BRIGHT,
    "go": Fore.BLUE + Style.BRIGHT,
    "ruby": Fore.RED + Style.BRIGHT,
    "mathematica": Fore.RED + Style.BRIGHT,
    "matlab": Fore.MAGENTA + Style.BRIGHT,
    "tex": Fore.GREEN + Style.BRIGHT
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
    lang_color = LANGUAGES_COLORS[lang] if lang in LANGUAGES_COLORS else ""
    url_color = Fore.BLUE + Style.BRIGHT

    for repo in repos_list:
        if not (repo["name"] is None and repo["description"] is None):
            print(lang_color + str(repo["name"]) + " " + str(repo["language"]))
            print(str(repo["description"]))
            print(str(repo["stargazers_count"]), "***", " ",
                  str(repo["forks_count"]), "|-", " ",
                  str(repo["subscribers_count"]),
                  "-.-")
            print("Created", str(repo["created_at"]), " ", "Last update",
                  str(repo["pushed_at"]))
            print(url_color + str(repo["html_url"]), "\n")


def show_trends_for_user(user, languages):
    """
    :param user: str
        Username of Github user
    :param languages: list
        List of languages to get trends for
    :return: void
        Prints trending repositories of user
    """

    github_user = GithubUser(user)
    for language in languages:
        print("Fetching trending", language.title(), "repositories for", user)
        trends = github_user.get_trending_daily_not_starred()
        print("Found", str(len(trends)), "repositories:\n")
        print_repos_details(trends, lang=language)


def main():
    """
    :return: void
        Prints trending repositories for user
    """

    show_trends_for_user(
        "sirfoga",
        [""]
    )  # example of usage


if __name__ == '__main__':
    main()
