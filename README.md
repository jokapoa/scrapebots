# Scrapebots

*Many Internet bots to scrape various web-platforms*
<!-- [![Code Health](https://landscape.io/github/sirfoga/pygce/master/landscape.svg?style=flat
)](https://landscape.io/github/sirfoga/pygce/master) -->


## Available bots
- [Amazon](amazon/amazon_items_scraper.py): get items in classic Amazon page
- [Github](github/tester.py): use API token to get info about users, repos ...
- [Virgin London Marathon](london-marathon/cli.py): download marathon results
- [Rotten Tomatoes](rottentomatoes/cli.py): search movies in database
- [andreadd.it](misc/andreadd.py): download books and notes
- [Google Images](misc/google_image.py): download images
- [Hackerrank](misc/hackerrank.py): download problems statements and solutions
- [Torrentz](misc/torr_mov.py): open Torrentz pages
- [Torrent](misc/torrent_downloader.py): download .torrent files


## Install
Usually just a few dependencies are needed:
- `pyhal`: `pip3 install pyhal --upgrade --force-reinstall`
- `bs4`: `pip3 install bs4 --upgrade --force-reinstall`
- `asyncio, asynchttp, asyncfiles`: `pip3 install asyncio asynchttp asyncfiles --upgrade --force-reinstall`


## Questions and issues
The [github issue tracker](https://github.com/sirfoga/scrapebots/issues) is **only** for bug reports and feature requests. Anything else, such as questions for help in using the library, should be posted as [pull requests](https://github.com/sirfoga/scrapebots/pulls).


## License
[Apache License](http://www.apache.org/licenses/LICENSE-2.0) Version 2.0, January 2004
