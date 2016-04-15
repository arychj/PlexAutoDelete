#!/usr/bin/env python

import os, shutil, sys, urllib2
from urllib import quote
import xml.etree.ElementTree as ET

_config = None

def Init(file):
	global _config 

	tree = ET.parse(file)
	_config = tree.getroot()
	
def Main():
	global _config

	for xLibrary in _config.findall('libraries/library'):
		for xShow in xLibrary.findall('./show'):
			xSearch = CallPlex("/library/sections/%s/search/?type=2&query=%s" % (xLibrary.attrib['section'], quote(xShow.text)))
			xResults = xSearch.findall('Directory')
			if len(xResults) == 1:
				xSeasons = CallPlex(xResults[0].attrib['key'])
				for xSeason in xSeasons.findall('Directory'):
					xEpisodes = CallPlex(xSeason.attrib['key'])
					for xEpisode in xEpisodes:
						if 'viewCount' in xEpisode.attrib:
							for xPart in xEpisode.findall('Media/Part'):
								title = GetEpisodeTitle(xShow.text, xSeason.attrib['index'], xEpisode.attrib['index'])

								if xShow.attrib['action'] == 'trash':
									print("Trashing '%s'..." % (title))
									Trash(xShow.text, xPart.attrib['file'])
								elif xShow.attrib['action'] == 'delete':
									print("Deleting '%s'..." % (title))
									Delete(xPart.attrib['file'])
									
def CallPlex(key):
	global _config, _platform, _plexBaseUrl

	url = "http://%s:%s%s" % (_config.find('server/host').text, _config.find('server/port').text, key)

	stream = urllib2.urlopen(url)
	sResponse = stream.read()
	xResponse = ET.fromstring(sResponse)

	return xResponse

def GetEpisodeTitle(show, season, episode):
	return "%s - S%02dE%02d" % (show, int(season), int(episode))

def Trash(show, file):
	global _config

	if _config.find('settings/debug').text != 'False':
		print 'FAKE TRASH'
	else:
		if os.path.isfile(file):
			destination = "%s/%s" % (_config.find('settings/directories/trash').text, show)
			if os.path.isdir(destination) != True:
				os.makedirs(destination)
			
			shutil.move(file, destination)

def Delete(file):
	global _config

	if _config.find('settings/debug').text != 'False':
		print 'FAKE DELETE'
	else:
		if os.path.isfile(file):
			os.remove(file)

### run the program ###
if len(sys.argv) != 2:
	print '\tUsage: ' + sys.argv[0] + ' config.xml'
else:
	Init(sys.argv[1])
	Main()
