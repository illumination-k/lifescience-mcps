from enum import Enum


class Format(str, Enum):
    JSON = "json"
    TSV = "tsv"
    TXT = "txt"
    XML = "xml"

    def __str__(self) -> str:
        return str(self.value)
