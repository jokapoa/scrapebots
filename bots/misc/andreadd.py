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


import os
import time
from urllib.parse import urlparse, urljoin

from hal.files.models import Directory
from hal.internet import parser
from hal.internet import web
from hal.wrappers.methods import \
    handle_exceptions  # notify user if something goes wrong

USING_TOR_TO_FETCH_PAGES = False  # use tor to prevent server-side banning


def url_factory(url):
    """
    :param url: string
        Url to edit according to webpage standards
    :return: string
        Valid url to use in andreadd.it domain
    """

    new_url = url.replace(" ", "%20")
    return new_url


class URLLink(object):  # TODO: maybe move to hal
    def __init__(self, name, url):
        object.__init__(self)

        self.name = name
        self.url = url

    @handle_exceptions
    def download(self, local_file):
        """
        :param local_file: string
            Path to local file where to store download link
        :return: void
            Download document in local file
        """

        if not os.path.exists(local_file):  # if not downloaded
            web.download_url(self.url, local_file)


class ADDDocument(URLLink):
    def __init__(self, name, category, download_link):
        """
        :param name: string
            Name of file
        :param download_link: string
            Url to download link
        """

        URLLink.__init__(self, name,
                         url_factory(download_link))  # set name and url fields

        self.name = name
        self.category = category
        self.download_name = urlparse(download_link).path.split("/")[
            -1]  # get name of file as saved in server


class ADDCourseClass(web.Webpage):
    def __init__(self, name, url):
        """
        :param name: string
            Name of class
        :param url: string
            Url of main page of class
        """

        web.Webpage.__init__(self, url_factory(url),
                             using_tor=USING_TOR_TO_FETCH_PAGES)
        self.name = name

    @staticmethod
    def get_document_list_from_ul(ul_table):
        """
        :param ul_table: Beautifulsoup
            html table in the form <ul><li></li> ... <li></li></ul>
        :return: [] of URLLink
            link to each document
        """

        document_list = []  # append here new documents
        li_list = ul_table.find_all("li")  # list of <li> elements in table
        for li_item in li_list:
            name = li_item.text
            links = li_item.find_all("a")  # find raw links

            for link in links:  # loop through all links
                document_list.append(
                    URLLink(
                        parser.html_stripper(name),  # parse name
                        link["href"]  # parse relative link
                    )
                )
        return document_list

    @staticmethod
    def get_table_category(table, min_letters_in_category=5,
                           unknown="unsorted"):
        """
        :param table: soup table
            Table containing list of documents
        :param min_letters_in_category: int
            Minimum number of letters in a well-formed name of a category
        :param unknown: string
            Category name on not found error or unknown category
        :return: string
            Category table is in
        """

        category = unknown

        try:
            valid_category = table.previous_sibling.previous_sibling.text  # raw name
            valid_category = parser.html_stripper(valid_category)  # parsed
            if len(valid_category) >= min_letters_in_category:
                category = valid_category
        except:
            pass

        return category[:64]  # get first 64 char

    def get_year(self, unknown="0"):
        """
        :param unknown: string
            On error in finding year, year has this value
        :return: int
            Year this course belongs to
        """

        year_position = self.url.find("/anno")
        year_position += len("/anno")
        try:
            return int(self.url[year_position])
        except:
            return unknown

    def get_documents_list(self):
        """
        :return: []
            List of downloadable document in class page
        """

        table_list = self.soup.find_all("ul", {
            "class": "plussbullets"})  # find tables containing documents
        document_list = []
        for i in range(len(table_list)):  # loop through category tables
            category = self.get_table_category(
                table_list[i])  # category table is in
            table_content = self.get_document_list_from_ul(
                table_list[i])  # parse content
            document_list += [
                ADDDocument(  # create new add document
                    item.name,  # get name
                    category,  # get category document belongs to
                    urljoin(self.url, item.url)  # fix relative link
                ) for item in table_content
                # loop through list of raw documents
                ]

        return document_list

    def download_all_documents(self, root_directory):
        """
        :param root_directory: string
            Path to root directory where to download files
        :return: void
            Download all documents of all classes in given path
        """

        documents_list = self.get_documents_list()  # get downloadable documents
        for document in documents_list:
            document_directory = os.path.join(root_directory,
                                              document.category)
            Directory.create_new(
                document_directory)  # create directory for this class of documents
            document.download(os.path.join(document_directory,
                                           document.download_name))  # download to local file


class ADDExtraCourse(ADDCourseClass):
    """ General university course e.g "English Test" or "List of Thesis" """

    def __init__(self, name, url):
        ADDCourseClass.__init__(self, name, url)

    def __str__(self):
        """
        :return: string
            Class type, name and url
        """

        return str(type(self)) + ", name:" + self.name + ", url:" + self.url


class ADDCourse(web.Webpage):
    def __init__(self, name, url):
        """
        :param name: string
            Name of course
        :param url: string
            Url of main page of course
        """

        web.Webpage.__init__(self, url_factory(url),
                             using_tor=USING_TOR_TO_FETCH_PAGES)
        self.name = name

    def __str__(self):
        """
        :return: string
            Class type, name and url
        """

        return str(type(self)) + ", name:" + self.name + ", url:" + self.url

    def get_class_list(self):
        """
        :return: []
            List of class divided per course year
        """

        classes = self.soup.find_all("td", {"class": "nome_materia"})
        classes = [ADDCourseClass(
            parser.html_stripper(c.text),  # find name
            urljoin(self.url, c.a["href"]),  # find url of class
        ) for c in classes if len(c.text) > 5]  # build course classes object
        return classes

    def download_all_documents(self, root_directory):
        """
        :param root_directory: string
            Path to root directory where to download files
        :return: void
            Download all documents of all classes in given path
        """

        course_class_list = self.get_class_list()
        for course_class in course_class_list:
            course_class_directory = os.path.join(root_directory,
                                                  str(course_class.get_year()),
                                                  course_class.name)
            Directory.create_new(
                course_class_directory)  # create folder for course class
            course_class.download_all_documents(
                course_class_directory)  # download course class documents there


class ADDNotes(web.Webpage):
    def __init__(self, url="http://www.andreadd.it/appunti/appunti.html"):
        """
        :param url: string
            Url of main page of notes
        """

        web.Webpage.__init__(self, url_factory(url),
                             using_tor=USING_TOR_TO_FETCH_PAGES)

    @staticmethod
    def is_extra_course(url):
        """
        :param url: string
            Url of course to check
        :return: bool
            True iff the courses at the url given is an extra-curriculum course
        """

        check_keyword = "primo anno"  # if there is this keyword in source page, then the course is a normal course
        web_page = web.Webpage(url)
        return check_keyword not in web_page.source

    def create_course_from_item_table(self, course):
        """
        :param course: soup
            HTML item of a table
        :return: ADDCourse or ADDExtraCourse
            parse HTML item and find appropriate class to create
        """

        name = parser.html_stripper(
            course.a.find_all("img")[0]["alt"].title())  # find name of course
        url = course.a["href"]  # relative link
        url = urljoin(self.url, url)  # complete url
        return ADDExtraCourse(name, url) if self.is_extra_course(
            url) else ADDCourse(name, url)

    def get_course_list(self):
        """
        :return: []
            List of courses available in website
        """

        table = self.soup.find_all("table")[0]  # find table of courses
        courses = table.find_all("tr")  # find all rows
        courses = [self.create_course_from_item_table(course)
                   # parse raw HTML table item
                   for course in courses]  # loop through all items of table
        return courses


def bot():
    """
    :return: void
        Download entire database in andreadd webpage
    """

    course_list = ADDNotes().get_course_list()
    print("Found", len(course_list), "courses")

    for course in course_list:
        print("\tSelected course", course.name)
        course_directory = os.path.join(os.getcwd(), str(int(time.time())),
                                        course.name)
        Directory.create_new(
            course_directory)  # create new directory for course
        print("\tDownloading documents to", course_directory, "...")
        course.download_all_documents(course_directory)


if __name__ == '__main__':
    bot()
