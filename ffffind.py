#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json, math, os, re, sys, requests, time, imghdr
from BeautifulSoup import BeautifulSoup
from urlparse import urlparse
from posixpath import basename, dirname
from shutil import copyfile
from jinja2 import Environment, PackageLoader, select_autoescape

reload(sys)
sys.setdefaultencoding('utf8')

headers = {'user-agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11'}

def main(user, pages="all"):
	"""
	user is a string, a ffffound.com username.
	pages is either "all" or the number of pages to fetch.
	"""
	offset = 0
	all_images = []
	page = 1
	# Where we'll save the pages. Images will be in an "images" dir in here:
	base_path = user+"/"
	img_path = base_path+"images/"
	while True:
		page_images = []
		print "Capturing page "+str(page)+" ..."
		print
		r = requests.get("http://ffffound.com/home/"+user+"/found/?offset="+str(offset), headers=headers)
		s = r.text.replace(u"\xc2\xa0", u" ")
		if "<div class=\"description\">" in s:
			offset += 25
			soup = BeautifulSoup(s)

			# Make the initial data about one image and add to page_images.
			for i in soup.findAll("div", { "class" : "description" }):
				if '<br />' in str(i):
					# There's a URL for the original image.
					url = urlparse("http://" + str(i).split("<br />")[0].replace("<div class=\"description\">", ""))
					image = {
						"image_url": url.geturl(),
						# Where we'll save the file to:
						"filename": basename(url.path),
						# The date+time the image was safed on Ffffound:
						"save_time": str(i).split("<br />")[1][:19],
					}
				else:
					# No URL for the original image.
					image = {
						"image_url": "",
						# This is terrible, but it'll get uniqified below...
						"filename": "backup_image",
						"save_time": str(i).replace("<div class=\"description\">", "")[:19],
					}
				page_images.append(image)

			# Add the page_title and page_url to each image's data.
			count = 0
			for i in soup.findAll("div", { "class": "title" }):
				try:
					a = i.findAll("a")[0]
				except IndexError:
					# Original URL is missing.
					page_images[count]["page_title"] = str(i)\
							.replace("<div class=\"title\">", u"")\
							.replace("</div>", u"")\
							.replace("<span class=\"quote\">Quoted from:</span>", u"")\
							.strip()
					page_images[count]["page_url"] = u""
				else:
					# The <title> of the original page the image was on:
					page_images[count]["page_title"] = a.string
					# The URL of the original page the image was on:
					page_images[count]["page_url"] = a["href"]

				count += 1


			# Add the backup_url to each image's data.
			count = 0
			for i in soup.findAll("img"):
				if str(i).find("_m.") != -1:
					# The version of the image on Ffffound, in case the 
					# original no longer exists:
					backup_url = str(i).split("src=\"")[1].split("\"")[0]
					page_images[count]["backup_url"] = backup_url
					count += 1

			for i in page_images:
				if os.path.exists(img_path+i["filename"]):
					# We already have a file with this name.
					# Make a unique version by adding the time to it.
					parts = os.path.splitext(i["filename"])
					t = str(time.time()).replace(".", "")
					new_filename = parts[0] + "_" + t + parts[1]
					print i["filename"] + " exists, using " + new_filename + "."
					i["filename"] = new_filename

				print "Downloading " + basename(i["image_url"]),

				# I can only apologise.
				try:
					r = requests.get(i['image_url'])
					print "... done."
					with open(img_path+i["filename"], 'wb') as f:
						f.write(r.content)
					if not imghdr.what(img_path+i["filename"]) in ["gif", "jpeg", "png"]:
						print "... unfortunately, it seems to be a bad image.\nDownloading backup",
						try:
							r = requests.get(i["backup_url"])
							with open(img_path+i["filename"], 'wb') as f:
								f.write(r.content)
							print "... which seems to have worked."
						except requests.exceptions.RequestException as err:
							print "... which also failed."
				except requests.exceptions.RequestException as e:
					print "... failed. Downloading backup",
					try:
						r = requests.get(i['backup_url'])
						with open(img_path+i["filename"], 'wb') as f:
							f.write(r.content)
						print "... which seems to have worked."
					except requests.exceptions.RequestException as e:
						print "... which also failed."
				print

			all_images += page_images

			if pages != "all" and page == pages:
				print "Reached page "+str(page)+", stopping."
				break

			page += 1
		else:
			print "Reached the end of the list, stopping."
			break

	if len(all_images) == 0:
		sys.exit()

	# Save the data as JSON:
	f = open(base_path+"images.json", "w")
	f.write( json.dumps(all_images, indent=2) )
	f.close()
	
	# Copy the CSS file over...
	copyfile('templates/styles.css', base_path+'styles.css')

	# And write all the pages...

	env = Environment(
		loader=PackageLoader('ffffind', 'templates'),
		autoescape=select_autoescape(['html',])
	)

	template = env.get_template('page.html')

	total_pages = int(math.ceil(float(len(all_images)) / 25))

	for page_count, page_images in enumerate(chunks(all_images, 25)):

		context = {
			'page_num': page_count+1,
			'user': user,
			'images': page_images,
		}

		if page_count < (total_pages - 1):
			context['next_page'] = page_count + 2

		if page_count > 0:
			context['previous_page'] = page_count

		f = open(base_path+"page"+str(page_count+1)+".html", "w")
		f.write( template.render(context) )
		f.close()

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

		pages = "all"
		if len(sys.argv) > 2:
			pages = int(sys.argv[2])

		if pages == "all":
			print "Downloading all pictures from user '"+user+"'"
		else:
			print "Downloading " + str(pages) + " page(s) of pictures from user '"+user+"'"
		print

		main(user, pages)

