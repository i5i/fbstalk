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
	conn.commit()
	conn.close()
	createGraphML()
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

# 		 	edges.append(i)
# 		 	edges.append(e) 
#1 		 	if edges2.count(e) > 1: 
		 	g.add_edge_by_label(str(i), str(e))
 	
 	parser = GraphMLParser() 
 	parser.write(g, "myGraph.graphml") 	
# 	g2 = Graph()
# 	c.execute('select distinct high from graphdata')
# 	dataList = c.fetchall() 
# 	g2nodes=[] 
# 	edges2=[]
# 	
# 	for i in dataList:
# 		 i=str(i)
# 		 i = i.replace("(u'","").replace("',)","") 
#  		 c.execute('select distinct low from graphdata where source=?', (i,))
#   		 relate=c.fetchall()
#  		 if not i in g2nodes: 
#  		 	g2.add_node(i)
#  		 	g2nodes.append(i)
#  		 for e in relate: 
#  		 	e=str(e) 
#  		 	e = e.replace("(u'","").replace("',)","")  
#  		 	if not e in g2nodes: 
#  		 		g2.add_node(e)
#  		 		g2nodes.append(e)
#  		 	edges2.append(i)
#  		 	edges2.append(e) 
#  		 	if edges2.count(e) > 1: 
#  		 	g2.add_edge_by_label(i, e)
#  	overlap=0
#  	overlap2=0

#  	g2nodes=[] 
#  	for i in g2.nodes():
#  		g2nodes.append(i['label'])
#   	for d in gnodes:
# 		if d in g2nodes:
#  			overlap+=1  
#  
# 	print "Nodes1: "+str(len(g.nodes()))
# 	print "Nodes2: "+str(len(g2.nodes()))
# 	print "Overlap: "+str(overlap)
# 
#  	c.execute('select * from graphdata2')
# 	dataList = c.fetchall() 
#  	c.execute('select * from graphdata')
#  	dataList2= c.fetchall() 
#  	print "Edges1: "+str(len(dataList))
#  	print "Edges2: "+str(len(dataList2))
# 	for i in dataList:
# 		if i in dataList2: 
# 			overlap2+=1 
# 	print "Edge overlap: "+str(overlap2)

# 	keywords = open("keywords.txt", "r").read()
# 	keywords= keywords.split(" ")
# 	c.execute('select distinct username from txt')
# 	dataList3= c.fetchall()
#  	
# 	for username in dataList3:
# 		count=0
# 		username=str(username)
# 		username = username.replace("(u'","")
# 		username=username.replace("\\n',)","") 
# 		username=username.replace("',)","") 
# 		print username
# 		filename=username+"/"+username+'_dump.txt'
# 		text_file = open(filename, "r").read()
# 		text_file=text_file.split(" &&& ") 
# 		for key in keywords: 
# 			key=key.replace("\n","")
# 			for txt in text_file: 
# 				if key.lower() in txt.lower(): 
# 					count+=1 
# 		for node in g2.nodes():
# 			if node['label']== username: 
# 				node['count']=count  
# 		for node in g.nodes():
# 			if node['label']== username: 
# 				node['count']=count  
# 				
#     	parser.write(g, "myGraph.graphml") 
#     	parser.write(g2, "myGraph2.graphml") 
# #     	
# 	text=open("myGraph.graphml",'r').read()
# 	text=text.replace('attr.name="count"', 'attr.name="count" for="node"')
# 	text=text.replace('attr.type="string" id="count"', 'attr.type="integer" id="count"')
# 	open("myGraph.graphml",'w').write(text)
 
# 	text=open("myGraph2.graphml",'r').read()
# 	text=text.replace('attr.name="count"', 'attr.name="count" for="node"')
# 	text=text.replace('attr.type="string" id="count"', 'attr.type="integer" id="count"')
# 	open("myGraph2.graphml",'w').write(text)

	
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
	global profile
	profile= False
	global posts
	posts=False
	global graphing
	graphing=False
	for i in arguments: 
		if i == "-profile": 
			profile= True
		if i == "-posts":
			posts= True
		if i == "-graph":
			graphing=True		        
  	mainProcess(user2)

if __name__ == '__main__':
	options(sys.argv)
 
