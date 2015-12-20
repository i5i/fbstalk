import sys, os, time

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys

def downloadFriends2(driver,userid):
    driver.get('https://www.facebook.com/'+str(userid)+'/friends')
    if "Sorry, we couldn't find any results for this search." in driver.page_source:
        print "Friends list is hidden"
        return ""
    else:
        #assert "Friends of " in driver.title
        lenOfPage = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
        match=False
        while(match==False):
                time.sleep(2)
                lastCount = lenOfPage
                lenOfPage = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
                if lastCount==lenOfPage:
                        match=True
        return driver.page_source
    
def downloadFriends(driver, username): 
    downloadsize=0

    #Friendslist
    filename = os.path.realpath('.')+"/data/"+username+"/"+username+'_friends.htm'
    print filename
    if not os.path.lexists(filename):
        print "[*] Caching Friends Page of: "+username
        html = (downloadFriends2(driver,username)).encode('utf8')
        text_file = open(filename, "w")
        text_file.write(html)
        text_file.close()
    else:
        html = open(filename, 'r').read()
    downloadsize=downloadsize+sys.getsizeof(html)
    return downloadsize, filename
