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


import argparse
import os
import sys

from hal.internet.web import Webpage

URL = "https://www.hackerrank.com/"
DOMAINS_URL = URL + "domains"


def get_domains(page):
    """ parse html source of page and returns list of domains """
    domains = []  # list of domains
    slug_tag = ",\"slug\":\""
    end_of_tag = "\""
    for domain in range(2, 25):  # only 16 domains at the moment
        tag = "\"id\":" + str(domain) + ",\"name\":\""
        tag_position = page.find(tag)
        if tag_position >= 0:  # found tag -> found domain
            slug_tag_position = page.find(slug_tag, tag_position + len(tag))
            start_of_name = slug_tag_position + len(slug_tag)
            end_of_name = page.find(end_of_tag, start_of_name)  # find last "
            domains.append(
                page[start_of_name:end_of_name])  # append name found
    return domains


def get_subdomains(domain, html_page):
    """ get sub-domains of given hackerrank domain (slug name)"""

    def get_all_subdomains(page):
        """ parse html and returns list of domains (with subdomains) """
        domains_delimiter = "}]},{\"id\":"
        subdomains = page.split(domains_delimiter)  # list of domains
        subdomains = subdomains[1:]  # discard first section
        last_subdomain = subdomains[-1]
        end_of_last_subdomain = last_subdomain.find(
            "}]}]")  # discard last section
        last_subdomain = last_subdomain[:end_of_last_subdomain]
        subdomains[-1] = last_subdomain
        return subdomains

    def parse_section(raw_section):
        """ parse html representation of section and extracts information """
        name_tag = "\"name\":\""
        slug_tag = "\"slug\":\""

        section_name = raw_section.find(name_tag)
        end_tag = raw_section.find("\"", section_name + len(name_tag))
        section_name = raw_section[
                       section_name + len(name_tag): end_tag]  # get full name

        section_slug = raw_section.find(slug_tag)
        end_tag = raw_section.find("\"", section_slug + len(slug_tag))
        section_slug = raw_section[
                       section_slug + len(slug_tag): end_tag]  # get slug

        return section_name, section_slug

    def parse_subdomains(raw_domain):
        """ parse raw domain string and returns list of subdomains"""
        subdomains = []
        index_of_subdomains = raw_domain.find(":[{")
        raw_subdomains = raw_domain[index_of_subdomains:].split(",{")
        for raw_subdomain in raw_subdomains:
            subdomain_name, subdomain_slug = parse_section(
                raw_subdomain)  # parse each section
            subdomains.append(subdomain_slug)  # append ot list
        return subdomains

    print("Getting subdomains of", domain, "...")

    if domain == "tutorials":  # only one subdomain
        return ["30-days-of-code"]

    all_domains = get_all_subdomains(html_page)
    for raw_domain in all_domains:
        parsed_domain_name, parsed_domain_slug = parse_section(raw_domain)
        if parsed_domain_slug == domain:  # get all subdomains
            return parse_subdomains(raw_domain)
    return []


def get_challenges(domain, subdomain):
    return []  # TODO: complete


def download_challenge(challenge, directory):
    pass  # TODO: complete


def get_pages():
    """ returns HTML sources of domain and subdomains pages """

    web_page = Webpage(DOMAINS_URL)
    source_page = web_page.source
    # subdomains_html = get_html_source(os.path.join(hackrrank_url, "algorithms"))
    return source_page, source_page  # same content for each 2 pages


def edit_args_parser(args):
    """ if directory non-existent -> create one """
    if not os.path.exists(args.directory):  # if non-existent directory
        os.makedirs(args.directory)  # create one


def main():
    parser = argparse.ArgumentParser(
        usage='-d <directory to store results>\n-h for full usage')
    parser.add_argument('-d', dest='directory',
                        help='directory to store results', required=True)
    args = parser.parse_args()
    edit_args_parser(args)  # edit args

    domain_page, subdomains_page = get_pages()  # get html source of sub-domains page

    domains = get_domains(domain_page)  # parse webpage for domains
    domains.sort()  # sort list
    for domain in domains:
        if not os.path.exists(os.path.join(args.directory, domain)):
            os.mkdir(os.path.join(args.directory, domain))  # create directory
        subdomains = get_subdomains(domain, subdomains_page)  # get subdomains
        for subdomain in subdomains:
            if not os.path.exists(
                    os.path.join(args.directory, domain, subdomain)):
                os.mkdir(os.path.join(args.directory, domain,
                                      subdomain))  # create directory
            challenges = get_challenges(domain, subdomain)
            for challenge in challenges:
                if not os.path.exists(
                        os.path.join(args.directory, domain, subdomain,
                                     challenge)):
                    os.mkdir(os.path.join(args.directory, domain, subdomain,
                                          challenge))  # create directory
                download_challenge(challenge,
                                   os.path.join(args.directory, domain,
                                                subdomain,
                                                challenge))  # download testcases and statement


if __name__ == '__main__':
    try:
        main()
    except Exception:
        print('\rUnhandled exception occurred..\n[!] %s' % sys.exc_info()[1])
        sys.exit(0)
