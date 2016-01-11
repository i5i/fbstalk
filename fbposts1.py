import time 
import datetime
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
chrome_options.add_argument('--proxy-server=http://127.0.0.1:8118')
chrome_options.add_experimental_option( "prefs", {'profile.default_content_settings.images': 2, 'profile.default_content_setting_values.notifications': 2})

facebook_usernames = [""]
facebook_password = ""

#encodes
reload(sys)  
sys.setdefaultencoding('utf8')

#setup
module.Database.createDatabase()
conn = sqlite3.connect('facebook.db')
conn.text_factory = str
def loginFacebook(driver, fbun):
	driver.implicitly_wait(120)
 	driver.get("https://www.facebook.com/")
	assert "Facebook - Log In or Sign Up" in driver.title
	time.sleep(3)
	driver.find_element_by_id('email').send_keys(fbun)
	driver.find_element_by_id('pass').send_keys(facebook_password)
	driver.find_element_by_id("loginbutton").click()
	html = driver.page_source
	if "Incorrect Email/Password Combination" in html:
		print "[!] Incorrect Facebook username (email address) or password"
		sys.exit()
 
def mainProcess(usernames):
#NUMBER OF FB ACCOUNTS
	fbct=8
	print "Processing "+str(len(usernames)-1)+" usernames"
	overlap=module.Database.getUsernames(usernames, conn)
	print str(overlap)+ " records already exist"
	if raw_input("Continue? Y/N ") == "y":
		driver = webdriver.Chrome(chrome_options=chrome_options) 
		loginFacebook(driver, facebook_usernames[0])
		timeread=time.time()
	 	time0=time.clock()
		userdata=[]
		driverct=0
		userct=0
		for username in usernames:
			if len(username) is not 0: 
				username=username.strip()
				time1=time.time() 
				size, w =module.Produce.produceYr(username, driver) 
				time2=time.time()
				ts = time.time() 
				st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
				print st
				list=[username, size, time2-time1, st]
				userdata.append(list)
				module.Database.write2Database("posts", userdata, conn)
				userdata=[]
				if w==True: 
	 				userct+=1
	 			if userct==3: 
	 				driver.close() 
	 				driver.quit 
	 				driver = webdriver.Chrome(chrome_options=chrome_options) 
	 				driverct+=1
	 				if driverct==fbct:
	 					time.sleep(600)
	 				driverct=driverct%fbct
	 				userct=0
	 				loginFacebook(driver, facebook_usernames[driverct])
	 	time3=time.clock()
	 	timeread=time.time()-timeread
	 	print "TOTAL TIME"
	 	print time3-time0
	 	print timeread
 		driver.close() 
 	 	driver.quit 
 	conn.close() 
	print "Done"

if __name__ == '__main__': 
	users = ""
	users = open("input.txt", 'r').read().split("\n")
  	mainProcess(users)
