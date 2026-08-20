"""Petit parseur robots.txt applique la regle du chemin le plus long.

`urllib.robotparser` renvoie la premiere regle qui correspond, ce qui autorise
a tort `/suche/` face a un `Allow: /` place avant. On implemente donc la regle
de precedence du standard (RFC 9309) : le motif le plus long l'emporte, et
`Allow` gagne a longueur egale.
"""

from __future__ import annotations

import re
from urllib.parse import unquote, urlparse


class RobotsRules:
    """Regles applicables a un User-Agent pour un hote donne."""

    def __init__(self, rules: list[tuple[bool, str]], crawl_delay: float | None):
        self._rules = rules              # (autorise, motif)
        self.crawl_delay = crawl_delay

    @classmethod
    def empty(cls) -> "RobotsRules":
        return cls([], None)

    @classmethod
    def parse(cls, text: str, user_agent: str) -> "RobotsRules":
        token = user_agent.split("/")[0].strip().lower()
        groups: dict[str, list[tuple[bool, str]]] = {}
        delays: dict[str, float] = {}
        current: list[str] = []
        expect_agent = True

        for raw_line in text.splitlines():
            line = raw_line.split("#", 1)[0].strip()
            if not line or ":" not in line:
                continue
            field, _, value = line.partition(":")
            field = field.strip().lower()
            value = value.strip()

            if field == "user-agent":
                if not expect_agent:
                    current = []
                    expect_agent = True
                current.append(value.lower())
                groups.setdefault(value.lower(), [])
            elif field in ("allow", "disallow"):
                expect_agent = False
                if not current:
                    continue
                for agent in current:
                    if value:
                        groups[agent].append((field == "allow", value))
                    elif field == "disallow":
                        # "Disallow:" vide = tout autorise, on ignore la regle.
                        continue
            elif field == "crawl-delay":
                expect_agent = False
                try:
                    for agent in current:
                        delays[agent] = float(value)
                except ValueError:
                    pass

        for agent in (token, "*"):
            if agent in groups:
                return cls(groups[agent], delays.get(agent))
        return cls.empty()

    # ------------------------------------------------------------------ test
    @staticmethod
    def _matches(pattern: str, path: str) -> int:
        """Longueur du motif s'il correspond au chemin, -1 sinon."""
        regex_parts: list[str] = []
        end_anchor = pattern.endswith("$")
        body = pattern[:-1] if end_anchor else pattern
        for chunk in body.split("*"):
            regex_parts.append(re.escape(chunk))
        regex = ".*".join(regex_parts)
        regex = "^" + regex + ("$" if end_anchor else "")
        return len(pattern) if re.match(regex, path) else -1

    def can_fetch(self, url: str) -> bool:
        parts = urlparse(url)
        path = unquote(parts.path or "/")
        if parts.query:
            path += "?" + parts.query

        best_len, best_allow = -1, True
        for allow, pattern in self._rules:
            length = self._matches(pattern, path)
            if length > best_len or (length == best_len and allow):
                if length >= 0:
                    best_len, best_allow = length, allow
        return best_allow
