def parseFriends(html):
	if len(html)>0:
		print "parsing friendslist"
		friendList=[]
		soup = BeautifulSoup(html)	
		friendNameData = soup.findAll("div", {"class" : "fsl fwb fcb"})
		for i in friendNameData:
			r = re.compile('href="https://www.facebook.com/(.*?)\?fref') 
			m = r.search(str(i)) 
			if m: 
				try:
					friendName = m.group(1)
					friendName = friendName.replace('"https://www.facebook.com/','')
					print friendName
					friendList.append(friendName)
				except IndexError:
					continue
				except AttributeError:
					continue
		return friendList
