#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import pandas as pd
import numpy as np
from lxml import etree
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-ownName", dest='ownName', type=str, help="name of the owner of the chat logs, written as in the logs", required=True)
parser.add_argument('-f','-filePath', dest='filePath', help='Facebook chat log file (HTML file)', default='raw/messages.htm')
parser.add_argument("-max", "-maxExportedMessages", dest='maxExportedMessages', type=int, default=1000000, help="maximum number of messages to export")
args = parser.parse_args()

maxExportedMessages = args.maxExportedMessages
ownName = args.ownName
filePath = args.filePath

print 'Parsing HTML file...'
archive = etree.parse(filePath)

data = []
timestamp = ''
senderName = ''
conversationWithName = ''
text = ''

for element in archive.iter():
	tag = element.tag
	content = element.text
	className = element.get('class')

	if tag == 'p':
		text = content

		# sometimes facebook messes up and uses a "@facebook.com" id instead of the name :(
		if conversationWithName != None and '@' not in senderName:
			
			if senderName != conversationWithName and senderName != ownName:
				print 'Assuming', senderName, 'is', conversationWithName
				senderName = conversationWithName

			data += [[timestamp, conversationWithName, senderName, text]]

	elif tag == 'span':
		if className == 'user':
			senderName = content
		elif className == 'meta':
			timestamp = pd.to_datetime(content[:-7], format='%A, %B %d, %Y at %H:%M%p').toordinal()

	elif tag == 'div' and className == 'thread':
		if content.count(',') > 1:
			conversationWithName = None
		elif '@' in content:
			conversationWithName = None
		else:
			content = content.replace(', ' + ownName, '')
			content = content.replace(ownName + ', ', '')

			if content.count(',') > 0:
				print 'Parsing error, is your ownName correct?'
				exit(0)

			conversationWithName = content

	if len(data) >= maxExportedMessages:
		break

print len(data), 'messages parsed.'

print 'Converting to DataFrame...'
df = pd.DataFrame(index=np.arange(0, len(data)), columns=['timestamp', 'conversationWithName', 'senderName', 'text'])
df = pd.DataFrame(data)

print 'Saving to pickle file...'
df.to_pickle('data/messenger.pkl')