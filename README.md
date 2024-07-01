# Bonk-bot
This is my bonk bot

# bonk_bot
User-friendly async python framework for writing bots in bonk.io.
Supported python versions: 3.8+
## Features
- API is using async and await for handling several connections and requests at once
- Different bonk.io servers support
- Event-based
## Installing
**Python 3.8 and higher required**

Go to your project's terminal and run the following command:
```
pip install bonk_bot
```
## Bot example
```py
import asyncio

from bonk_bot.BonkBot import bonk_guest_login
from bonk_bot.Game import Game, Player, Message
from bonk_bot.Types import Servers, Modes

bot = bonk_guest_login("Safizapi")
bot.set_main_avatar(None)


@bot.on("game_connect")
async def on_connect(game: Game):
    print(f"Connected game {game.room_name}")


@bot.on("player_join")
async def on_player_join(game: Game, player: Player):
    await game.send_message(f"Hi, {player.username}")


@bot.on("message")
async def on_message(game: Game, message: Message):
    if message.content == "!ping" and not message.author.is_bot:
        await game.send_message("Pong!")


@bot.on("game_disconnect")
async def on_game_disconnect(game: Game):
    print(f"Disconnected from game {game.room_name}")


async def main():
    game = await bot.create_game(name="Cool room", max_players=8, server=Servers.Warsaw())
    await game.set_mode(Modes.Grapple())

    await bot.run()


asyncio.run(main())
```
## Events
- **game_join**: triggered when bot joins the room
- **player_join**: triggered when some player joins the room
- **player_left**: triggered when some player leaves the room
- **player_ready**: triggered when some player presses ready button
- **error**: triggered when some connection error is occures
- **player_team_change**: triggered when some player changes team
- **team_lock**: triggered when host locks teams
- **team_unlock**: triggered when host unlocks teams
- **message**: triggered when some player sends message
- **bot_kick**: triggered when bot is kicked from the game
- **bot_ban**: triggered when bot is banned from the game
- **player_kick**: triggered when some player is kicked from the room
- **player_ban**: triggered when some player is banned from the room
- **mode_change**: triggered when host changes mode
- **player_balance**: triggered when some player is balanced
- **teams_turn_on**: triggered when host turns on teams
- **teams_turn_off**: triggered when host turns off teams
- **host_change**: triggered when game host changes
- **new_room_name**: triggered when host changes room name
- **new_room_password**: triggered when host sets a new password for game
- **room_password_clear**: triggered when host clears game password
- **game_disconnect**: triggered when bot disconnects from the game
