import re
from typing import Iterable, Set, List

class SearchPrefixBuilder:
    TEXT_FIELDS = (
        "description_en",
        "description_ru",
        "title_en",
        "title_ru",
        "label_en",
        "label_ru",
        "username",
        "name"
    )

    TAG_FIELDS = (
        "tags_en",
        "tags_ru",
    )

    _PUNCT_RE = re.compile(r"[^\w\s]", re.UNICODE)

    def normalize_text(self, text: str) -> str:
        if not isinstance(text, str):
            return ""

        text = text.lower().strip()
        text = self._PUNCT_RE.sub("", text)
        return text

    def tokenize(self, text: str) -> Set[str]:
        normalized = self.normalize_text(text)
        if not normalized:
            return set()

        return {word for word in normalized.split() if word}

    def generate_prefixes(self, word: str) -> Set[str]:
        if not word:
            return set()

        return {word[:i] for i in range(1, len(word) + 1)}

    def _extract_words_from_text_fields(self, doc: dict) -> Set[str]:
        words: Set[str] = set()

        for field in self.TEXT_FIELDS:
            value = doc.get(field)
            if isinstance(value, str):
                words.update(self.tokenize(value))

        return words

    def _extract_words_from_tag_fields(self, doc: dict) -> Set[str]:
        words: Set[str] = set()

        for field in self.TAG_FIELDS:
            value = doc.get(field)
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, str):
                        words.update(self.tokenize(item))

        return words

    def extract_keywords(self, doc: dict) -> List[str]:
        words = set()
        words.update(self._extract_words_from_text_fields(doc))
        words.update(self._extract_words_from_tag_fields(doc))
        return sorted(words)

    def build_prefixes(self, doc: dict) -> List[str]:
        keywords = self.extract_keywords(doc)
        prefixes = set()

        for word in keywords:
            prefixes.update(self.generate_prefixes(word))

        return sorted(prefixes)

    def build_search_payload(self, doc: dict) -> dict:
        keywords = self.extract_keywords(doc)
        prefixes = self.build_prefixes(doc)

        return {
            "search_keywords": keywords,
            "search_prefixes": prefixes,
        }