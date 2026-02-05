import json
from contextlib import ExitStack
import hashlib
from pathlib import Path
from typing import Generator, Iterable, Union
from datetime import datetime, timezone


def file_generator(root: Path) -> Generator[bytes, None, None]:
    """Get bytes from all files within `root`

    Args:
        root (Path): Base directory whose contents will be
            included in the manifest.

    Yields:
        Generator[bytes, None, None]: Yields the binary contents of each file.
    """
    with ExitStack() as stack:
        paths = (p for p in root.rglob("**/*") if p.is_file())
        files = (stack.enter_context(p.open("rb")) for p in paths)
        buffers = (f.read() for f in files)
        yield from buffers


def hash_all(buffers: Iterable[Union[bytes, bytearray, memoryview]]) -> tuple[str, int]:
    """Creates a single hex digest from all the binary information.

    Args:
        buffers (Iterable[Union[bytes, bytearray, memoryview]]): Binary
            data to be hashed. Does not support `io.BinaryIO` (file object).

    Returns:
        str: The complete hash as a string of hexidecimal digits.
    """
    count = 0
    hasher = hashlib.md5(usedforsecurity=False)
    for buffer in buffers:
        count += 1
        hasher.update(buffer)
    return hasher.hexdigest(), count


def for_directory(root: Union[Path, str], github_url: Union[Path, str]) -> str:
    """Produce a "manifest" of the files for a project.

    Args:
        root (Union[Path, str]): Folder with files, such as "toolbox_references".
        github_url (Union[Path, str]): Github repo path to identify the project.
            The repo's name will become the `name` identifying this manifest's
            contents.

    Returns:
        str: JSON formatted manifest file contents.
    """
    root = Path(root)
    github_url = Path(github_url)
    name = github_url.stem

    hash, file_count = hash_all(file_generator(root))
    contents = json.dumps(
        {
            "name": name,
            "repo": str(github_url),
            "date": datetime.now().astimezone(timezone.utc).isoformat(),
            "hash": hash,
            "files": file_count,
        },
        indent=2,
    )

    return contents
