# Poll bot

This is a discord bot that can generate polls and tally said polls. I have made this bot specifically for one discord server and thus it doesnt really have that much customizability.

## How to use

This project depends on python and pycord to be installed in order to run.
Once you have installed these you can simply do `python main.py` in order to start the bot.

When you first launch the bot it will create two files for storing data and ask for some information on how to configure the bot.

To generate a poll simply do `/poll` and fill out the details.

To tally up results right click on the poll message and then click `Apps > Tally`.

Only authorized users can use these commands. To authorize another user do `/add_allowed` and then choose the user.