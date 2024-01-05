from functools import lru_cache


@lru_cache(maxsize=128)
def read_file_content(file_path: str, length: int = 0) -> str:
    with open(file_path, "r", encoding="utf8") as file:
        if length <= 0:
            return file.read()
        else:
            return file.read(length)
