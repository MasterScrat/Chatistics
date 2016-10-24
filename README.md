# ChatShape

**Python scripts to generate histograms and shaped word clouds from chat logs.** Currently supports Google Hangouts and Facebook Messenger log formats.

<p align="center">
<img src="https://github.com/MasterScrat/ChatShape/raw/master/screenshots/cloud.png" width="400" height="400">
<img src="https://github.com/MasterScrat/ChatShape/raw/master/screenshots/cloud2.png" width="400" height="400">
<br><br>
<img src="https://github.com/MasterScrat/ChatShape/raw/master/screenshots/densities.png" width="705" height="418">
<br><br>
<img src="https://github.com/MasterScrat/ChatShape/raw/master/screenshots/histo.png" width="701" height="406">
</p>

## How to use it?

### 1. Download your chat logs

#### Google Hangouts

Use Google Takeout: https://accounts.google.com/ServiceLogin?service=backup

Request an archive containing your chat logs. Extract the file called `Hangouts.json` and put it in the `raw` folder of ChatShape.

*Google switched from "Google Talk" to "Google Hangouts" mid-2013. You will only get your Hangouts logs.*

#### Facebook Messenger

1. Go to "Settings" from the top right drop-down menu.
2. Click on "Download a copy of your Facebook data" at the bottom of the General section.
3. Click on "Start My Archive". It will take Facebook a while to generate it.
4. Once it is done download and extract the archive, then move the file `messages.htm` in the `raw` folder of ChatShape.

### 2. Parse the logs into ChatShape format

You will need to specify your own name to the parsers. Use the exact same format as you have on Messenger or Hangouts.

* Google Hangouts: `python parse_hangouts.py -ownName "John Doe"`
* Facebook Messenger: `python parse_messenger.py -ownName "John Doe"`

This will generate pickle files in the `data` folder. For more options use the `-h` argument on the parsers.

### 3. Render the logs

#### Histograms

Plot all messages with:

`python analyse.py -data data/*`

You can then filter the messages as needed:

````
  -filterConversation FILTERCONVERSATION
                        only keep messages sent in a conversation with this
                        sender
  -filterSender FILTERSENDER
                        only keep messages sent by this sender
  -removeSender REMOVESENDER
                        remove messages sent by this sender
````

Eg to see all the messages sent between you and Jane Doe: 

`python analyse.py -data data/* -filterConversation "Jane Doe"`

To see the messages sent to you by the top 15 people with whom you talk the most:

`python analyse.py -data data/* -removeSender "Your Name" -n 15`


#### The Cloud!

You will need a mask file to render the word cloud. 

`python cloud.py -data data/* -m img/mask_image.jpg`

The white bits of the image will be left empty, the rest will be filled with words using the color of the image. [See the WordCloud library documentation](https://github.com/amueller/word_cloud) for more information.

You can filter which messages to use using the same flags as with histograms.


## Improvement ideas

* Integrate with [gtalk_export](https://github.com/coandco/gtalk_export/) to handle Google Talk format.
* Parsers for more chat platforms: WhatsApp? Pidgin? ...
* WordCloud has some issues with non-English languages. For example in French it will transform "ouais" (yep) in "ouai". Fixing this would probably require a pull request on the WordCloud project.
* For now if the phrase "don't worry" appears a lot, "don't" will be removed (as a stopword) and only "worry" will appear in the cloud. This is misleading. It would be interesting to implement an n-gram approach to consider groups of words. [This example from WordCloud](https://github.com/amueller/word_cloud/blob/bc8e76ef98e3fdfa506deb56a3050e7a481e99ef/examples/bigrams.py) could be a good starting point.
* Figure out OWN_NAME automatically.
* Handle group chats.

Pull requests welcome!


## Misc

* Word cloud generated using https://github.com/amueller/word_cloud
* Stopwords from https://github.com/6/stopwords-json
* Code under MIT license