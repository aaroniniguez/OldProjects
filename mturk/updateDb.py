import Scraper
from urlparse import urlparse
import re
import dbhits
import helper
s = Scraper.Scraper()
def runf(self, url):
	r = self.download(url, "alt='mechanical turk'")
	m_obj = re.search("did not match any HITs|no more available HITs",r.text, re.IGNORECASE)
	if m_obj is not None:
		print "\tkilled"
		dbhits.changeLife(url)	
	else:
		print "\talive"
	return 
links = dbhits.getLinks()
#links = ["https://www.mturk.com/mturk/preview?groupId=2E3PVP3TVOK527O8SSYQIO0I0YX14B"]
s.run(links, runf)
