#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import pandas as pd
import numpy as np
from lxml import etree

MAX_EXPORTED_MSGS = 1000*1000
OWN_NAME = 'Florian Laurent'

print 'Parsing HTML file...'
archive = etree.parse('raw/messages.htm')

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
			
			if senderName != conversationWithName and senderName != OWN_NAME:
				print 'Assuming', senderName, 'is', conversationWithName
				senderName = conversationWithName

			data += [[timestamp, conversationWithName, senderName, text]]
			#print("%s with %s (%s): %s" % (senderName, conversationWithName, timestamp, text))

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
			content = content.replace(', ' + OWN_NAME, '')
			content = content.replace(OWN_NAME + ', ', '')
			conversationWithName = content

	if len(data) >= MAX_EXPORTED_MSGS:
		break

print len(data), 'messages parsed.'

print 'Converting to DataFrame...'
df = pd.DataFrame(index=np.arange(0, len(data)), columns=['timestamp', 'conversationWithName', 'senderName', 'text'])
df = pd.DataFrame(data)

print 'Saving to pickle file...'
df.to_pickle('data/messenger.pkl')