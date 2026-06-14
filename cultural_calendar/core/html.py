"""HTML parsing utilities: link/article/meta extractors and text normalizers."""

from __future__ import annotations

import html
import re
from html.parser import HTMLParser
from typing import Any
from urllib.parse import urljoin


def normalize_space(value: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(value)).strip()


def strip_tags(value: str) -> str:
    return normalize_space(re.sub(r"<[^>]+>", " ", value))


class LinkTextParser(HTMLParser):
    def __init__(self, base_url: str):
        super().__init__()
        self.base_url = base_url
        self.links: list[dict[str, str]] = []
        self._href_stack: list[str | None] = []
        self._text_stack: list[list[str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() == "a":
            href = dict(attrs).get("href")
            self._href_stack.append(href)
            self._text_stack.append([])

    def handle_data(self, data: str) -> None:
        if self._text_stack:
            self._text_stack[-1].append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "a" and self._href_stack:
            href = self._href_stack.pop()
            text_parts = self._text_stack.pop()
            text = normalize_space(" ".join(text_parts))
            if href and text:
                self.links.append({"text": text, "url": urljoin(self.base_url, href)})


class ArticleParser(HTMLParser):
    def __init__(self, base_url: str):
        super().__init__()
        self.base_url = base_url
        self.articles: list[dict[str, Any]] = []
        self._depth = 0
        self._text_parts: list[str] = []
        self._links: list[dict[str, str]] = []
        self._href_stack: list[str | None] = []
        self._link_text_stack: list[list[str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        if tag == "article":
            self._depth += 1
            if self._depth == 1:
                self._text_parts = []
                self._links = []
        elif self._depth:
            self._depth += 1
        if self._depth and tag == "a":
            href = dict(attrs).get("href")
            self._href_stack.append(href)
            self._link_text_stack.append([])

    def handle_data(self, data: str) -> None:
        if self._depth:
            self._text_parts.append(data)
            if self._link_text_stack:
                self._link_text_stack[-1].append(data)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if self._depth and tag == "a" and self._href_stack:
            href = self._href_stack.pop()
            text = normalize_space(" ".join(self._link_text_stack.pop()))
            if href:
                self._links.append({"text": text, "url": urljoin(self.base_url, href)})
        if self._depth:
            self._depth -= 1
            if tag == "article" or self._depth == 0:
                text = normalize_space(" ".join(self._text_parts))
                if text or self._links:
                    self.articles.append({"text": text, "links": self._links[:]})
                self._text_parts = []
                self._links = []
                self._href_stack = []
                self._link_text_stack = []


class MetaParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title = ""
        self.meta: dict[str, str] = {}
        self._in_title = False
        self._title_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = {key.lower(): value for key, value in attrs if value is not None}
        if tag.lower() == "title":
            self._in_title = True
        if tag.lower() == "meta":
            name = attrs_dict.get("name") or attrs_dict.get("property")
            content = attrs_dict.get("content")
            if name and content:
                self.meta[name.lower()] = normalize_space(content)

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self._title_parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "title":
            self._in_title = False
            self.title = normalize_space(" ".join(self._title_parts))
