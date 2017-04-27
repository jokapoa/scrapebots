# Scrapebots

*Many Internet bots to scrape various web-platforms*

[![Code Health](https://landscape.io/github/sirfoga/scrapebots/master/landscape.svg?style=flat
)](https://landscape.io/github/sirfoga/scrapebots/master)


## Available bots
| name | description | data size |
| ------------- | ------------- | ------------- |
| [Amazon](amazon/amazon_items_scraper.py)  | parse items in classic Amazon page  | DNF |
| [Github](github/tester.py)  | use API token to get info about users, repos ...  | DNF |
| [Virgin London Marathon](london_marathon/fetch_details_urls.py)  | download marathon results (since 2014)  | ~175000 |
| [andreadd.it](misc/andreadd.py) | download books and notes  | ~1GB |
| [Google Images](misc/google_image.py) | download images  | DNF |
| [Hackerrank](misc/hackerrank.py) | download problems statements and solutions  | DNF |
| [Torrentz](misc/torr_mov.py) | open Torrentz queries | DNF |
| [Torrent](misc/torrent_downloader.py) | download .torrent files | DNF |
| [FSG media downloader](misc/fsgmedia-downloader.py) | download pictures from (Samsung) FSG servers | ~4TB |
| [NYC Marathon](nyc_marathon/fetch_details.py) | download full marathon results (since 1970)  | ~1 million |


## TODO bots
| name | description | data size |
| ------------- | ------------- | ------------- |
| [ultra-marathon statisiken](http://statistik.d-u-v.org/geteventlist.php?year=all&dist=all&country=all&page=1) | ultramarathon performances | ~3 million |
| [connemarathon (with pdf -> text conversion)](http://www.connemarathon.com/results/) | connemarathon (since 2002)  | ~300000 |


## Install
Usually just a few dependencies are needed:
- `pyhal`: `pip3 install pyhal --upgrade --force-reinstall`
- `bs4`: `pip3 install bs4 --upgrade --force-reinstall`
- `asyncio, asynchttp, asyncfiles`: `pip3 install asyncio asynchttp asyncfiles --upgrade --force-reinstall`


## Questions and issues
The [github issue tracker](https://github.com/sirfoga/scrapebots/issues) is **only** for bug reports and feature requests. Anything else, such as questions for help in using the library, should be posted as [pull requests](https://github.com/sirfoga/scrapebots/pulls).


## License
[Apache License](http://www.apache.org/licenses/LICENSE-2.0) Version 2.0, January 2004
