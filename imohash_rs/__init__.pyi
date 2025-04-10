__version__ = '0.1.0'

SAMPLE_THRESHOLD: int = 128 * 1024
SAMPLE_SIZE: int = 16 * 1024


class Hash:
    """
    Holds imohash hash value. Provides methods for value formatting, similar to `hashlib.md5()`
    """
    def __init__(self, value: int) -> None:
        """
        Creates imohash hash value hold object.
        :param int value: hash as int number
        """

    def __str__(self) -> str:
        """
        Returns hash as string of hex number, e.g. `07ce528a343b2b99d4bd1bcdd648d138`
        :return: str value
        """

    def __int__(self) -> int:
        """
        Returns hash as int number, e.g. `75523435159185273289332158803318328839`
        :return: int value
        """

    def __bytes__(self) -> bytes:
        r"""
        Returns hash as bytes, e.g. ``b'\x07\xceR\x8a4;+\x99\xd4\xbd\x1b\xcd\xd6H\xd18'`
        :return: bytes value
        """

    def hexdigest(self) -> str:
        """
        Returns hash as string of hex number, e.g. `07ce528a343b2b99d4bd1bcdd648d138`
        :return: str value
        """

    def digest(self) -> bytes:
        r"""
        Returns hash as bytes, e.g. ``b'\x07\xceR\x8a4;+\x99\xd4\xbd\x1b\xcd\xd6H\xd18'`
        :return: bytes value
        """

    def __repr__(self) -> str:
       """
       Returns `Hash` instance object representation, e.g. `Hash(value=75523435159185273289332158803318328839)`
       :return: str value
       """


class Imohash:
    def __init__(self, sample_threshold: int = SAMPLE_THRESHOLD, sample_size: int = SAMPLE_SIZE) -> None:
        """
        Creates a new Hasher using the provided sample size and sample threshold values.
        The entire file will be hashed (i.e. no sampling), if sample_size < 1.

        :raises OverflowError: e.g. `out of range integral type conversion attempted`
        :raises TypeError: e.g. `unexpected keyword argument`/` 'str' object cannot be interpreted as an integer`
        """

    def get(self, data: bytes) -> Hash:
        """
        Returns hash of bytes data.

        :param bytes data:
        :raises TypeError: e.g. argument 'data': 'str' object cannot be converted to 'PyBytes'
        :return: `Hash` instance object
        """

    def get_for_file(self, path: str) -> Hash:
        """
        Returns file hash.

        :param str path: path to a file to hash
        :raises IsADirectoryError
        :raises FileNotFoundError
        :return: `Hash` instance object
        """

    def __repr__(self) -> str:
        """
        Returns instance object representation, e.g. `Imohash(sample_threshold=42, sample_size=23)`
        :return: str value
        """
