import socketio
from typing import Union

from .Game import Game
from .Types import Modes


class Room:
    """
    Class for rooms from bonk.io room list.

    :param bot: bot class that loaded the room.
    :param room_id: database ID of room.
    :param name: name of the room.
    :param players: current amount of players that play in this room.
    :param max_players: maximal amount of players that can play in this room at the same time.
    :param has_password: whether room has password or not.
    :param mode: the mode that is currently played in the room.
    :param min_level: the minimal level that is required to join the room.
    :param max_level: the maximal level along with you can join the room.
    """

    def __init__(
        self,
        bot,
        room_id: int,
        name: str,
        players: int,
        max_players: int,
        has_password: bool,
        mode: Union[Modes.Classic, Modes.Arrows, Modes.DeathArrows, Modes.Grapple, Modes.VTOL, Modes.Football],
        min_level: int,
        max_level: int
    ) -> None:
        self.bot = bot
        self.room_id: int = room_id
        self.name: str = name
        self.players: int = players
        self.max_players: int = max_players
        self.has_password: bool = has_password
        self.mode: Union[Modes.Classic, Modes.Arrows, Modes.DeathArrows, Modes.Grapple, Modes.VTOL, Modes.Football] = mode
        self.min_level: int = min_level
        self.max_level: int = max_level

    async def join(self, password="") -> Game:
        """
        Joins game from room list.

        :param password: password to join room.

        Example usage::

            bot = bonk_account_login("name", "pass")

            async def main():
                room = [room for room in bot.get_rooms() if room.name == "test room"][0]
                game = await room.join()

                await bot.run()

            asyncio.run(main())
        """

        game = Game(
            self.bot,
            self.name,
            socketio.AsyncClient(ssl_verify=False),
            False,
            self.mode,
            False,
            self.bot.event_emitter,
            game_join_params=[self.room_id, password]
        )
        await game.connect()

        return game
