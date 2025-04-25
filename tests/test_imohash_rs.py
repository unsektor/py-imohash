import typing
import hashlib
import uuid
import os
import io

import pytest

import imohash_rs

__all__ = (
    'TestImohash'
)

tests = [
    (16384, 131072, 0, "00000000000000000000000000000000"),
    (16384, 131072, 1, "01659e2ec0f3c75bf39e43a41adb5d4f"),
    (16384, 131072, 127, "7f47671cc79d4374404b807249f3166e"),
    (16384, 131072, 128, "800183e5dbea2e5199ef7c8ea963a463"),
    (16384, 131072, 4095, "ff1f770d90d3773949d89880efa17e60"),
    (16384, 131072, 4096, "802048c26d66de432dbfc71afca6705d"),
    (16384, 131072, 131072, "8080085a3d3af2cb4b3a957811cdf370"),
    (16384, 131073, 131072, "808008282d3f3b53e1fd132cc51fcc1d"),
    (16384, 131072, 500000, "a0c21e44a0ba3bddee802a9d1c5332ca"),
    (50, 131072, 300000, "e0a712edd8815c606344aed13c44adcf"),
    #
    (0, 100, 999, "e7078bfc9bdf7d7706adbd21002bb752"),
    (50, 9999, 999, "e7078bfc9bdf7d7706adbd21002bb752"),
    (250, 20, 999, "e7078bfc9bdf7d7706adbd21002bb752"),
    (250, 20, 1000, "e807ae87d3dafb5eb6518a5a256297e9"),
]


def M(size: int) -> bytes:
    chunks = []
    hasher = hashlib.md5()
    while 16 * len(chunks) < size:
        hasher.update(b"A")
        chunks.append(hasher.digest())

    return b"".join(chunks)[0:size]


_cached_instance: typing.Dict[typing.Tuple[int, int], imohash_rs.Imohash] = {}


class TestImohash:
    @pytest.mark.parametrize(['sample_size', 'sample_threshold', 'size', 'result'], tests)
    def test_get(self, sample_size: int, sample_threshold: int, size: int, result: str) -> None:
        # arrange
        stream = io.BytesIO()
        stream.write(M(size))
        stream.seek(0)

        # act
        if (sample_threshold, sample_size) not in _cached_instance:
            _cached_instance[(sample_threshold, sample_size)] = imohash_rs.Imohash(
                sample_threshold=sample_threshold,
                sample_size=sample_size
            )

        hasher = _cached_instance[(sample_threshold, sample_size)]
        actual_result = hasher.get(data=stream.read()).hexdigest()

        # assert
        assert result == actual_result

    @pytest.mark.parametrize(['sample_size', 'sample_threshold', 'size', 'result'], tests)
    def test_get_for_file(self, sample_size: int, sample_threshold: int, size: int, result: str) -> None:
        # arrange
        file_path = ".test_data" + str(uuid.uuid4())
        with open(file_path, 'wb') as stream:
            stream.write(M(size))

        try:
            # act
            if (sample_threshold, sample_size) not in _cached_instance:
                _cached_instance[(sample_threshold, sample_size)] = imohash_rs.Imohash(
                    sample_threshold=sample_threshold,
                    sample_size=sample_size
                )
            hasher = _cached_instance[(sample_threshold, sample_size)]
            actual_result = hasher.get_for_file(path=file_path).hexdigest()

            # assert
            assert result == actual_result
        finally:
            os.remove(file_path)
