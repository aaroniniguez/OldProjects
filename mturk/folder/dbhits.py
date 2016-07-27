import MySQLdb as mdb
import sys

con = mdb.connect("ec2-54-245-25-94.us-west-2.compute.amazonaws.com", "root", "Impossible123", "test")
cur = con.cursor()

def createUsersTable():
	cur.execute("""
	drop table if exists users
	""")
	cur.execute("""CREATE TABLE users
	(id int primary key auto_increment,username varchar(100), status varchar(100), submits int, 
	password varchar(100), email varchar(100), confirmed int, confirmed-code int)
	""")
def createRedditTable():
	cur.execute("""
	drop table if exists redditPlaceholder
	""")
	cur.execute("""CREATE TABLE redditPlaceholder
	(id int primary key auto_increment,title varchar(200))
	""")
def putTitle(title):
	cur.execute("DELETE from redditPlaceholder")
	con.commit()
	cur.execute("""
	INSERT INTO redditPlaceholder (title) VALUES (%s)
	""",[title])
	con.commit()
def getTitle():
	cur.execute("""
	SELECT title from redditPlaceholder
	""")
	result = cur.fetchone()
	if result == None:
		return None
	else:
		return result[0]

#forums
def createPlaceHolderTable():
	cur.execute("""CREATE TABLE placeholder
	(id int primary key auto_increment, threadUrl varchar(200), page varchar(200), siteName varchar(100))
	""")
def getPage(threadUrl, siteName):
	cur.execute("""
	SELECT page from placeholder where siteName = %s and threadUrl = %s 
	""",[siteName, threadUrl])
	result = cur.fetchone()
	if result is None:
		return None
	else: 
		return result[0]
def setPage(threadUrl, page, siteName):
	cur.execute("""
	select * from placeholder where siteName = %s	
	""",[siteName])
	result = cur.fetchone()
	#INSERt or UPDATE row
	if not result:
		cur.execute("""
		INSERT INTO placeholder (threadUrl, page, siteName) VALUES (%s,%s,%s)
		""", [threadUrl, page, siteName])
		con.commit()
	else:
		cur.execute("""
		UPDATE placeholder SET page=%s, threadUrl=%s WHERE siteName=%s;
		""", [page,threadUrl, siteName])
		con.commit()
#end forums

#new hits table
def createHitTable2():
	cur.execute("""CREATE TABLE hits2 
	(id int primary key auto_increment, source varchar(200), comments blob, mturkurl varchar(200),originalurl varchar(200), title varchar(200), requesterName varchar(100), requesterId varchar(50), description blob, reward varchar(25), qualifications varchar(200),submitter varchar(200), t TIMESTAMP DEFAULT CURRENT_TIMESTAMP, alive INT DEFAULT 1)""")
def addHit2(source,comments, mturkurl, originalurl, title, rname, rid, description, reward, qualifications, submitter):
	cur.execute("""INSERT INTO hits2 (source, comments, mturkurl, originalurl, title, requesterName, requesterId, description, reward, qualifications, submitter)
	VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",[source, comments, mturkurl,originalurl, title, rname, rid, description, reward, qualifications, submitter])
	con.commit()
def checkDuplicate2(mturkLink):
	cur.execute("""SELECT mturkurl from hits2 where mturkurl = %s""",[mturkLink])
	if cur.fetchone() is None:
		return False
	else:
		return True
def changeLife2(url):
	cur.execute("""delete from hits2 where mturkurl = %s""",[url])
	con.commit()
	return
def getLinks():
	cur.execute("""SELECT mturkurl from hits2 where alive = 1""")
	rowlist = cur.fetchall()
	urls = []
	for row in rowlist: 
		urls.append(row[0])
	return urls
#hits table
def createHitTable():
	cur.execute("""CREATE TABLE hits 
	(id int primary key auto_increment, source varchar(200), comments blob, mturkurl varchar(200),originalurl varchar(200), title varchar(200), requesterName varchar(100), requesterId varchar(50), description blob, reward varchar(25), qualifications varchar(200), t TIMESTAMP DEFAULT CURRENT_TIMESTAMP, alive INT DEFAULT 1)""")
def addHit(source, comments, mturkurl, originalurl, title, rname, rid, description, reward, qualifications):
	cur.execute("""INSERT INTO hits (source, comments, mturkurl, originalurl, title, requesterName, requesterId, description, reward, qualifications)
	VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",[source, comments, mturkurl,originalurl, title, rname, rid, description, reward, qualifications])
	con.commit()
def checkDuplicate(mturkLink):
	cur.execute("""SELECT mturkurl from hits where mturkurl = %s""",[mturkLink])
	if cur.fetchone() is None:
		return False
	else:
		return True
def changeLife(url):
	cur.execute("""delete from hits where mturkurl = %s""",[url])
	con.commit()
	return
def getLinks():
	cur.execute("""SELECT mturkurl from hits where alive = 1""")
	rowlist = cur.fetchall()
	urls = []
	for row in rowlist: 
		urls.append(row[0])
	return urls
#requester table, has only bad requesters
def createRequesterTable():
	cur.execute("""
	CREATE TABLE requesters (id int primary key auto_increment, requester varchar(200))	
	""")
def checkRequester(requester):
	cur.execute("""
	select * from requesters where requester =%s
	""", [requester])
	if cur.fetchone() is None:
		return True
	else:
		return False
if __name__ == "__main__":
	#createPlaceHolderTable()
	#createHitTable()
	#createRedditTable()
	#createRequesterTable()
	#createHitTable2()
	createUsersTable()
