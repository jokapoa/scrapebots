from bs4 import BeautifulSoup

f = "~/Downloads/chrome/Amazon.com_ Raymond M. Smullyan_ Books, Biography, Blog, Audiobooks, Kindle.html"
soup = BeautifulSoup(open(f, "r").read(), "lxml")


def get_title_of_item(item):
    col_right = item.find_all("div", {"class": "a-fixed-left-grid-col a-col-right"})  # right column of item
    t = col_right[0].find_all("div", {"class": "a-row a-spacing-none"})  # divs containing title
    return t[0].a["title"]  # get title


def get_items_of_page(soup):
    return soup.find_all("div", {"class": "s-item-container"})


def get_titles_of_items_in_page(soup):
    items = get_items_of_page(soup)
    for i in items:
        yield get_title_of_item(i)


list(get_titles_of_items_in_page(BeautifulSoup(open(f, "r").read(), "lxml")))
