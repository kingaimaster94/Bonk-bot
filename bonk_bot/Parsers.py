import base64
import datetime
import json
import struct
from typing import Union
from urllib.parse import unquote_plus

from .Types import Teams, Modes
from .Avatar import Avatar


# <3 Fotis
def parse_avatar(avatar: str) -> Avatar:
    """
    Used to decode avatar from base64 string.

    :param avatar: base64 encoded avatar string that is decoded in this function.
    """

    avatar = unquote_plus(avatar)
    avatar = base64.b64decode(avatar + "==")

    def peek(count, offset: int = 0):
        nonlocal avatar
        data = avatar[offset:count + offset]
        avatar = avatar[offset + count:]
        return data

    _ = peek(7)

    shapes_count = (int.from_bytes(peek(1), "big") - 1) // 2
    shapes = []
    _ = peek(3)
    if shapes_count > 0:
        _ = peek(6)
        for i in range(shapes_count):
            shape = dict()

            shape["id"] = int.from_bytes(peek(1), "big")
            shape["scale"] = struct.unpack(">f", peek(4))[0]
            shape["angle"] = struct.unpack(">f", peek(4))[0]
            shape["x"] = struct.unpack(">f", peek(4))[0]
            shape["y"] = struct.unpack(">f", peek(4))[0]
            shape["flipX"] = int.from_bytes(peek(1), "big") == 1
            shape["flipY"] = int.from_bytes(peek(1), "big") == 1
            shape["color"] = int.from_bytes(peek(3, 1), "big")

            shapes.append(shape)

            if i != shapes_count - 1:
                peek(5)

    base_color = int.from_bytes(peek(3), "big")
    avatar = dict()

    avatar["layers"] = shapes
    avatar["bc"] = base_color

    return Avatar(avatar)


# Credits to https://shaunx777.github.io/dbid2date/
def db_id_to_date(db_id: int) -> Union[datetime.datetime, str]:
    """
    Returns approximate account date creating from account database ID.

    :param db_id: account database ID.
    """

    with open("bonk_bot/dbids.json") as file:
        db_ids = json.load(file)
        index = 0

    while index < len(db_ids) and db_ids[index]["number"] < db_id:
        index += 1

    if index == 0:
        return f"Before {db_ids[0]['date']}"
    elif index == len(db_ids):
        return f"After {db_ids[-1]['date']}"

    first_number = db_ids[index - 1]["number"]
    second_number = db_ids[index]["number"]

    first_date = db_ids[index - 1]["date"]
    second_date = db_ids[index]["date"]
    first_timestamp = datetime.datetime.strptime(first_date, "%Y-%m-%d").timestamp()
    second_timestamp = datetime.datetime.strptime(second_date, "%Y-%m-%d").timestamp()

    diff = (db_id - first_number) / (second_number - first_number)
    time = first_timestamp + diff * (second_timestamp - first_timestamp)

    return datetime.datetime.fromtimestamp(time).strftime("%Y-%m-%d %H:%M:%S")


def team_from_number(
    number: int
) -> Union[Teams.Spectator, Teams.FFA, Teams.Red, Teams.Blue, Teams.Green, Teams.Yellow]:
    """
    Returns mode class from its number according to bonk.io api.

    :param number: the number of team in bonk.io api.
    """

    teams = {
        0: Teams.Spectator(),
        1: Teams.FFA(),
        2: Teams.Red(),
        3: Teams.Blue(),
        4: Teams.Green(),
        5: Teams.Yellow(),
    }

    return teams[number]


def mode_from_short_name(
    short_name: str
) -> Union[Modes.Classic, Modes.Arrows, Modes.DeathArrows, Modes.Grapple, Modes.VTOL, Modes.Football]:
    """
    Returns mode class from its short name according to bonk.io api.

    :param short_name: mode short name in bonk.io api.
    """

    modes = {
        "b": Modes.Classic(),
        "ar": Modes.Arrows(),
        "ard": Modes.DeathArrows(),
        "sp": Modes.Grapple(),
        "v": Modes.VTOL(),
        "f": Modes.Football(),
    }

    return modes[short_name]
