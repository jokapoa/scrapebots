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


from models import GithubUser, GithubApi


def print_repo_details(repos_list):
    """
    :param repos_list: [] of GithubUserRepo
        List of repos to print to stdout
    :return: void
        Prints details to stdout
    """

    for r in repos_list:
        print(r["name"], str(r["language"]))
        print(r["description"])
        print(str(r["stargazers_count"]), "***", " ", str(r["forks_count"]), "|-", " ", str(r["subscribers_count"]),
              "-.-")
        print("Created", str(r["created_at"]), " ", "Last update", str(r["pushed_at"]))
        print(r["html_url"], "\n")


def print_user_repos(username):
    """
    :param username: str
        Username of Github user
    :return: void
        Fetches list of user repos and prints details to stdout
    """

    user = GithubUser(username)
    repos = user.get_repos()
    print("Found", str(len(repos)), "repositories")
    print_repo_details(repos)


def print_trending_daily_repos():
    """
    :return: void
        Fetches list of daily trending repos and prints details to stdout
    """

    repos = GithubApi.get_trending_daily()
    print("Found", str(len(repos)), "repositories")
    print_repo_details(repos)


def print_trending_daily_not_starred_repos(username):
    """
    :param username: str
        Username of Github user
    :return: void
        Fetches list of trending daily repos and not starred by user and prints details to stdout
    """

    user = GithubUser(username)
    repos = user.get_trending_daily_not_starred()
    print("Found", str(len(repos)), "repositories")
    print_repo_details(repos)


def main():
    print_user_repos("sirfoga")
    # print_trending_daily_repos()
    # print_trending_daily_not_starred_repos("sirfoga")


if __name__ == "__main__":
    main()
