# ljscrapper
Scrapper for LiveJournal blogs (it only scraps articles' titles and dates).

## Details
- Since LJ doesn't have a proper API, this tool can be useful if you are carefully reading some blogs.
- Right now this script only stores its data in {blogname}.json file per blog

## Requirements
- python3
- libraries:
  - bs4
  - requests

## How to
- To start you need to know:
  - blog name (like in url: **blogname**.livejournal.com)
  - id of any article (like in url: blogname.livejournal.com/**1337**.html)
- Run script in console with `python3 main.py` and follow instructions

## Examples


## TODO
- Add tags scrapping
- Add conversion to html-page with all the links
- Add DB support
