# coding: utf-8

import scraperwiki
import lxml.html
import urllib2
import sys
from datetime import datetime

burl = "https://bulbapedia.bulbagarden.net"
url = burl + "/wiki/List_of_Pokemon_Trading_Card_Game_expansions"

types = {
  "Grass": "G",
  "Fire": "R",
  "Water": "W",
  "Lightning": "L",
  "Fighting": "F",
  "Psychic": "P",
  "Colorless": "C",
  "Darkness": "D",
  "Metal": "M",
  "Dragon": "N",
  "Fairy": "Y",
}

def open(url):
	req = urllib2.Request(url, headers={'User-Agent' : 'Mozilla/5.0 (X11; Linux i686; rv:64.0) Gecko/20100101 Firefox/64.0'})
	con = urllib2.urlopen( req )
	return con.read()

def build_db(url):
	html = open(url)
	root = lxml.html.fromstring(html)
	tr = root.cssselect('.sortable tr')
	for td in tr:
		a = td[3].cssselect("a")
		if len(a) > 0 and a[0].text != "Cosmic Eclipse":
			set_id = td[0].text.strip()
			set_name = td[3].cssselect("a")[0].text.strip()
			set_url = burl + td[3].cssselect("a")[0].attrib["href"]
			set_date = datetime.strptime(td[7].text.strip(), "%B %d, %Y")
			set_abbr = td[9].text.strip()
			if set_id == "":
				set_id = set_abbr
			record = {
				"id" : set_id,
				"set_name" : set_name,
				"abbr" : set_abbr,
				"date" : set_date,
				"url" : set_url,
			}
			scraperwiki.sqlite.save(unique_keys=["id"], data=record, table_name="sets")
			#parse_set(set_abbr, set_url)

def parse_set(set, url):
	counter = 0
	html = open(url)
	root = lxml.html.fromstring(html)
	tr = root.cssselect("tr > td:nth-of-type(1) > table.roundy:nth-of-type(1) > tr:nth-of-type(2) > td:nth-of-type(1) > table:nth-of-type(1) > tr")
	if len(tr) == 0:
		tr = root.cssselect("div#mw-content-text > h2 + table.roundy table[width='100%'] > tr")
	for el in tr:
		if len(el) == 6:
			a = el[2].cssselect('a')
			if len(a) > 0:
				num = el[0].text.split("/")[0].strip()
				if a[0].attrib['title'] == "Mega":
					name = "M " + a[1].text
				else:
					name = a[0].text
				if el[2].cssselect('img[alt="Tag Team GX"],img[alt="GX"]'):
					name = name + "-GX"
				elif el[2].cssselect('img[alt="EX"]'):
					name = name + "-EX"
				elif el[2].cssselect('img[alt="BREAK"]'):
					name = name + "-BREAK"
				if el[3].cssselect('img'):
					img = el[3].cssselect('img')
					type = img[0].attrib['alt']
				else:
					type = el[3].text.strip()
				if el[4].cssselect('a'):
					imgr = el[4].cssselect('a')
					rarity = imgr[0].attrib['title']
				else:
					rarity = el[4].text.strip()
				if type in types:
					type = types[type]
				record = {
					"id" : set+num,
					"set_abbr" : set,
					"n" : num,
					"name" : name,
					"url" : burl + a[0].attrib['href'],
					"type" : type,
					"rarity" : rarity,
				}
				counter = counter + 1
				scraperwiki.sqlite.save(unique_keys=["id"], data=record, table_name="cards")
	print set + " " + str(counter) + " entries"

build_db(url)
