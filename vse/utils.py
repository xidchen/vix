import os


def last_two_levels(file_path: str) -> str:
    head, tail = os.path.split(file_path)
    head, second_level = os.path.split(head)
    last_two_levels_path = os.path.join(second_level, tail)
    return last_two_levels_path
