import sys
import re
import os
import sqlite3
from bs4 import BeautifulSoup
import module.Database
global uid
from pygraphml import GraphMLParser
from pygraphml import Graph
from pygraphml import Node
from pygraphml import Edge
global postcount
postcount=100

#produces network graph, list of friends and includes number of friends in db plus
reload(sys)  
sys.setdefaultencoding('utf8')
conn2 = sqlite3.connect('graph.db')
c = conn2.cursor()
sql = 'create table if not exists graphdata (high INTEGER, low INTEGER)'
sql2 = 'create table if not exists userdata (uid INTEGER UNIQUE, username TEXT)'
c.execute(sql)
c.execute(sql2)
conn2.commit()

def parseFriends(html):
	if len(html)>0:
		print "parsing friendslist"
		friendList=[]
		soup = BeautifulSoup(html)	
		friendNameData = soup.findAll("div", {"class" : "fsl fwb fcb"})
		for i in friendNameData:
			r = re.compile('href="https://www.facebook.com/(.*?)\?fref') 
			m = r.search(str(i)) 
			if m: 
				try:
					friendName = m.group(1)
					friendName = friendName.replace('"https://www.facebook.com/','')
					friendList.append(friendName)
				except IndexError:
					continue
				except AttributeError:
					continue
		return friendList


def produce2(username):
	print "[*] Username:\t"+str(username)
	downloadsize=0
	nrfriends=0
	#Friendslist
	filename = os.path.realpath('.')+"/data/"+username+"/"+username+'_friends.htm'
	if not os.path.lexists(filename):
		return (downloadsize, nrfriends, [])
	html = open(filename, 'r').read()
	downloadsize=downloadsize+sys.getsizeof(html)
  	dataList = parseFriends(html)
 	nrfriends=len(dataList)
	return (downloadsize, nrfriends, dataList)	

def mainProcess(usernames):
	conn = sqlite3.connect('facebook.db')
	conn.text_factory = str
	into2=[]
	user=[]
	priority=[]
	file=open("ainput.txt", 'w')
	file2=open("binput.txt", 'w')
	for username in usernames: 
		if len(username)>0:
			username=username.strip()
			downloadsize, nrfriends, dataList =produce2(username)
			u=module.Database.getUID(username, conn)
 			module.Database.write2Database("userdata", [[int(u[0]), username]], conn2)
			module.Database.edit1(username, nrfriends, conn)
	 		u2=""
	 		for s in u: 
	 			if s.isdigit():
	 				u2+=s
	 		u2=int(u2)
	 		user.append([u2, username])
			for name in dataList: 
				if name not in usernames: 
					file.write(name+"\n")
					if name not in priority:
						priority.append(name)
					else:
						file2.write(name+"\n")
				name=name.strip()
				i=module.Database.getUID(name, conn)
			  	if str(i) is not "0":
					i2=""
		 			for s in i: 
		 				if s.isdigit():
		 					i2+=s
		 			i2=int(i2)
		 			user.append([i2, name])
		 			high=max(u2,i2)
		 			low=min(u2,i2)
		 			into=[high, low]
		 			if into not in into2: 
		 				into2.append(into)
	rows=module.Database.getgraph(conn2)
	items=[]
	listofrows=[]
 	if len(rows)==0:
 		module.Database.write2Database("graphdata", [[1,0]], conn2)
 		rows=module.Database.getgraph(conn2)
 	for row in rows:
 		listofrows.append(list(row))
 	for into3 in into2: 
 		if into3 not in listofrows: 
 			items.append(into3) 
 	if len(items)>0: 
 		module.Database.write2Database("graphdata", items, conn2)
 	createGraphML()
	conn.commit()
	conn.close()
	conn2.close()
	
	
def createGraphML():
	global g
	g = Graph()
	c.execute('select uid from userdata')
	dataList = c.fetchall() 
	gnodes=[]
  	edges=[]
	for i in dataList: 
		 i=str(i)
 		 i = i.replace("(","").replace(",)","").replace("L","") 
 		 i= int(i)
		 c.execute('select distinct low from graphdata where high=?', (i,))
		 relate=c.fetchall()
 		 if not i in gnodes: 
 		 	g.add_node(i)
 		 	gnodes.append(i)
   		 	
 		 for e in relate: 
  		 	e=str(e) 
  		 	e = e.replace("(","").replace(",)","").replace("L","")
  		 	e=int(e) 
  		 	if not e in gnodes: 
  		 		g.add_node(e)
  		 		gnodes.append(e)
		 	g.add_edge_by_label(str(i), str(e))
 	
 	parser = GraphMLParser() 
 	parser.write(g, "myGraph.graphml") 	

	
def options(arguments):
	user2=[]
	conn = sqlite3.connect('facebook.db')
	conn.text_factory = str
	sql = 'select username from txt'
	c2 = conn.cursor()
	c2.execute(sql)
	dataList = c2.fetchall()
	for i in dataList:
		user2.append(list(i)[0])
	conn.close()		        
  	mainProcess(user2)

if __name__ == '__main__':
	options(sys.argv)
 
