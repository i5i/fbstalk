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

reload(sys)  
sys.setdefaultencoding('utf8')

def normalize(s):
	if type(s) == unicode: 
       		return s.encode('utf8', 'ignore')
	else:
        	return str(s)
 
def produce3(username):
	print "[*] Username:\t"+str(username)
 	n=0
	finalcount=0
	while n < 12:
		n+=1
		filename = os.path.realpath('.')+"/data/"+username+"/"+username+'_2015_'+str(n)+'.htm'
		if os.path.lexists(filename):
			html = open(filename, 'r').read()
			count = parseTimeline(html, username) 
	 	 	finalcount+=count
	return (finalcount)	

def delete(username):
	print "Delete Username:\t"+str(username)
	n=0
	while n < 12:
		n+=1
		filename = os.path.realpath('.')+"/data/"+username+"/"+username+'_2015_'+str(n)+'.htm'
		if os.path.lexists(filename): 	
			os.remove(filename)

def parseTimeline(html,username): 
	peopleIDLikes= []
	textdump=""
	soup=[] 
	soup = BeautifulSoup(html)	
	# 	timeline = soup.findAll("span",{"class" : "fsm fwn fcg"})
	timeline = soup.findAll("div",{"class" : "userContentWrapper _5pcr"})
	postnr=len(timeline)
	return postnr

def mainProcess(usernames):
	print "Processing "+str(len(usernames)-1)+" usernames"
	timeread=time.time()
 	time0=time.clock()
	for username in usernames:
		if len(username) is not 0: 
			username=username.strip()
			final=produce3(username)
			print final
			if final==0:
				delete(username)
 	time3=time.clock()
 	timeread=time.time()-timeread
 	print "TOTAL TIME"
 	print time3-time0
	print "Done"
	
def options(arguments):
	users = ""
	users = open("input.txt", 'r').read().split("\n")	        
  	mainProcess(users)

if __name__ == '__main__':
	options(sys.argv)
 
