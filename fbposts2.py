# -*- coding: utf-8 -*-
import sys
import re
import os
import time
import sqlite3
from bs4 import BeautifulSoup
#from wordcloud import WordCloud, STOPWORDS
import module.Database

reload(sys)  
sys.setdefaultencoding('utf8')
module.Database.createDatabase()
conn = sqlite3.connect('facebook.db')
conn.text_factory = str
c = conn.cursor()
c.execute('create table if not exists avg (username TEXT unique, avg TEXT)')
#c.execute('create table if not exists three (username TEXT unique, erakond TEXT, jeesus TEXT, neeger TEXT)')
conn.commit()
def normalize(s):
	if type(s) == unicode: 
       		return s.encode('utf8', 'ignore')
	else:
        	return str(s)
 
def produce3(username):
	print "[*] Username:\t"+str(username)
	downloadsize=0
 	n=0
	finalcount=0
	words=""
	size=0
	avg=0
	while n < 12:
		n+=1
		filename = os.path.realpath('.')+"/data/"+username+"/"+username+'_2015_'+str(n)+'.htm'
		if os.path.lexists(filename): 	
			html = open(filename, 'r').read()
			size =sys.getsizeof(html)
			words2, count, avg = parseTimeline(html, username) 
	 		words=words+" "+words2
	 	 	finalcount+=count
#	three=[username]
#	keys=['erakond', 'jeesus', 'neeger']
#	for key in keys:
#		keycount=words.lower().count(key.lower())
#		print keycount
#		three.append(str(keycount)) 
#	module.Database.write2Database("three", [three], conn)
	return (finalcount, words, size, avg)	

def parseTimeline(html,username): 
	peopleIDLikes= []
	textdump=""
	soup=[] 
	soup = BeautifulSoup(html)	
	# 	timeline = soup.findAll("span",{"class" : "fsm fwn fcg"})
	timeline = soup.findAll("div",{"class" : "userContentWrapper _5pcr"})
	postnr=len(timeline)
	words1=""
	print "parsing timeline" 
	print len(timeline)
	for i in timeline:
		textdump=textdump+" "+i.text
		words1=words1+" "+i.text
 	filename=os.path.realpath('.')+"/data/"+username+"/"+username+'_dump.txt'
 	text_file = open(filename, "w")
 	text_file.write(normalize(textdump.encode('utf8')))
 	text_file.close()	
 	if postnr>0: 
 		avg= len(words1.split(" "))/postnr
 	else:
 		avg=0
	return words1, postnr, avg

def mainProcess(usernames):
	print "Processing "+str(len(usernames)-1)+" usernames"
	words4=""
	timeread=time.time()
 	time0=time.clock()
	keywords = open("keywords.txt", "r").read().split("\n")
	userdata=[]
	for username in usernames:
		if len(username) is not 0: 
			username=username.strip()
			time1=time.clock() 
			count, words3, size, avg =produce3(username) 
 			module.Database.edit2(username, count, conn)
 			module.Database.edit3(username, size, conn)
			time2=time.clock()
			words4=words4+" "+words3
			list=[username, avg]
 			userdata.append(list)
 
 	module.Database.write2Database("avg", userdata, conn)
 	time3=time.clock()
 	timeread=time.time()-timeread
 	print "TOTAL TIME"
 	print time3-time0
 	print timeread
#  	more_stopwords =["ja", "aga", "kui", "siis", "tongue", "nii", "ka", "et", "see", "ma","oma","oli", "emoticon", "ei","ning", "seda", "või", "smile", "grin", "Kas", "kes", "veel"]
#  	for more in more_stopwords: 
#  		STOPWORDS.add(more)
#  	utf=["Translation","February","shared","eeShare", "link", "nüüd", "või", "ära", "Kas"]
#   	for u in utf: 
#   		words4=words4.replace(u, "")
#  	wordcloud = WordCloud(stopwords=STOPWORDS).generate(words4)
# 	image = wordcloud.to_image()
# 	image.save("words.png","PNG")
# 	keywords = open("keywords.txt", "r").read().split("\n")
# 	text_file= open("keywordcount.txt", "w")
# 	for key in keywords:
# 		key=key.strip()
# 		keycount=words4.lower().count(key.lower()) 
# 		line=key+" : "+str(keycount)+"\n"
# 		text_file.write(line)
#     print str(len(words4.split(" ")))
# 	text_file.close()
 	conn.commit()
 	conn.close() 
	print "Done"
	
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
 
