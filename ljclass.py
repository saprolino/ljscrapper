import requests
from bs4 import BeautifulSoup
import json
import re
import jinja2
import datetime
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
# https://www.livejournal.com/go.bml?journal={}&itemid={}}&dir=prev
# https://www.livejournal.com/go.bml?journal={}&itemid={}}&dir=next


class Blog:
    def __init__(self, blogname=None):
        self.blogname = "" if blogname == None else blogname

        self.articles = dict()
        # self.url_lj_template = "https://{}.livejournal.com/{}.html"
        # self.url_domain_template = "https://{}/{}.html"
        self.url_template = "https://{}.livejournal.com/{}.html"
        self.last_updated = None
        self.size = None
        self.ssl_enabled = False if "." in self.blogname else True
        self.url_prev_template = "https://www.livejournal.com/go.bml?journal={}&itemid={}&dir=prev"
        self.url_next_template = "https://www.livejournal.com/go.bml?journal={}&itemid={}&dir=next"
        self.shift = 16 + len(self.blogname)

    # self.shift = 1

    def parse(self, id):
        cookies_jar = requests.cookies.RequestsCookieJar()
        cookies_jar.set('prop_opt_readability', "1", domain='.livejournal.com', path='/')
        cookies_jar.set('adult_explicit', "1", domain='livejournal.com', path='/')
        # the_url = self.url_domain_template.format(self.blogname, id) if "." in self.blogname else self.url_lj_template.format(self.blogname, id)
        # print(the_url)
        # input()
        the_url = self.url_template.format(self.blogname, id)
        page = requests.get(the_url, cookies=cookies_jar, verify=self.ssl_enabled)
        data = page.text
        soup = BeautifulSoup(data, features="html.parser")
        title = soup.title.string[:-self.shift].rstrip()
        date = soup.findAll("time", {"class": "b-singlepost-author-date published dt-published"})
        if not len(date):
            date = soup.findAll("p", {"class": "aentry-head__date"})[0].getText().strip()
            date = datetime.datetime.strptime(date, "%B %d %Y, %H:%M")
            date = date.strftime("%Y-%m-%d %H:%M:%S")
        else:
            date = date[0].getText()
        tags = soup.findAll("span", {"class": "b-singlepost-tags-items"})
        if len(tags):
            tags = list(map(str.strip, tags[0].getText().split(", ")))
        else:
            tags = []
        self.articles[str(id)] = {"title": title, "date": date, "tags": tags}
        return "{} {} {} {}".format(id, date, title, tags)

    def getSomeId(self):
        if "." in self.blogname:
            url = 'https://' + self.blogname
            pattern = self.blogname + "\/[0-9]+\.html"
        else:
            url = 'https://' + self.blogname + '.livejournal.com'
            pattern = self.blogname + "\.livejournal\.com\/[0-9]+\.html"

        page = requests.get(url).text
        m = re.search(pattern, page).group()
        id = m.split("/")[-1][:-5]
        return id

    def getPreviousId(self, id):
        requestUrl = self.url_prev_template.format(self.blogname, id)
        page = requests.get(requestUrl, verify=self.ssl_enabled)
        if page.url == requestUrl:
            return 0
        else:
            return page.url.split("/")[-1][:-5]

    def getNextId(self, id):
        requestUrl = self.url_next_template.format(self.blogname, id)
        page = requests.get(requestUrl, verify=self.ssl_enabled)
        if page.url == requestUrl:
            return 0
        else:
            return page.url.split("/")[-1][:-5]

    def retrieveFromOldest(self, id, up_to=-1):
        current_id = id
        prev_id = self.getPreviousId(current_id)
        while current_id and up_to>=0:
            page = self.parse(current_id)
            current_id, prev_id = prev_id, self.getPreviousId(prev_id)
            print(page)
            up_to -= 1

    def getState(self):
        print("There are {} articles in your data".format(len(self.articles)))

    def retrieveFromNewest(self, id, up_to=-1):
        if id == -1:
            current_id = self.getSomeId()
        else:
            current_id = id
        next_id = self.getNextId(current_id)
        while current_id and up_to>=0:
            page = self.parse(current_id)
            current_id, next_id = next_id, self.getNextId(next_id)
            print(page)
            up_to -= 1

    def saveToFile(self, filename):
        self.last_updated = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.size = len(self.articles)
        with open(filename, 'w', encoding='utf8') as fp:
            json.dump({"blogname": self.blogname, "size": self.size, "updated": self.last_updated, "articles": self.articles}, fp, ensure_ascii=False, sort_keys=True,
                      indent=4)

    def readFromFile(self, filename):
        with open(filename, 'r', encoding='utf8') as fp:
            data = json.load(fp)
            self.blogname, self.articles = data["blogname"], data["articles"]
            self.ssl_enabled = False if "." in self.blogname else True
            self.shift = 16 + len(self.blogname)

    def anyNewer(self):
        if len(self.articles) == 0:
            return True
        newest = max(self.articles, key=lambda i: self.articles[i]["date"])
        return bool(self.getNextId(newest))

    def anyOlder(self):
        if len(self.articles) == 0:
            return True
        oldest = min(self.articles, key=lambda i: self.articles[i]["date"])
        return bool(self.getPreviousId(oldest))

    def retrieveDown(self, up_to=-1):  # takes the oldest article in self.articles and continues retrieving
        current_id = min(self.articles, key=lambda i: self.articles[i]["date"])
        self.retrieveFromOldest(current_id, up_to)

    def retrieveUp(self, up_to=-1):  # takes the oldest article in self.articles and continues retrieving
        current_id = max(self.articles, key=lambda i: self.articles[i]["date"])
        self.retrieveFromNewest(current_id, up_to)
