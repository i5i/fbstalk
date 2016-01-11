import sqlite3

def createDatabase():
	conn = sqlite3.connect('facebook.db')
	c = conn.cursor()
	sql1 = 'create table if not exists graphdata (high TEXT, low TEXT)' 
	sql2 = 'create table if not exists metadata (UID TEXT, username TEXT unique, datainbytes TEXT, speed TEXT, friendcount TEXT, posts TEXT, bio TEXT, timestamp TEXT)'
	sql3 = 'create table if not exists txt (username TEXT unique, UID TEXT)'
	sql4 = 'create table if not exists posts (username TEXT unique, size TEXT, time TEXT, timestamp TEXT)'
	c.execute(sql1)
	c.execute(sql2)
	c.execute(sql3)
	c.execute(sql4)
	conn.commit()

def write2Database(dbName,dataList, conn):
	try:
		print"[*] Writing "+str(len(dataList))+" record(s) to database table: "+dbName
		numOfColumns = len(dataList[0])
		c = conn.cursor() 
		if numOfColumns==1:
			for i in dataList:
				try:
					c.execute('INSERT INTO '+dbName+' VALUES (?)', i)
					conn.commit()
				except sqlite3.IntegrityError:
					continue
		if numOfColumns==2:
			for i in dataList:
				try:
					c.execute('INSERT INTO '+dbName+' VALUES (?,?)', i)
					conn.commit()
				except sqlite3.IntegrityError:
					continue
		if numOfColumns==3:
			for i in dataList:
				try:
					c.execute('INSERT INTO '+dbName+' VALUES (?,?,?)', i)
					conn.commit()
				except sqlite3.IntegrityError:
					continue
		if numOfColumns==4:
			for i in dataList:
				try:
					c.execute('INSERT INTO '+dbName+' VALUES (?,?,?,?)', i)
					conn.commit()
				except sqlite3.IntegrityError:
					continue
		if numOfColumns==8:
			for i in dataList:
				try:
					c.execute('INSERT INTO '+dbName+' VALUES (?,?,?,?,?,?,?,?)', i)
					conn.commit()
				except sqlite3.IntegrityError:
					continue
	except TypeError as e:
		print e
		pass
	except IndexError as e:
		print e
		pass

def getgraph(conn):
	c = conn.cursor() 
	c.execute('select * from graphdata')
	dataList1 = []
	dataList1 = c.fetchall()
	return dataList1

def edit1(username, count, conn):
	c = conn.cursor() 
	c.execute('UPDATE metadata SET friendcount=? where username=?',(str(count),str(username),))
	
def edit2(username, count, conn):
	userList = []
	c = conn.cursor() 
	c.execute('UPDATE metadata SET posts=? where username=?',(str(count),str(username),))

def edit3(username, size, conn):
	userList = []
	c = conn.cursor() 
	c.execute('UPDATE posts SET size=? where username=?',(str(size),str(username),))
	
def getUID(username, conn):
	userList = []
	c = conn.cursor() 
	c.execute('select UID from txt where username=?',(str(username),))
	dataList1 = []
	dataList1 = c.fetchall()
	if len(dataList1)>0:
		return dataList1[0]
	else: 
		return 0

def getUsernames(usernames, conn):
	c = conn.cursor()
	c.execute('select username from txt')
	dataList1 = []
	count=0
	dataList1 = c.fetchall()
	if len(dataList1)>0:
		for i in dataList1:
			if i[0] in usernames:
				count+=1		
	return count