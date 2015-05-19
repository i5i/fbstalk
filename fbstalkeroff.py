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
from termcolor import colored, cprint
from pygraphml import GraphMLParser
from pygraphml import Graph
from pygraphml import Node
from pygraphml import Edge
import time
import facebook
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
import time,re,sys
from selenium.webdriver.common.keys import Keys
import datetime
from bs4 import BeautifulSoup
from StringIO import StringIO

requests.adapters.DEFAULT_RETRIES = 10

h = httplib2.Http(".cache")


facebook_username = "jens.mikli@gmail.com"
facebook_password = "moons6ja8"

global uid
uid = ""
username = ""
internetAccess = True
cookies = {}
all_cookies = {}
reportFileName = ""

#For consonlidating all likes across Photos Likes+Post Likes
peopleIDList = []
likesCountList = []
timePostList = []
placesVisitedList = []

#DB
conn = sqlite3.connect('facebook.db')
conn.text_factory = str

def createGraphML():
	g = Graph()
	c = conn.cursor()
	c.execute('select distinct source from graphdata')
	dataList = c.fetchall() 
	
	for i in dataList:
		 i=str(i)
		 i = i.replace("(u'","").replace("',)","").replace("('","")  
		 print i 
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
	parser.write(g, "facebook.graphml") 	
 

def normalize(s):
	if type(s) == unicode: 
       		return s.encode('utf8', 'ignore')
	else:
        	return str(s)

def findUser(findName):
	stmt = "SELECT uid,current_location,username,name FROM user WHERE contains('"+findName+"')"
	stmt = stmt.replace(" ","+")
	url="https://graph.facebook.com/fql?q="+stmt+"&access_token="+facebook_access_token
	resp, content = h.request(url, "GET")
	results = json.loads(content)
	count=1
	for x in results['data']:
		print str(count)+'\thttp://www.facebook.com/'+x['username']
		count+=1

def convertUser2ID(username):
	stmt = "SELECT uid,current_location,username,name FROM user WHERE username=('"+username+"')"
	stmt = stmt.replace(" ","+")
	url="https://graph.facebook.com/fql?q="+stmt+"&access_token="+facebook_access_token
	resp, content = h.request(url, "GET")
	if resp.status==200:
		results = json.loads(content)
		if len(results['data'])>0:
			return results['data'][0]['uid']
		else:
			print "[!] Can't convert username 2 uid. Please check username"
			sys.exit()
			return 0
	else:
		print "[!] Please check your facebook_access_token before continuing"
		sys.exit()
		return 0

def convertID2User(uid):
	stmt = "SELECT uid,current_location,username,name FROM user WHERE uid=('"+uid+"')"
	stmt = stmt.replace(" ","+")
	url="https://graph.facebook.com/fql?q="+stmt+"&access_token="+facebook_access_token
	resp, content = h.request(url, "GET")
	results = json.loads(content)
	return results['data'][0]['uid']

#/setup


def write2Database(dbName,dataList):
	try:
		cprint("[*] Writing "+str(len(dataList))+" record(s) to database table: "+dbName,"white")
		#print "[*] Writing "+str(len(dataList))+" record(s) to database table: "+dbName
		numOfColumns = len(dataList[0])
		c = conn.cursor()
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
		if numOfColumns==5:
			for i in dataList:
				try:
					c.execute('INSERT INTO '+dbName+' VALUES (?,?,?,?,?)', i)
					conn.commit()
				except sqlite3.IntegrityError:
					continue
		if numOfColumns==6:
			for i in dataList:
				try:
					c.execute('INSERT INTO '+dbName+' VALUES (?,?,?,?,?,?)', i)
					conn.commit()
				except sqlite3.IntegrityError:
					continue
	except TypeError as e:
		print e
		pass
	except IndexError as e:
		print e
		pass





def parseUserInfo(html):
	userEduWork = []
	userLivingCity = ""
	userCurrentCity = ""
	userLiveEvents = []
	userGender = ""
	userStatus = ""
	userGroups = []
	tempList=[]
	soup = BeautifulSoup(str(html)) 
	pageLeft = soup.findAll("code") 
	for i in pageLeft: 
		text = i.findAll(text=True)
		for s in text:
			u=BeautifulSoup(s).findAll("li", {"id": "current_city"}) 
			for x in u: 		
				n=BeautifulSoup(str(x)).find("span")
				#for m in n:  
				userCurrentCity=n.text

	tempList.append([userEduWork,userLivingCity,userCurrentCity,userLiveEvents,userGender,userStatus,userGroups])
	return tempList

def parseAppsUsed(html):
	soup = BeautifulSoup(html)	
	appsData = soup.findAll("div", {"class" : "_glj"})
	tempList = []
	for x in appsData:
		tempList.append(x.text)
	return tempList


def getFriends(uid):
	userList = []
	c = conn.cursor()
	c.execute('select username from friends where sourceUID=?',(uid,))
	dataList1 = []
	dataList1 = c.fetchall()
	if len(dataList1)>0:
		for i in dataList1:
			userList.append([uid,'',str(normalize(i)),'',''])
	return userList
	

def parseFriends(html):
	mthList = ['january','february','march','april','may','june','july','august','september','october','november','december']
	if len(html)>0:
		soup = BeautifulSoup(html)	

		friendBlockData = soup.findAll("div",{"class" : "_glj"})
		friendNameData = soup.findAll("div", {"class" : "_5d-5"})
		knownSinceData = soup.findAll("div", {"class" : "_52eh"})
	
		friendList=[]
		for i in friendBlockData:
			soup1 = BeautifulSoup(str(i))
                        rood= soup1.find("div",{"class" : "_gll"})
			friendNameData = soup1.find("div",{"class" : "_5d-5"})
			lastKnownData = soup1.find("div",{"class" : "_52eh"}) 
			r = re.compile('a href=(.*?)\?ref') 
			m = r.search(str(rood)) 
			if m:          
				try:	
					friendName = friendNameData.text
					friendName = friendName.replace('"https://www.facebook.com/','')
					value = (lastKnownData.text).split("since")[1].strip()
					#Current year - No year listed in page
					if re.search('\d+', value):					
						value = value+" "+str((datetime.datetime.now()).year)
						month = ((re.sub(" \d+", " ", value)).lower()).strip()
						monthDigit = 0
						count=0
						for s in mthList:
							if s==month:
								monthDigit=count+1
							count+=1	
						year = re.findall("(\d+)",value)[0]
						fbID = m.group(1).replace('"https://www.facebook.com/','')
						friendList.append([str(uid),friendName,fbID,int(monthDigit),int(year)])
					else:
						#Not current year 
						if re.search('\d+, \d+', value): 
							month,year = value.split(" ") 
							month = month.lower()
							monthDigit = 0
							count=0
							for s in mthList:
								if s==month:
									monthDigit=count+1
								count+=1
							fbID = m.group(1).replace('"https://www.facebook.com/','')
							friendList.append([str(uid),friendName,fbID,int(monthDigit),int(year)])
	
	
				except IndexError:
					continue
				except AttributeError:
					continue
		i=0
		data = sorted(friendList, key=operator.itemgetter(4,3))
		#	#print x[2]+'\t'+x[1]
		return data



def parseVideosBy(html):
	soup = BeautifulSoup(html)	
	appsData = soup.findAll("div", {"class" : "_42bw"})
	tempList = []
	for x in appsData:
		r = re.compile('href="(.*?)&amp')
		m = r.search(str(x))
		if m:
			filename = str(m.group(1)).replace("https://www.facebook.com/video.php?v=","v_")
			filename = filename+".html"
                        print filename
			url = m.group(1)
                        print url
			if not os.path.lexists(filename):
				html1 = downloadFile(url)
				#driver.get(url)	
				#html1 = driver.page_source
				text_file = open(filename, "w")
				text_file.write(normalize(html1))
				text_file.close()
			else:
				html1 = open(filename, 'r').read()
			soup1 = BeautifulSoup(html1)	
			titleData = soup1.find("h2", {"class" : "uiHeaderTitle"})
			tempList.append([uid,url,url])
	return tempList



def parseLikesPosts(id):
	print "parse likes"
	peopleID = []
	filename = 'likes_'+str(id)
	if not os.path.lexists(filename): 
		print "no likes"
		html1="nuthing"
	else:
		html1 = open(filename, 'r').read()
	soup1 = BeautifulSoup(html1)
	peopleLikeList = soup1.findAll("div",{"class" : "fsl fwb fcb"})

	if len(peopleLikeList)>0:
		print "[*] Extracting Likes from Post: "+str(id)
		for x in peopleLikeList:
			soup2 = BeautifulSoup(str(x))
			peopleLike = soup2.find("a")
			peopleLikeID = peopleLike['href'].split('?')[0].replace('https://www.facebook.com/','')
			if peopleLikeID == 'profile.php':	
				r = re.compile('id=(.*?)&fref')
				m = r.search(str(peopleLike['href']))
				if m:
					peopleLikeID = m.group(1)
			print "[*] Liked Post: "+"\t"+peopleLikeID
			if peopleLikeID not in peopleID:
				peopleID.append(peopleLikeID)
		
		return peopleID	

def parsePost(id,username):
	print "parse post"
	filename = 'posts__'+str(id)
	if not os.path.lexists(filename):
		print "no posts"+str(id)
		html1="nuthing"
	else:
		html1 = open(filename, 'r').read()
	soup1 = BeautifulSoup(html1)
	htmlList = soup1.find("h5",{"class" : "_6nl"})
	tlTime = soup1.find("abbr")
	if " at " in str(htmlList):
		soup2 = BeautifulSoup(str(htmlList))
		locationList = soup2.findAll("a",{"class" : "profileLink"})
		locUrl = locationList[len(locationList)-1]['href']
		locDescription = locationList[len(locationList)-1].text
		locTime = tlTime['data-utime']
		placesVisitedList.append([locTime,locDescription,locUrl])



def parsePhotosOf(html):
	soup = BeautifulSoup(html)	
	photoPageLink = soup.findAll("a", {"class" : "_23q"})
	tempList = []
	for i in photoPageLink:
		html = str(i)
		soup1 = BeautifulSoup(html)
		pageName = soup1.findAll("img", {"class" : "img"})
		pageName1 = soup1.findAll("img", {"class" : "scaledImageFitWidth img"})
		pageName2 = soup1.findAll("img", {"class" : "_46-i img"})	
		for z in pageName2:
			if z['src'].endswith('.jpg'):
				url1 = i['href']
				r = re.compile('fbid=(.*?)&set=bc')
				m = r.search(url1)
				if m:
					filename = 'fbid_'+ m.group(1)+'.html'
					filename = filename.replace("profile.php?id=","")
					if not os.path.lexists(filename):
						#html1 = downloadPage(url1)
						html1 = downloadFile(url1)
						print "[*] Caching Photo Page: "+m.group(1)
						text_file = open(filename, "w")
						text_file.write(normalize(html1))
						text_file.close()
					else:
						html1 = open(filename, 'r').read()
				soup2 = BeautifulSoup(html1)
				username2 = soup2.find("div", {"class" : "fbPhotoContributorName"})
				r = re.compile('a href="(.*?)"')
				m = r.search(str(username2))
				if m:	
					username3 = m.group(1)
					username3 = username3.replace("https://www.facebook.com/","")
					username3 = username3.replace("profile.php?id=","")
					print "[*] Extracting Data from Photo Page: "+username3
					tempList.append([str(uid),z['alt'],z['src'],i['href'],username3])
		for y in pageName1:
			if y['src'].endswith('.jpg'):
				url1 = i['href']
				r = re.compile('fbid=(.*?)&set=bc')
				m = r.search(url1)
				if m:
					filename = 'fbid_'+ m.group(1)+'.html'
					filename = filename.replace("profile.php?id=","")
					if not os.path.lexists(filename):
						#html1 = downloadPage(url1)
						html1 = downloadFile(url1)
						print "[*] Caching Photo Page: "+m.group(1)
						text_file = open(filename, "w")
						text_file.write(normalize(html1))
						text_file.close()
					else:
						html1 = open(filename, 'r').read()
				soup2 = BeautifulSoup(html1)
				username2 = soup2.find("div", {"class" : "fbPhotoContributorName"})
				r = re.compile('a href="(.*?)"')
				m = r.search(str(username2))
				if m:	
					username3 = m.group(1)
					username3 = username3.replace("https://www.facebook.com/","")
					username3 = username3.replace("profile.php?id=","")
					print "[*] Extracting Data from Photo Page: "+username3
					tempList.append([str(uid),y['alt'],y['src'],i['href'],username3])
		for x in pageName:
			if x['src'].endswith('.jpg'):
				url1 = i['href']
				r = re.compile('fbid=(.*?)&set=bc')
				m = r.search(url1)
				if m:
					filename = 'fbid_'+ m.group(1)+'.html'
					filename = filename.replace("profile.php?id=","")
					if not os.path.lexists(filename):
						#html1 = downloadPage(url1)
						html1 = downloadFile(url1)
						print "[*] Caching Photo Page: "+m.group(1)
						text_file = open(filename, "w")
						text_file.write(normalize(html1))
						text_file.close()
					else:
						html1 = open(filename, 'r').read()
				soup2 = BeautifulSoup(html1)
				username2 = soup2.find("div", {"class" : "fbPhotoContributorName"})
				r = re.compile('a href="(.*?)"')
				m = r.search(str(username2))
				if m:	
					username3 = m.group(1)
					username3 = username3.replace("https://www.facebook.com/","")
					username3 = username3.replace("profile.php?id=","")
					print "[*] Extracting Data from Photo Page: "+username3
					tempList.append([str(uid),x['alt'],x['src'],i['href'],username3])
	return tempList


def parsePhotosLiked(html):
	soup = BeautifulSoup(html)	
	photoPageLink = soup.findAll("a", {"class" : "_23q"})
	tempList = []

	for i in photoPageLink:
		html = str(i)
		soup1 = BeautifulSoup(html)
		pageName = soup1.findAll("img", {"class" : "img"})
		
		for z in pageName:
			url1 = i['href']	
			r = re.compile('fbid=(.*?)&set=bc')
			m = r.search(url1)
			if m:
				filename = 'fbid_'+ m.group(1)+'.html'
				filename = filename.replace("profile.php?id=","")
				if not os.path.lexists(filename):
					#html1 = downloadPage(url1)
					html1 = downloadFile(url1)
					print "[*] Caching Photo Page: "+m.group(1)
					text_file = open(filename, "w")
					text_file.write(normalize(html1))
					text_file.close()
				else:
					html1 = open(filename, 'r').read()
				soup2 = BeautifulSoup(html1)
				username2 = soup2.find("div", {"class" : "fbPhotoContributorName"})
				r = re.compile('href="(.*)?fref=photo"')
				m = r.search(str(username2))
				if m:	
					username3 = m.group(1)
					username3 = username3.replace("https://www.facebook.com/","")
					username3 = username3.replace("?","") 
					if username3.count('/')==2: 
						username3 = username3.split('/')[2] 
					print "[*] Extracting Data from Photo Page: "+username3 
					tmpStr = [] 
					tmpStr.append([str(uid), normalize(z['alt']), normalize(z['src']),normalize(i['href']),normalize(username3)]) 
					write2Database('photosLiked',tmpStr)

	return tempList

def parsePhotosCommented(html):
	soup = BeautifulSoup(html)	
	photoPageLink = soup.findAll("a", {"class" : "_23q"})
	tempList = []

	for i in photoPageLink:
		html = str(i)
		soup1 = BeautifulSoup(html)
		pageName = soup1.findAll("img", {"class" : "img"})
		
		for z in pageName:
			url1 = i['href']	
			r = re.compile('fbid=(.*?)&set=bc')
			m = r.search(url1)
			if m:
				filename = 'fbid_'+ m.group(1)+'.html'
				filename = filename.replace("profile.php?id=","")
			if not os.path.lexists(filename):
				#html1 = downloadPage(url1)
				html1 = downloadFile(url1)
				print "[*] Caching Photo Page: "+m.group(1)
				text_file = open(filename, "w")
				text_file.write(normalize(html1))
				text_file.close()
			else:
				html1 = open(filename, 'r').read()
			soup2 = BeautifulSoup(html1)
			username2 = soup2.find("div", {"class" : "fbPhotoContributorName"})
			r = re.compile('href="(.*)?fref=photo"')
			m = r.search(str(username2))
			if m: 
				username3 = m.group(1) 
				username3 = username3.replace("https://www.facebook.com/","") 
				username3 = username3.replace("?","") 
				if username3.count('/')==2: 
					username3 = username3.split('/')[2] 
				print "[*] Extracting Data from Photo Page: "+username3 
				tempList.append([str(uid),z['alt'],z['src'],i['href'],username3])
	return tempList

def sidechannelFriends(uid):
	userList = []
	c = conn.cursor()
	c.execute('select distinct username from photosLiked where sourceUID=?',(uid,))
	dataList1 = []
	dataList1 = c.fetchall()
	if len(dataList1)>0:
		for i in dataList1:
			if 'pages' not in str(normalize(i[0])):
				userList.append([uid,'',str(normalize(i[0])),'',''])
	c.execute('select distinct username from photosCommented where sourceUID=?',(uid,))
	dataList1 = []
	dataList1 = c.fetchall()
	if len(dataList1)>0:	
		for i in dataList1:
			if 'pages' not in str(normalize(i[0])):
				userList.append([uid,'',str(normalize(i[0])),'',''])
	c.execute('select distinct username from photosOf where sourceUID=?',(uid,))
	dataList1 = []
	dataList1 = c.fetchall()
	if len(dataList1)>0:	
		for i in dataList1:
			if 'pages' not in str(normalize(i[0])):
				userList.append([uid,'',str(normalize(i[0])),'',''])
	return userList

def parseTimeline(html,username):
	soup = BeautifulSoup(html)	
# 	q=soup.findAll("div",{"class": "userContentWrapper"}) 
# 	for i in q: 
# 		print BeautifulSoup(str(i)).findAll("span",{"class": "fwb fcg"}).text
# 	tlDateTimeLoc = soup.findAll("a",{"class" : "uiLinkSubtle"})

# 	download all entries sort them into posts and non posts then dump non post to friend name
#     and save posts to crawl later 
	tlDateTimeLoc = soup.findAll("span",{"class" : "fsm fwn fcg"}) 
 	for i in tlDateTimeLoc: 
 		n=BeautifulSoup(str(i)).findAll("a")
 		if len(n) > 0: 
 			if "posts" in n[0]['href']: 
 				n=n[0]['href'].split("/") 
 				print n[3]
 				parsePost(n[3],username)
				peopleIDLikes = parseLikesPosts(n[3])

				try:
					for id1 in peopleIDLikes:
						global peopleIDList
						global likesCountList
						if id1 in peopleIDList:
							lastCount = 0
							position = peopleIDList.index(id1)
							likesCountList[position] +=1
						else:
							peopleIDList.append(id1)
							likesCountList.append(1)
				except TypeError:
					continue
				except AttributeError:
					continue
	
	tlTime = soup.findAll("abbr")
	temp123 = soup.findAll("div",{"role" : "article"})
	placesCheckin = []
	timeOfPostList = [] 
	counter = 0
 
	for y in temp123:
		soup1 = BeautifulSoup(str(y))
		tlDateTimeLoc = soup1.findAll("a",{"class" : "uiLinkSubtle"})
		#Universal Time
		try:
			soup2 = BeautifulSoup(str(tlDateTimeLoc[0]))
			tlDateTime = soup2.find("abbr")	
			#Facebook Post Link	
			tlLink = tlDateTimeLoc[0]['href']
 
			try:
				tz = get_localzone()
				unixTime = str(tlDateTime['data-utime'])
				localTime = (datetime.datetime.fromtimestamp(int(unixTime)).strftime('%Y-%m-%d %H:%M:%S'))
				timePostList.append(localTime)
				timeOfPost = localTime
				timeOfPostList.append(localTime)
 
				print "[*] Time of Post: "+localTime
			except TypeError:
				continue
			if "posts" in tlLink:
				print tlLink.strip()
				pageID = tlLink.split("/")
				print pageID[3]
				parsePost(pageID[3],username)
				peopleIDLikes = parseLikesPosts(pageID[3])
 
				try:
					for id1 in peopleIDLikes:
						global peopleIDList
						global likesCountList
						if id1 in peopleIDList:
							lastCount = 0
							position = peopleIDList.index(id1)
							likesCountList[position] +=1
						else:
							peopleIDList.append(id1)
							likesCountList.append(1)
				except TypeError:
					continue
				except AttributeError:
					continue
			if len(tlDateTimeLoc)>2:
				try:
					#Device / Location
					if len(tlDateTimeLoc[1].text)>0:
						print "[*] Location of Post: "+unicode(tlDateTimeLoc[1].text)
					if len(tlDateTimeLoc[2].text)>0:
						print "[*] Device: "+str(tlDateTimeLoc[2].text)
				except IndexError:
					continue	
 
			else:
				try:
					#Device / Location
					if len(tlDateTimeLoc[1].text)>0:
						if "mobile" in tlDateTimeLoc[1].text:
							print "[*] Device: "+str(tlDateTimeLoc[1].text)
						else:
							print "[*] Location of Post: "+unicode(tlDateTimeLoc[1].text)
 					
				except IndexError:
					continue	
			#Facebook Posts
			tlPosts = soup1.find("span",{"class" : "userContent"})
 			
			try:
				tlPostSec = soup1.findall("span",{"class" : "userContentSecondary fcg"})
				tlPostMsg = ""
 			
				#Places Checked In
			except TypeError:
				continue
			soup3 = BeautifulSoup(str(tlPostSec))
			hrefLink = soup3.find("a")
 
			"""
			if len(str(tlPostSec))>0:
				tlPostMsg = str(tlPostSec)
				#if " at " in str(tlPostMsg) and " with " not in str(tlPostMsg):
				if " at " in str(tlPostMsg):
					print str(tlPostSec)
 
					print tlPostMsg
					#print hrefLink
					#placeUrl = hrefLink['href'].encode('utf8').split('?')[0]
					#print "[*] Place: "+placeUrl										
					#placesCheckin.append([timeOfPost,placeUrl])
			"""
 
			try:
				if len(tlPosts)>0:				
					tlPostStr = re.sub('<[^>]*>', '', str(tlPosts))
					if tlPostStr!=None:
						print "[*] Message: "+str(tlPostStr)
			except TypeError as e:
				continue
 
 
			tlPosts = soup1.find("div",{"class" : "translationEligibleUserMessage userContent"})
			try:
				if len(tlPosts)>0:
					tlPostStr = re.sub('<[^>]*>', '', str(tlPosts))
					print "[*] Message: "+str(tlPostStr)	
			except TypeError:
				continue
		except IndexError as e:
			continue
		counter+=1
 	
	tlDeviceLoc = soup.findAll("a",{"class" : "uiLinkSubtle"})
 
	print '\n'
 
	global reportFileName
	if len(reportFileName)<1:
		reportFileName = username+"/"+username+"_report.txt"
	reportFile = open(reportFileName, "w")
	c = conn.cursor()
 	tempList = []
	totalLen = len(timeOfPostList)
	count = 0
	if len(peopleIDList)>0:
		likesCountList, peopleIDList  = zip(*sorted(zip(likesCountList,peopleIDList),reverse=True))
  	
		reportFile.write("\n********** Analysis of Facebook Post Likes **********\n")
		while count<len(peopleIDList):
			testStr = str(likesCountList[count]).encode('utf8')+'\t'+str(peopleIDList[count]).encode('utf8')
			reportFile.write(testStr+"\n")
			count+=1	
  
	reportFile.write("\n********** Analysis of Interactions between "+str(username)+" and Friends **********\n")
	c = conn.cursor()
	c.execute('select userName from friends where sourceUID=?',(uid,))
	dataList = c.fetchall()
	photosliked = []
	photoscommented = []
	userID = []
 	
	photosLikedUser = []
	photosLikedCount = []
	photosCommentedUser = []
	photosCommentedCount = []
 	
	for i in dataList:
		c.execute('select * from photosLiked where sourceUID=? and username=?',(uid,i[0],))
		dataList1 = []
		dataList1 = c.fetchall()
		if len(dataList1)>0:
			photosLikedUser.append(normalize(i[0]))
			photosLikedCount.append(len(dataList1))
	for i in dataList:
		c.execute('select * from photosCommented where sourceUID=? and username=?',(uid,i[0],))
		dataList1 = []
		dataList1 = c.fetchall()
		if len(dataList1)>0:	
			photosCommentedUser.append(normalize(i[0]))
			photosCommentedCount.append(len(dataList1))
	if(len(photosLikedCount)>1):	
		reportFile.write("Photo Likes: "+str(username)+" and Friends\n")
		photosLikedCount, photosLikedUser  = zip(*sorted(zip(photosLikedCount, photosLikedUser),reverse=True))	
		count=0
		while count<len(photosLikedCount):
			tmpStr = str(photosLikedCount[count])+'\t'+normalize(photosLikedUser[count])+'\n'
			count+=1
			reportFile.write(tmpStr)
	if(len(photosCommentedCount)>1):	
		reportFile.write("\n********** Comments on "+str(username)+"'s Photos **********\n")
		photosCommentedCount, photosCommentedUser  = zip(*sorted(zip(photosCommentedCount, photosCommentedUser),reverse=True))	
		count=0
		while count<len(photosCommentedCount):
			tmpStr = str(photosCommentedCount[count])+'\t'+normalize(photosCommentedUser[count])+'\n'
			count+=1
			reportFile.write(tmpStr)
 
	reportFile.close()

def parsePhotosby(html):
	soup = BeautifulSoup(html)	
	photoPageLink = soup.findAll("a", {"class" : "_23q"})

	tempList = []
	for i in photoPageLink:
		html = str(i)
		soup1 = BeautifulSoup(html)
		pageName = soup1.findAll("img", {"class" : "img"})
		
        
		for z in pageName:
			url1 = i['href']	
			r = re.compile('fbid=(.*?)&set=bc')
			m = r.search(url1)
			if m:
				filename = 'fbid_'+ m.group(1)+'.html'
				filename = filename.replace("profile.php?id=","") 
				if not os.path.lexists(filename): 
					#html1 = downloadPage(url1) 
					html1 = downloadFile(url1)
					print "[*] Caching Photo Page: "+m.group(1)
					text_file = open(filename, "w")
					text_file.write(normalize(html1))
					text_file.close()
				else:
					html1 = open(filename, 'r').read() 
				soup2 = BeautifulSoup(html1) 
				username2 = soup2.find("div", {"class" : "fbPhotoContributorName"}) 
				r = re.compile('href="(.*)?fref=photo"') 
				m = r.search(str(username2))
				if m:	
					username3 = m.group(1)
					print username3
					username3 = username3.replace("https://www.facebook.com/","")
					username3 = username3.replace("?","")
					print "[*] Extracting Data from Photo Page: "+username3
					tempList.append([str(uid),z['alt'],z['src'],i['href'],username3])
				
		
	return tempList


def parsePagesLiked(html):
	soup = BeautifulSoup(html)	
	pageName = soup.findAll("div", {"class" : "_gll"})
	pageCategory = soup.findAll("div", {"class" : "_pac"})
	tempList = []
	count=0
	r = re.compile('href="(.*?)\?ref')
	for x in pageName:
		m = r.search(str(x))
                #print (x.text).encode('ascii', 'ignore')

		if m:
			pageCategory[count]
			tempList.append([uid,x.text,pageCategory[count].text,m.group(1)])
                tempList.append([uid,x.text,pageCategory[count].text,m.group(1)])
		count+=1
	return tempList

def parsePlacesVisited(html):
	soup = BeautifulSoup(html)	
	pageName = soup.findAll("div", {"class" : "_glj"})
	pageCategory = soup.findAll("div", {"class" : "_pac"})
	tempList = []
	count=0
	r = re.compile('href="(.*?)\?ref')
	for x in pageName:
		m = r.search(str(x))
                #print (x.text).encode('ascii', 'ignore')
		if m:
			pageCategory[count]
			tempList.append([uid,x.text,"",m.group(1)])
		count+=1
	return tempList

def parsePlacesLiked(html):
	soup = BeautifulSoup(html)	
	pageName = soup.findAll("div", {"class" : "_gll"})
	pageCategory = soup.findAll("div", {"class" : "_pac"})
	tempList = []
	count=0
	r = re.compile('href="(.*?)\?ref')
	for x in pageName:
		m = r.search(str(x))
                #print (x.text).encode('ascii', 'ignore')
		if m:
			pageCategory[count]
			tempList.append([uid,x.text,pageCategory[count].text,m.group(1)])
		count+=1
	return tempList

def produce(uid, username):
	username = username.strip()
	if not os.path.exists(username): 
		os.makedirs(username)
	print "[*] Username:\t"+str(username) 
	print "[*] Uid:\t"+str(uid)
 	downloadsize=0
 	nrfriends=0 
 	
 	#Friendslist
	filename = username+"/"+username+'_friends.htm'

	if not os.path.lexists(filename):
	   	print "[*] Missing Friends Page of: "+username
   	else:
		html = open(filename, 'r').read() 
		downloadsize=downloadsize+sys.getsizeof(html)
   
#  	dataList = parseFriends(html)
#  	nrfriends=len(dataList)
#  	print "[*] Writing Friends List to Database: "+username
#  	write2Database('friends',dataList)
#  	graphdata=[]
#  	for i in dataList: 
#  		graphdata.append([username, i[2]])
#  	print graphdata
#  	write2Database('graphdata', graphdata)	
#  	
#  	
#   	filename = username+"/"+username+'.htm'  
#   	if not os.path.lexists(filename):
#   		print "Missing Timeline" 
#   	else: 
#   		html = open(filename, 'r').read() 
#   		downloadsize=downloadsize+sys.getsizeof(html) 
#   		dataList = parseTimeline(html,username) 
# 
# 
# 
# # #additional information and report file
# 	filename = username+"/"+username+'_photosOf.htm'
#  	if not os.path.lexists(filename):
#  			print "[*] Missing Photos By: "+username
#  	else:
#  			html = open(filename, 'r').read() 
#  			downloadsize=downloadsize+sys.getsizeof(html) 
#  			dataList = parsePhotosby(html) 
#  			write2Database('photosOf',dataList)	
#  	filename = username+"/"+username+'_photosLiked.htm'
# 
#  	   	
# 	if not os.path.lexists(filename):
# 	   	print "[*] Missing Photos Liked By: "+username
# 	else:
# 		html = open(filename, 'r').read() 
# 		downloadsize=downloadsize+sys.getsizeof(html) 
# 		dataList = parsePhotosLiked(html)	
# 	filename = username+"/"+username+'_photoscommented.htm'  
#  	 		
# 	if not os.path.lexists(filename): 
# 		print "[*] Missing Commented On By: "+username  
# 	else: 
# 		html = open(filename, 'r').read() 
# 		downloadsize=downloadsize+sys.getsizeof(html) 
# 		dataList = parsePhotosCommented(html) 
# 		write2Database('photosCommented',dataList)
# 
# 	filename = username+"/"+username+'.htm' 		
# 
#  	
# 
# 
#  	 		
#   	     
# 			
# 	print "[*] Extracting Friends from Likes/Comments: "+username 
# 	datalist=sidechannelFriends(uid)
# 	nrfriends=len(datalist)
# 	write2Database('friends',datalist) 
# 	graphdata=[]
# 	for i in datalist: 
# 		graphdata.append([username, i[2]])
# 	write2Database('graphdata', graphdata)
#  		
# 	if profile == True: 
# 		#userprofile
# 		print "[*] Downloading User Information" 
# 		tmpInfoStr = [] 
# 		userID =  getFriends(uid) 
# 		html2="" 
# 		for x in userID: 
# 			i = str(normalize(x[2])) 
# 			i = i.replace("('","").replace("',","").replace(')','') 
# 			i = i.replace('"https://www.facebook.com/','') 
# 			print "[*] Looking up information on "+i 
# 			filename = i.encode('utf8')+'.html' 
# 			if "/" not in filename: 
# 				if not os.path.exists(i.encode('utf8')): 
# 					os.makedirs(i.encode('utf8')) 
# 				filename = i.encode('utf8')+"/"+filename 
# 				if not os.path.lexists(filename): 
# 					print 'Writing to '+filename 
# 					url = 'https://www.facebook.com/'+i.encode('utf8')+'/about?section=living' 
# 					html = downloadFile(url) 
# 					if len(html)>0: 
# 						text_file = open(filename, "w") 
# 						text_file.write(normalize(html)) 
# 						text_file.close() 
#   				else: 
#   					print 'Skipping: '+filename	
#  	        		
#        		print "[*] Looking up edu information on "+i 
#        		filename2 = i.encode('utf8')+'_edu.html' 
#        		if "/" not in filename2: 
#        			if not os.path.exists(i.encode('utf8')): 
#        				os.makedirs(i.encode('utf8'))
#        			filename2 = i.encode('utf8')+"/"+filename2   
#        			if not os.path.lexists(filename2): 
#        				print 'Writing to '+filename2  
#        				url = 'https://www.facebook.com/'+i.encode('utf8')+'/about?section=education' 
#        				html2 = downloadFile(url) 
#        				if len(html2)>0: 
#        					text_file = open(filename2, "w") 
#        					text_file.write(normalize(html2)) 
#        					text_file.close() 
#        			else: 
#        				print 'Skipping: '+filename2
#          				 
# 	   		print "[*] Looking up contact information on "+i 
# 	   		filename3 = i.encode('utf8')+'_con.html' 
# 	   		if "/" not in filename3:
# 	   			if not os.path.exists(i.encode('utf8')): 
# 	   				os.makedirs(i.encode('utf8'))	   			
# 	   			filename3 = i.encode('utf8')+"/"+filename3   
# 	   			if not os.path.lexists(filename3): 
# 	   				print 'Writing to '+filename3  
# 	   				url = 'https://www.facebook.com/'+i.encode('utf8')+'/about?section=contact-info' 
# 	   				html3 = downloadFile(url) 
# 	   				if len(html3)>0: 
# 	   					text_file = open(filename3, "w") 
# 	   					text_file.write(normalize(html3)) 
# 	   					text_file.close() 
# 	   			else: 
#    				print 'Skipping: '+filenamew3 	
#  	        				
#        		print "[*] Parsing User Information: "+i 
#        		print filename
#        		html = open(filename, 'r').read() 
#        		downloadsize=downloadsize+sys.getsizeof(html)
#        		userInfoList = parseUserInfo(html)[0] 
#        		html2 = open(filename2, 'r').read() 
#        		downloadsize=downloadsize+sys.getsizeof(html2)
#        		edustr=parseUserEdu(html2) 
#        		html3 = open(filename3, 'r').read() 
#        		downloadsize=downloadsize+sys.getsizeof(html3)
#        		genstr=parseUserGen(html3) 
#        		tmpStr = [] 
#        		tmpStr.append([uid,str(normalize(i)),str(normalize(edustr)),str(normalize(userInfoList[1])),str(normalize(userInfoList[2])),str(normalize(userInfoList[3])),str(normalize(genstr)),str(normalize(userInfoList[5])),normalize(str(userInfoList[6]).encode('utf8'))])			#tmpStr.append([uid,"str(normalize(i))","str(normalize(userInfoList[0]))","str(normalize(userInfoList[1]))","str(normalize(edustr))","str(normalize(userInfoList[3]))","str(normalize(userInfoList[4]))","str(normalize(userInfoList[5]))","normalize(str(userInfoList[6]).encode('utf8'))"]) 
#        		try: 
#        			write2Database('friendsDetails',tmpStr) 
#        		except: 
#        			continue  	 			       
 	print "DONE"
	return (downloadsize, nrfriends)

def mainProcess():
	c = conn.cursor()
	c.execute('select distinct sourceUID, username, channel from metadata')
	dataList = c.fetchall() 
	for n in dataList:
		if n[2] == "main": 
			produce(n[0], n[1])
	#createGraphML() 
	conn.close() 
	sys.exit()

if __name__ == '__main__': 
	mainProcess()
 
