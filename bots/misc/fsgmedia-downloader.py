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


"""
FSG media section downloader.
Steps:
    1. download archive of indexes from sitemap http://media.formulastudent.de/sitemap-index.xml
    2. each sitemap is a .gz file:
        2a. extract each archive to get .xml file
    3. loop through xml tree and get images urls
        3a. each image url is like http://media.formulastudent.de/FSG12/20121027-BOSCH-Engineering/i-5srDhs8/0/O/image.jpg
    4. parse url, create necessary folders and download images
"""

import gzip
import os
import time

from bs4 import BeautifulSoup
from hal.internet.web import Webpage
from hal.internet.web import download_url
from hal.wrappers.methods import handle_exceptions

# const vars
# folders
DOWNLOAD_FOLDER = os.path.join(os.getcwd(), "fsg-download")
SITEMAP_FOLDER = os.path.join(DOWNLOAD_FOLDER, "sitemaps")
IMAGES_FOLDER = os.path.join(DOWNLOAD_FOLDER, "images")

# urls
SITEMAP_URL = "http://media.formulastudent.de/sitemap-index.xml"
FSG_MEDIA_URL = "http://media.formulastudent.de/"
REDIRECT_MEDIA_URL = "https://photos.smugmug.com/"

# misc
MAX_LENGTH_VERBOSE_WORD = 32


def get_eta(start_time, percentage_completed):
    """
    :param start_time: float
        Time of start
    :param percentage_completed: float
        Percentage of done work by now
    :return: float
        Time left
    """

    time_now = time.time()  # measure time
    time_elapsed = time_now - start_time
    time_eta = 100.0 / percentage_completed * time_elapsed
    return time_eta


def get_sitemaps_urls():
    """
    :return: list of str
        List of sitemaps urls
    """

    sitemap_content = Webpage(SITEMAP_URL).get_html_source()
    soup = BeautifulSoup(sitemap_content, "lxml")
    sitemaps = soup.find_all("sitemap")[1:]  # discard base sitemap
    urls = []
    for s in sitemaps:
        url = str(s.loc.text)  # get url of sitemap
        sitemap_id = url.split("-")[-1].replace(".xml.gz", "")
        if int(
                sitemap_id) >= 0:  # TODO tune this to get only chunks (min: 0, max: 32)
            urls.append(url)

    return urls


def get_sitemap_content(url):
    """
    :param url: str
        Url of sitemap
    :return: str
        Sitemap content as xml
    """

    local_file_download = url.split("/")[-1]  # get name of file to download
    local_file_path = os.path.join(SITEMAP_FOLDER, local_file_download)
    download_url(url, local_file_path)  # download sitemap
    gzipper = gzip.GzipFile(local_file_path, "r")
    file_content = gzipper.read()  # unzip

    return file_content


def get_list_of_images_from_sitemap(sitemap):
    """
    :param sitemap: str
        Xml file content containing meta-data about images
    :return: list of str
        List of urls of all image
    """

    soup = BeautifulSoup(sitemap, "lxml")
    urlset = soup.find_all("urlset")[0]
    images = urlset.find_all("image:image")  # main images
    images_urls = []
    for i in images:
        url = i.find_all("image:url")[0].text
        images_urls.append(url)

    return images_urls


def download_image(url):
    """
    :param url: str
        Url of image to download
    :return: bool
        Tries to download image to right folder (parses url to get location); if successful returns True, otherwise False
    """

    relative_url = url.replace(FSG_MEDIA_URL,
                               "")  # get url relative to fsg servers
    tokens = relative_url.split("/")  # split url to directories
    img_name = tokens[-1]  # get image name
    download_folder = os.path.join(IMAGES_FOLDER, tokens[0],
                                   tokens[1])  # reproduce local relative url

    if not os.path.exists(download_folder):  # create necessary directories
        os.makedirs(download_folder)

    local_file = os.path.join(download_folder, img_name)  # get local file path
    if not os.path.exists(local_file):  # already downloaded -> skipping
        try:
            url = url.replace(FSG_MEDIA_URL,
                              REDIRECT_MEDIA_URL)  # make redirection to right servers
            download_url(url, local_file)  # download image
            return True
        except Exception as e:
            print("\t\t\tFailed download image ...",
                  url[-MAX_LENGTH_VERBOSE_WORD:], "\n")
            return False
    else:
        print("\t\t\tAlready downloaded ... skipping")
        return True


def prepare_download_folders():
    """
    :return: bool
        Tries to create necessary folders to download files in; if not successful returns False
    """

    try:
        if not os.path.exists(SITEMAP_FOLDER):
            os.makedirs(SITEMAP_FOLDER)

        if not os.path.exists(IMAGES_FOLDER):
            os.makedirs(IMAGES_FOLDER)

        return True
    except Exception as e:
        print(str(e))
        return False


@handle_exceptions
def main():
    """"
    :return: void
        FSG media section downloader
    """

    prepare_download_folders()
    sitemap_urls = get_sitemaps_urls()
    tot_sitemaps = len(sitemap_urls)

    timer_total = time.time()  # timer to time performance
    for j in range(len(sitemap_urls)):
        try:
            print("Getting content of sitemap ...",
                  sitemap_urls[j][-MAX_LENGTH_VERBOSE_WORD:])
            c = get_sitemap_content(sitemap_urls[j])
            print("Got content of sitemap")
            try:
                print("\tGetting images")
                images = get_list_of_images_from_sitemap(c)
                tot_images = len(images)
                print("\tGot images. Amount:", tot_images)

                timer_sitemap = time.time()  # timer to time performance
                for i in range(len(images)):
                    try:
                        print("\t\tDownloading image ...",
                              images[i][-MAX_LENGTH_VERBOSE_WORD:])
                        is_download_successful = download_image(
                            images[i])  # download image

                        # notify user of sitemap download progress
                        percentage = float(i + 1) / tot_images * 100.0
                        time_eta = get_eta(timer_sitemap,
                                           percentage)  # get eta
                        print("\t\tCompleted image", i + 1, "/", tot_images,
                              "(", "{:03.2f}".format(percentage), "%)")
                        print("\t\t\tETA sitemap", j + 1, "about",
                              "{:03.2f}".format(time_eta / 60.0), "' =",
                              "{:03.2f}".format(time_eta / (60.0 * 60.0)), "h")

                        # notify user of total download progress
                        percentage = float(i + 1) / (
                            tot_sitemaps * tot_images) * 100.0
                        time_eta = get_eta(timer_total, percentage)  # get eta
                        print("\t\t\tETA total about ",
                              "{:03.2f}".format(time_eta / 60.0), "' =",
                              "{:03.2f}".format(time_eta / (60.0 * 60.0)), "h")

                        if is_download_successful:
                            print("\t\tDownloaded")
                        else:
                            raise ValueError("Cannot download image")
                    except Exception as e:
                        print("\n[!] Failed downloading image ...",
                              images[i][-MAX_LENGTH_VERBOSE_WORD:], "\n")
            except Exception as e:
                print("\n[!] Failed getting images from sitemap ...",
                      sitemap_urls[j][-MAX_LENGTH_VERBOSE_WORD:], "\n")
        except Exception as e:
            print("\n[!] Failed getting content of sitemap ...",
                  sitemap_urls[j][-MAX_LENGTH_VERBOSE_WORD:], "\n")

        percentage = float(j + 1) / tot_sitemaps * 100.0
        time_eta = get_eta(timer_total, percentage)  # get eta
        print("\t\tCompleted sitemap", j + 1, "/", tot_sitemaps, "(",
              "{:03.2f}".format(percentage), "%)")
        print("\t\tETA total:", "{:03.2f}".format(time_eta / 60.0), "' =",
              "{:03.2f}".format(time_eta / (60.0 * 60.0)),
              "h")


if __name__ == '__main__':
    main()
