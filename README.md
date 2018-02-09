# Chatistics

**Python 3 scripts to convert chat logs from various messenger platforms into Panda DataFrames.**
Can also generate ggplot histograms and word clouds from fetched chat logs.

<p align="center">
<img src="https://github.com/MasterScrat/Chatistics/raw/master/screenshots/cloud.png" width="400" height="400">
<img src="https://github.com/MasterScrat/Chatistics/raw/master/screenshots/cloud3.png" width="400" height="400">
</p>

## Support Matrix

|      Platform         | Direct Chat   | Group Chat    |
|:------------------:   |:-----------:  |:----------:   |
| Facebook Messenger    |     ✔         |     ✔         |
| Google Hangouts       |     ✔         |     ✘         |
| Telegram              |     ✔         |     ✘         |
| Whatsapp              |     ✘         |     ✘         |

## Exported data

Data exported for each message regardless of the platform:

|          Column          |                                        Content                                       |
|:--------------------:|:------------------------------------------------------------------------------------:|
| timestamp            | UNIX timestamp                                                                       |
| conversationId       | A conversation ID, unique by platform                                               |
| conversationWithName | Name of the other people in a direct conversation, **or** name of the group conversation |
| senderName           | Name of the sender                                                                   |
| text                 | Text of the message                                                        |
| language             | Language of the conversation as inferred by [langdetect](https://pypi.python.org/pypi/langdetect)                               |
| datetime             | The proleptic Gregorian ordinal (= number of days since 01/01/0001)                  |

## How to use it?

### 1. Download your chat logs

#### Google Hangouts

Use Google Takeout: https://takeout.google.com/settings/takeout

Request an archive containing your Hangouts chat logs. Extract the file called `Hangouts.json` and put it in the `raw` folder of Chatistics.

*Google switched from "Google Talk" to "Google Hangouts" mid-2013. Sadly you will only get your Hangouts logs using Takeout.*

#### Facebook Messenger

1. Go to the "Settings" page: https://www.facebook.com/settings
2. Click on "Download a copy of your Facebook data" at the bottom of the General section.
3. Click on "Start My Archive". It will take Facebook a while to generate it.
4. Once it is done download and extract the archive, then move the `messages` folder in the `raw` folder of Chatistics.

### 2. Parse the logs into DataFrames

Install the required Python packages:

```
virtualenv Chatistics
source Chatistics/bin/activate
pip install -r requirements.txt
```

You will need to give your own name to the parsers so it can make sense of the conversations. 
Use the exact same format as you have on Messenger or Hangouts.

#### Google Hangouts
`python parsers/hangouts.py --own-name "John Doe"`

#### Facebook Messenger
`python parsers/messenger.py --own-name "John Doe"`

#### Telegram
1. Create your Telegram application to access chat logs ([instructions](https://core.telegram.org/api/obtaining_api_id)).
You will need `api_id` and `api_hash`.
2. Paste these values to `parsers/config.py` into corresponding variables.
3. Grab your message history data
`python parsers/telegram.py`

The pickle files will now be ready for analysis in the `data` folder! 

For more options use the `-h` argument on the parsers.

### 3. Visualise

Chatistics can plot the chat logs as histograms, showing how many messages each interlocutor sent. 
It can also generate word clouds based on word density and a base image.

#### Histograms

Plot all messages with:

`python analyse.py --data data/*`

You can filter messages as needed:

```
  --filter-conversation FILTERCONVERSATION
                        only keep messages sent in a conversation with this sender
  --filter-sender FILTERSENDER
                        only keep messages sent by this sender
  --remove-sender REMOVESENDER
                        remove messages sent by this sender
```

Eg to see all the messages sent between you and Jane Doe: 

`python analyse.py --data data/* --filter-conversation "Jane Doe"`

To see the messages sent to you by the top 10 people with whom you talk the most:

`python analyse.py --data data/* --remove-sender "Your Name" -n 10`

<img src="https://github.com/MasterScrat/Chatistics/raw/master/screenshots/histo.png" width="701" height="406">

You can also plot the conversation densities using the `--plot-density` flag.

<img src="https://github.com/MasterScrat/Chatistics/raw/master/screenshots/densities.png" width="705" height="418">


#### Word Cloud

You will need a mask file to render the word cloud. The white bits of the image will be left empty, the rest will be filled with words using the color of the image. [See the WordCloud library documentation](https://github.com/amueller/word_cloud) for more information.

`python cloud.py --data data/* -m img/mask_image.jpg`

You can filter which messages to use using the same flags as with histograms.


## Improvement ideas

* Parsers for more chat platforms: WhatsApp? Pidgin? ...
* Figure out OWN_NAME automatically.
* Handle group chats.
* See [TODO file](https://github.com/MasterScrat/Chatistics/blob/master/TODO) for more.

Pull requests are welcome!


## Troubleshooting

### ValueError: unknown locale: UTF-8

Fix with:

```
export LC_ALL=en_US.UTF-8
export LANG=en_US.UTF-8
```

### LXML incompatible library

```
ImportError: dlopen(/Users/flaurent/Sites/Chatistics/Chatistics/lib/python2.7/site-packages/lxml/etree.so, 2): Library not loaded: @rpath/libxml2.2.dylib
  Referenced from: /Users/flaurent/Sites/Chatistics/Chatistics/lib/python2.7/site-packages/lxml/etree.so
  Reason: Incompatible library version: etree.so requires version 12.0.0 or later, but libxml2.2.dylib provides version 10.0.0
```

This will fix it: https://stackoverflow.com/a/31607751/318557


### ModuleNotFoundError: No module named 'parsers'

Fix with: 

```
export PYTHONPATH=$(pwd)
```

## Misc

* Word cloud generated using https://github.com/amueller/word_cloud
* Stopwords from https://github.com/6/stopwords-json
* Code under MIT license
