import sys  
from PyQt4.QtGui import *  
from PyQt4.QtCore import *  
from PyQt4.QtWebKit import *  
from xvfbwrapper import Xvfb
import lxml.html
import requests

#takes in a list of urls
#returns dict mapping url to html
#if http errors 400-500, None in place of html
#uses requests module to check for http errors

class Render(QWebPage):  
	def __init__(self, urls):  
		self.app = QApplication(sys.argv)  
		QWebPage.__init__(self)  
		self.urls = urls  
		self.data = {}
		self.newpage = QWebPage()
		self.crawl()  
		self.app.exec_()  
	def crawl(self):  
		#important! delete teh page object, pyqt doesn't want to let it go.
		self.newpage.deleteLater()
		if self.urls:  
			url = self.urls.pop(0)
			#check for http errors
			try:
				r = requests.get(url)
				r.raise_for_status()
			except requests.HTTPError:
				print "invalid response code ", r.status_code
				self.data[url] = None
				self.crawl()
			else:
				print 'crawling', url
				self.t = QTimer(timeout=self._loadFinished,singleShot=True)
				self.t.setInterval(8000)
				self.newpage = QWebPage()
				self.newpage.loadFinished.connect(self.t.start)
				self.newpage.mainFrame().load(QUrl(url))  
				print "\tmainframe loaded"
		else:  
			self.app.quit()  
	def _loadFinished(self):
		mybytes =  self.newpage.bytesReceived()
		frame = self.newpage.mainFrame()
		url = str(frame.url().toString())  
		print "\t crawling url ",url," finished, getting html"
		html = frame.toHtml().__str__().encode("utf-8")
		doc = lxml.html.document_fromstring(html)
		selector = "a#skip_button"
		for a in doc.cssselect(selector):
			mturkurl = a.get("href")
			if mturkurl == None:
				print "NOOOOOOOOOOOOOOOOOOOOOO"
				self.urls.append(url)
			else:
				print "\tfound ",mturkurl
				self.data[url] = html  
		self.crawl()
if __name__ == "__main__":
	#set up server
	args = {"nolisten":"tcp"}
	vdisplay = Xvfb(**args)
	vdisplay.start()
	urls = ['http://adf.ly/SQOLM', 'http://adf.ly/SQ2P5', 'http://adf.ly/SQ6UA']  
	r = Render(urls)  
	print r.data.keys()
	#delete pyqt before stoping the server
	del r
	vdisplay.stop()
