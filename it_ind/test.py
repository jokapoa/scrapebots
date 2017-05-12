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


from urllib.parse import urlencode

from bs4 import BeautifulSoup
from selenium import webdriver

VALUE_NOT_FOUND = str("DNF")
PATH_TO_CHROMEDRIVER = "/home/stefano/Coding/misc/chromedriver"


def get_text_or_dnf(raw_html):
    """
    :param raw_html: str
        Raw HTML snippet to parse
    :return: str
        .text field or DNF value
    """

    try:
        return str(raw_html.text).strip()
    except:
        return VALUE_NOT_FOUND


class GoogleSearchBot(object):
    """ Selenium bot to search Google data """

    BROWSER_WAIT_TIMEOUT_SECONDS = 3

    def __init__(self, chromedriver_path):
        """
        :param chromedriver_path: str
            Path to Chrome driver to use as browser
        """

        object.__init__(self)
        self.browser = webdriver.Chrome(chromedriver_path)

    @staticmethod
    def _get_search_url(query, page=0, per_page=10, lang="en"):
        # note: num per page might not be supported by google anymore (because of google instant)

        params = {
            "nl": lang,
            "q": query.encode("utf8"),
            "start": page * per_page,
            "num": per_page
        }
        params = urlencode(params)
        return u"http://www.google.com/search?" + params

    @staticmethod
    def _get_name(li):
        """Return the name of a google search."""

        a = li.find("a")
        # return a.text.encode("utf-8").strip()
        if a is not None:
            return a.text.strip()
        return None

    @staticmethod
    def _get_link(li):
        """Return external link from a search."""

        a = li.find("a")
        # return a.text.encode("utf-8").strip()
        if a is not None:
            return a["href"].strip()
        return None

    @staticmethod
    def _get_description(li):
        """Return the description of a google search.
        TODO: There are some text encoding problems to resolve."""

        sdiv = li.find("div", attrs={"class": "s"})
        if sdiv:
            stspan = sdiv.find("span", attrs={"class": "st"})
            if stspan is not None:
                return stspan.text.strip()
        else:
            return None

    def parse_page_results(self, html):
        """
        :return: [] of {}
            Each dict is a result of the query browser has just made
        """

        results = []
        soup = BeautifulSoup(html, "html.parser")
        soup = soup.find_all("div", {"class": "_NId"})[-1]
        divs = soup.findAll("div", attrs={"class": "rc"})
        for d in divs:
            name = self._get_name(d)
            link = self._get_link(d)
            description = self._get_description(d)
            results.append(
                {
                    "name": name,
                    "link": link,
                    "description": description
                }
            )
        return results

    def get_search_results(self, query):
        """
        :param query: str
            Words to search
        :return: void
            Browser navigates to Google page, search query and returns list of results
        """

        try:
            self.browser.get(
                self._get_search_url(query)
            )
            results = self.parse_page_results(self.browser.page_source)
        except:
            results = []
            print("Errors while searching for \"", query, "\"")

        return results


def main():
    bot = GoogleSearchBot(PATH_TO_CHROMEDRIVER)
    queries = [
        "FRUCTORO S.R.L.", "10 X 3 S.N.C. DI FONTANA & SCHIAVON", "2 EMME SNC DI MARCON TIZIANO & C.",
        "2A INFINITY SOLUTIONS DI AGNOLETTO ALBERTO", "2I RETE GAS S.P.A.", "2M OFFICINE MECCANICHE S.R.L.",
        "2M PAINT DI MARTIGNAGO MIRKO", "3 BI - R.B. DI BIANCHIN R. E MORETTO M. S.N.C.", "3 ESSE S.R.L.",
        "3 G S.N.C. DI GOBBETTO MAURIZIO & C.", "3 INVESTIMENTI DI VITTORIO MARCON & C. S.S.",
        "3EMME S.A.S. DI LORENZON MICHELE & C.", "3EMME S.A.S. DI LORENZON MICHELE & C.", "CAVALLIN RAFFAELA",
        "DAMARIDA SAS DI CAVALLIN ANNAMARIA & C.", "A.C. AUTOTRASPORTI DI CAUDURO ANTONELLO",
        "A.M. DI MARTIGNON ALESSIO", "A.M.O RESTAURANT SNC DI LUIGI E MAURO OROFALO", "A.S.D. PISCINA DI QUINTO",
        "ABC ACQUATECH S.R.L.", "ABITA IMMOBILIARE S.R.L.", "ABLEREX ELECTRONICS ITALY S.R.L.", "ACACIA NICOLA",
        "ACADIA SRLS", "ACCADEMIA STUDIO SRL", "ACCONCIATORE MASCHILE RUDY DI MILAN RUDI",
        "ASTREA S.N.C. DI GATTO ENRICO & C.", "ACQUALIVING S.R.L.", "CONDOTTA CLAUDIO",
        "CASSA DI RISPARMIO DEL VENETO S.P.A.", "ADAMI MARIA", "ADAMI ROMEO", "ADASTRA SRL",
        "ADL AMERICAN DATALINE S.R.L.", "AEMME DI DE MARCHI MARISA & C. S.N.C.",
        "AEP S.A.S. DI BARATELLA ALESSANDRO & C.", "AERRE SERVICE DI RENOSTO ANTONIO",
        "AFRA E TOBIA SCARPA & C. - S.N.C.", "AGENTI LIBRALESSO EZIO E CARRARO EMANUELE S.N.C.", "AGENZIA VIOLA S.R.L.",
        "AGGIO S.A.S. DI MERSIA AGGIO & C.", "AGO.FIL S.R.L.", "M.J.A. SOCIETA' A RESPONSABILITA' LIMITATA",
        "AGRI AGGIO  S.N.C. DI AGGIO MAURO  E C.",
        "ASSICURAZIONI RONCATO DI RONCATO M. & C. - SOCIETA' IN NOME COLLE TTIVO",
        "AGRICOLA 5 SOCIETA' AGRICOLA SOCIETA' SEMPLICE", "AGRICOLA ANTIGA S.R.L.", "HAIR GALLERY DI GROLLO SIMONETTA",
        "AGRICOLA SAN GIOVANNI - SOCIETA' SEMPLICE"
    ]
    queries = [str(q).strip() for q in queries]  # strip
    for q in queries:
        results = bot.get_search_results(q)
        results = results[:3]  # get only top 3 results
        print(q)
        for r in results:
            print(r)
        print("\n")


if __name__ == '__main__':
    main()
