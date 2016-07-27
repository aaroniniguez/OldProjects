import lxml.html
import ScraperJavascript
import Scraper
import re
from xvfbwrapper import Xvfb
import json
import requests
import sys
from lxml.etree import tostring
import pprint
import time
#import dbhits
from gevent import Timeout
import random
#use proxy's with requests
def isalive(url):
	r = requests.get(url)
	m_obj = re.search("did not match any HITs|no more available HITs",r.text, re.IGNORECASE)
	if m_obj is not None:
		return False
	return True
def prequests(url, keyword, protocol="get", payload=None, session = None):
	headers = {
		"Cache-Control":"max-age=0",
		"User-Agent":"Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.72 Safari/537.36",
		"Host":"www.mturk.com",
		"Accept-Language":"en-US,en;q=0.8",
		"Connection":"keep-alive",
		"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
	}
	import sqlite3
	connectDb = sqlite3.connect("/data/proxies/proxies.db")
	query = connectDb.cursor()
	#get all proxies from database
	query.execute("""select proxy from proxies where success='1'""")
	workerips = query.fetchall()
	print workerips
	ips = []
	for ip in workerips:
		ip = ip[0]
		ips.append(ip.rstrip("\n"))
	while True:
		#randomize ips
		random.shuffle(ips)
		ip = ips.pop(0)
		ips.append(ip)
		try:
			r = bytearray()
			text = ""
			with Timeout(30,False):
				if protocol == "get":
					if session:
						r = session.get(url, headers=headers, proxies={"http":"http://"+ip})
					else:
						r = requests.get(url, headers=headers, proxies={"http":"http://"+ip})
				elif protocol == "post":
					if session:
						r = session.post(url, headers=headers, data=payload, proxies={"http":ip})
					else:
						r = requests.post(url, headers=headers, data=payload, proxies={"http":ip})
				text = r.text
			if not (len(text)):
				raise Exception("too slow")
			#4xx or 5xx response error raised
			r.raise_for_status()
			#sometimes using proxies causes a different page to load than the one you want, search for keyword, title
			m_obj = re.search(keyword, text , re.IGNORECASE)
			if m_obj is None:
				raise Exception(keyword+" not found at "+url)
		except requests.ConnectionError:
			print "connection error"
		except requests.HTTPError:
			#stop scraping, the page cannot be loaded
			#raise Exception("invalid http response"+ str(r.status_code) +" on "+ url)
			print "invalid http response"
		except requests.Timeout:
			print "timeout"
		except requests.TooManyRedirects:
			print "too many redirects"
		except Exception, e:
			print e
		else:
			print "\t using ip ", ip
			return r
#test html output by writing to file
def write(html, result = "./result.html"):
	f = open(result, "wb")
	f.write(html.encode("utf-8"))
	f.close()
def loginAmazon():
	s = requests.Session()
	loginPage = "https://www.mturk.com/mturk/beginsignin"
	r = prequests(url = loginPage,keyword="mturk", session=s)
	print "first page: ", r.url[:40]
	write(r.text)
	doc = lxml.html.document_fromstring(r.text)
	selector = "input[name=awscbid]"
	#login failed, blocked as robot by amazon
	if not doc.cssselect(selector):
		print r.text
		print "\tError: blocked"
		loginAmazon()
	for token in doc.cssselect(selector):
		awscbid = token.get("value")
	selector = "input[name=awssig]"
	for token in doc.cssselect(selector):
		awssig = token.get("value")
	selector = "form[name=ssopForm]"
	for token in doc.cssselect(selector):
		action = token.get("action")
	selector = "input[name=awscbctx]"
	for token in doc.cssselect(selector):
		awscbctx = token.get("value")
	payload = {
		"awscbid":awscbid,
		"awscbctx":awscbctx,
		"awscredential":"",
		"awsnoclientpipeline":"true",
		"awssig":awssig,
		"awsstrict":"false",
		"awsturknosubway":"true",
		"wa":"wsignin1.0",
		"wctx":awscbctx,
		"wreply":"https://www.mturk.com:443/mturk/endsignin",
		"wtrealm":awscbid,
		"email":"aaroniniguez1@gmail.com",
		"action":"sign-in",
		"password":"Impossible123",
		"Continue.x":"61",
		"Continue.y":"10"
	}
	r = prequests(url = 'https://www.amazon.com'+action,keyword="mturk", protocol="post",session = s, payload=payload)
	print "\tsecond url ", r.url[:40]
	write(r.text)
	return s
def convertSearchbar(url, wordsList,s):
	newLinks = []
	r = s.get(url)
	#check if hits exist
	if ("HITs containing" in r.text) or ("HITs Created" in r.text):
		doc = lxml.html.document_fromstring(r.text)
		titlesList = [a.text_content().replace("\n", "").replace("\t", "").strip().split() for a in doc.cssselect("a.capsulelink")]
		#get group id or hit id or each hit info section
		hitsinfo = [tostring(span) for span in doc.cssselect("span.capsulelink")]
		ids = []
		for hitinfo in hitsinfo:
			onehitid = re.search("(?<=groupId=).{30}",hitinfo,re.IGNORECASE)
			if not onehitid:
				onehitid = re.search("(?<=hitId=).{30}",hitinfo,re.IGNORECASE)
			ids.append(onehitid.group(0))
		titles = []
		counts = []
		for title in titlesList:
			count = len(set(wordsList) & set(title))
			title  = " ".join(title)
			titles.append(title)
			counts.append(count)
		m = max(counts)
		indices = [i for i, j in enumerate(counts) if j == m]
		hitIdMatches = []
		for i in indices:
			hitIdMatches.append(ids[i])
		#add hit(s) to list
		for hitId in hitIdMatches:
			#add hit
			mturkLink = "https://www.mturk.com/mturk/preview?groupId="+hitId
			newLinks.append(mturkLink)
	return newLinks
def validPreviewLink(url):
	#check syntax of url
	if ("mturk.com/mturk/preview?groupId=" not in url):
		return False
	else:
		container = url.split("=")
		if len(container[1]) is not 30:
			return False
	#now scrape the page, check for invalid page
	r = requests.get(url)
	if "Invalid URL parameters" in r.text:
		print "invalid url params, preview link is bad"
		return False
	if isalive(url):
		print "alive link ", url
		return True
	print "dead link, ", url
	return False
def getLinks(html):
	links = []
	link = ""
	doc = lxml.html.document_fromstring(html)
	for a in doc.cssselect("a"):
		url = a.get("href")
		if validPreviewLink(url):
			links.append(url)
	return links
def getLink(html):
	link = ""
	doc = lxml.html.document_fromstring(html)
	for a in doc.cssselect("a"):
		url = a.get("href")
		if ("mturk.com/mturk/searchbar" in url) or (validPreviewLink(url)):
			link = url
			return link
		if "adf.ly" in url:
			link = url
	#only add listing that has link
	if link == "":
		return None
	else:
		return link
def getMturkLink(hits):
	#set up server
	args = {"nolisten":"tcp"}
	vdisplay = Xvfb(**args)
	vdisplay.start()
	adflyLinks = []
	newHits = []
	for hit in hits:
		if "adf.ly" in hit["originalLink"]:
			adflyLinks.append(hit["originalLink"])
		else:
			#they're the same
			hit["mturkLink"] = hit["originalLink"]
			newHits.append(hit)
	if adflyLinks:
		r = ScraperJavascript.Render(adflyLinks)  
		for adflyurl in r.data:
			html = r.data[adflyurl]
			if html:
				doc = lxml.html.document_fromstring(html)
				selector = "a#skip_button"
				for a in doc.cssselect(selector):
					mturkurl = a.get("href")
					if ("mturk.com/mturk/searchbar" not in mturkurl) and ("mturk.com/mturk/preview" not in mturkurl):
						mturkurl = None
			#page had 400-500 error
			else:
				mturkurl = None
			for hit in hits:
				if hit["originalLink"] == adflyurl:
					#don't add the hits with no mturkurl
					if mturkurl:
						hit["mturkLink"] = mturkurl
						newHits.append(hit)
		#delete pyqt before stoping the server
		del r
	vdisplay.stop()
	return newHits
def getHitInfo(groupid):
	hitinfo = {}
	url = "http://mturk-tracker.com/api/hitgroupcontent/?format=json&limit=1&group_id="+groupid
	r = requests.get(url)
	#mturk tracker didn't work
	if "total_count\": 0}" in r.text:
		#try to scrape
		r = requests.get("https://www.mturk.com/mturk/preview?groupId="+groupid)
		if "accept_hit.gif" in r.text:
			doc = lxml.html.document_fromstring(r.text)
			reward = doc.cssselect("span.reward")[0].text_content().replace("$","")
			div = doc.cssselect("div[style=\"white-space:nowrap; overflow:hidden; text-overflow:ellipsis;\"]")[0]
			title = div.text_content().strip().replace("\n","").replace("\t","")
			td = doc.cssselect("td.capsule_field_text[width=\"100%\"]")[0].text_content()
			requester_name = td.strip().replace("\t","").replace("\n","")
			qualifications = doc.cssselect("td[colspan=\"11\"] table tr td.capsule_field_text")[0]
			quals = qualifications.text_content().strip().replace("\n","").replace("\t","")
			requester_id = doc.cssselect("input[name=\"requesterId\"]")[0].get("value")
			description = ""
			reward = float(reward.replace("$", ""))
		#last resort, set all values to null
		else:
			requester_id = ""
			title = ""
			requester_name = ""
			description = ""
			reward = ""
			quals = ""
	else:
		hitObject = json.loads(r.text)["objects"][0]
		requester_id = hitObject["requester_id"]
		title = hitObject["title"]
		requester_name = hitObject["requester_name"]
		description = hitObject["description"]
		reward = hitObject["reward"]
		qualifications = hitObject["qualifications"]
		if "<img src=" in qualifications:
			quals = ["none"]
			quals = ",".join(quals)
		else:
			quals = [x.strip() for x in qualifications.split(",")]
			quals = quals[0::3]
			quals = ",".join(quals)
	hitinfo["requester_id"] = requester_id
	hitinfo["title"] = title
	hitinfo["requester_name"] = requester_name
	hitinfo["description"] = description
	hitinfo["reward"] = reward
	hitinfo["quals"] = quals
	#anti spam, weed out the bad hits

	##check db for bad requesters.
	if dbhits.checkRequester(requester_name) is False:
		print "requester is bad"
		return None
	if reward <= .05:
		print "reward equal to or less than 5"
		return None
	return hitinfo
if __name__ == "__main__":
	i = 1
	while True:
		i = i +1
		if i == 10: 
			break
		loginAmazon()
