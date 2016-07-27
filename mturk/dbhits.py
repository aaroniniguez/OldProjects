import sqlite3

createDb = sqlite3.connect("sample.db")
query = createDb.cursor()

#reddit
def createPlaceHolderTableReddit():
	query.execute("""CREATE TABLE redditPlaceholder
	(id INTEGER PRIMARY KEY, title TEXT)
	""")
def putTitle(title):
	query.execute("DELETE from redditPlaceholder")
	createDb.commit()
	query.execute("""
	INSERT INTO redditPlaceholder (title) VALUES (?)
	""",[title])
	createDb.commit()
def getTitle():
	query.execute("""
	SELECT title from redditPlaceholder
	""")
	result = query.fetchone()
	if result == None:
		return None
	else:
		return result[0]
#end reddit

#forums
def createPlaceHolderTable():
	query.execute("""CREATE TABLE placeholder
	(id INTEGER PRIMARY KEY, threadUrl TEXT, page TEXT, siteName TEXT)
	""")
def getPage(threadUrl, siteName):
	query.execute("""
	SELECT page from placeholder where siteName = ? and threadUrl = ?
	""",[siteName, threadUrl])
	result = query.fetchone()
	if result is None:
		return None
	else: 
		return result[0]
def setPage(threadUrl, page, siteName):
	query.execute("""
	select * from placeholder where siteName = ?	
	""",[siteName])
	result = query.fetchone()
	#INSERt or UPDATE row
	if not result:
		query.execute("""
		INSERT INTO placeholder (threadUrl, page, siteName) VALUES (?,?,?)
		""", [threadUrl, page, siteName])
		createDb.commit()
	else:
		query.execute("""
		UPDATE placeholder SET page=? WHERE siteName=?;
		""", [page, siteName])
		createDb.commit()
#end forums

def createTable():
	query.execute("""CREATE TABLE hits 
	(id INTEGER PRIMARY KEY, source TEXT, comments TEXT, mturkurl TEXT,originalurl TEXT, title TEXT, requesterName TEXT, requesterId TEXT, description TEXT, reward TEXT, qualifications TEXT, t TIMESTAMP DEFAULT CURRENT_TIMESTAMP, alive INT DEFAULT 1)""")
def addHit(source, comments, mturkurl, originalurl, title, rname, rid, description, reward, qualifications):
	query.execute("""INSERT INTO hits (source, comments, mturkurl, originalurl, title, requesterName, requesterId, description, reward, qualifications)
	VALUES (?,?,?,?,?,?,?,?,?,?)""",[source, comments, mturkurl,originalurl, title, rname, rid, description, reward, qualifications])
	createDb.commit()
def checkDuplicate(mturkLink):
	query.execute("""SELECT mturkurl from hits where mturkurl = ?""",[mturkLink])
	if query.fetchone() is None:
		return False
	else:
		return True
def changeLife(url):
	query.execute("""UPDATE hits SET alive = 0 where mturkurl = ?""",[url])
	createDb.commit()
	return
def getLinks():
	query.execute("""SELECT mturkurl from hits where alive = 1""")
	rowlist = query.fetchall()
	urls = []
	for row in rowlist: 
		urls.append(row[0])
	return urls
def updateHits():
	#check if hit is dead
	
	#delete hits older than 2 days
	query.execute("""DELETE from hits where
	datetime(t) <= datetime('now','-2 days')""")
def main():
	createTable()
	addHit("teresa", "http://google.com")
	createDb.commit()
if __name__ == "__main__":
	createTable()
	createPlaceHolderTable()
	createPlaceHolderTableReddit()
