# -*- coding: utf-8 -*-

import sys
import re
import os
import time
import sqlite3
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from wordcloud import WordCloud, STOPWORDS
import module.Database

global uid
global postcount

#NR of posts downloaded per user
postcount=200

#facebook dummy account login info 
facebook_username = "cirtemys2@gmail.com"
facebook_password = "moons6"

#browser settings images disabled 
chrome_options = Options()
chrome_options.add_experimental_option( "prefs", {'profile.default_content_settings.images': 2})
driver = webdriver.Chrome(chrome_options=chrome_options)

reload(sys)  
sys.setdefaultencoding('utf8')
module.Database.createDatabase()
conn = sqlite3.connect('facebook.db')
conn.text_factory = str

def normalize(s):
	if type(s) == unicode: 
       		return s.encode('utf8', 'ignore')
	else:
        	return str(s)
def loginFacebook(driver):
	driver.implicitly_wait(120)
	driver.get("https://www.facebook.com/")
	assert "Facebook - Log In or Sign Up" in driver.title
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
 
def produce3(username):
	print "[*] Username:\t"+str(username)
	downloadsize=0
 	
 	filename = os.path.realpath('.')+"/data/"+username+"/"+username+'_timeline.htm' 	
	html = open(filename, 'r').read()
	words2, count = parseTimeline(html, username) 
	
	return (count, words2)	

def mainProcess(usernames):
	print "Processing "+str(len(usernames)-1)+" usernames"
	words4=""
	loginFacebook(driver)
	timeread=time.time()
 	time0=time.clock()

	for username in usernames:
		if len(username) is not 0: 
			username=username.strip()
			time1=time.clock() 
			count, words3 =produce3(username) 
			module.Database.edit2(username, count, conn)
			time2=time.clock()
			words4=words4+" "+words3

 	
 	time3=time.clock()
 	timeread=time.time()-timeread
 	print "TOTAL TIME"
 	print time3-time0
 	print timeread
 	more_stopwords =["ja", "aga", "kui", "siis", "tongue", "nii", "ka", "et", "see", "ma","oma","oli", "emoticon", "ei","ning", "seda", "või", "smile", "grin", "Kas", "kes", "veel"]
 	for more in more_stopwords: 
 		STOPWORDS.add(more)
 	utf=["Translation", "nüüd", "või", "ära", "Kas"]
  	for u in utf: 
  		words4=words4.replace(u, "")
 	wordcloud = WordCloud(stopwords=STOPWORDS).generate(words4)
	image = wordcloud.to_image()
	image.save("words.png","PNG")
	driver.close() 
 	driver.quit 
 	conn.commit()
 	conn.close() 
	print "Done"


def parseTimeline(html,username): 
	peopleIDLikes= []
	textdump=""
	count=0
	soup=[] 
	soup = BeautifulSoup(html)	
	timeline = soup.findAll("span",{"class" : "fsm fwn fcg"}) 
	postnr=0
	words1=""
	print "parsing timeline"
	for i in timeline: 
		n=BeautifulSoup(str(i)).findAll("a")
		if n is not None:
			if len(n)>0:
				try:  
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
									i=(i.text).replace("&&&", " ")
									textdump=textdump+" &&& "+i
									words1=words1+" "+i
		  				
						comments=soup2.findAll("div",{"class" : "UFICommentContent"}) 
						for i in comments: 
							if username in str(i):
								soup3=BeautifulSoup(str(i)) 
								comments2=soup3.findAll("span", {"class" : "UFICommentBody"}) 
								count+=1 
								for u in comments2: 
									u=(u.text).replace("&&&", " ")
									textdump=textdump+" &&& "+u
									words1=words1+" "+u
				except IndexError:
					print "no refrence" 
  				
# 				q=parseLikesPosts(n[3])
# 				if q is not None: 
# 					peopleIDLikes.append(q)
	filename=os.path.realpath('.')+"/data/"+username+"/"+username+'_dump.txt'
	text_file = open(filename, "w")
	text_file.write(normalize(textdump.encode('utf8')))
	text_file.close()

# 	datalist=[]
# 	datalist.append([username])
# 	write2Database('txt', datalist)			
	return words1, count

def parsePost(id,username):
	filename = 'posts/posts__'+str(id)
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
	
def options(arguments):
	if len(facebook_username)<1 or len(facebook_password)<1: 
		print "[*] Please fill in 'facebook_username' and 'facebook_password' before continuing." 
		sys.exit()
	users = ""
	users = open("input.txt", 'r').read().split("\n")	        
  	mainProcess(users)

if __name__ == '__main__':
	options(sys.argv)
 
