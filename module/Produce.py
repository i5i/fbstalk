import os, re, sys, time, requests
from bs4 import BeautifulSoup
import DownloadsController
cookies = {}
all_cookies = {}
def normalize(s):
	if type(s) == unicode: 
       		return s.encode('utf8', 'ignore')
	else:
        	return str(s)

def downloadID(driver,username):
	#driver.get('https://www.facebook.com/'+str(username))
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

def downloadFile(url):	
	global cookies
	for s_cookie in all_cookies:
			cookies[s_cookie["name"]]=s_cookie["value"]
	r = requests.get(url,cookies=cookies)
	html = r.content
	return html

def convertUser2ID2(source,username):
 	fbid=0
 	m = re.search("<meta property=\"al:android:url\" content=\"fb://profile/(\d+)\"", str(source)) 
 	if m: 
		fbid = m.group(1) 
 	return fbid
  
def produce2(username):
	username = username.strip()
	if not os.path.exists(username): 
		os.makedirs(username)
	print "[*] Username:\t"+str(username)
	
	filename = upath+"/"+username+'_timeline.htm' 		
	html = open(filename, 'r').read() 
	uid = convertUser2ID2(html,username)
	if not uid:
		print "[!] Problem converting username to uid"
		return (0,0)
	else:
		print "[*] Uid:\t"+str(uid)
#downloadfriends
	downloadsize=sys.getsizeof(html)
	return (uid, downloadsize)

def produce(username, driver):
	username = username.strip()
	upath= os.path.realpath('.')+"/data/"+username
	if not os.path.isdir(upath): 
		os.makedirs(upath)
	print "[*] Username:\t"+str(username)
	filename = upath+"/"+username+'_timeline.htm' 		
	if not os.path.lexists(filename): 
		print "[*] Caching Timeline Page of: "+username 
		html =(downloadID(driver, username)).encode('utf8')
		text_file = open(filename, "w") 
		text_file.write(html) 
		text_file.close() 
	else: 
		html = open(filename, 'r').read() 
	uid = convertUser2ID2(html,username)
	if not uid:
		print "[!] Problem converting username to uid"
		return (0,0)
	else:
		print "[*] Uid:\t"+str(uid)
		
	print "[*] Looking up contact information on "+username 
	filename3 =upath+"/"+username+'_con.html'  
	if not os.path.lexists(filename3): 
		print 'Writing to '+filename3  
		url = 'https://www.facebook.com/'+username+'/about?section=contact-info' 
		driver.get(url)	
		html3 = driver.page_source
		if len(html3)>0: 
			text_file = open(filename3, "w") 
			text_file.write(normalize(html3)) 
			text_file.close() 
	else: 
		print 'Skipping: '+filename3
	
	html3 = open(filename3, 'r').read() 
	genstr=parseUserGen(html3) 
	downloadsize, filename = (DownloadsController.downloadFriends(driver, username))
	downloadsize+=sys.getsizeof(html)
	downloadsize+=sys.getsizeof(html3)
	return (uid, downloadsize, genstr)

def parseUserGen(html):
	usergen = "NA" 
	soup = BeautifulSoup(str(html)) 
# 	pageLeft = soup.findAll("code") 
# 	for i in pageLeft: 
# 		text = i.findAll(text=True)
# 		for s in text:
	u=soup.findAll("span", {"class": "_50f4"}) 
	for x in u: 
		if x.text == "Male" or x.text == "Female": 
			usergen=x.text
	return usergen
