import dbhits
import helper
import sys

source = "http://thehitfinder.com"
link = sys.argv[1]
comments = sys.argv[2]
#validate link
if helper.validPreviewLink(link):
	#get hit info
	groupid = link.split("=")[1]
	info = helper.getHitInfo(groupid)
	if info:
		#do no add duplicate in database
		if not dbhits.checkDuplicate2(link):
			dbhits.addHit2(source, comments.encode("utf-8") , link, link, info["title"].encode("utf-8"), info["requester_name"], info["requester_id"], info["description"], info["reward"], info["quals"], "")
		if not dbhits.checkDuplicate(link):
			dbhits.addHit(source, comments.encode("utf-8") , link, link, info["title"].encode("utf-8"), info["requester_name"], info["requester_id"], info["description"], info["reward"], info["quals"])
