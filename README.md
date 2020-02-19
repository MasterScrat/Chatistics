# Chatistics

**Python 3 scripts to convert chat logs from various messaging platforms into Pandas DataFrames.**
Can also generate histograms and word clouds from the chat logs.

<p align="center">
<img src="https://github.com/MasterScrat/Chatistics/raw/master/static/cloud.png" width="45%">
<img src="https://github.com/MasterScrat/Chatistics/raw/master/static/cloud3.png" width="45%">
</p>

### Changelog

**10 Jan 2020:** UPDATED *ALL* THE THINGS! Thanks to [mar-muel](https://github.com/mar-muel) and [manueth](https://github.com/manueth), pretty much everything has been updated and improved, and **WhatsApp** is now supported!

**21 Oct 2018:** Updated Facebook Messenger and Google Hangouts parsers to make them work with the new exported file formats.

**9 Feb 2018:** Telegram support added thanks to [bmwant](https://github.com/bmwant).

**24 Oct 2016:** Initial release supporting Facebook Messenger and Google Hangouts.

### Support Matrix

|      Platform             | Direct Chat | Group Chat |
|:-------------------------:|:-----------:|:----------:|
| Facebook Messenger        |     ✔       |     ✘     |
| Google Hangouts           |     ✔       |     ✘     |
| Telegram (API)            |     ✔       |     ✘     |
| Telegram (Desktop Client) |     ✔       |     ✔     |
| WhatsApp                  |     ✔       |     ✔     |

### Exported data

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

# Exporting your chat logs

## 1. Download your chat logs

### Google Hangouts

**Warning:** Google Hangouts archives can take a long time to be ready for download - up to one hour in our experience.

1. Go to Google Takeout: https://takeout.google.com/settings/takeout
2. Request an archive containing your Hangouts chat logs
3. Download the archive, then extract the file called `Hangouts.json`
4. Move it to `./raw_data/hangouts/`

### Facebook Messenger

**Warning:** Facebook archives can take a *very* long time to be ready for download - up to 12 hours! They can weight several gigabytes. Start with an archive containing just a few months of data if you want to quickly get started, this shouldn't take more than a few minutes to complete.

1. Go to the page "Your Facebook Information": https://www.facebook.com/settings?tab=your_facebook_information
2. Click on "Download Your Information"
3. Select the date range you want. **The format *must* be JSON.** Media won't be used, so you can set the quality to "Low" to speed things up.
4. Click on "Deselect All", then scroll down to select "Messages" only
5. Click on "Create File" at the top of the list. It will take Facebook a while to generate your archive.
4. Once the archive is ready, download and extract it, then move the content of the `messages` folder into `./raw_data/messenger/`

### WhatsApp

Unfortunately, WhatsApp only lets you export your conversations **from your phone** and **one by one**.

1. On your phone, open the chat conversation you want to export
2. On **Android**, tap on <kbd>⋮</kbd> > <kbd>More</kbd> > <kbd>Export chat</kbd>. On **iOS**, tap on the interlocutor's name > <kbd>Export chat</kbd>
3. Choose "Without Media"
4. Send chat to yourself eg via Email
5. Unpack the archive and add the individual .txt files to the folder `./raw_data/whatsapp/`

### Telegram (Desktop Client)

1. Open Telegram Desktop Client
2. Open Settings > Export Telegram data
5. Unpack result.json file to the folder `./raw_data/telegram/`

### Telegram (API)

The Telegram API works differently: you will first need to setup Chatistics, then query your chat logs programmatically. 
This process is documented below. Exporting Telegram chat logs is very fast.

## 2. Setup Chatistics

First, install the required Python packages using conda:

```
conda env create -f environment.yml
conda activate chatistics
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

# Telegram (Desktop Client)
python parse.py telegram_json
```

### Telegram (API)
1. Create your Telegram application to access chat logs ([instructions](https://core.telegram.org/api/obtaining_api_id)).
You will need `api_id` and `api_hash` which we will now set as environment variables.
2. Run `cp secrets.sh.example secrets.sh` and fill in the values for the environment variables `TELEGRAM_API_ID`, `TELEGRAMP_API_HASH` and `TELEGRAM_PHONE` (your phone number including country code).
3. Run `source secrets.sh`
4. Execute the parser script using `python parse.py telegram_api`

The pickle files will now be ready for analysis in the `data` folder!

For more options use the `-h` argument on the parsers (e.g. `python parse.py telegram_api --help`).


## 3. All done! Play with your data

Chatistics can print the chat logs as raw text. It can also create histograms, showing how many messages each interlocutor sent, or generate word clouds based on word density and a base image.

### Export

You can view the data in stdout (default) or export it to csv, json, or as a Dataframe pickle.

```
python export.py
```
You can use the same filter options as described above in combination with an output format option:

```
  -f {stdout,json,csv,pkl}, --format {stdout,json,csv,pkl}
                        Output format (default: stdout)
```

### Histograms

Plot all messages with:

`python visualize.py breakdown`

Among other options you can filter messages as needed (also see `python visualize.py breakdown --help`):

```
  --platforms {telegram,whatsapp,messenger,hangouts}
                        Use data only from certain platforms (default: ['telegram_api', 'telegram_json', 'whatsapp', 'messenger', 'hangouts'])
  --filter-conversation
                        Limit by conversations with this person/group (default: [])
  --filter-sender
                        Limit to messages sent by this person/group (default: [])
  --remove-conversation
                        Remove messages by these senders/groups (default: [])
  --remove-sender
                        Remove all messages by this sender (default: [])
  --contains-keyword
                        Filter by messages which contain certain keywords (default: [])
  --outgoing-only       
                        Limit by outgoing messages (default: False)
  --incoming-only       
                        Limit by incoming messages (default: False)
```

Eg to see all the messages sent between you and Jane Doe:

`python visualize.py breakdown --filter-conversation "Jane Doe"`

To see the messages sent to you by the top 10 people with whom you talk the most:

`python visualize.py breakdown -n 10 --incoming-only`

<img src="https://github.com/MasterScrat/Chatistics/raw/master/static/histo.png" width="100%">

You can also plot the conversation densities using the `--as-density` flag.

<img src="https://github.com/MasterScrat/Chatistics/raw/master/static/densities.png" width="100%">


### Word Cloud

You will need a mask file to render the word cloud. The white bits of the image will be left empty, the rest will be filled with words using the color of the image. [See the WordCloud library documentation](https://github.com/amueller/word_cloud) for more information.

`python visualize.py cloud -m raw_outlines/users.jpg`

You can filter which messages to use using the same flags as with histograms.

# Development

Install dev environment using
```
conda env create -f environment_dev.yml
```

Run tests from project root using

```
python -m pytest
```

## Improvement ideas

* Parsers for more chat platforms: Discord? Signal? Pidgin? ...
* Handle group chats on more platforms.
* See [open issues](https://github.com/MasterScrat/Chatistics/issues) for more ideas.

Pull requests are welcome!

## Social medias

- [HackerNews '20](https://news.ycombinator.com/item?id=22069699)

- [/r/MachineLearning '20](https://www.reddit.com/r/MachineLearning/comments/epi628/p_chatistics_python_scripts_to_turn_your/)

- [/r/datascience '18](https://www.reddit.com/r/datascience/comments/7vvpbl/chatistics_python_scripts_to_turn_your_messenger/)

- [/r/MachineLearning '18](https://www.reddit.com/r/MachineLearning/comments/7s1d2a/p_chatistics_python_scripts_to_turn_your/)

## Projects using Chatistics

[Meet your Artificial Self: Generate text that sounds like you](https://github.com/mar-muel/artificial-self-AMLD-2020) workshop

## Credits

* Main contributors: [@MasterScrat](https://github.com/MasterScrat), [@mar-muel](https://github.com/mar-muel), [@manueth](https://github.com/manueth), [@bmwant](https://github.com/bmwant)
* Word cloud generated using https://github.com/amueller/word_cloud
* Stopwords from https://github.com/6/stopwords-json
* Code under MIT license
