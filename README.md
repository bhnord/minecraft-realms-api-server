# Minecraft Realms API Server (Discord Bot Integration)

This server displays players online in your realms server(s)
it hosts a basic local server to serve the Minecraft Realms API
it works in tandem with the bot developed [here](https://github.com/bhnord/discord-bot)
that displays this information in Discord

## Setup

### Entering your login information

1. create a new file called `.env` in the base path.
2. in the .env file, enter your username, email, and password, as well the server id of the Realms server
   you want to track in the following format:

```
USERNAME="your_username_here"
EMAIL="your_email_here"
PASSWD="your_passwd_here"
SERVER_ID="your_server_id_here"
```

Use the Realms API ([see here](https://wiki.vg/Realms_API#GET_.2Fworlds)) to
find out your server ID

### Running a virtual environment

run the following comamnds (Unix)

1. `python3 -m venv .venv` to setup a virtual environment
2. `source ./.venv/bin/activate` to enter the virtual environment
3. `pip install -r requirements.txt` to install the necessary dependencies

### Running the Application

run the flask app (`flask run`) and the server will start up
