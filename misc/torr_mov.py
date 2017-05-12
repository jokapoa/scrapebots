import webbrowser

u = "https://torrentz2.eu//verifiedP?f="
f = "/home/stefano/tmp/m.txt"


def get_torrentz_url(q):
    torrentz_q = q.replace(" ", "+")
    return u + torrentz_q


def search_torrentz(q):
    url = get_torrentz_url(q)
    webbrowser.open(url)


def search_torrentz_from_file(path_in):
    lines = open(path_in, "r").readlines()
    for l in lines:
        search_torrentz(l.strip())


if __name__ == '__main__':
    search_torrentz_from_file(f)
