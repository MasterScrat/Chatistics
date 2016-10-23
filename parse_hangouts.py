#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import json
import pandas as pd
import numpy as np
import datetime

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

def saveNameForId(name, id):
	if not id in names:
		names[id] = name
	elif names[id] != name:
		print 'Assuming', name, 'is', names[id]

data = []
conversationId = ""
conversationWithId = ""
conversationWithName = ""

print 'Extracting messages...'
for state in archive["conversation_state"]:

	if "conversation_id" in state:
		conversationId = state["conversation_id"]["id"]

	if "conversation" in state["conversation_state"]:
		for participant in state["conversation_state"]["conversation"]["participant_data"]:
			if "fallback_name" in participant:
				saveNameForId(participant["fallback_name"], participant["id"]["gaia_id"])

	for event in state["conversation_state"]["event"]:
		timestamp = int(event["timestamp"])

		if "conversation_id" in event:
			conversationId = event["conversation_id"]["id"]

		if "chat_message" in event and "segment" in event["chat_message"]["message_content"]:
			content = event["chat_message"]["message_content"]
			text = content["segment"][0]["text"]
			conversationId = event["conversation_id"]["id"]
			senderId = event["sender_id"]["chat_id"]

			participants = state["conversation_state"]["conversation"]["current_participant"]

			if len(participants) == 2:
				for participant in participants:
					if participant["gaia_id"] != OWN_ID:
						conversationWithId = participant["gaia_id"]

				if idToName(senderId)!=None or idToName(conversationWithId)!=None:
					if senderId != OWN_ID and senderId != conversationWithId:
						# unexpected sender
						print idToName(senderId), 'in conversation with', idToName(conversationWithId), '!'

					# saves the message
					timestamp = datetime.date.fromtimestamp(timestamp/1000000).toordinal()
					data += [[timestamp, idToName(conversationWithId), idToName(senderId), text]]

				else:
					# unknown sender
					print "No senderName for either senderId", senderId, conversationWithId

				if len(data) >= MAX_EXPORTED_MSGS:
					break

print len(data), 'messages parsed.'

print 'Converting to DataFrame...'
df = pd.DataFrame(index=np.arange(0, len(data)), columns=['timestamp', 'conversationWithName', 'senderName', 'text'])
df = pd.DataFrame(data)

print 'Saving to pickle file...'
df.to_pickle('data/hangouts.pkl')