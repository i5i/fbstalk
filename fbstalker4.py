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
from bs4.diagnose import profile
from wx import PostScriptDC

requests.adapters.DEFAULT_RETRIES = 10

h = httplib2.Http(".cache")

facebook_username = "cirtemys2@gmail.com"
facebook_password = "moons6"


global postcount
global uid
uid = ""
username = ""
postcount=100
internetAccess = True
cookies = {}
all_cookies = {}
reportFileName = ""

#For consonlidating all likes across Photos Likes+Post Likes
peopleIDList = []
likesCountList = []
timePostList = []
placesVisitedList = []

#Chrome Options
chromeOptions = webdriver.ChromeOptions()
prefs = {"profile.managed_default_content_settings.images":2}
chromeOptions.add_experimental_option("prefs",prefs)
driver = webdriver.Chrome(chrome_options=chromeOptions)

#encodes
reload(sys)  
sys.setdefaultencoding('utf8')


def createDatabase():
	conn = sqlite3.connect('facebook.db')
	c = conn.cursor()
	sql = 'create table if not exists photosLiked (sourceUID TEXT, description TEXT, photoURL TEXT unique, pageURL TEXT, username TEXT)'
	sql1 = 'create table if not exists photosCommented (sourceUID TEXT, description TEXT, photoURL TEXT unique, pageURL TEXT, username TEXT)'
	sql2 = 'create table if not exists friends (sourceUID TEXT, name TEXT, userName TEXT unique, month TEXT, year TEXT)'
	sql3 = 'create table if not exists friendsDetails (sourceUID TEXT, userName TEXT unique, userEduWork TEXT, userLivingCity TEXT, userGender TEXT)'
	sql6 = 'create table if not exists photosOf (sourceUID TEXT, description TEXT, photoURL TEXT unique, pageURL TEXT, username TEXT)'
	sql7 = 'create table if not exists photosBy (sourceUID TEXT, description TEXT, photoURL TEXT unique, pageURL TEXT, username TEXT)'
	sql8 = 'create table if not exists userdata (sourceUID TEXT, username TEXT, channel TEXT)'
	sql9 = 'create table if not exists graphdata (source TEXT, dest TEXT)'
	sql10 = 'create table if not exists graphdata2 (source TEXT, dest TEXT)' 
	sql11 = 'create table if not exists friends2 (sourceUID TEXT, name TEXT, userName TEXT unique)' 
	sql12 = 'create table if not exists metadata (sourceUID TEXT, username TEXT, datainbytes TEXT, speed TEXT, friendcount TEXT, posts TEXT)'
	sql13 = 'create table if not exists txt (username TEXT unique)'
	c.execute(sql)
    	c.execute(sql1)
    	c.execute(sql2)
    	c.execute(sql3)
    	c.execute(sql6)
    	c.execute(sql7)
    	c.execute(sql8)
    	c.execute(sql9)
    	c.execute(sql10)
    	c.execute(sql11)
    	c.execute(sql12)
    	c.execute(sql13)
    	conn.commit()

createDatabase()
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

def createMaltego(username):
	g = Graph()
	totalCount = 50
	start = 0
	nodeList = []
	edgeList = []

	while(start<totalCount):
       		nodeList.append("")	
	        edgeList.append("")
	        start+=1

	nodeList[0] = g.add_node('Facebook_'+username)
	nodeList[0]['node'] = createNodeFacebook(username,"https://www.facebook.com/"+username,uid)


	counter1=1
	counter2=0                
	userList=[]

	c = conn.cursor()
	c.execute('select userName from friends where sourceUID=?',(uid,))
	dataList = c.fetchall()
	nodeUid = ""
	for i in dataList:
		if i[0] not in userList:
			userList.append(i[0])
			try:
				nodeUid = str(convertUser2ID2(driver,str(i[0])))
				#nodeUid = str(convertUser2ID(str(i[0])))
			   	nodeList[counter1] = g.add_node("Facebook_"+str(i[0]))
   				nodeList[counter1]['node'] = createNodeFacebook(i[0],'https://www.facebook.com/'+str(i[0]),nodeUid)
   				edgeList[counter2] = g.add_edge(nodeList[0], nodeList[counter1])
   				edgeList[counter2]['link'] = createLink('Facebook')
    				nodeList.append("")
 		   		edgeList.append("")
    				counter1+=1
    				counter2+=1
			except IndexError:
				continue
	if len(nodeUid)>0:	
		parser = GraphMLParser()
		if not os.path.exists(os.getcwd()+'/Graphs'):
	    		os.makedirs(os.getcwd()+'/Graphs')
		filename = 'Graphs/Graph1.graphml'
		parser.write(g, "Graphs/Graph1.graphml")
		cleanUpGraph(filename)
		filename = username+'_maltego.mtgx'
		print 'Creating archive: '+filename
		zf = zipfile.ZipFile(filename, mode='w')
		print 'Adding Graph1.graphml'
		zf.write('Graphs/Graph1.graphml')
		print 'Closing'
		zf.close()
 

def cleanUpGraph(filename):
	newContent = []
	with open(filename) as f:
		content = f.readlines()
		for i in content:
			if '<key attr.name="node" attr.type="string" id="node"/>' in i:
				i = i.replace('name="node" attr.type="string"','name="MaltegoEntity" for="node"')
			if '<key attr.name="link" attr.type="string" id="link"/>' in i:
				i = i.replace('name="link" attr.type="string"','name="MaltegoLink" for="edge"')
			i = i.replace("&lt;","<")
			i = i.replace("&gt;",">")
			i = i.replace("&quot;",'"')
			newContent.append(i.strip())

	f = open(filename,'w')
	for item in newContent:
		f.write("%s\n" % item)
	f.close()

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

def convertUser2ID2(driver,username):
	url="http://graph.facebook.com/"+username
	resp, content = h.request(url, "GET")
	if resp.status==200:
		results = json.loads(content)
		if len(results['id'])>0:
			fbid = results['id']
			return fbid

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

def loginFacebook(driver):
	driver.implicitly_wait(120)
	driver.get("https://www.facebook.com/")
	assert "Welcome to Facebook" in driver.title
	time.sleep(3)
	driver.find_element_by_id('email').send_keys(facebook_username)
	driver.find_element_by_id('pass').send_keys(facebook_password)
	driver.find_element_by_id("loginbutton").click()
	global all_cookies
	all_cookies = driver.get_cookies()
	html = driver.page_source
	if "Incorrect Email/Password Combination" in html:
		print "[!] Incorrect Facebook username (email address) or password"
		sys.exit()


def write2Database(dbName,dataList):
	try:
		cprint("[*] Writing "+str(len(dataList))+" record(s) to database table: "+dbName,"white")
		#print "[*] Writing "+str(len(dataList))+" record(s) to database table: "+dbName
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

def downloadFile(url):	
	global cookies
	for s_cookie in all_cookies:
			cookies[s_cookie["name"]]=s_cookie["value"]
	r = requests.get(url,cookies=cookies)
	html = r.content
	return html

def downloadPhotosBy(driver,userid):
	driver.get('https://www.facebook.com/search/'+str(userid)+'/photos-by')
	if "Sorry, we couldn't find any results for this search." in driver.page_source:
		print "Photos commented list is hidden"
        lenOfPage = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
        match=False
        while(match==False):
                time.sleep(3)
                lastCount = lenOfPage
                lenOfPage = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
                if lastCount==lenOfPage:
                        match=True
	return driver.page_source

def downloadPhotosOf(driver,userid):
	driver.get('https://www.facebook.com/search/'+str(userid)+'/photos-of')
	if "Sorry, we couldn't find any results for this search." in driver.page_source:
		print "Photos commented list is hidden"
        lenOfPage = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
        match=False
        while(match==False):
                time.sleep(3)
                lastCount = lenOfPage
                lenOfPage = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
                if lastCount==lenOfPage:
                        match=True
	return driver.page_source

def downloadPhotosCommented(driver,userid):
	driver.get('https://www.facebook.com/search/'+str(userid)+'/photos-commented')
	if "Sorry, we couldn't find any results for this search." in driver.page_source:
		print "Photos commented list is hidden"
        lenOfPage = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
        match=False
        while(match==False):
                time.sleep(3)
                lastCount = lenOfPage
                lenOfPage = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
                if lastCount==lenOfPage:
                        match=True
	return driver.page_source
	
def downloadPhotosLiked(driver,userid):
	driver.get('https://www.facebook.com/search/'+str(userid)+'/photos-liked')
	if "Sorry, we couldn't find any results for this search." in driver.page_source:
		print "Pages liked list is hidden"
        lenOfPage = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
        match=False
        while(match==False):
                time.sleep(2)
                lastCount = lenOfPage
                lenOfPage = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
                if lastCount==lenOfPage:
                        match=True
	return driver.page_source

def downloadUserInfo(driver,userid):
	url = 'https://www.facebook.com/'+str(userid).strip()+'/info'
	driver.get(url)	
	if "Sorry, this page isn't available" in driver.page_source:
		print "[!] Cannot access page "+url
		return ""
        lenOfPage = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
        match=False
        while(match==False):
                time.sleep(3)
                lastCount = lenOfPage
                lenOfPage = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
                if lastCount==lenOfPage:
                        match=True
	return driver.page_source

def parseUserGen(html):
	usergen = "NA" 
	soup = BeautifulSoup(str(html)) 
	pageLeft = soup.findAll("code") 
	for i in pageLeft: 
		text = i.findAll(text=True)
		for s in text:
			u=BeautifulSoup(s).findAll("span", {"class": "_50f4"}) 
			for x in u: 
				if x.text == "Male" or x.text == "Female": 
					usergen=x.text
	return usergen

def parseUserEdu(html):
	userEduWork = [] 
	soup = BeautifulSoup(str(html)) 
	pageLeft = soup.findAll("code") 
	for i in pageLeft: 
		text = i.findAll(text=True)
		for s in text:
			u=BeautifulSoup(s).findAll("div", {"class": "_2lzr _50f5 _50f7"}) 
			for x in u: 		
				userEduWork.append((x.text))
	return userEduWork

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

def downloadTimeline(username):
	url = 'https://www.facebook.com/'+username.strip()
	driver.get(url)	
	print "[*] Crawling Timeline"
	if "Sorry, this page isn't available" in driver.page_source:
		print "[!] Cannot access page "+url
		return ""
        lenOfPage = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
        match=False
        while(match==False):
                lastCount = lenOfPage
                time.sleep(3)
                lenOfPage = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
                if lastCount==lenOfPage: 
                	match=True
	return driver.page_source




def downloadPage(url):
	driver.get(url)	
	html = driver.page_source
	return html

	
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

def getFriends2(uid):
	userList = []
	c = conn.cursor()
	c.execute('select userName from friends2 where sourceUID=?',(uid,))
	dataList1 = []
	dataList1 = c.fetchall()
	if len(dataList1)>0:
		for i in dataList1:
			userList.append([uid,'',str(normalize(i)),'',''])
	return userList

def downloadPagesLiked(driver,userid):
	driver.get('https://www.facebook.com/search/'+str(userid)+'/pages-liked')
	if "Sorry, we couldn't find any results for this search." in driver.page_source:
		print "Pages liked list is hidden"
        lenOfPage = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
        match=False
        while(match==False):
                time.sleep(3)
                lastCount = lenOfPage
                lenOfPage = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
                if lastCount==lenOfPage:
                        match=True
	return driver.page_source
	


def downloadFriends(driver,userid):
	driver.get('https://www.facebook.com/search/'+str(userid)+'/friends')
	if "Sorry, we couldn't find any results for this search." in driver.page_source:
		print "Friends list is hidden"
		return ""
	else:
		#assert "Friends of " in driver.title
	        lenOfPage = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
       		match=False
        	while(match==False):
        	        time.sleep(3)
               		lastCount = lenOfPage
                	lenOfPage = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
                	if lastCount==lenOfPage:
                	        match=True
		return driver.page_source

def parseFriends(html):
	print "parsing friendslist"
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
	peopleID = []
	filename = 'likes_'+str(id)
	if not os.path.lexists(filename):
		print "[*] Caching Post Likes: "+str(id)
		url = "https://www.facebook.com/browse/likes?id="+str(id)
		driver.get(url)	
		if "Sorry, this page isn't available" in driver.page_source:
			print "[!] Cannot access page "+url
			return ""
        	lenOfPage = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
        	match=False
        	while(match==False):
        	        time.sleep(1)
        	        lastCount = lenOfPage
               		lenOfPage = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
                	if lastCount==lenOfPage:
                	        match=True
		html1 = driver.page_source	
		text_file = open(filename, "w")
		text_file.write(normalize(html1))
		text_file.close()
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
		
# 		os.remove(filename)
		return peopleID	

def parsePost(id,username):
	filename = 'posts__'+str(id)
	if not os.path.lexists(filename):
		print "[*] Caching Facebook Post: "+str(id)
		url = "https://www.facebook.com/"+username+"/posts/"+str(id)
		driver.get(url)	
		if "Sorry, this page isn't available" in driver.page_source:
			print "[!] Cannot access page "+url
			return ""
        	lenOfPage = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
        	match=False
        	while(match==False):
        	        time.sleep(1)
        	        lastCount = lenOfPage
               		lenOfPage = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
                	if lastCount==lenOfPage:
                	        match=True
		html1 = driver.page_source	
		text_file = open(filename, "w")
		text_file.write(normalize(html1))
		text_file.close()
	else:
		html1 = open(filename, 'r').read()
	return html1

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
				userList.append([uid,'',str(normalize(i[0]))])
	c.execute('select distinct username from photosCommented where sourceUID=?',(uid,))
	dataList1 = []
	dataList1 = c.fetchall()
	if len(dataList1)>0:	
		for i in dataList1:
			if 'pages' not in str(normalize(i[0])):
				userList.append([uid,'',str(normalize(i[0]))])
	c.execute('select distinct username from photosOf where sourceUID=?',(uid,))
	dataList1 = []
	dataList1 = c.fetchall()
	if len(dataList1)>0:	
		for i in dataList1:
			if 'pages' not in str(normalize(i[0])):
				userList.append([uid,'',str(normalize(i[0]))])
	return userList

def parseTimeline(html,username): 
	peopleIDLikes= []
	textdump=""
	count=0
	soup = BeautifulSoup(html)	
	tlDateTimeLoc = soup.findAll("span",{"class" : "fsm fwn fcg"}) 
	postnr=0
 	for i in tlDateTimeLoc: 
 		n=BeautifulSoup(str(i)).findAll("a")
 		if len(n) > 0 : 
 			if "posts" in n[0]['href']  and postnr < postcount: 
 				postnr+=1
 				n=n[0]['href'].split("/") 			
 				html1=parsePost(n[3],username)
 				soup2= BeautifulSoup(html1) 
 				posted=soup2.findAll("span",{"class" : "fwb fcg"}) 
 				soup3= BeautifulSoup(str(posted))
 				posted2=soup3.findAll("a")
 				posted3=str(posted2).split(",")
 				if len(posted3)>0: 
 					if username in posted3[0]:
						count+=1
						posted4=soup2.findAll("div",{"class" : "_5pbx userContent"})
						for i in posted4:
							 textdump=textdump+" &&& "+i.text
 				
 				comments=soup2.findAll("div",{"class" : "UFICommentContent"}) 
 				for i in comments: 
 					if username in str(i):
 						soup3=BeautifulSoup(str(i)) 
 						comments2=soup3.findAll("span", {"class" : "UFICommentBody"}) 
 						count+=1 
 						for u in comments2: 
 							textdump=textdump+" &&& "+u.text
				q=parseLikesPosts(n[3])
				if q is not None: 
					peopleIDLikes.append(q)
	filename=username+"/"+username+'_dump.txt'
	text_file = open(filename, "w")
	text_file.write(normalize(textdump.encode('utf8')))
	text_file.close()
	datalist=[]
	datalist.append([username])
	write2Database('txt', datalist)			
	return peopleIDLikes, count

# 

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

def produce3(username):
	count=0
	username = username.strip()
	if not os.path.exists(username): 
		os.makedirs(username)
	global uid
	uid = convertUser2ID2(driver,username)
	if not uid:
		print "[!] Problem converting username to uid"
		sys.exit() 
		
	downloadsize=0
 	filename = username+"/"+username+'.htm' 
	nrfriends=0
    #additional information for deducing friends
 	filename = username+"/"+username+'_photosOf.htm'
  	if not os.path.lexists(filename):
  			print "[*] Caching Photos By: "+username
  			html = (downloadPhotosOf(driver,uid)).encode('utf8')
  			text_file = open(filename, "w")
  			text_file.write(html)
  			text_file.close()
  	else:
  			html = open(filename, 'r').read() 
  	print sys.getsizeof(html)	 			
  	downloadsize=downloadsize+sys.getsizeof(html)
	dataList = parsePhotosby(html) 
	write2Database('photosOf',dataList)	

#    	print filename
 	filename = username+"/"+username+'_photosLiked.htm'  	
	if not os.path.lexists(filename):
	   	print "[*] Caching Photos Liked By: "+username
		html = (downloadPhotosLiked(driver,uid)).encode('utf8')
		text_file = open(filename, "w")
		text_file.write(html)
		text_file.close()
	else:
		html = open(filename, 'r').read()
 	print sys.getsizeof(html)			
	downloadsize=downloadsize+sys.getsizeof(html)
	
	dataList = parsePhotosLiked(html)
 		
	filename = username+"/"+username+'_photoscommented.htm' 
 	 		
	if not os.path.lexists(filename): 
		print "[*] Caching Commented On By: "+username 
		html = (downloadPhotosCommented(driver,uid)).encode('utf8')
		text_file = open(filename,"w") 
		text_file.write(html) 
		text_file.close() 
	else: 
		html = open(filename, 'r').read() 
  	print sys.getsizeof(html)		
	downloadsize=downloadsize+sys.getsizeof(html)
	dataList = parsePhotosCommented(html)
	write2Database('photosCommented',dataList)
 	
 	if posts == True: 
 		print "TIMELINE"
 		filename = username+"/"+username+'.htm' 		
	 	if not os.path.lexists(filename): 
	 		print "[*] Caching Timeline Page of: "+username 
	 		html =(downloadTimeline(username)).encode('utf8')
	 		text_file = open(filename, "w") 
	 		text_file.write(html) 
	 		text_file.close() 
	 	else: 
	 		html = open(filename, 'r').read() 
		downloadsize=downloadsize+sys.getsizeof(html) 
		dataList, count = parseTimeline(html,username)  
		
	print "[*] Extracting Friends from Likes/Comments: "+username 
	datalist=sidechannelFriends(uid)
	if posts == True:
		for i in dataList:
			for u in i: 
				datalist.append([uid, '', u])
	nrfriends=len(datalist)
	print "Writing Deduced Friends to Database"
	write2Database('friends2',datalist) 
	graphdata=[]
	for i in datalist: 
		graphdata.append([username, i[2]]) 
	print "Writing Graph Data to Database"
	write2Database('graphdata2', graphdata) 
 	
	if profile == True: 
		#userprofile
		print "[*] Downloading User Information" 
		tmpInfoStr = [] 
		userID =  getFriends2(uid) 
		html2="" 
		for x in userID: 
			i = str(normalize(x[2])) 
			i = i.replace("('","").replace("',","").replace(')','') 
			i = i.replace('"https://www.facebook.com/','') 
			print "[*] Looking up information on "+i 
			filename = i.encode('utf8')+'.html' 
			if "/" not in filename: 
				if not os.path.exists(i.encode('utf8')): 
					os.makedirs(i.encode('utf8')) 
				filename = i.encode('utf8')+"/"+filename 
				if not os.path.lexists(filename): 
					print 'Writing to '+filename 
					url = 'https://www.facebook.com/'+i.encode('utf8')+'/about?section=living' 
					html = downloadFile(url) 
					if len(html)>0: 
						text_file = open(filename, "w") 
						text_file.write(normalize(html)) 
						text_file.close() 
  				else: 
  					print 'Skipping: '+filename	
 	        		
        		print "[*] Looking up edu information on "+i 
        		filename2 = i.encode('utf8')+'_edu.html' 
        		if "/" not in filename2: 
        			if not os.path.exists(i.encode('utf8')): 
        				os.makedirs(i.encode('utf8'))
        			filename2 = i.encode('utf8')+"/"+filename2   
        			if not os.path.lexists(filename2): 
        				print 'Writing to '+filename2  
        				url = 'https://www.facebook.com/'+i.encode('utf8')+'/about?section=education' 
        				html2 = downloadFile(url) 
        				if len(html2)>0: 
        					text_file = open(filename2, "w") 
        					text_file.write(normalize(html2)) 
        					text_file.close() 
        			else: 
        				print 'Skipping: '+filename2
	          				 
		   		print "[*] Looking up contact information on "+i 
		   		filename3 = i.encode('utf8')+'_con.html' 
		   		if "/" not in filename3:
		   			if not os.path.exists(i.encode('utf8')): 
		   				os.makedirs(i.encode('utf8'))	   			
		   			filename3 = i.encode('utf8')+"/"+filename3   
		   			if not os.path.lexists(filename3): 
		   				print 'Writing to '+filename3  
		   				url = 'https://www.facebook.com/'+i.encode('utf8')+'/about?section=contact-info' 
		   				html3 = downloadFile(url) 
		   				if len(html3)>0: 
		   					text_file = open(filename3, "w") 
		   					text_file.write(normalize(html3)) 
		   					text_file.close() 
		   			else: 
		   				print 'Skipping: '+filename3
	   	 	        				
	       		print "[*] Parsing User Information: "+i 

	       		html = open(filename, 'r').read() 
	       		downloadsize=downloadsize+sys.getsizeof(html.encode('utf8'))
	       		userInfoList = parseUserInfo(html)[0] 

	       		html2 = open(filename2, 'r').read() 
        		downloadsize=downloadsize+sys.getsizeof(html2)
        		edustr=parseUserEdu(html2) 

        		html3 = open(filename3, 'r').read() 
        		downloadsize=downloadsize+sys.getsizeof(html3)
        		genstr=parseUserGen(html3) 

	       		tmpStr = [] 
        		tmpStr.append([uid, str(normalize(i)), str(normalize(edustr)), str(normalize(userInfoList[2])), str(normalize(genstr)),])			#tmpStr.append([uid,"str(normalize(i))","str(normalize(userInfoList[0]))","str(normalize(userInfoList[1]))","str(normalize(edustr))","str(normalize(userInfoList[3]))","str(normalize(userInfoList[4]))","str(normalize(userInfoList[5]))","normalize(str(userInfoList[6]).encode('utf8'))"]) 
        		try: 
        			write2Database('friendsDetails',tmpStr) 
        		except: 
        			continue  	
 		
 	print "DONE"
	return (uid, downloadsize, nrfriends, count)		

def produce2(username):
	username = username.strip()
	if not os.path.exists(username): 
		os.makedirs(username)
	print "[*] Username:\t"+str(username)
	global uid
	uid = convertUser2ID2(driver,username)
	if not uid:
		print "[!] Problem converting username to uid"
		sys.exit()
	else:
		print "[*] Uid:\t"+str(uid)
	downloadsize=0
 	filename = username+"/"+username+'.htm' 
	nrfriends=0
	#Friendslist
	filename = username+"/"+username+'_friends.htm'
	print filename
	if not os.path.lexists(filename):
	   	print "[*] Caching Friends Page of: "+username
		html = (downloadFriends(driver,uid)).encode('utf8')
		text_file = open(filename, "w")
		text_file.write(html)
		text_file.close()
   	else:
		html = open(filename, 'r').read()
 
	downloadsize=downloadsize+sys.getsizeof(html)
  	dataList = parseFriends(html)
 	nrfriends=len(dataList)
 	print "[*] Writing Friends List to Database: "+username
	write2Database('friends',dataList)
	graphdata=[]
	for i in dataList: 
		graphdata.append([username, i[2]])
	print "Writing Graph Data to Database"
	write2Database('graphdata', graphdata) 
 	print "DONE"
 	
 
	if profile == True: 
		#userprofile
		print "[*] Downloading User Information" 
		tmpInfoStr = [] 
		userID =  getFriends(uid) 
		html2="" 
		for x in userID: 
			i = str(normalize(x[2])) 
			i = i.replace("('","").replace("',","").replace(')','') 
			i = i.replace('"https://www.facebook.com/','') 
			print "[*] Looking up information on "+i 
			filename = i.encode('utf8')+'.html' 
			if "/" not in filename: 
				if not os.path.exists(i.encode('utf8')): 
					os.makedirs(i.encode('utf8')) 
				filename = i.encode('utf8')+"/"+filename 
				if not os.path.lexists(filename): 
					print 'Writing to '+filename 
					url = 'https://www.facebook.com/'+i.encode('utf8')+'/about?section=living' 
					html = downloadFile(url) 
					if len(html)>0: 
						text_file = open(filename, "w") 
						text_file.write(normalize(html)) 
						text_file.close() 
  				else: 
  					print 'Skipping: '+filename	
  	        		
        		print "[*] Looking up edu information on "+i 
        		filename2 = i.encode('utf8')+'_edu.html' 
        		if "/" not in filename2: 
        			if not os.path.exists(i.encode('utf8')): 
        				os.makedirs(i.encode('utf8'))
        			filename2 = i.encode('utf8')+"/"+filename2   
        			if not os.path.lexists(filename2): 
        				print 'Writing to '+filename2  
        				url = 'https://www.facebook.com/'+i.encode('utf8')+'/about?section=education' 
        				html2 = downloadFile(url) 
        				if len(html2)>0: 
        					text_file = open(filename2, "w") 
        					text_file.write(normalize(html2)) 
        					text_file.close() 
        			else: 
        				print 'Skipping: '+filename2
 	          				 
		   		print "[*] Looking up contact information on "+i 
		   		filename3 = i.encode('utf8')+'_con.html' 
		   		if "/" not in filename3:
		   			if not os.path.exists(i.encode('utf8')): 
		   				os.makedirs(i.encode('utf8'))	   			
		   			filename3 = i.encode('utf8')+"/"+filename3   
		   			if not os.path.lexists(filename3): 
		   				print 'Writing to '+filename3  
		   				url = 'https://www.facebook.com/'+i.encode('utf8')+'/about?section=contact-info' 
		   				html3 = downloadFile(url) 
		   				if len(html3)>0: 
		   					text_file = open(filename3, "w") 
		   					text_file.write(normalize(html3)) 
		   					text_file.close() 
		   			else: 
		   				print 'Skipping: '+filename3
 	   	 	        				
	       		print "[*] Parsing User Information: "+i 
 	
	       		html = open(filename, 'r').read() 
	       		downloadsize=downloadsize+sys.getsizeof(html.encode('utf8'))
	       		userInfoList = parseUserInfo(html)[0] 
 	 
	       		html2 = open(filename2, 'r').read() 
        		downloadsize=downloadsize+sys.getsizeof(html2)
        		edustr=parseUserEdu(html2) 
    
        		html3 = open(filename3, 'r').read() 
        		downloadsize=downloadsize+sys.getsizeof(html3)
        		genstr=parseUserGen(html3) 
  
	       		tmpStr = [] 
        		tmpStr.append([uid, str(normalize(i)), str(normalize(edustr)), str(normalize(userInfoList[2])), str(normalize(genstr)),])			#tmpStr.append([uid,"str(normalize(i))","str(normalize(userInfoList[0]))","str(normalize(userInfoList[1]))","str(normalize(edustr))","str(normalize(userInfoList[3]))","str(normalize(userInfoList[4]))","str(normalize(userInfoList[5]))","normalize(str(userInfoList[6]).encode('utf8'))"]) 
        		try: 
        			write2Database('friendsDetails',tmpStr) 
        		except: 
        			continue  	
#        		
	return (uid, downloadsize, nrfriends)


 			

def mainProcess(usernames, rec):
	loginFacebook(driver)
	time0=time.clock()
	for username in usernames: 
		time1=time.clock() 
		s, bsize, nrfriends =produce2(username)
		time2=time.clock()
		print time2-time1
		tmpStr = [] 
		tmpStr.append([normalize(s),str(username), "main"]) 
		write2Database('userdata',tmpStr) 
		time3=time.clock() 
		s, asize, nrfriends2, count =produce3(username)
		time4=time.clock()
		print time4-time3
		tmpStr = [] 
		tmpStr.append([normalize(s),str(username), "side"]) 
		write2Database('userdata',tmpStr)
		tmpStr = [] 
		tmpStr.append([normalize(s),str(username), normalize(bsize+asize), normalize((time2-time1)+(time4-time3)), normalize(nrfriends+ nrfriends2),normalize(count)]) 
		write2Database('metadata',tmpStr)
	
	rec=int(rec) 
	userList=[]
	suserList=[]
	fullStr=[]
	fullStr2=[]
	print rec
	superrec=rec
	while rec > 0: 
		newlist=[]
		c = conn.cursor() 
		c.execute('select username from friends') 
		dataList = c.fetchall() 
		print dataList
		for i in dataList: 
			if i[0] not in userList: 
				userList.append(i[0])
				newlist.append(i[0])
		print "new"
		for user in newlist:
			print user
			time1=time.clock()
			s, bsize, nrfriends=produce2(user)
			time2=time.clock()
			print time2-time1
			tmpStr = [] 
			tmpStr.append([normalize(s),str(user), "main"])  
			write2Database('userdata',tmpStr) 
			fullStr.append([normalize(s),str(user), bsize, time2-time1, nrfriends]) 
 		newlist=[]
		c = conn.cursor() 
		c.execute('select username from friends2') 
		dataList = c.fetchall() 
		print "into data"
		for i in dataList: 
			if i[0] not in suserList: 
				suserList.append(i[0])
				newlist.append(i[0])
		print "new"
		for user in newlist:
			print "side"
			time1=time.clock()
			s, bsize, nrfriends, count=produce3(user)
			time2=time.clock()
			print time2-time1
			tmpStr = [] 
			tmpStr.append([normalize(s),str(user), "side"])  
			write2Database('userdata',tmpStr)
			fullStr2.append([normalize(s),str(user), bsize, time2-time1, nrfriends, count])
 		rec-=1
 	
	tmpStr=[]
	for i in fullStr:
		for n in fullStr2: 
			if i[1]==n[1]: 
				tmpStr.append([normalize(i[0]),str(i[1]), normalize(i[2]+n[2]), normalize(i[3]+n[3]), normalize(i[4]+ n[4]),normalize(n[5])]) 
	for i in fullStr: 
		if i[1] not in tmpStr[1:2]:
			tmpStr.append([normalize(i[0]),str(i[1]), normalize(i[2]), normalize(i[3]), normalize(i[4]),normalize(0)])
	for i in fullStr2: 
		if i[1] not in tmpStr[1:2]:
			tmpStr.append([normalize(i[0]),str(i[1]), normalize(i[2]), normalize(i[3]), normalize(i[4]),normalize(n[5])])
	write2Database('metadata',tmpStr)
	driver.close() 
	driver.quit 
	conn.close() 
	timez=time.clock()
	print "TOTAL TIME"
	print timez-time0

def options(arguments):
	user = ""
	user = open("input.txt", 'r').read().split(" ")
	global profile
	profile= False
	global posts
	posts=False
	for i in arguments: 
		if i == "-profile": 
			profile= True
		if i == "-posts":
			posts= True
	if len(arguments)>=1: 
		rec= int(arguments[1])
		print rec
	else:
		rec=0 	        
  	mainProcess(user, rec)


def showhelp():
	print """
	#####################################################
	#                  fbStalker.py                 #
	#               [Trustwave Spiderlabs]              #
	#####################################################
	Usage: python fbStalker.py [NUMBER OF RERUNS] [OPTIONS]

	[NUMBER OF RERUNS]
	a number representing how many times the program takes its own output as input
	subsequent runs take longer to process due to larger data loads
	
	[OPTIONS]

	-profile
	attempts to download education, work, location and gender information
	
	-posts
	downloads user posts and deduces friends from likes
	"""

if __name__ == '__main__':
	if len(sys.argv) <= 1:
		showhelp()
		driver.close()
		driver.quit
		conn.close()
		sys.exit()
 	else:
		if len(facebook_username)<1 or len(facebook_password)<1:
			print "[*] Please fill in 'facebook_username' and 'facebook_password' before continuing."
			sys.exit()
  		options(sys.argv)
 
