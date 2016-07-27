import lxml.html
from lxml.etree import tostring
import dbhits
import helper
import requests
import re
from helper import prequests

def download():
	url = "http://mturkforum.com/forumdisplay.php?30-Great-HITS"
	r = prequests(url, "mturk")
	doc = lxml.html.document_fromstring(r.text)
	selector = "ol.threads li h3.threadtitle a.title"
	thread = doc.cssselect(selector)[0]
	threadUrl = "http://mturkforum.com/"+thread.get("href")
	#get last saved page
	print "found thread starting: ", threadUrl
	page = dbhits.getPage(threadUrl, "mturkForum")
	if not page:
		page = threadUrl
	r = prequests(page, "mturk")
	html = r.text
	while True:
		print r.url
		doc = lxml.html.document_fromstring(html)
		count = doc.cssselect("a.postcounter")
		#get posts
		posts = doc.cssselect("blockquote.postcontent.restore")
		for post in posts:
			#get mturk links, source
			source = "http://mturkforum.com/"+count.pop(0).get("href")
			links = helper.getLinks(tostring(post)) 
			print links
			#get comments
			if (len(links) == 1):
				mobj = re.search("(<b>Title:</b>)(.*?)(</font></div>)",tostring(post), re.I|re.S)
				if mobj:
					comments = tostring(post).replace(mobj.group(0),"").replace("\n","").replace("\t","").replace("&#13;", "")
					comments = lxml.html.fromstring(comments).text_content()
				else:
					#try different format
					hit = re.findall(r'<b>Title:</b>.*?</a>.*?</a>.*?</a>',tostring(post), re.DOTALL)
					if hit:
						comments =tostring(post).replace(hit[0],"").replace("\n","").replace("\t","").replace("&#13;", "")
						comments = lxml.html.fromstring(comments).text_content()
					else:
						comments = tostring(post).replace("\n","").replace("\t","").replace("&#13;","")
						comments = lxml.html.fromstring(comments).text_content()
			#antispam
			elif len(links) > 5:
				continue
			elif len(links) > 1:
				comments = ""
			if links:
				#get hit info
				for link in links:
					groupid = link.split("=")[1]
					info = helper.getHitInfo(groupid)
					if info:
				#add hit unless reward is zero or duplicate in database
						if not dbhits.checkDuplicate(link):
							dbhits.addHit(source, comments.encode("utf-8") , link, link, info["title"].encode("utf-8"), info["requester_name"], info["requester_id"], info["description"], info["reward"], info["quals"])
		#download next page
		links = doc.cssselect("a[rel='next']")
		if links:
			page = "http://mturkforum.com/"+links[0].get("href")
			#print nextpage
			r = prequests(page,"mturk")
			html = r.text 
		#reached last page
		else:
			dbhits.setPage(threadUrl, page,"mturkForum")
			return
def downloadWiki():
	url = "http://mturkwiki.net/forum/viewforum.php?f=2&sid=2639a6db184f465265020d52378a3d1c"
	r = requests.get(url)
	doc = lxml.html.document_fromstring(r.text)
	selector = "dt[title='No unread posts']"
	threadUrl = "http://mturkwiki.net/forum/"+doc.cssselect(selector)[3].cssselect("a")[0].get("href").replace("./","")
	#get last saved position
	threadUrl = threadUrl.split("&sid=")[0]
	page = dbhits.getPage(threadUrl,"mturkWiki")
	if not page:
		page = threadUrl
	r = requests.get(page)
	html = r.text
	while True:
		doc = lxml.html.document_fromstring(html)
		#get posts
		posts = doc.cssselect("div.postbody")
		for post in posts:
			#get mturk links, source
			if post.cssselect("h3 a"):
				source = threadUrl+post.cssselect("h3 a")[0].get("href")
			#post is ad skip
			else:
				continue
			links = helper.getLinks(tostring(post)) 
			#get comments
			post = post.cssselect("div.content")[0]
			if (len(links) == 1):
				hit = re.findall(r'<span style=\"font-weight: bold\">Title:.*?</a>.*?</a>.*?</a>',tostring(post), re.DOTALL)
				#wiki hit format
				if hit:
					comments =tostring(post).replace(hit[0],"").replace("\n","").replace("\t","").replace("&#13;", "")
					comments = lxml.html.fromstring(comments).text_content()
				else:
					comments = tostring(post).replace("\n","").replace("\t","").replace("&#13;","")
					comments = lxml.html.fromstring(comments).text_content()
			elif len(links) > 1:
				comments = ""
			if links:
				#get hit info
				for link in links:
					groupid = link.split("=")[1]
					info = helper.getHitInfo(groupid)
				#add hit
					if not dbhits.checkDuplicate2(link):
						if info is not None:
							dbhits.addHit2(source, comments , link, link, info["title"], info["requester_name"], info["requester_id"], info["description"], info["reward"], info["quals"], "")
					if not dbhits.checkDuplicate(link):
						if info is not None:
							dbhits.addHit(source, comments , link, link, info["title"], info["requester_name"], info["requester_id"], info["description"], info["reward"], info["quals"])
		#download next page
		links = doc.cssselect("a.right-box")
		if links:
			page = "http://mturkwiki.net/forum/"+links[0].get("href").replace("./","")
			r = prequests(page, "mturk")
			html = r.text 
		#reached last page
		else:
			#save to database
			dbhits.setPage(threadUrl, page, "mturkWiki")
			return
if __name__ == "__main__":
	#download()
	downloadWiki()
