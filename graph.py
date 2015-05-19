# -*- coding: utf-8 -*-
from __future__ import division
import httplib2,json
import zlib
import zipfile
import sys
import re
import datetime
import operator
import sqlite3
import os
from datetime import datetime
from datetime import date
import pytz 
from tzlocal import get_localzone
import requests
from pygraphml import GraphMLParser
from pygraphml import Graph
from pygraphml import Node
from pygraphml import Edge


import time,re,sys
import datetime
from bs4 import BeautifulSoup
from StringIO import StringIO



global uid
uid = ""
username = ""


#For consonlidating all likes across Photos Likes+Post Likes
peopleIDList = []
likesCountList = []
timePostList = []
placesVisitedList = []

conn = sqlite3.connect('facebook.db')
conn.text_factory = str

def createGraphML():
	conn = sqlite3.connect('facebook.db')
	global g
	g = Graph()
	c = conn.cursor()
	c.execute('select distinct source from graphdata')
	dataList = c.fetchall() 
	
	for i in dataList:
		 i=str(i)
		 i = i.replace("(u'","").replace("',)","") 
		 c.execute('select distinct dest from graphdata where source=?', (i,))
		 relate=c.fetchall()
		 if not i in g.nodes(): 
		 	g.add_node(i)
		 for e in relate: 
		 	e=str(e) 
		 	e = e.replace("(u'","").replace("',)","")  
		 	if not e in g.nodes(): 
		 		g.add_node(e)
		 	g.add_edge_by_label(i, e)

	
	parser = GraphMLParser() 
	parser.write(g, "myGraph.graphml") 	
	g2 = Graph()
	c.execute('select distinct source from graphdata2')
	dataList = c.fetchall() 
	
	for i in dataList:
		 i=str(i)
		 i = i.replace("(u'","").replace("',)","") 
		 c.execute('select distinct dest from graphdata2 where source=?', (i,))
		 relate=c.fetchall()
		 if not i in g2.nodes(): 
		 	g2.add_node(i)
		 for e in relate: 
		 	e=str(e) 
		 	e = e.replace("(u'","").replace("',)","")  
		 	if not e in g2.nodes(): 
		 		g2.add_node(e)
		 	g2.add_edge_by_label(i, e)
	
	overlap=0
	overlap2=0
	gnodes=[]
	g2nodes=[] 
	for i in g2.nodes():
		g2nodes.append(i['label'])
	for d in g.nodes():
		gnodes.append(d['label'])
		if d['label'] in g2nodes:
 			overlap+=1  
 	print "Nodes1: "+str(len(g.nodes()))
 	print "Nodes2: "+str(len(g2.nodes()))
 	print "Overlap: "+str(overlap)
	c.execute('select * from graphdata2')
	dataList = c.fetchall() 
	c.execute('select * from graphdata')
	dataList2= c.fetchall() 
	print "Edges1: "+str(len(dataList))
	print "Edges2: "+str(len(dataList2))
	for i in dataList:
		if i in dataList2: 
			overlap2+=1 
	print "Edge overlap: "+str(overlap2)
	keywords = open("keywords.txt", "r").read()
	keywords= keywords.split(" ")
	c.execute('select distinct  username from txt')
	dataList3= c.fetchall()
	
	for username in dataList3:
		count=0
		username=str(username)
		username = username.replace("(u'","")
		username=username.replace("\\n',)","") 
		username=username.replace("',)","") 
		print username
		filename=username+"/"+username+'_dump.txt'
		text_file = open(filename, "r").read()
		text_file=text_file.split(" &&& ") 
		for key in keywords: 
			key=key.replace("\n","")
			for txt in text_file: 
				if key in txt.lower(): 
					count+=1 
		for node in g2.nodes():
			if node['label']== username: 
				node['count']=count  
		for node in g.nodes():
			if node['label']== username: 
				node['count']=count  
				
    	parser.write(g, "myGraph.graphml") 
    	parser.write(g2, "myGraph2.graphml") 
    	
	text=open("myGraph.graphml",'r').read()
	text=text.replace('attr.name="count"', 'attr.name="count" for="node"')
	text=text.replace('attr.type="string" id="count"', 'attr.type="integer" id="count"')
	open("myGraph.graphml",'w').write(text)

	text=open("myGraph2.graphml",'r').read()
	text=text.replace('attr.name="count"', 'attr.name="count" for="node"')
	text=text.replace('attr.type="string" id="count"', 'attr.type="integer" id="count"')
	open("myGraph2.graphml",'w').write(text)
	
if __name__ == '__main__':
	createGraphML()
	conn.close()
	
