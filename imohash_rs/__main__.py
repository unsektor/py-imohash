import argparse
import typing
import sys

import imohash_rs


def format_hash(
    hash_: imohash_rs.Hash,
    format_: typing.Literal['int', 'bytes', 'hex']
) -> typing.Union[int, bytes, str]:
    if format_ == 'int':
        return int(hash_)

    if format_ == 'bytes':
        return bytes(hash_)

    return hash_.hexdigest()


class InteractiveApplication:
    def __init__(self, imohash: imohash_rs.Imohash) -> None:
        self._imohash = imohash

    def run(self, format_: typing.Literal['int', 'bytes', 'hex']) -> None:
        while True:
            try:
                data = input('> ')
            except (EOFError, KeyboardInterrupt):
                break

            print(
                format_hash(
                    hash_=self._imohash.get(
                        data=data.encode('utf-8')
                    ),
                    format_=format_
                )
            )


class FilesApplication:
    def __init__(self, imohash: imohash_rs.Imohash) -> None:
        self._imohash = imohash

    def run(self, path: str, format_: typing.Literal['int', 'bytes', 'hex']) -> None:
        hash_ = format_hash(
            hash_=self._imohash.get_for_file(path=path),
            format_=format_
        )

        print(f"{hash_!s}  {path!s}")


def create_cli_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog='imohash_rs',
        description="imohash_rs is a sample application to hash files, similar to md5sum."
    )
    parser.add_argument(
        '-t', '--sample-threshold',
        action='store',
        default=imohash_rs.SAMPLE_THRESHOLD,
        help='Sample threshold value'
    )
    parser.add_argument(
        '-s', '--sample-size',
        action='store',
        default=imohash_rs.SAMPLE_SIZE,
        help='Sample size value. The entire file will be hashed (i.e. no sampling), if sample_size < 1.'
    )
    parser.add_argument(
        '-f', '--format',
        choices=('int', 'bytes', 'hex'),
        default='hex',
        help='Hash representation format'
    )
    parser.add_argument(
        '-i', '--interactive',
        action='store_true',
        default=None,
        help='Interactive hash computation mode. Conflicts with [file_path ...] argument.'
    )
    parser.add_argument(
        'file_path',
        nargs='*',
        help='File paths to compute hash of. Conflict with `-i/--interactive` argument.'
    )
    return parser


def main(argument_list: typing.List[str]) -> int:
    argument_parser = create_cli_parser()
    arguments = argument_parser.parse_args(argument_list)

    sample_threshold: int = int(arguments.sample_threshold)
    sample_size: int = int(arguments.sample_size)
    interactive: bool = arguments.interactive
    format_: typing.Literal['int', 'bytes', 'hex'] = arguments.format
    file_path_list: typing.List[str] = arguments.file_path

    imohash = imohash_rs.Imohash(
        sample_threshold=sample_threshold,
        sample_size=sample_size,
    )

    if not file_path_list and interactive is None:
        interactive = True
    elif not (bool(interactive) ^ bool(file_path_list)):
        print('Error: exactly at least one argument `--interactive/-i` or `[file_path ...]` is required', file=sys.stderr)
        return 1

    if interactive:
        print(f'Interactive mode (format: {format_!s})')
        application = InteractiveApplication(imohash=imohash)
        application.run(format_=format_)
        return 0

    application = FilesApplication(imohash=imohash)

    import concurrent.futures
    with concurrent.futures.ThreadPoolExecutor() as pool:
        for file_path in file_path_list:
            pool.submit(application.run, path=file_path, format_=format_)
    return 0


if __name__ == '__main__':
    exit_code = main(argument_list=sys.argv[1:])
    exit(exit_code)
