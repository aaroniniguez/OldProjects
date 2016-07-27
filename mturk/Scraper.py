import gevent.monkey
gevent.monkey.patch_all()
from gevent.queue import Queue
from gevent import Greenlet
import re
import random
import requests
from gevent import Timeout
import time
import gevent
import helper

tasks = Queue()
results = Queue()
ips = Queue()

#to do
#if you have less number of work than workers make multiple workers work on the same work and see who finishes first

TIMEOUT = 30 #kill open connectino after 20 seconds
WAITTIME = 5 #time to wait before using same ip

class Consumer(Greenlet):
	def __init__(self,ip,tasks,results,ips, runf, workLoad):
		Greenlet.__init__(self)
		self.workLoad = workLoad
		self.tasks = tasks
		self.results = results
		self.ips = ips
		self.curip = ip
		self.runf = runf
		#this ip has not been used yet
		self.iptime = 0
	def _run(self):
		while not self.tasks.empty():
			url = self.tasks.get()
			#run the user given function on each task
			self.runf(self, url)
			break
		#return the ip so other workers can use it	
		ipdic = {self.curip:self.iptime}
		self.ips.put(ipdic)
		return 
	def getNewIp(self):
		if self.ips.empty() == False:
			ipdic = self.ips.get()
			self.curip = ipdic.keys()[0]
			self.iptime = ipdic[self.curip]
		return
	def download(self,url,keyword):
		numtries = 0
		while True:
			numtries += 1
			if numtries >= 2:
				#get new ip if one exists
				self.getNewIp()
				numtries = 1
			curtime = time.time()
			diftime = curtime - self.iptime;
			#if (self.iptime != 0) and (diftime < WAITTIME):
			 #wait 5 to 6 seconds in total, before using the same proxy
			#	gevent.sleep(random.uniform(WAITTIME-diftime,WAITTIME+1-diftime))
			try:
				r = bytearray()
				text = ""
				with Timeout(TIMEOUT,False):
					#just use server ip instead of having to search for a working proxy ip
					#to do: fix this...
					if self.workLoad == 1:
						r = requests.get(url)
					else:
						r = requests.get(url, proxies={"http":self.curip})
					text = r.text
				if not (len(text)):
					raise Exception("too slow")
				if "You have exceeded the maximum allowed page request rate for this website." in text:
					raise Exception("maximum allowed requests")
				#4xx or 5xx response error raised
				r.raise_for_status()
				#sometimes using proxies causes a different page to load than the one you want, search for keyword, title
				m_obj = re.search(keyword, text , re.IGNORECASE)
				if m_obj is None:
					helper.write(r.text,self.curip.replace(".",""))
					raise Exception(keyword+" not found at "+url)
			except requests.ConnectionError:
				print "connection error"
			except requests.HTTPError:
				#stop scraping, the page cannot be loaded
				raise Exception("invalid http response"+ str(r.status_code) +" on "+ url)
			except requests.Timeout:
				print "timeout"
			except requests.TooManyRedirects:
				print "too many redirects"
			except Exception, e:
				print e
			else:
				return r
			finally:
				self.iptime = time.time()
	#while not results.empty():
	#	content = results.get().encode("utf-8")
	#	exists = dbhits.checkRecord(content)
	#	if exists == False:
	#		dbhits.addHit(content,"google.com")
		#some websites use this encoding
class Scraper():
	def producer(self, tasklist):
		self.workLoad = len(tasklist)
		for url in tasklist:
			tasks.put(url)
	def run(self, tasklist, runf):
		self.producer(tasklist)
		threads = []
		import sqlite3
		starttime = time.time()
		connectDb = sqlite3.connect("/data/proxies/proxies.db")
		query = connectDb.cursor()
		#get all proxies from database
		query.execute("""SELECT proxy FROM proxies where success =1 and avgTime < 10 limit 500""")
		workerips = query.fetchall()
		endtime = time.time()
		print "took " + str(endtime-starttime) +" to get proxies"
		for ip in workerips:
			ip = ip[0]
			ip = ip.rstrip("\n")
			obj = Consumer(ip,tasks,results,ips, runf, self.workLoad)
			obj.start()
			threads.append(obj)
		gevent.joinall(threads)
	def results(self):
		return results
if __name__ == "__main__":
	def runf():
		print "hi"
	s = Scraper()
	s.run([], runf)
