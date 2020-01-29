# What is this?

This is a **prototype** of a notification bot for Microsofts streaming platform called Mixer, using it's [Constellation API](https://dev.mixer.com/reference/constellation/introduction), which was written using limited Python knowledge and Python 3.

## What can it do?

Currently this bot **somewhat supports** some basic events such as Follows, Sparks, Hosts, Subscriptions and Skills

## What will it be able to do?

The end goal of this bot is to make some flashy light animations using RGB LED strips whenever one of the events occurs. Possibly in the future this bot will also utillize some sort of display to show some graphics whenever a event occurs.

## Why would you want something like this?

Well - streaming is all about audience interaction. Having the streamers environment react to what the viewers are doing is, in my opinion, a very nice way of having a passive level of interaction.

## Great! What's in it for me?

Well, if you want to help the development of this bot I would be happy over getting constructive feedback, idea. Should you want to take my base and expand it with your coding knowledge, you are more than welcome to. Any help would be greatly appreciated.
Progress from my side is going to be slow as I decided this to be one of my first projects to get to know python better and I am coding in my free time.

## What do I need to run this?

### Libraries native to Python:
- os
- sys
- json
- time
- requests
- threading

### Libraries you may have to install
- [lomond](https://pypi.org/project/lomond/)

### Adding your credentials

If you look into config_example.py you will see that you will have to add your own credentials, those namely being the:

- CLIENTID
which you can get by filling in some information about your application [here](https://mixer.com/lab/oauth)

- CHANNELID
which you can get by visiting this link:
https://mixer.com/api/v1/channels/<username>?fields=id
by replacing <username> with your mixer username

- NONCE
which, as far as I understand it, is a unique identifier for identifying the hello event the Constellation API sends when you first connect.

you can read more about how to connect to Mixers APIs [here](https://dev.mixer.com/reference/chat/connection).
