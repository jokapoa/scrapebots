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


from .search_engines import PagineGialleSearchBot

PATH_TO_CHROMEDRIVER = "/home/stefano/Coding/misc/chromedriver"


def main():
    bot = PagineGialleSearchBot(PATH_TO_CHROMEDRIVER)
    queries = [
        ("FRUCTORO S.R.L.", "31055"),
        ("10 X 3 S.N.C. DI FONTANA & SCHIAVON", "31055"),
        ("2 EMME SNC DI MARCON TIZIANO & C.", "31050"),
        ("2A INFINITY SOLUTIONS DI AGNOLETTO ALBERTO", "31040"),
        ("2I RETE GAS S.P.A.", "31055"),
        ("2M OFFICINE MECCANICHE S.R.L.", "31055"),
        ("2M PAINT DI MARTIGNAGO MIRKO", "31040"),
        ("3 BI - R.B. DI BIANCHIN R. E MORETTO M. S.N.C.", "31040"),
        ("3 ESSE S.R.L.", "31040"),
        ("3 G S.N.C. DI GOBBETTO MAURIZIO & C.", "31040"),
        ("3 INVESTIMENTI DI VITTORIO MARCON & C. S.S.", "31055"),
        ("3EMME S.A.S. DI LORENZON MICHELE & C.", "31050"),
        ("3EMME S.A.S. DI LORENZON MICHELE & C.", "31055"),
        ("CAVALLIN RAFFAELA", "31036"),
        ("DAMARIDA SAS DI CAVALLIN ANNAMARIA & C.", "31036"),
        ("A.C. AUTOTRASPORTI DI CAUDURO ANTONELLO", "31040"),
        ("A.M. DI MARTIGNON ALESSIO", "31050"),
        ("A.M.O RESTAURANT SNC DI LUIGI E MAURO OROFALO", "31050"),
        ("A.S.D. PISCINA DI QUINTO", "31055"),
        ("ABC ACQUATECH S.R.L.", "31040"),
        ("ABITA IMMOBILIARE S.R.L.", "31055"),
        ("ABLEREX ELECTRONICS ITALY S.R.L.", "31050"),
        ("ACACIA NICOLA", "31050"),
        ("ACADIA SRLS", "31055"),
        ("ACCADEMIA STUDIO SRL", "31055"),
        ("ACCONCIATORE MASCHILE RUDY DI MILAN RUDI", "31055"),
        ("ASTREA S.N.C. DI GATTO ENRICO & C.", "31036"),
        ("ACQUALIVING S.R.L.", "31055"),
        ("CONDOTTA CLAUDIO", "31036"),
        ("CASSA DI RISPARMIO DEL VENETO S.P.A.", "31036"),
        ("ADAMI MARIA", "31040"),
        ("ADAMI ROMEO", "31040"),
        ("ADASTRA SRL", "31055"),
        ("ADL AMERICAN DATALINE S.R.L.", "31055"),
        ("AEMME DI DE MARCHI MARISA & C. S.N.C.", "31055"),
        ("AEP S.A.S. DI BARATELLA ALESSANDRO & C.", "31050"),
        ("AERRE SERVICE DI RENOSTO ANTONIO", "31055"),
        ("AFRA E TOBIA SCARPA & C. - S.N.C.", "31040"),
        ("AGENTI LIBRALESSO EZIO E CARRARO EMANUELE S.N.C.", "31050"),
        ("AGENZIA VIOLA S.R.L.", "31055"),
        ("AGGIO S.A.S. DI MERSIA AGGIO & C.", "31055"),
        ("AGO.FIL S.R.L.", "31055"),
        ("M.J.A. SOCIETA' A RESPONSABILITA' LIMITATA", "31036"),
        ("AGRI AGGIO  S.N.C. DI AGGIO MAURO  E C.", "31055"),
        ("ASSICURAZIONI RONCATO DI RONCATO M. & C. - SOCIETA' IN NOME COLLE TTIVO", "31036"),
        ("AGRICOLA 5 SOCIETA' AGRICOLA SOCIETA' SEMPLICE", "31055"),
        ("AGRICOLA ANTIGA S.R.L.", "31040"),
        ("HAIR GALLERY DI GROLLO SIMONETTA", "31036"),
        ("AGRICOLA SAN GIOVANNI - SOCIETA' SEMPLICE", "31050")
    ]
    for q in queries:
        results = bot.get_search_results(q[0], q[1])
        results = results[:3]  # get only top results
        print(q)
        for r in results:
            print(r)
        print("\n")


if __name__ == '__main__':
    main()
    # bot = GoogleSearchBot(PATH_TO_CHROMEDRIVER)
    # bot.browser.get("https://www.google.com")
