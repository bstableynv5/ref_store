from pathlib import Path
from ref_store import manifest


def main():
    root = Path("C:/work/ref_store/src")
    print(manifest.for_directory(root, "https://github.com/bstableynv5/ref_store"))


if __name__ == "__main__":
    main()
