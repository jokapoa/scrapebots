# scrapebots

*Internet bots to scrape web-platforms*

[![Code Health](https://landscape.io/github/sirfoga/scrapebots/master/landscape.svg?style=flat
)](https://landscape.io/github/sirfoga/scrapebots/master) [![Code Climate](https://lima.codeclimate.com/github/sirfoga/scrapebots/badges/gpa.svg)](https://codeclimate.com/github/sirfoga/scrapebots) ![pylint Score](https://mperlet.de/pybadge/badges/0.00.svg)

[![FOSSA Status](https://app.fossa.io/api/projects/git%2Bhttps%3A%2F%2Fgithub.com%2Fsirfoga%2Fscrapebots.svg?type=shield)](https://app.fossa.io/projects/git%2Bhttps%3A%2F%2Fgithub.com%2Fsirfoga%2Fscrapebots?ref=badge_shield) [![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0) [![Open Source Love](https://badges.frapsoft.com/os/v1/open-source.svg?v=103)](https://opensource.org/licenses/Apache-2.0) [![Contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg?style=flat)](https://github.com/sirfoga/scrapebots/issues)


## Available bots
| name | description | data size |
| ------------- | ------------- | ------------- |
| [andreadd.it](bots/misc/andreadd.py) | download [Polimi](http://www.polimi.it/en/) books and notes | ~1GB |
| [Amazon](bots/amazon/amazon_items_scraper.py)  | parse items in classic Amazon page | DNF |
| [connemarathon](bots/conne_marathon/bot.py) | connemarathon (since 2002)  | ~30000 |
| [FSG media downloader](bots/misc/fsgmedia-downloader.py) | download pictures from (Samsung) FSG servers | ~4TB |
| [Github](bots/github/tester.py)  | use API token to get info about users, repos | DNF |
| [Google Images](bots/misc/google_image.py) | download images  | DNF |
| [Hackerrank](bots/misc/hackerrank.py) | download problems statements and solutions | DNF |
| [IMDB](bots/imdb) | scrape largets dataset of movies | DNF |
| [ITA industries](bots/ita_industries/cli.py) | italian industries data | DNF |
| [London Marathon](bots/london_marathon/fetch_details_urls.py) | download marathon results (since 2014)  | ~175000 |
| [NYC Marathon](bots/nyc_marathon/fetch_details.py) | download full marathon results (since 1970)  | ~1 million |
| [Rotten Tomaroes](bots/rottentomatoes/cli.py) | browse [Rotten Tomatoes](https://www.rottentomatoes.com/) database | DNF |
| [Torrent](bots/misc/torrent_downloader.py) | download .torrent files | DNF |
| [Torrentz](bots/misc/torr_mov.py) | open Torrentz queries | DNF |
| [Tour De France](bots/letour/cli.py) | results of Tour de France since 1903 | ~160000 |
| [ultra-marathon statisik](bots/statistik_ultramarathon) | ultra-marathon performances | ~3 million |

## TODO bots
| name | description | data size |
| ------------- | ------------- | ------------- |
| [Giro d'Italia](http://www.giroditalia.it/it/classifiche/) | results of Giro d'Italia | ~3500 |
| [index-of.es](http://index-of.es/) | programming books | DNF |

## Install
Usually just a few dependencies are needed:
- `pyhal`: `pip3 install pyhal --upgrade --force-reinstall`
- `bs4`: `pip3 install bs4 --upgrade --force-reinstall`
- `asyncio, asynchttp, asyncfiles`: `pip3 install asyncio asynchttp asyncfiles --upgrade --force-reinstall`


## Questions and issues
The [github issue tracker](https://github.com/sirfoga/scrapebots/issues) is **only** for bug reports and feature requests. Anything else, such as questions for help in using the library, should be posted as [pull requests](https://github.com/sirfoga/scrapebots/pulls).


## License
[Apache License](http://www.apache.org/licenses/LICENSE-2.0) Version 2.0, January 2004
