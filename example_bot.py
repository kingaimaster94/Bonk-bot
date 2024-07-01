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
