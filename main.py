import requests
from bs4 import BeautifulSoup
import os
from ljclass import *
import sys
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

blogname = input("Input blogname: ")
# blogname = "livejournal"

# url_lj_template = "https://{}.livejournal.com/"
# url_domain_template = "https://{}/"
url_template = "https://{}.livejournal.com/"
the_url = url_template.format(blogname)
x = requests.get(the_url, verify=False).status_code

if x == 404:
	print("This blog doesn't exist.")
	sys.exit()
else:
	print("This blog exists...")

chunk_size = 10
if len(sys.argv) == 2:
	chunk_size = int(sys.argv[1])

directory = "data"
ext = ".json"

location = directory + "/" + blogname + ext

try:
	f = open(location)
	f.close()
	print("Using existing file...")
	a = Blog()
except FileNotFoundError:
	print("File doesn't exist, making a new one ({})...".format(location))
	#id = input("Input some article's id: ")
	a = Blog(blogname)
	a.retrieveFromNewest(-1, 1)
	a.saveToFile(location)

a.readFromFile(location)

#52504

while a.anyOlder():
	a.retrieveDown(chunk_size)
	a.saveToFile(location)

while a.anyNewer():
	a.retrieveUp(chunk_size)
	a.saveToFile(location)

a.getState()
#1008373

#print(a.articles)
#a.readFromFile("result.json")
#print(a.articles)
