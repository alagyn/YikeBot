# YikeBot

* Maintains a count of the Yikes accrued by Discord users
* Implemented using [Discord.py](https://discordpy.readthedocs.io/en/latest/index.html "Discord.py Homepage")

### Required Modules
* discord.py\[voice\]
* python-dotenv

### Usage
```


<....> = Required argument
[....] = Optional argument

╞══════════════════════════════════════════════════════════════════════╡

_help for command list

_yike <user> [amount] 
  Adds a yike to the specified user, default amount is 1
  Must be called from a channel visible to at least half the server
  
_unyike <user> [amount]
  Starts the unyiking process. Unyiking requires a voting process
  using the emoji reactions on a message the bot sends (thumbs up and down).
  A sucessful unyike requires the number of thumbs up to exceed the the number
  of down by at least 2 (to prevent a single person from unyiking)
  Must be called from a channel visible to at least half the server
  
_list [user]
  Lists the number of yikes for everyone on the server or optionally
  for a single user
  
_quote <user> <Quote>
  Records a quote from a user
  
_[getquote | getquotes] [user] [-m]
  Returns a list of quotes for the server or optionally just a user
  By default the list is sent as a text file attachment, 
  but the -m flag will make the bot send the entire list as a message
  (beware large quote lists)
  
_edit <delta> <New quote>
  Edits the delta-th quote, with 0 being the most recent quote
  
_clear
  Deletes the most recent messages and user command
  
╞══════════════════════════════════════════════════════════════════════╡  
  
ADMIN COMMANDS - must be bot owner to execute

_[logout | lo]
  Logs out the bot and terminates the program
  
_[reset | r]
  Reloads all command extensions for updates without restarting the program

```


---

##### Good Lord thou must smite this JavaScript
*The JavaScript was smote by the great Python, and every programmer in the world breathed a sigh of relief*
