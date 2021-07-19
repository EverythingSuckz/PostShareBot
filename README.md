# PostShareBot

A bot where the subscribers can send their own content to the channel admins and could contribute their Telegram channel.

## Setup

### Heroku
 Soon!

### Host it locally (easy)

```sh
git clone https://github.com/EverythingSuckz/PostShareBot
cd PostShareBot
pip3.9 install -r requirements.txt
# create a .env file and add all the variables there
python3.9 bot.py
```
an example of `.env` file
```sh
API_ID=
API_HASH=
BOT_TOKEN=
DB_URI=
LOG_GROUP=
POST_CHANNEL=
```

### Mandatory Variables

`API_ID` : Goto [my.telegram.org](https://my.telegram.org) to obtain this.

`API_HASH` : Goto [my.telegram.org](https://my.telegram.org) to obtain this.

`BOT_TOKEN` : Get the bot token from [@BotFather](https://telegram.dog/BotFather).

`DB_URI` : Get this value from [ElephantSQL](http://elephantsql.com/).

`LOG_GROUP` : Create a new group (private), add [@missrose_bot](https://telegram.dog/MissRose_bot) and type `/id`. Now copy paste the ID into this field.
**Note**: The should be either a group or a [supergroup](https://telegram.org/blog/supergroups).

`POST_CHANNEL` : The channel where you want the approved posts to be posted in. If your channel is public, then you may pass the channel username here or if it's private, then you'll have to do some extra works, like forward any post from your private channel to [@missrose_bot](https://telegram.dog/MissRose_bot) and reply `/id`. Now copy paste the channel ID into this field.


Report your issues and doubts at the [Support Chat](https://t.me/WhyThisUsername).

## License 

[![GNU Affero General Public License Image](https://www.gnu.org/graphics/agplv3-155x51.png)](https://www.gnu.org/licenses/agpl-3.0.en.html)  

Copyright (C) 2021 by [EverythingSuckz](https://github.com/EverythingSuckz) under [GNU Affero General Public License](https://www.gnu.org/licenses/agpl-3.0.en.html).

Post Share Bot is Free Software: You can use, study share and improve it at your
will. Specifically you can redistribute and/or modify it under the terms of the
[GNU Affero General Public License](https://www.gnu.org/licenses/agpl-3.0.en.html) as
published by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version. 