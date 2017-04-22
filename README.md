# ffffind.py

A Python 2.7 script for downloading your [Ffffound](http://ffffound.com) images.

It will download the images, make HTML pages in which to view them, and save data about them all in a JSON file. It will first try to download the image from the original source (to get the highest quality possible), falling back to use the version cached at Ffffound.

This is based on [a script](https://gist.github.com/ashildebrandt/9ad37ea659a0fbff5a05#comments) by [Ash Hildebrandt](https://github.com/ashildebrandt). The many terrible things about this hacked together, cargo-cult script are all my fault, not his. Thanks Ash!

## Running it

Install the required modules using [pip](https://pip.pypa.io/en/stable/) probably in a [virtualenv](http://python-guide-pt-br.readthedocs.io/en/latest/dev/virtualenvs/):

	pip install -r requirements.txt

Then run the script:

	python ffffind.py username

Replace `username` with your username on Ffffound, eg:

	python ffffind.py philgyford

It can take a long time to run, depending on how many images you ffffound and how slowly the servers respond.

To test it with only a few pages you can pass in the number of pages to fetch.
e.g.:

	python ffffind.py philgyford 2

That will fetch the first two pages of pictures for `philgyford`.


## Results

If all goes well you will end up with a structure like this in the script's directory (but with your username):

	philgyford/
		images/
			0soundmagn01.jpg
			0001TV-1431.gif
			002.jpg
			etc...
		images.json
		page1.html
		page2.html
		page3.html
		etc...
		styles.css

Open `page1.html` in a web browser and enjoy those happy image-based memories.

### images.json

`images.json` contains data about all of the images saved. It is structured something like this:


	[
		{
			"page_title": "Photos of a traffic jam stuck in the woods for 70 years | Death and Taxes", 
			"backup_url": "http://img.ffffound.com/static-data/assets/6/eda34c4268e421ec4131f0a1b2ecba5e810ab12a_m.jpg", 
			"filename": "chatillon-car-graveyard-abandoned-cars-cemetery-belgium-4.jpg", 
			"image_url": "http://www.deathandtaxesmag.com/wp-content/uploads/2014/07/chatillon-car-graveyard-abandoned-cars-cemetery-belgium-4.jpg", 
			"save_time": "2014-07-11 18:36:57", 
			"page_url": "http://www.deathandtaxesmag.com/224339/photos-of-a-traffic-jam-stuck-in-the-woods-for-70-years/"
		}, 	
		...
	]

* `page_title` is the title of the web page the image was originally found on.
* `backup_url` is the URL of the version of the image displayed on Ffffound. This might be smaller than the original.
* `filename` is the name of the image in the `images` directory.
* `image_url` is the URL of the image on the original web page.
* `save_time` is the date and time the image was saved to Ffffound.
* `page_url` is the URL of the web page the image was originally found on.

The script tries to fetch the image from `image_url`, but if that fails, it uses `backup_url` instead.

Some images might not have an `image_url` and/or `page_url`, if, for example, the image was removed from Ffffound at the request of the copyright owner.


## Caveats

* There are some issues with encoding, that result in odd characters appearing in the generated pages. Ffffound doesn't have any content-type encoding specified and I've spent way too long trying to get this working nicely. Any suggestions welcome.
* I know the code is horrible.

## Contact

Phil Gyford  
phil@gyford.com  
@philgyford
