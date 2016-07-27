import lxml.html
from lxml.etree import tostring
import helper
import requests
import re
from helper import prequests
from tld import get_tld
url = "http://fortcollins.craigslist.org/sks/5133905999.html"
r = prequests(url, "posted:")
doc = lxml.html.document_fromstring(r.text)
selector = ".showcontact"
for a in doc.cssselect(selector):
	endofurl = a.get("href")
url = "http://"+get_tld(r.url)
newurl = url+endofurl
print newurl
r = prequests(newurl, "Reply Info")
f = open("text.txt", "wb")
f.write(r.text)
f.close()
