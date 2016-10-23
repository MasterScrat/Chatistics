#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import matplotlib.pyplot as plt
from ggplot import *
import json
import pprint
import operator
import pandas as pd
import numpy as np
import datetime
import pprint

OWN_ID = "106758968942084595234"
MAX_EXPORTED_MSGS = 1000*1000

print 'Parsing JSON file...'
archive = json.load(open('raw/Hangouts.json'))

names = {}
def idToName(id):
	if id in names:
		return names[id]
	else:
		return None

data = []
conversationId = ""
conversationWithId = ""
conversationWithName = ""

#pp = pprint.PrettyPrinter(indent=4)

print 'Extracting messages...'
for state in archive["conversation_state"]:

	if "conversation_id" in state:
		conversationId = state["conversation_id"]["id"]

	if "conversation" in state["conversation_state"]:
		for participant in state["conversation_state"]["conversation"]["participant_data"]:
			if "fallback_name" in participant:
				names[participant["id"]["gaia_id"]] = participant["fallback_name"]

	for event in state["conversation_state"]["event"]:
		timestamp = int(event["timestamp"])

		if "conversation_id" in event:
			conversationId = event["conversation_id"]["id"]

		if "chat_message" in event and "segment" in event["chat_message"]["message_content"]:
			content = event["chat_message"]["message_content"]
			text = content["segment"][0]["text"]
			conversationId = event["conversation_id"]["id"]
			senderId = event["sender_id"]["chat_id"]

			# cant rely on current_participant! need to map conversation_id to interlocutor manually
			for participant in state["conversation_state"]["conversation"]["current_participant"]:
				if participant["gaia_id"] != OWN_ID:
					conversationWithId = participant["gaia_id"]

			if idToName(senderId)!=None or idToName(conversationWithId)!=None:
				row = [datetime.date.fromtimestamp(timestamp/1000000).toordinal(), conversationWithId, idToName(conversationWithId), senderId, idToName(senderId), text]
				data += [row]
			else:
				print "No senderName for either senderId", senderId, conversationWithId

			if len(data) >= MAX_EXPORTED_MSGS:
				break

print len(data), 'messages parsed.'

print 'Converting to DataFrame...'
df = pd.DataFrame(index=np.arange(0, 200000), columns=['timestamp', 'conversationWithId', 'conversationWithName','senderId', 'senderName', 'text'])
df = pd.DataFrame(data)

print 'Saving to pickle file...'
df.to_pickle('data/hangouts.pkl')