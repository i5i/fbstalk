import os, re, sys, time, requests, random
import BeautifulSoup
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
	if "Sorry, this page isn't available" in driver.page_source:
		print "[!] Cannot access page "+url
		return ""
	if "Sorry, this content isn't available right now"in driver.page_source:
		print "[!] Cannot access page "+url
		sys.exit() 
	return driver.page_source

def download2015(driver,username,n):
	#driver.get('https://www.facebook.com/'+str(username))
	url = 'https://www.facebook.com/'+username.strip()+'/timeline/2015/'+str(n)
	driver.get(url)	
	if "Sorry, this page isn't available" in driver.page_source:
		print "[!] Cannot access page "+url
		return "" 
 	if "Sorry, this content isn't available right now"in driver.page_source:
		print "[!] Cannot access page "+url
		sys.exit() 
 	lenOfPage = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
	match=False
	while(match==False): 
 		lastCount = lenOfPage 
 		time.sleep(random.randint(2, 5))
 		lenOfPage=driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
# 		soup=BeautifulSoup
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

def produce(username, driver):
	write=False
	username = username.strip()
	upath= os.path.realpath('.')+"/data/"+username
	if not os.path.isdir(upath): 
		os.makedirs(upath)
	print "[*] Username:\t"+str(username)
	filename = upath+"/"+username+'_timeline.htm' 		
	if not os.path.lexists(filename): 
		print "[*] Caching Timeline Page of: "+username 
		html =(downloadID(driver, username)).encode('utf8')
		if len(html)>0:
			write=True
			text_file = open(filename, "w") 
			text_file.write(html) 
			text_file.close() 
	else: 
		html = open(filename, 'r').read() 
	uid = convertUser2ID2(html,username)
	if not uid:
		print "[!] Problem converting username to uid"
		if os.path.lexists(filename): 
			os.remove(filename)
		sys.exit()
	else:
		print "[*] Uid:\t"+str(uid)
	time.sleep(random.randint(2, 5))
	downloadsize, filename = (DownloadsController.downloadFriends(driver, username))
	downloadsize+=sys.getsizeof(html)
	genstr="-"
	return (uid, downloadsize, genstr, write)

def produceYr(username, driver):
	w=False
	username = username.strip()
	downloadsize=0
	upath= os.path.realpath('.')+"/data/"+username
	if not os.path.isdir(upath): 
		os.makedirs(upath)
	print "[*] Crawling Timeline"
	n=9
	while n < 12:
		n+=1
		filename = upath+"/"+username+'_2015_'+str(n)+'.htm' 		
		if not os.path.lexists(filename): 
			print "[*] Caching 2015 Page "+str(n)+" of: "+username 
			html2 =(download2015(driver, username, n)).encode('utf8')
			if len(html2)>0: 
				w=True
				text_file = open(filename, "w") 
				text_file.write(html2) 
				text_file.close() 
		else: 
			print 'Skipping: '+filename
			html2 = open(filename, 'r').read() 
		downloadsize+=sys.getsizeof(html2)	
	return (downloadsize, w)
   
def produceGn(username, driver):
	username = username.strip()
	upath= os.path.realpath('.')+"/data/"+username
	if not os.path.isdir(upath): 
		os.makedirs(upath)
	print "[*] Username:\t"+str(username)	
# 	print "[*] Looking up contact information on "+username 
# 	filename3 =upath+"/"+username+'_con.html'  
# 	if not os.path.lexists(filename3): 
# 		print 'Writing to '+filename3  
# 		url = 'https://www.facebook.com/'+username+'/about?section=contact-info' 
# 		driver.get(url)	
# 		html3 = driver.page_source
# 		if len(html3)>0: 
# 			text_file = open(filename3, "w") 
# 			text_file.write(normalize(html3)) 
# 			text_file.close() 
# 	else: 
# 		print 'Skipping: '+filename3
# 		html3 = open(filename3, 'r').read() 
# 	genstr=parseUserGen(html3) 
	return (uid, downloadsize, genstr) 	


def parseUserGen(html):
	usergen = "NA" 
	soup = BeautifulSoup(str(html)) 
	u=soup.findAll("span", {"class": "_50f4"}) 
	for x in u: 
		if x.text == "Male" or x.text == "Female": 
			usergen=x.text
	return usergen
