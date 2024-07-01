class Servers:
    """Class for holding server types."""

    class Warsaw:
        def __init__(self) -> None:
            self.latitude = 52.2370
            self.longitude = 21.0175
            self.country = "PL"

        def __str__(self) -> str:
            return "b2warsaw1"

    class Stockholm:
        def __init__(self) -> None:
            self.latitude = 59.3346
            self.longitude = 18.0632
            self.country = "SE"

        def __str__(self) -> str:
            return "b2stockholm1"

    class Frankfurt:
        def __init__(self) -> None:
            self.latitude = 50.1109
            self.longitude = 8.6821
            self.country = "GE"

        def __str__(self) -> str:
            return "b2frankfurt1"

    class London:
        def __init__(self) -> None:
            self.latitude = 51.5098
            self.longitude = -0.1180
            self.country = "UK"

        def __str__(self) -> str:
            return "b2london1"

    class Seoul:
        def __init__(self) -> None:
            self.latitude = 37.5326
            self.longitude = 127.0246
            self.country = "KR"

        def __str__(self) -> str:
            return "b2seoul1"

    class Seattle:
        def __init__(self) -> None:
            self.latitude = 47.6080
            self.longitude = -122.3352
            self.country = "US"

        def __str__(self) -> str:
            return "b2seattle1"

    class SanFrancisco:
        def __init__(self) -> None:
            self.latitude = 37.7740
            self.longitude = -122.4312
            self.country = "US"

        def __str__(self) -> str:
            return "b2sanfrancisco1"

    class Mississippi:
        def __init__(self) -> None:
            self.latitude = 35.5147
            self.longitude = -89.9125
            self.country = "US"

        def __str__(self) -> str:
            return "b2river1"

    class Dallas:
        def __init__(self) -> None:
            self.latitude = 32.7792
            self.longitude = -96.8089
            self.country = "US"

        def __str__(self) -> str:
            return "b2dallas1"

    class NewYork:
        def __init__(self) -> None:
            self.latitude = 40.7306
            self.longitude = -73.9352
            self.country = "US"

        def __str__(self) -> str:
            return "b2ny1"

    class Atlanta:
        def __init__(self) -> None:
            self.latitude = 33.7537
            self.longitude = -84.3863
            self.country = "US"

        def __str__(self) -> str:
            return "b2atlanta1"

    class Sydney:
        def __init__(self) -> None:
            self.latitude = -33.8651
            self.longitude = 151.2099
            self.country = "AU"

        def __str__(self) -> str:
            return "b2sydney1"

    class Brazil:
        def __init__(self) -> None:
            self.latitude = -22.9083
            self.longitude = -43.1963
            self.country = "BR"

        def __str__(self) -> str:
            return "b2brazil1"


class Modes:
    """Class for holding mode types."""

    class Classic:
        def __init__(self) -> None:
            self.ga = "b"
            self.short_name = "b"

        def __str__(self) -> str:
            return "Classic"

    class Arrows:
        def __init__(self) -> None:
            self.ga = "b"
            self.short_name = "ar"

        def __str__(self) -> str:
            return "Arrows"

    class DeathArrows:
        def __init__(self) -> None:
            self.ga = "b"
            self.short_name = "ard"

        def __str__(self) -> str:
            self.ga = "b"
            return "Death Arrows"

    class Grapple:
        def __init__(self) -> None:
            self.ga = "b"
            self.short_name = "sp"

        def __str__(self) -> str:
            self.ga = "b"
            return "Grapple"

    class VTOL:
        def __init__(self) -> None:
            self.ga = "b"
            self.short_name = "v"

        def __str__(self) -> str:
            return "VTOL"

    class Football:
        def __init__(self) -> None:
            self.ga = "f"
            self.short_name = "f"

        def __str__(self) -> str:
            return "Football"


class Teams:
    """Class for holding team types."""

    class Spectator:
        def __init__(self) -> None:
            self.number = 0

        def __str__(self) -> str:
            return "Spectator"

    class FFA:
        def __init__(self) -> None:
            self.number = 1

        def __str__(self) -> str:
            return "FFA"

    class Red:
        def __init__(self) -> None:
            self.number = 2

        def __str__(self) -> str:
            return "Red"

    class Blue:
        def __init__(self) -> None:
            self.number = 3

        def __str__(self) -> str:
            return "Blue"

    class Green:
        def __init__(self) -> None:
            self.number = 4

        def __str__(self) -> str:
            return "Green"

    class Yellow:
        def __init__(self) -> None:
            self.number = 5

        def __str__(self) -> str:
            return "Yellow"
