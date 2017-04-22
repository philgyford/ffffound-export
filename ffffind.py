#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

	ash_ffffind.py
	v1.1 (September 14, 2015)
	by me@aaronhildebrandt.com
	
	Automatically downloads all images from ffffound saved by a specific user.
	Will first try to download the image from the original source (to get the highest quality possible).
	If that fails, it'll download the cached version from ffffound.
	
	Prerequisities:
		Beautiful Soup (http://www.crummy.com/software/BeautifulSoup/)
		requests (http://docs.python-requests.org)
	
	Usage:
		python ffffind.py username

"""



import os, re, sys, requests, time, urllib, imghdr
from BeautifulSoup import BeautifulSoup
from urlparse import urlparse
from posixpath import basename, dirname

reload(sys)
sys.setdefaultencoding('utf8')

headers = {'user-agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11'}

def main(user):
	offset = 0
	page = 1
	# Where we'll save the pages. Images will be in an "images" dir in here:
	base_path = user+"/"
	while True:
		images = []
		print "Capturing page "+str(page)+" ..."
		print
		r = requests.get("http://ffffound.com/home/"+user+"/found/?offset="+str(offset), headers=headers)
		s = r.text.replace(u"\xc2\xa0", u" ")
		if "<div class=\"description\">" in s:
			offset += 25
			soup = BeautifulSoup(s)
			for i in soup.findAll("div", { "class" : "description" }):
				# The URL of the original image:
				url = urlparse("http://" + str(i).split("<br />")[0].replace("<div class=\"description\">", ""))
				# The date+time the image was safed on Ffffound:
				try:
					save_time = str(i).split("<br />")[1][:19]
				except IndexError:
					save_time = str(i).split("<br />")[0][:19]
				images.append({
					"image_url": url.geturl(),
					# Where we'll save the file to:
					"filename": basename(url.path),
					"filepath": base_path+"images/"+basename(url.path),
					"save_time": save_time
				})
			count = 0
			for i in soup.findAll("div", { "class": "title" }):
				try:
					a = i.findAll("a")[0]
				except IndexError:
					# Original URL is missing.
					images[count]["page_title"] = str(i).replace("<span class=\"quote\">Quoted from:</span>", u"")
					images[count]["page_url"] = u""
				else:
					# The <title> of the original page the image was on:
					images[count]["page_title"] = a.string
					# The URL of the original page the image was on:
					images[count]["page_url"] = a["href"]
				count += 1
			count = 0
			for i in soup.findAll("img"):
				if str(i).find("_m.") != -1:
					# The version of the image on Ffffound, in case the 
					# original no longer exists:
					images[count]["backup"] = str(i).split("src=\"")[1].split("\"")[0]
					count += 1
			for i in images:
				if os.path.exists(i["filepath"]):
					# We already have a file with this name.
					# Make a unique version by adding the time to it.
					parts = os.path.splitext(i["filename"])
					t = str(time.time()).replace(".", "")
					new_filename = parts[0] + "_" + t + parts[1]
					new_filepath = base_path+"images/"+new_filename
					print i["filepath"] + " exists, using " + new_filepath + "."
					i["filename"] = new_filename
					i["filepath"] = new_filepath

				print "Downloading " + basename(i["image_url"]),
				try:
					urllib.urlretrieve(i["image_url"], i["filepath"])
					print "... done."
					if not imghdr.what(i["filepath"]) in ["gif", "jpeg", "png", None]:
						print "... unfortunately, it seems to be a bad image.\nDownloading backup",
						try:
							urllib.urlretrieve(i["backup"], i["filepath"])
							print "... which seems to have worked."
						except:
							print "... which also failed."
					if os.path.getsize(i["filepath"]) < 5000:
						raise
				except:
					print "... failed. Downloading backup",
					try:
						urllib.urlretrieve(i["backup"], i["filepath"])
						print "... which seems to have worked."
					except:
						print "... which also failed."
				print
			page += 1
		else:
			print "Reached the end of the list, stopping."
			break

	if len(images) == 0:
		sys.exit()

	f = open(base_path+"styles.css", "w")
	f.write(u"""
body {
	font-family: Georgia;
	color: #000000;
	background-color: #ffffff;
	font-size: 14px;
}	
h1 {
	font-size: 40px;
}
""")
	count = 1
	for chunk in list(chunks(images, 25)):

		html = u""

		for i in chunk:
			if i["page_url"] == "":
				page_link = i["page_title"]
			else:
				page_link = u'<a href="%(page_url)s">%(page_title)s</a>' % ({
						"page_url": i["page_url"],
						"page_title": i["page_title"],
					})

			html += u"""
<div class="asset">
	<div class="header">
		<div class="title">
			<span class="quote">Quoted from:</span>
			%(page_link)s
		</div>
	</div>
	<div class="description">
		%(tidy_page_url)s
		<br>
		%(save_time)s
	</div>
	<div class="image">
		<a href="%(img_url)s" title="See full-size version">
			<img src="%(img_url)s" alt="%(page_title)s">
		</a>
	</div>
</div>
""" % ({
	"page_link": page_link,
	"page_title": i["page_title"],
	"tidy_page_url": re.sub(r'^https?://', u'', i["page_url"]),
	"save_time": i["save_time"],
	"img_url": u"images/" + i["filename"],
})

		f = open(base_path+"page"+str(count)+".html", "w")

		f.write(u"""<!doctype html>
<html>
    <head>
        <meta charset="utf-8">
        <meta http-equiv="x-ua-compatible" content="ie=edge">
        <title>FFFFOUND! (page %(count)s)</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link rel="stylesheet" href="styles.css">
    </head>
    <body>
	<h1>%(user)s&rsquo;s found</h1>
	%(images)s
	</body>
</html>""" % ({
	"count": count,
	"user": user,
	"images": html,
}))

		f.close()

		count += 1



	
def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in xrange(0, len(l), n):
        yield l[i:i + n]


if __name__ == '__main__':
	print
	print("ffffound image downloader")
	print
	if len(sys.argv) < 2:
		print "Usage:\n\t python ffffind.py username"
		print
	else:
		try:
			if not os.path.exists("./"+sys.argv[1]):
				os.mkdir(sys.argv[1])
				os.mkdir(sys.argv[1]+"/images")
			else:
				print "%s directory already exists." % sys.argv[1]
				sys.exit()
		except:
			print "Error creating directory."
			sys.exit()
		user = sys.argv[1]
		print "Downloading all pictures from user '"+user+"'"
		print
		main(user)
