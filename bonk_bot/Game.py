import asyncio
import random
from random import shuffle
from string import ascii_lowercase
import socketio
from typing import List, Union
from pymitter import EventEmitter

from .Avatar import Avatar
from .BonkMaps import OwnMap, Bonk2Map, Bonk1Map
from .Settings import PROTOCOL_VERSION, links
from .Types import Servers, Modes, Teams
from .Parsers import team_from_number, mode_from_short_name


class Game:
    """
    Class for holding real-time game info and events.

    :param bot: bot class that uses the account.
    :param room_name: name of the room.
    :param socket_client: socketio client for sending and receiving events.
    :param is_host: indicates whether bot is host or not.
    :param mode: mode that is currently played.
    :param is_created_by_bot: indicates whether room is created by bot or not. Needed to define which method should be
            called in .connect() method.
    :param event_emitter: pymitter event emitter for handling events in bot class.
    :param game_create_params: params that are needed for game creation.
    :param game_join_params: params that are needed to join the game.
    :param is_connected: indicates whether bot is connected or not.
    """

    def __init__(
        self,
        bot,
        room_name: str,
        socket_client: socketio.AsyncClient,
        is_host: bool,
        mode: Union[Modes.Classic, Modes.Arrows, Modes.DeathArrows, Modes.Grapple, Modes.VTOL, Modes.Football],
        is_created_by_bot: bool,
        event_emitter: EventEmitter,
        game_create_params: Union[list, None] = None,
        game_join_params: Union[list, None] = None,
        is_connected: bool = False
    ) -> None:
        self.bot = bot
        self.room_name: str = room_name
        self.room_password: str = ""
        self.players: List[Player] = []
        self.messages: List[Message] = []
        self.is_host: bool = is_host
        self.is_bot_ready: bool = False
        self.is_banned: bool = False
        self.mode: Union[Modes.Classic, Modes.Arrows, Modes.DeathArrows, Modes.Grapple, Modes.VTOL, Modes.Football] = mode
        self.extended_teams: bool = False
        self.team_lock: bool = False
        self.rounds: int = 3
        self.bonk_map: Union[OwnMap, Bonk2Map, Bonk1Map, None] = None
        self.__initial_state: str = ""
        self.__socket_client: socketio.AsyncClient = socket_client
        self.__event_emitter: EventEmitter = event_emitter
        self.__is_created_by_bot: bool = is_created_by_bot
        self.__game_create_params: Union[list, None] = game_create_params
        self.__game_join_params: Union[list, None] = game_join_params
        self.__is_connected: bool = is_connected

    async def connect(self) -> None:
        """Method that establishes connection with game. You don't need to use it."""

        self.bot.games.append(self)

        if self.__is_created_by_bot:
            await self.__create(*self.__game_create_params)
        else:
            await self.__join(*self.__game_join_params)

    @staticmethod
    def __get_peer_id() -> str:
        """Generates new peer_id that is needed for game connection."""

        alph = list(ascii_lowercase + "0123456789")
        shuffle(alph)
        return "".join(alph[:10]) + "000000"

    # async def play(self) -> None:
    #     if not self.is_host:
    #         raise Exception("Can't start a game: bot is not a host")
    #
    #     await self.__socket_client.emit(
    #         5,
    #         {
    #
    #         }
    #     )

    async def change_bot_team(
        self,
        team: Union[Teams.Spectator, Teams.FFA, Teams.Red, Teams.Blue, Teams.Green, Teams.Yellow]
    ) -> None:
        """
        Changes current bot team.

        :param team: target team that is bot moving in.
        """

        if not (
            isinstance(team, Teams.Spectator) or
            isinstance(team, Teams.FFA) or
            isinstance(team, Teams.Red) or
            isinstance(team, Teams.Blue) or
            isinstance(team, Teams.Green) or
            isinstance(team, Teams.Yellow)
        ):
            raise TypeError("Can't move player: team param is not a valid team")

        await self.__socket_client.emit(
            6,
            {
                "targetTeam": team.number
            }
        )

    async def toggle_team_lock(self, flag: bool) -> None:
        """
        Lock free team switching.

        :param flag: on -> True (locked teams) | off -> False (free team switching).
        """

        await self.__socket_client.emit(
            7,
            {
                "teamLock": flag
            }
        )
        self.team_lock = True

    async def send_message(self, message: str) -> None:
        """
        Send message from bot in the game.

        :param message: message content.
        """

        await self.__socket_client.emit(
            10,
            {
                "message": message
            }
        )

    async def toggle_bot_ready(self, flag: bool) -> None:
        """
        Turn on/off bot ready mark in the game.

        :param flag: on -> True (bot is ready) | off -> False (bot is not ready).
        """

        await self.__socket_client.emit(
            16,
            {
                "ready": flag
            }
        )
        self.is_bot_ready = flag

    async def set_mode(
        self,
        mode: Union[Modes.Classic, Modes.Arrows, Modes.DeathArrows, Modes.Grapple, Modes.VTOL, Modes.Football]
    ) -> None:
        """
        Change game mode.

        :param mode: one of the Modes class types.
        """

        if not (
            isinstance(mode, Modes.Classic) or
            isinstance(mode, Modes.Arrows) or
            isinstance(mode, Modes.DeathArrows) or
            isinstance(mode, Modes.Grapple) or
            isinstance(mode, Modes.VTOL) or
            isinstance(mode, Modes.Football)
        ):
            raise TypeError("Can't move player: team param is not a valid team")

        await self.__socket_client.emit(
            20,
            {
                "ga": mode.ga,
                "mo": mode.short_name
            }
        )
        self.mode = mode

    async def set_rounds(self, rounds: int) -> None:
        """
        Change rounds to win.

        :param rounds: rounds that player has to reach to win the game.
        """

        await self.__socket_client.emit(
            21,
            {
                "w": rounds
            }
        )
        self.rounds = rounds

    async def set_map(self, bonk_map: Union[OwnMap, Bonk2Map, Bonk1Map]) -> None:
        """
        Change game map.

        :param bonk_map: the map that is wanted to be played in the game.
        """

        if not (
            isinstance(bonk_map, OwnMap) or
            isinstance(bonk_map, Bonk2Map) or
            isinstance(bonk_map, Bonk1Map)
        ):
            raise TypeError("Input param is not a map")

        await self.__socket_client.emit(
            23,
            {
                "m": bonk_map.map_data
            }
        )
        self.bonk_map = bonk_map

    async def toggle_teams(self, flag: bool) -> None:
        """
        Turn on/off extended (red, blue, green and yellow) teams.

        :param flag: on -> True (extended teams) | off -> False (only FFA).
        """

        await self.__socket_client.emit(
            32,
            {
                "t": flag
            }
        )
        self.extended_teams = flag

    async def record(self) -> None:
        """Record the last 15 seconds of round."""

        await self.__socket_client.emit(33)

    async def change_room_name(self, new_room_name: str) -> None:
        """
        Change room name.

        :param new_room_name: new room name.
        """

        await self.__socket_client.emit(
            52,
            {
                "newName": new_room_name
            }
        )
        self.room_name = new_room_name

    async def change_room_password(self, new_password: str) -> None:
        """
        Change room password.

        :param new_password: new room password.
        """

        await self.__socket_client.emit(
            53,
            {
                "newPass": new_password
            }
        )
        self.room_password = new_password

    async def leave(self) -> None:
        """Disconnect from the game."""

        await self.__socket_client.disconnect()
        self.__is_connected = False
        self.players = []
        self.messages = []

        self.__event_emitter.emit("game_disconnect", self)

    async def close(self) -> None:
        """Close the game."""

        await self.__socket_client.emit(50)
        await self.leave()

        self.__event_emitter.emit("game_disconnect", self)

    async def wait(self) -> None:
        """Prevents socketio session from stopping. You don't need to use it."""
        await self.__socket_client.wait()

    async def __create(
        self,
        name="Test room",
        max_players=6,
        is_hidden=False,
        password="",
        min_level=0,
        max_level=999,
        server=Servers.Warsaw()
    ) -> None:
        socket_address = f"https://{server}.bonk.io/socket.io"

        @self.__socket_client.event
        async def connect():
            self.is_host = True
            new_peer_id = self.__get_peer_id()

            if not self.bot.is_guest:
                await self.__socket_client.emit(
                    12,
                    {
                        "peerID": new_peer_id,
                        "roomName": name,
                        "maxPlayers": max_players,
                        "password": password,
                        "dbid": self.bot.user_id,
                        "guest": False,
                        "minLevel": min_level,
                        "maxLevel": max_level,
                        "latitude": server.latitude,
                        "longitude": server.latitude,
                        "country": server.country,
                        "version": PROTOCOL_VERSION,
                        "hidden": int(is_hidden),
                        "quick": False,
                        "mode": "custom",
                        "token": self.bot.token,
                        "avatar": self.bot.main_avatar.json_data
                    }
                )
            else:
                await self.__socket_client.emit(
                    12,
                    {
                        "peerID": new_peer_id,
                        "roomName": name,
                        "maxPlayers": max_players,
                        "password": password,
                        "dbid": random.randint(10_000_000, 14_000_000),
                        "guest": True,
                        "minLevel": min_level,
                        "maxLevel": max_level,
                        "latitude": server.latitude,
                        "longitude": server.longitude,
                        "country": server.country,
                        "version": PROTOCOL_VERSION,
                        "hidden": int(is_hidden),
                        "quick": False,
                        "mode": "custom",
                        "guestName": self.bot.username,
                        "avatar": self.bot.main_avatar.json_data
                    }
                )
            self.__is_connected = True

            self.players.append(
                Player(
                    self.bot,
                    self,
                    self.__socket_client,
                    True,
                    new_peer_id,
                    self.bot.username,
                    False,
                    self.bot.get_level(),
                    False,
                    False,
                    Teams.FFA(),
                    0,
                    self.bot.main_avatar
                )
            )

        self.__event_emitter.emit("game_connect", self)
        await self.__socket_events()

        await self.__socket_client.connect(socket_address)
        await self.__keep_alive()

        while not self.__is_connected:
            await asyncio.sleep(0.5)

    async def __join(self, room_id: int, password="") -> None:
        async with self.bot.aiohttp_session.post(
            url=links["get_room_address"],
            data={
                "id": room_id
            }
        ) as resp:
            room_data = await resp.json()

        if room_data.get("e") == "ratelimited":
            raise GameConnectionError("Cannot connect to server, connection ratelimited: sent to many requests", self)

        @self.__socket_client.event
        async def connect():
            if not self.bot.is_guest:
                await self.__socket_client.emit(
                    13,
                    {
                        "joinID": room_data["address"],
                        "roomPassword": password,
                        "guest": False,
                        "dbid": 2,
                        "version": PROTOCOL_VERSION,
                        "peerID": self.__get_peer_id(),
                        "bypass": "",
                        "token": self.bot.token,
                        "avatar": self.bot.main_avatar.json_data
                    }
                )
            else:
                await self.__socket_client.emit(
                    13,
                    {
                        "joinID": room_data["address"],
                        "roomPassword": password,
                        "guest": True,
                        "dbid": 2,
                        "version": PROTOCOL_VERSION,
                        "peerID": self.__get_peer_id(),
                        "bypass": "",
                        "guestName": self.bot.username,
                        "avatar": self.bot.main_avatar.json_data
                    }
                )

            self.__is_connected = True

        self.__event_emitter.emit("game_connect", self)
        await self.__socket_events()

        await self.__socket_client.connect(f"https://{room_data['server']}.bonk.io/socket.io")
        await self.__keep_alive()

        while not self.__is_connected:
            await asyncio.sleep(0.5)

    async def __keep_alive(self) -> None:
        while self.__is_connected:
            await self.__socket_client.emit(
                18,
                {
                    "jsonrpc": "2.0",
                    "id": "9",
                    "method": "timesync",
                }
            )
            await asyncio.sleep(5)

    async def __socket_events(self) -> None:
        @self.__socket_client.on(3)
        async def players_on_bot_join(w1, w2, players: list, w3, w4, w5, w6, w7):
            [
                self.players.append(
                    Player(
                        self.bot,
                        self,
                        self.__socket_client,
                        False,
                        player["peerID"],
                        player["userName"],
                        player["guest"],
                        player["level"],
                        player["ready"],
                        player["tabbed"],
                        team_from_number(player["team"]),
                        players.index(player),
                        Avatar(player["avatar"])
                    )
                ) for player in players if player is not None
            ]

            bot = [player for player in self.players if player.username == self.bot.username and player.level == self.bot.get_level()][0]
            self.players[self.players.index(bot)].is_bot = True

            for x in self.players:
                if x.team.number > 1:
                    self.extended_teams = True

            self.__event_emitter.emit("game_join", self)

        @self.__socket_client.on(4)
        async def on_player_join(
            short_id: int,
            peer_id: str,
            username: str,
            is_guest: bool,
            level: int,
            w,
            avatar: dict
        ) -> None:
            joined_player = Player(
                self.bot,
                self,
                self.__socket_client,
                False,
                peer_id,
                username,
                is_guest,
                level,
                False,
                False,
                Teams.FFA(),
                short_id,
                Avatar(avatar)
            )

            self.players.append(joined_player)

            if self.is_host:
                await self.__socket_client.emit(
                    11,
                    {
                        "sid": short_id,
                        "gs": {
                            "map": {
                                "v": 13,
                                "s": {
                                    "re": False,
                                    "nc": False,
                                    "pq": 1,
                                    "gd": 25,
                                    "fl": False
                                },
                                "physics": {
                                    "shapes": [],
                                    "fixtures": [],
                                    "bodies": [],
                                    "bro": [],
                                    "joints": [],
                                    "ppm": 12
                                },
                                "spawns": [],
                                "capZones": [],
                                "m": {
                                    "a": "💀",
                                    "n": "Test map",
                                    "dbv": 2,
                                    "dbid": 1157352,
                                    "authid": -1,
                                    "date": "2024-06-04 06:03:34",
                                    "rxid": 0,
                                    "rxn": "",
                                    "rxa": "",
                                    "rxdb": 1,
                                    "cr": [
                                        "💀"
                                    ],
                                    "pub": True,
                                    "mo": "",
                                    "vu": 0,
                                    "vd": 0
                                }
                            },
                            "gt": 2,
                            "wl": "pog",
                            "q": False,
                            "tl": False,
                            "tea": False,
                            "ga": self.mode.ga,
                            "mo": self.mode.short_name,
                            "bal": [],
                            "GMMode": ""
                        }
                    }
                )
            self.__event_emitter.emit("player_join", self, joined_player)

        @self.__socket_client.on(5)
        async def on_player_left(short_id: int, w) -> None:
            left_player = [player for player in self.players if player.short_id == short_id][0]
            self.players.remove(left_player)

            self.__event_emitter.emit("player_left", self, left_player)

        @self.__socket_client.on(8)
        async def on_player_ready(short_id: int, flag: bool) -> None:
            player = [player for player in self.players if player.short_id == short_id][0]
            player.is_ready = flag

            if flag:
                self.__event_emitter.emit("player_ready", self, player)

        @self.__socket_client.on(16)
        async def on_error(error) -> None:
            exception = GameConnectionError(error, self)

            if error == "invalid_params":
                exception = GameConnectionError(
                    "Invalid parameters. It means you've configured bot wrong, maybe your avatar. "
                    "If you're sure this is library issue, send pull request on https://github.com/Safizapi/bonk_bot",
                    self
                )

            self.__event_emitter.emit("error", self, error)

            if error in [
                "invalid_params",
                "password_wrong",
                "room_full",
                "players_xp_too_high",
                "players_xp_too_low",
                "guests_not_allowed",
                "already_in_this_room",
                "room_not_found"
            ]:
                await self.leave()

            raise exception

        @self.__socket_client.on(18)
        async def on_player_team_change(short_id: int, team_number: int) -> None:
            player = [player for player in self.players if player.short_id == short_id][0]
            team = team_from_number(team_number)
            player.team = team

            self.__event_emitter.emit("player_team_change", self, player, team)

        @self.__socket_client.on(19)
        async def on_team_lock(flag: bool) -> None:
            self.team_lock = flag

            if flag:
                self.__event_emitter.emit("team_lock", self)
            else:
                self.__event_emitter.emit("team_unlock", self)

        @self.__socket_client.on(20)
        async def on_message(short_id: int, message: str) -> None:
            author = [player for player in self.players if player.short_id == short_id][0]
            _message = Message(message, author, self)

            self.messages.append(Message(message, author, self))

            if not author.is_bot:
                self.__event_emitter.emit("message", self, _message)

        @self.__socket_client.on(21)
        async def on_lobby_load(data: dict) -> None:
            self.mode = mode_from_short_name(data["mo"])
            self.team_lock = data["tl"]
            self.rounds = data["wl"]

        @self.__socket_client.on(24)
        async def on_player_kick(short_id: int, kick_only: bool) -> None:
            player = [player for player in self.players if player.short_id == short_id][0]

            if kick_only:
                if player.is_bot:
                    self.__event_emitter.emit("bot_kick", self)
                    await self.leave()
                else:
                    self.__event_emitter.emit("player_kick", self, player)
            else:
                if player.is_bot:
                    self.__event_emitter.emit("bot_ban", self)
                    await self.leave()
                    self.is_banned = True
                else:
                    self.__event_emitter.emit("player_ban", self, player)

        @self.__socket_client.on(26)
        async def on_mode_change(ga, mode_short_name: str) -> None:
            self.mode = mode_from_short_name(mode_short_name)

            self.__event_emitter.emit("mode_change", self, self.mode)

        @self.__socket_client.on(29)
        async def on_map_change(map_data: str) -> None:
            pass

        @self.__socket_client.on(36)
        async def on_player_balance(short_id: int, percents: int) -> None:
            player = [player for player in self.players if player.short_id == short_id][0]
            player.balanced_by = percents

            self.__event_emitter.emit("player_balance", self, player, percents)

        @self.__socket_client.on(39)
        async def on_teams_toggle(flag: bool) -> None:
            self.extended_teams = flag

            if flag:
                self.__event_emitter.emit("teams_turn_on", self)
            else:
                self.__event_emitter.emit("teams_turn_off", self)

        @self.__socket_client.on(41)
        async def on_host_change(data: dict) -> None:
            old_host = [player for player in self.players if player.short_id == data["oldHost"]][0]
            new_host = [player for player in self.players if player.short_id == data["newHost"]][0]

            if old_host.is_bot and not new_host.is_bot:
                self.is_host = False
            elif not old_host.is_bot and new_host.is_bot:
                self.is_host = True

            self.__event_emitter.emit("host_change", self, old_host, new_host)

        @self.__socket_client.on(58)
        async def on_new_room_name(new_room_name: str) -> None:
            self.room_name = new_room_name

            self.__event_emitter.emit("new_room_name", self, new_room_name)

        @self.__socket_client.on(59)
        async def on_room_password_change(flag: int) -> None:
            if bool(flag):
                self.__event_emitter.emit("new_room_password", self)
            else:
                self.__event_emitter.emit("room_password_clear", self)


class Player:
    """
    Class that holds bonk.io game players' info.

    :param bot: bot class that uses in the same game with player.
    :param game: the game which player is playing in.
    :param socket_client: socketio client for emitting events.
    :param is_bot: indicates whether player is bot or not.
    :param peer_id: player's game peer id.
    :param username: player's username.
    :param is_guest: indicates whether player is guest or not.
    :param level: player's level.
    :param is_ready: indicates whether player is ready or not.
    :param is_tabbed: indicates whether player is tabbed or not.
    :param team: Teams' class that indicates player's team.
    :param short_id: player's id in the game.
    :param avatar: player's avatar.
    """

    def __init__(
        self,
        bot,
        game: Game,
        socket_client: socketio.AsyncClient,
        is_bot: bool,
        peer_id: str,
        username: str,
        is_guest: bool,
        level: int,
        is_ready: bool,
        is_tabbed: bool,
        team: Union[Teams.Spectator, Teams.FFA, Teams.Red, Teams.Blue, Teams.Green, Teams.Yellow],
        short_id: int,
        avatar: Avatar
    ) -> None:
        self.bot = bot
        self.is_bot: bool = is_bot
        self.game: Game = game
        self.username: str = username
        self.is_guest: bool = is_guest
        self.level: int = level
        self.is_ready: bool = is_ready
        self.is_tabbed: bool = is_tabbed
        self.team: Union[Teams.Spectator, Teams.FFA, Teams.Red, Teams.Blue, Teams.Green, Teams.Yellow] = team
        self.balanced_by: int = 0
        self.short_id: int = short_id
        self.avatar: Avatar = avatar
        self.__socket_client: socketio.AsyncClient = socket_client
        self.__peer_id: str = peer_id

    async def send_friend_request(self) -> None:
        """Send friend request to the player."""

        await self.__socket_client.emit(
            35,
            {
                "id": self.short_id
            }
        )

    async def give_host(self) -> None:
        """Give the host permissions to player."""

        await self.__socket_client.emit(
            34,
            {
                "id": self.short_id
            }
        )
        self.game.is_host = False

    async def kick(self) -> None:
        """Kick player from game."""

        await self.__socket_client.emit(
            9,
            {
                "banshortid": self.short_id,
                "kickonly": True
            }
        )

    async def ban(self) -> None:
        """Ban player from game."""

        await self.__socket_client.emit(
            9,
            {
                "banshortid": self.short_id,
                "kickonly": False
            }
        )

    async def move_to_team(
        self,
        team: Union[Teams.Spectator, Teams.FFA, Teams.Red, Teams.Blue, Teams.Green, Teams.Yellow]
    ) -> None:
        """
        Move player to another team.

        :param team: Teams class that indicates player's team.
        """

        if not (
            isinstance(team, Teams.Spectator) or
            isinstance(team, Teams.FFA) or
            isinstance(team, Teams.Red) or
            isinstance(team, Teams.Blue) or
            isinstance(team, Teams.Green) or
            isinstance(team, Teams.Yellow)
        ):
            raise TypeError("Can't move player: team param is not a valid team")

        await self.__socket_client.emit(
            26,
            {
                "targetID": self.short_id,
                "targetTeam": team.number
            }
        )
        self.team = team

    async def balance(self, percents: int) -> None:
        """
        Nerf/buff player.

        :param percents: the percent you want to balance player by (in range [-100, 100]).
        """

        if not (percents in range(-100, 101)):
            raise ValueError("Can't balance player: percents param is not in range [-100, 100]")

        await self.__socket_client.emit(
            29,
            {
                "sid": self.short_id,
                "bal": percents
            }
        )
        self.balanced_by = percents


class Message:
    """
    Class that holds info about game message.

    :param content: message content.
    :param author: Player class that indicates the author of message.
    :param game: Game class that indicates the game where message was sent.
    """

    def __init__(self, content: str, author: Player, game: Game) -> None:
        self.content: str = content
        self.author: Player = author
        self.game: Game = game


class GameConnectionError(Exception):
    """Raised when game connection has some error."""

    def __init__(self, message: str, game: Game) -> None:
        self.message: str = message
        self.game: Game = game
