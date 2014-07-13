import urllib2
import mechanize
from bs4 import BeautifulSoup
import os


def get_html(url):
	header = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}

	request = urllib2.Request(url, headers=header)

	try:
		br = mechanize.Browser()
		response = br.open(request)
		return response.get_data()
	except urllib2.HTTPError, e:
		print e.fp.read()


def get_info(title):
	movie = {}

	url = "http://www.imdb.com/title/{}".format(title)

	site = BeautifulSoup(get_html(url))

	top_bar = site.find(id="overview-top")
	
	header = top_bar.find("h1", {"class": "header" })
	movie['name'] = header.find("span", {"itemprop": "name"}).string
	movie['year'] = header.find("a").string

	info_bar = top_bar.find("div", {"class": "infobar"})

	try:
		movie['content_rating'] = info_bar.find("span", {"itemprop": "contentRating"})['content']
	except TypeError as e:
		movie['content_rating'] = "N/A"

	movie['duration'] = info_bar.find("time").string
	index = movie['duration'].find(" min")
	movie['duration'] = movie['duration'][:index]

	movie['release_date'] = info_bar.find("meta", {"itemprop": "datePublished"})['content']

	movie['rating'] = top_bar.find("div", {"class": "star-box"}).find("div", {"class": "star-box-giga-star"}).string
	movie['director'] = top_bar.find("div", {"itemprop": "director"}).find("span", {"itemprop": "name"}).string
	movie['actors'] = [tag.string for tag in top_bar.find("div", {"itemprop": "actors"}).find_all("span", {"itemprop": "name"})]

	movie['genre'] = [tag.string for tag in site.find("div", {"id": "titleStoryLine"}).find("div", {"itemprop": "genre"}).find_all("a")]

	details = site.find("div", {"id": "titleDetails"})
	movie['country'] = details.find("h4", text="Country:").parent.find("a").text

	# Find award wins and nominations.
	awards = site.find("div", {"id": "titleAwardsRanks"}).find_all("span", {"itemprop": "awards"})
	awards = [award.find("b").text for award in awards if award.find("b") is not None]

	oscar_nominations = 0
	oscar_wins = 0
	for award in awards:
		if "Nominated" in award:
			start = "for "
			end = "Oscar"
			oscar_nominations = int(award[award.find(start) + len(start) : award.rfind(end)])
		elif "Won" in award:
			start = "Won"
			end ="Oscar"
			oscar_wins = int(award[award.find(start) + len(start) : award.rfind(end)])

	movie['oscar_nominations'] = oscar_nominations
	movie['oscar_wins'] = oscar_wins

	for prop in movie:	
		
		if not str(type(movie[prop])) == "<type 'list'>":	#  :'(
			movie[prop] = str(movie[prop]).strip(" \t\n\r")
		else:
			movie[prop] = str([ele.encode("utf-8").strip(" \t\n\r") for ele in movie[prop]])

	
	return movie


# print get_info(imdb_movie_id)
