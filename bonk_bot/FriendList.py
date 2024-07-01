import datetime
from typing import List, Union

from .Settings import links
from .Parsers import db_id_to_date
from .Game import Game


class Friend:
    """
    Class for holding account's friends.

    :param bot: bot class that uses the account.
    :param user_id: friend's account database ID.
    :param username: friend's account username.
    :param room_id: the room ID where friend is playing.
    """

    def __init__(self, bot, user_id: int, username: str, room_id: Union[int, None]) -> None:
        self.bot = bot
        self.user_id: int = user_id
        self.username: str = username
        self.room_id: Union[int, None] = room_id

    async def unfriend(self) -> None:
        """Remove friend from account friend list."""

        async with self.bot.aiohttp_session.post(
            url=links["friends"],
            data={
                "token": self.bot.token,
                "task": "unfriend",
                "theirid": self.user_id
            }
        ) as resp:
            response = await resp.json()

        print(response)

    def get_creation_date(self) -> Union[datetime.datetime, str]:
        """Get friend's account creation date."""

        return db_id_to_date(self.user_id)

    async def join_game(self) -> Game:
        """
        Establish connection with room where friend is playing.

        Example usage::

            bot = bonk_account_login("name", "pass")

            friend_list = bot.get_friend_list()
            friend = [friend for friend in friend_list.get_friends() if friend.username == "test" and friend.room_id][0]

            async def main():
                game = friend.join_game()
                await game.send_message("Hello!")

                await bot.run()

            asyncio.run(main())
        """

        room = [room for room in self.bot.get_rooms() if room.room_id == self.room_id][0]
        game = room.join()
        await game.connect()

        return game


class FriendRequest:
    """
    Class for holding account's friend requests.

    :param bot: bot class that uses account.
    :param user_id: account database ID.
    :param username: account username.
    :param date: the date of sending friend request.
    """

    def __init__(self, bot, user_id: int, username: str, date: str) -> None:
        self.bot = bot
        self.user_id: int = user_id
        self.username: str = username
        self.date: str = date

    async def accept(self) -> None:
        """Accept friend request."""

        async with self.bot.aiohttp_session.post(
            url=links["friends"],
            data={
                "token": self.bot.token,
                "task": "accept",
                "theirid": self.user_id
            }
        ) as resp:
            response = await resp.json()

        print(response)

    async def delete(self) -> None:
        """Decline friend request."""

        async with self.bot.aiohttp_session.post(
            url=links["friends"],
            data={
                "token": self.bot.token,
                "task": "deleterequest",
                "theirid": self.user_id
            }
        ) as resp:
            response = await resp.json()

        print(response)


class FriendList:
    """
    Class for routing Friend and FriendRequest classes. Account's full friend list.

    :param bot: bot class that uses the account.
    :param raw_data: json data about account's friends and friend requests.
    """

    def __init__(self, bot, raw_data: dict) -> None:
        self.bot = bot
        self.__raw_data: dict = raw_data

    def get_friends(self) -> List[Friend]:
        """Get friends from account friend list."""

        return [
            Friend(
                self.bot,
                friend["id"],
                friend["name"],
                friend["roomid"]
            ) for friend in self.__raw_data["friends"]
        ]

    def get_friend_requests(self) -> List[FriendRequest]:
        """Get friend requests from account friend list."""

        return [
            FriendRequest(
                self.bot,
                request["id"],
                request["name"],
                request["date"]
            ) for request in self.__raw_data["requests"]
        ]
