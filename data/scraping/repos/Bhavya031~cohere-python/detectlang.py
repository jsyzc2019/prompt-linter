from typing import List

from cohere.response import CohereObject


class Language(CohereObject):

    def __init__(self, code: str, name: str):
        self.language_code = code
        self.language_name = name

    def __repr__(self) -> str:
        return f"Language<language_code: \"{self.language_code}\", language_name: \"{self.language_name}\">"


class DetectLanguageResponse:

    def __init__(self, results: List[Language]):
        self.results = results
