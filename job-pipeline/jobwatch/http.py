"""Client HTTP poli : robots.txt, delai par hote, User-Agent identifiable."""

from __future__ import annotations

import logging
import time
from urllib.parse import urlparse, urlunparse

import requests

from .robots import RobotsRules

log = logging.getLogger("jobwatch.http")


class RobotsDisallowed(RuntimeError):
    """Levee quand robots.txt interdit l'URL au User-Agent configure."""


class PoliteFetcher:
    """Effectue les requetes HTTP en respectant robots.txt et un delai minimal.

    Le delai est applique *par hote* : deux sites differents ne s'attendent
    pas mutuellement, mais deux pages du meme site sont toujours espacees.
    """

    def __init__(
        self,
        user_agent: str,
        delay: float = 2.0,
        timeout: int = 30,
        respect_robots: bool = True,
        max_retries: int = 3,
    ):
        self.user_agent = user_agent
        self.delay = delay
        self.timeout = timeout
        self.respect_robots = respect_robots
        self.max_retries = max_retries
        self._last_call: dict[str, float] = {}
        self._robots: dict[str, RobotsRules] = {}
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": user_agent,
                "Accept-Language": "fr-CH,fr;q=0.9,en;q=0.6,de;q=0.4",
            }
        )

    # ---------------------------------------------------------------- robots
    def _robots_for(self, url: str) -> RobotsRules:
        parts = urlparse(url)
        origin = f"{parts.scheme}://{parts.netloc}"
        if origin in self._robots:
            return self._robots[origin]

        robots_url = urlunparse((parts.scheme, parts.netloc, "/robots.txt", "", "", ""))
        rules = RobotsRules.empty()
        try:
            self._wait(parts.netloc)
            resp = self.session.get(robots_url, timeout=self.timeout)
            self._last_call[parts.netloc] = time.monotonic()
            if resp.status_code < 400 and resp.text:
                rules = RobotsRules.parse(resp.text, self.user_agent)
            # 4xx/5xx : pas de robots.txt exploitable, tout est autorise.
        except requests.RequestException as exc:
            log.debug("robots.txt injoignable pour %s (%s)", origin, exc)
        self._robots[origin] = rules
        return rules

    def allowed(self, url: str) -> bool:
        if not self.respect_robots:
            return True
        return self._robots_for(url).can_fetch(url)

    def crawl_delay(self, url: str) -> float:
        """Delai effectif : le notre, ou celui demande par le site s'il est plus long."""
        if not self.respect_robots:
            return self.delay
        return max(self.delay, float(self._robots_for(url).crawl_delay or 0))

    # ------------------------------------------------------------------ http
    def _wait(self, host: str) -> None:
        last = self._last_call.get(host)
        if last is None:
            return
        remaining = self.delay - (time.monotonic() - last)
        if remaining > 0:
            time.sleep(remaining)

    def get(self, url: str, **kwargs) -> requests.Response:
        return self.request("GET", url, **kwargs)

    def request(self, method: str, url: str, **kwargs) -> requests.Response:
        if not self.allowed(url):
            raise RobotsDisallowed(f"robots.txt interdit {url}")

        host = urlparse(url).netloc
        delay = self.crawl_delay(url)
        backoff = 2.0
        last_exc: Exception | None = None

        for attempt in range(1, self.max_retries + 1):
            last = self._last_call.get(host)
            if last is not None:
                remaining = delay - (time.monotonic() - last)
                if remaining > 0:
                    time.sleep(remaining)
            try:
                resp = self.session.request(
                    method, url, timeout=self.timeout, **kwargs
                )
                self._last_call[host] = time.monotonic()
                if resp.status_code in (429, 500, 502, 503, 504):
                    raise requests.HTTPError(
                        f"{resp.status_code} sur {url}", response=resp
                    )
                return resp
            except requests.RequestException as exc:
                self._last_call[host] = time.monotonic()
                last_exc = exc
                if attempt == self.max_retries:
                    break
                log.warning(
                    "%s (tentative %d/%d), nouvelle tentative dans %.0fs",
                    exc, attempt, self.max_retries, backoff,
                )
                time.sleep(backoff)
                backoff *= 2

        raise last_exc  # type: ignore[misc]
