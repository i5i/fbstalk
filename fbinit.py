import time 
import re
import sys
import os
import requests
import sqlite3
import module.Database
import module.Produce 
 
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
chrome_options = Options()
chrome_options.add_experimental_option( "prefs", {'profile.default_content_settings.images': 2})

#requests.adapters.DEFAULT_RETRIES = 10
#h = httplib2.Http(".cache")

facebook_username = "cirtemys2@gmail.com"
facebook_password = "moons6"
postcount=100
global uid
uid = ""
username = ""

#encodes
reload(sys)  
sys.setdefaultencoding('utf8')

#setup
module.Database.createDatabase()
conn = sqlite3.connect('facebook.db')
conn.text_factory = str

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
 
def mainProcess(usernames):
	print "Processing "+str(len(usernames)-1)+" usernames"
	overlap=module.Database.getUsernames(usernames, conn)
	print str(overlap)+ " records already exist"
	if raw_input("Continue? Y/N ") == "y":
		driver = webdriver.Chrome(chrome_options=chrome_options)
		loginFacebook(driver)
		timeread=time.time()
	 	time0=time.clock()
		userdata=[]
		userdata2=[]
		for username in usernames:
			if len(username) is not 0: 
				username=username.strip()
				time1=time.clock() 
				s, size, genstr =module.Produce.produce(username, driver) 
				time2=time.clock()
				list=[username, s]
				list2=[s, username, size, time2-time1 ,'0','0', genstr]
				userdata.append(list)
				userdata2.append(list2)
	 	time3=time.clock()
	 	timeread=time.time()-timeread
	 	print "TOTAL TIME"
	 	print time3-time0
	 	print timeread
	 	module.Database.write2Database("txt", userdata, conn)
	 	module.Database.write2Database("metadata", userdata2, conn)
 		driver.close() 
 	 	driver.quit 
 	conn.close() 
	print "Done"

if __name__ == '__main__': 
	if len(facebook_username)<1 or len(facebook_password)<1: 
		print "[*] Please fill in 'facebook_username' and 'facebook_password' before continuing." 
		sys.exit()
	users = ""
	users = open("input.txt", 'r').read().split("\n")
  	mainProcess(users)
