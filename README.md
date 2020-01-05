# Chatistics

**Python 3 scripts to convert chat logs from various messaging platforms into Panda DataFrames.**
Can also generate ggplot histograms and word clouds from fetched chat logs.

<p align="center">
<img src="https://github.com/MasterScrat/Chatistics/raw/master/static/cloud.png" width="400" height="400">
<img src="https://github.com/MasterScrat/Chatistics/raw/master/static/cloud3.png" width="400" height="400">
</p>

## Changelog

**21 Oct 2018:** Updated Facebook Messenger and Google Hangouts parsers to make them work with the new exported file formats.

**9 Feb 2018:** Telegram support added thanks to @bmwant.

**24 Oct 2016:** Initial release supporting Facebook Messenger and Google Hangouts.

## Support Matrix

|      Platform      | Direct Chat  | Group Chat |
|:------------------:|:-----------: |:----------:|
| Facebook Messenger |     ✔        |     ✘      |
| Google Hangouts    |     ✔        |     ✘      |
| Telegram           |     ✔        |     ✘      |
| WhatsApp           |     ✔        |     ✔      |

## Exported data

Data exported for each message regardless of the platform:

|          Column      |                                        Content                                       |
|:--------------------:|:------------------------------------------------------------------------------------:|
| timestamp            | UNIX timestamp (in seconds)                                                                       |
| conversationId       | A conversation ID, unique by platform                                                |
| conversationWithName | Name of the other people in a direct conversation, **or** name of the group conversation |
| senderName           | Name of the sender                                                                   |
| outgoing             | Boolean value whether the message is outgoing/coming from owner                      |
| text                 | Text of the message                                                                  |
| language             | Language of the conversation as inferred by [langdetect](https://pypi.python.org/pypi/langdetect) |
| platform             | Platform (see support matrix above)                                                  |

## How to use it?

### 1. Download your chat logs

#### Google Hangouts

Use Google Takeout: https://takeout.google.com/settings/takeout

Request an archive containing your Hangouts chat logs. Extract the file called `Hangouts.json` and put it in the `./raw_data/hangouts/` folder of Chatistics.

*Google switched from "Google Talk" to "Google Hangouts" mid-2013. Sadly you will only get your Hangouts logs using Takeout.*

#### Facebook Messenger

1. Go to the "Settings" page: https://www.facebook.com/settings
2. Click on "Download a copy of your Facebook data" at the bottom of the General section.
3. Click on "Start My Archive". It will take Facebook a while to generate it.
4. Once it is done download and extract the archive, then move the contents of the `messages` folder into `./raw_data/messenger/` folder of Chatistics.

#### WhatsApp

Unfortunately, WhatsApp only lets you export your conversations one by one. [See instructions here](https://faq.whatsapp.com/en/wp/22548236)

1. Open the chat you wish to export
2. On Android, tap on <kbd>⋮</kbd> > <kbd>More</kbd> > <kbd>Export chat</kbd>. On iOS, tap on the interlocutor's name > <kbd>Export chat</kbd>
3. Choose "Without Media"
4. Send chat to yourself eg via Email
5. Unpack the archive and add the individual txt files to the folder `./raw_data/whatsapp/`

### 2. Parse the logs into DataFrames

First, install the required Python packages:

**Use conda (recommended)**

```
conda env create -f environment.yml
conda activate chatistics
```

**Or virtualenv**

```
virtualenv chatistics
source chatistics/bin/activate
pip install -r requirements.txt
```
You can now parse the messages by using the command `python parse.py <platform> <arguments>`.

By default the parsers will try to infer your own name (i.e. your username) from the data. If this fails you can provide your own name to the parser by providing the `--own-name` argument. The name should match your name exactly as used on that chat platform.

```
# Google Hangouts
python parse.py hangouts

# Facebook Messenger
python parse.py messenger

# WhatsApp
python parse.py whatsapp
```

#### Telegram
1. Create your Telegram application to access chat logs ([instructions](https://core.telegram.org/api/obtaining_api_id)).
You will need `api_id` and `api_hash` which we will now set as environment variables.
2. Run `cp secrets.sh.example secrets.sh` and fill in the values for the environment variables `TELEGRAM_API_ID`, `TELEGRAMP_API_HASH` and `TELEGRAM_PHONE` (your phone number including country code).
3. Run `source secrets.sh`
4. Execute the parser script using `python parse.py telegram`

The pickle files will now be ready for analysis in the `data` folder!

For more options use the `-h` argument on the parsers (e.g. `python parse.py telegram --help`).

### 3. Visualise

Chatistics can plot the chat logs as histograms, showing how many messages each interlocutor sent.
It can also generate word clouds based on word density and a base image.

#### Histograms

Plot all messages with:

`python visualize.py breakdown`

Among other options you can filter messages as needed (also see `python visualize.py breakdown --help`):

```
  --platforms {telegram,whatsapp,messenger,hangouts}
                        Use data only from certain platforms (default: ['telegram', 'whatsapp', 'messenger', 'hangouts'])
  --filter-conversation
                        Limit by conversations with this person/group (default: [])
  --filter-sender
                        Limit to messages sent by this person/group (default: [])
  --remove-conversation
                        Remove messages by these senders/groups (default: [])
  --remove-sender
                        Remove all messages by this sender (default: [])
  --contains-keyword
                        Filter by messages which contain certain keywords
```

Eg to see all the messages sent between you and Jane Doe:

`python visualize.py breakdown --filter-conversation "Jane Doe"`

To see the messages sent to you by the top 10 people with whom you talk the most:

`python visualize.py breakdown --remove-sender "Your Name" -n 10`

<img src="https://github.com/MasterScrat/Chatistics/raw/master/static/histo.png" width="701" height="406">

You can also plot the conversation densities using the `--as-density` flag.

<img src="https://github.com/MasterScrat/Chatistics/raw/master/static/densities.png" width="705" height="418">


#### Word Cloud

You will need a mask file to render the word cloud. The white bits of the image will be left empty, the rest will be filled with words using the color of the image. [See the WordCloud library documentation](https://github.com/amueller/word_cloud) for more information.

`python visualize.py cloud -m raw_outlines/users.jpg`

You can filter which messages to use using the same flags as with histograms.

#### Print

You can print the data to standard out by using the command

```
python print.py
```
You can use the same filter options as described above.


## Improvement ideas

* Parsers for more chat platforms: Signal? Pidgin? ...
* Handle group chats on more platforms.

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


## Misc

* Word cloud generated using https://github.com/amueller/word_cloud
* Stopwords from https://github.com/6/stopwords-json
* Code under MIT license
