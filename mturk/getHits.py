import lxml.html
from lxml.etree import tostring
import requests
import dbhits
import helper
import re

#self is consumer object
def download():
	url = "http://www.reddit.com/r/hitsworthturkingfor/new"
	headers = {
		"Cache-Control":"max-age=0",
		"User-Agent":"Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.72 Safari/537.36",
		"Accept-Language":"en-US,en;q=0.8",
		"Connection":"keep-alive",
		"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
	}
	r = requests.get(url, headers = headers)
	#no need to decode as requests does it for you
	html = r.text
	doc = lxml.html.document_fromstring(html)
	selector = "div.entry.unvoted a.title"
	i = 0
	hits = []
	placeHolderTitle = dbhits.getTitle()
	print "placeholder: ", placeHolderTitle
	for a in doc.cssselect(selector):
		i += 1
		if i == 26:
			break
		url = "http://reddit.com"+a.get("href")
		r = requests.get(url, headers = headers)
		html = r.text
		doc2 = lxml.html.document_fromstring(html)
		#get main message
		selector2 = "div.usertext-body div.md"
		title = doc2.cssselect("p.title a")[0].text_content()
		if i == 1:
			firstTitle = title
		if title == placeHolderTitle:
			break
		titleWords = title.split()
		postobject = doc2.cssselect(selector2)[1]
		postWords = postobject.text_content().split()
		post = tostring(postobject).replace("\n","").replace("\t", "")
		wordsList = titleWords+postWords
		#sulfur boy format
		if "powered by " in post:
			comments = ""
		else: 
			comments = post
		source = r.url
		mturkLink = helper.getLink(post)
		if mturkLink:
			hit = {
				"source": source,
				"comments": comments,
				"mturkLink": "",
				"originalLink": mturkLink,
				"wordsList":wordsList
			}
			hits.append(hit)
	dbhits.putTitle(firstTitle)
	if hits:
		#login to amazon
		s = helper.loginAmazon()
		#scrape adfly pages for destination link
		hits = helper.getMturkLink(hits)
		newHits = []
		for hit in hits:
			if "mturk.com/mturk/searchbar" in hit["mturkLink"]:
				#convert mturk.com/mturk/searchbar to mturk.com/mturk/preview...may be >1
				newLinks = helper.convertSearchbar(hit["mturkLink"], hit["wordsList"],s)
				if newLinks:
					for link in newLinks:
						hit["mturkLink"] = link
						newHits.append(hit)
			else:
				newHits.append(hit)
		#get hit info
		#add hit to database
		for hit in newHits:
			groupid = hit["mturkLink"].split("=")[1]
			info = helper.getHitInfo(groupid)
			if info:
				if not dbhits.checkDuplicate2(hit["mturkLink"]):
					dbhits.addHit2(hit["source"], hit["comments"].encode("utf-8") , hit["mturkLink"],hit["originalLink"], info["title"].encode("utf-8"), info["requester_name"], info["requester_id"], info["description"].encode("utf-8"), info["reward"], info["quals"], "")
				if not dbhits.checkDuplicate(hit["mturkLink"]):
					#print "adding hit"
					#print "\t title: ", info["title"]
					#print "\t quals: ", info["quals"]
					#print "\t reward: ", info["reward"]
					print "added hit ", hit["source"]
					dbhits.addHit(hit["source"], hit["comments"].encode("utf-8") , hit["mturkLink"],hit["originalLink"], info["title"].encode("utf-8"), info["requester_name"], info["requester_id"], info["description"].encode("utf-8"), info["reward"], info["quals"])
	return
if __name__=="__main__":
	download()
