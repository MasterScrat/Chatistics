#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import json
import pprint
import operator
import numpy as np
import pandas as pd
import datetime
import pprint
from lxml import etree
import dateparser
import time

MAX_EXPORTED_MSGS = 1000*1000

pp = pprint.PrettyPrinter(indent=4)

print 'Parsing HTML file...'
archive = etree.parse('raw/messages.htm')

data = []

timestamp = ''
senderName = ''
text = ''

for element in archive.iter():
	tag = element.tag
	content = element.text

	if tag == 'p':
		text = content
		#print("%s (%s): %s" % (senderName, timestamp, text))

		# TODO conversationWithName!!
		row = [timestamp, senderName, senderName, senderName, senderName, text]
		data += [row]

	elif tag == 'span':
		className = element.get('class')

		if className == 'user':
			senderName = content
		elif className == 'meta':
			#dt = dateparser.parse(content[:-2])
			#timestamp = int(time.mktime(dt.timetuple()))
			#timestamp = datetime.date.fromtimestamp(timestamp).toordinal()
			timestamp = pd.to_datetime(content[:-7], format='%A, %B %d, %Y at %H:%M%p').toordinal()

	if len(data) >= MAX_EXPORTED_MSGS:
		break

print len(data), 'messages parsed.'

print 'Converting to DataFrame...'
df = pd.DataFrame(index=np.arange(0, 200000), columns=['timestamp', 'conversationWithId', 'conversationWithName','senderId', 'senderName', 'text'])
df = pd.DataFrame(data)

print 'Saving to pickle file...'
df.to_pickle('data/messenger.pkl')