# 🏁 PokeSprint

**A Discord bot that runs "Poké-Races": races between friends through a game, with milestones, live rankings and a bonus/malus roulette.**

Each race is a list of objectives to reach in a game (for example, beating each gym of a Pokémon game). Players report their progress from their own private channel, the bot keeps the ranking up to date, announces it to everyone, and spins a roulette that hands out a bonus or a malus at each step.

> The bot speaks **French**. The code and this documentation are in English.

## ✨ Features

- **Race management** from an interactive Discord menu: create, edit and delete races, each with its game, its milestones and its lists of positive and negative events
- **Player profiles** ("trainer cards"): each player has a private channel where they play their turns, and a card listing their ongoing races and their final position in finished ones
- **Progress tracking**: players move to their next objective with `!next`, the bot updates the ranking and posts it in the server's notification channel
- **Bonus / malus roulette** at each milestone, with a catch-up mechanic (see below)
- **Automatic finish**: the race ends on its own as soon as all players but one have reached the last objective
- **Multi-server**: one bot instance serves several Discord servers, each with its own races and players
- **Admin server**: a dedicated server can broadcast announcements to every server that set a notification channel

## 🎡 The roulette

Every time a player reaches a new milestone, the bot spins a roulette in the notification channel and draws one of the race's events.

- **Bonus or malus?** A malus is the default. The chance of drawing a bonus starts at 20 % and rises up to 40 % the further a player is behind the leader, so players who fall behind get help to catch up.
- **No repeats**: an event already drawn is not drawn again until the whole list has come out.
- **Re-spins**: the roulette can spin again (up to 4 times in a row). The chance of a re-spin grows from 10 % to 25 % as the race goes on, so the end of a race gets more chaotic.

## 💬 Commands

| Command | Where | What it does |
|---|---|---|
| `!help` | anywhere | Lists the commands available on this server |
| `!setchannel <channel_id>` | any server | Sets the channel where the bot posts rankings and announcements |
| `!profiles` | any server | Opens the player menu: list, add, edit, delete |
| `!races` | any server | Opens the race menu: list, create, edit, delete |
| `!run <race> <player1> <player2> ...` | any server | Starts a race with the given players (one race at a time per server) |
| `!pause <race>` | any server | Pauses a race, or reopens a finished one in pause |
| `!end <race>` | any server | Ends a race |
| `!info` | player's private channel | Shows your current and next objective |
| `!next` | player's private channel | Moves you to your next objective and spins the roulette |
| `!broadcast <message>` | admin server only | Sends an announcement to every server with a notification channel |

`!trailer` shows the teaser of a specific event (a story and hints). Its image and audio hints are not included in the repository.

## 🚀 Getting started

### Requirements

- Python 3.10 or newer
- Docker, for the MariaDB database
- A Discord bot token, from the [Discord Developer Portal](https://discord.com/developers/applications), with the **Message Content** intent enabled

### Setup

```sh
# 1. Configure the environment
cp .env.example .env
# then fill in DISCORD_TOKEN, DISCORD_SERVER_ADMIN_ID and the database settings

# 2. Start the database (MariaDB + phpMyAdmin); the schema is created on first start
docker compose -f docker/docker-compose.yml up -d

# 3. Install the dependencies and run the bot
python -m venv venv
source venv/bin/activate        # venv\Scripts\activate on Windows
pip install -r requirements.txt
python main.py
```

| Variable | Description |
|---|---|
| `DISCORD_TOKEN` | Token of your Discord bot |
| `DISCORD_SERVER_ADMIN_ID` | ID of the server allowed to use admin commands |
| `MARIADB_DATABASE`, `MARIADB_ROOT_PASSWORD`, `MARIADB_PORT` | Database settings, shared by the bot and Docker |
| `PMA_HOST`, `PORT` | phpMyAdmin settings |

## 🗂️ Project structure

```
main.py                 Entry point: loads .env and starts the bot
src/init_bot.py         Creates the bot and registers servers on startup
src/commands.py         Declares every command
src/cmd/public/         One file per command or menu
src/cmd/admin/          Admin-only commands
src/Class/              Database access and server helpers
docker/                 MariaDB + phpMyAdmin, and the SQL schema
```

## 🛠️ Tech stack

Python · discord.py · MariaDB · Docker Compose · phpMyAdmin

## 👤 About

PokeSprint is a personal project by [Robin Biard](https://github.com/M1ST3R77), built in 2025 to run Poké-Races with friends.
