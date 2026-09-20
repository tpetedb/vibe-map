"""The local chat bridge: the game asks, the learner's own CLI answers.

A browser page cannot reach a terminal subscription, so `vibe chat serve` runs a
loopback HTTP bridge the game talks to. The bridge never accepts a command to
run, only a question; it builds the system prompt itself from the course data,
so the page sends identifiers rather than text to execute. Every limit here has
a reason in docs/adr/0009-local-chat-bridge.md.
"""

from __future__ import annotations

import http.server
import json
import secrets
import threading
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlsplit

from vibemap import campaign
from vibemap.config import Config
from vibemap.providers import ProviderMissing, get_provider, stream

# Loopback only. A bridge on 0.0.0.0 would hand the learner's subscription to
# everyone on the cafe wifi.
HOST = "127.0.0.1"
# The page has to find the bridge, and it cannot read the port off a terminal,
# so the default port is fixed. --port 0 takes a free one for anyone who would
# rather type the port into the panel.
DEFAULT_PORT = 7717
# Origins allowed to talk to the bridge. Loopback on any port (the game served
# locally), file:// (which sends "null") and the hosted copy.
ALLOWED_HOSTS = frozenset({"localhost", "127.0.0.1", "[::1]"})
ALLOWED_SCHEMES = frozenset({"http", "https"})
HOSTED_ORIGIN = "https://tpetedb.github.io"
FILE_ORIGIN = "null"
# Caps: a question is a question. The body cap is what the socket reads at all.
MAX_BODY = 16_384
MAX_QUESTION = 4_000
# A pairing code is the shared secret, so it is long enough to be worth
# guessing and the bridge stops answering long before a guess lands.
CODE_LENGTH = 8
CODE_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
MAX_FAILURES = 10
DEFAULT_TIMEOUT = 180
HISTORY_HINT = "Answer in at most 200 words, plain words, no headings."


class Refused(Exception):
    """The request is refused; `status` is what the caller gets back."""

    def __init__(self, status: int, message: str) -> None:
        super().__init__(message)
        self.status = status
        self.message = message


def new_code() -> str:
    """A fresh pairing code, in the alphabet the game shows (no O, I, 0, 1)."""
    return "".join(secrets.choice(CODE_ALPHABET) for _ in range(CODE_LENGTH))


def normalise_code(code: str) -> str:
    """Upper case, spaces and dashes dropped. Refuses anything unusable."""
    cleaned = "".join(c for c in code.upper() if c in CODE_ALPHABET)
    if len(cleaned) < 4:
        raise ValueError(
            f"a pairing code is at least 4 characters from {CODE_ALPHABET}; "
            f"the panel shows one of {CODE_LENGTH}"
        )
    return cleaned


def origin_allowed(origin: str, extra: frozenset[str] = frozenset()) -> bool:
    """True when this Origin header may talk to the bridge."""
    if not origin:
        return False
    if origin in extra or origin == FILE_ORIGIN or origin == HOSTED_ORIGIN:
        return True
    parts = urlsplit(origin)
    return parts.scheme in ALLOWED_SCHEMES and parts.hostname in ALLOWED_HOSTS


@dataclass(frozen=True, slots=True)
class Ask:
    """One question, with the identifiers that say what it is about.

    Identifiers, never text: the bridge looks the stop, the mentor and the
    artifact up in the course data itself, so nothing the page sends becomes
    part of the prompt except the question.
    """

    question: str
    world: str = "campus"
    stop: int | None = None
    mentor: str | None = None
    artifact: str | None = None

    @classmethod
    def from_payload(cls, payload: Any) -> Ask:
        if not isinstance(payload, dict):
            raise ValueError("the body is a JSON object with a question")
        question = str(payload.get("question", "")).strip()
        if not question:
            raise ValueError("no question")
        if len(question) > MAX_QUESTION:
            raise ValueError(f"a question is at most {MAX_QUESTION} characters")
        world = str(payload.get("world") or "campus")
        if world not in campaign.WORLD_NAMES:
            raise ValueError(f"unknown world {world!r}")
        return cls(
            question=question,
            world=world,
            stop=_opt_int(payload.get("stop")),
            mentor=_opt_id(payload.get("mentor")),
            artifact=_opt_id(payload.get("artifact")),
        )


def _opt_int(value: Any) -> int | None:
    if value in (None, "", False):
        return None
    try:
        n = int(value)
    except (TypeError, ValueError):
        raise ValueError("stop is a number") from None
    return n if 1 <= n <= 9 else None


def _opt_id(value: Any) -> str | None:
    if not value:
        return None
    text = str(value)
    # Identifiers in the course data are lower case words with dashes.
    return (
        text if len(text) <= 40 and all(c.isalnum() or c == "-" for c in text) else None
    )


def context_line(ask: Ask) -> str:
    """The one line the panel shows as the context chip, built from the course."""
    parts = [campaign.WORLD_NAMES.get(ask.world, ask.world)]
    stop = _stop(ask)
    if stop:
        parts.append(f"stop {stop.n}, {stop.name}")
    if ask.mentor:
        try:
            parts.append(campaign.mentor(ask.mentor)["name"])
        except ValueError:
            pass
    art = _artifact(ask)
    if art:
        parts.append(art["name"])
    return " · ".join(parts)


def _stop(ask: Ask):
    if ask.stop is None:
        return None
    evening = campaign.evenings().get(ask.world)
    if not evening:
        return None
    for ws in evening.workstreams:
        if ws.n == ask.stop:
            return ws
    return None


def _artifact(ask: Ask) -> dict[str, Any] | None:
    if not ask.artifact:
        return None
    for a in campaign.artifacts():
        if a["id"] == ask.artifact:
            return a
    return None


def system_prompt(ask: Ask, cfg: Config) -> str:
    """The prompt the provider runs: the course around the question, then the question.

    Built here rather than in the page, so a page cannot dictate what the
    learner's own agent is told to do.
    """
    evening = campaign.evenings().get(ask.world)
    lines = [
        "You are the guide inside Vibe Code Camp, a game that teaches coding "
        "with an AI agent. Someone playing it has a question about what they "
        "are looking at. Answer it for them.",
        "",
        f"Player: {cfg.learner.name}. Difficulty: {cfg.learner.difficulty}.",
    ]
    if evening:
        lines.append(f"Island: {evening.island}. Evening: {evening.title}.")
    stop = _stop(ask)
    if stop:
        lines.append(f"Stop {stop.n} ({stop.hour}): {stop.name}. Goal: {stop.outcome}.")
        for label, url in stop.sources:
            lines.append(f"Reference: {label} {url}")
    if ask.mentor:
        try:
            m = campaign.mentor(ask.mentor)
        except ValueError:
            m = None
        if m:
            lines.append(f"Mentor in view: {m['name']}, {m['role']}. {m['bio']}")
            for idea in m.get("ideas", [])[:4]:
                lines.append(f"Their idea: {idea}")
    art = _artifact(ask)
    if art:
        lines.append(
            f"Artifact in view: {art['name']}, which teaches {art['concept']}. "
            f"{art['what']}"
        )
    lines += [
        "",
        "Rules: plain words, no jargon the stop has not introduced, no em "
        "dashes, no emoji. Prefer the exact command or file the player should "
        "look at. Say when you do not know. " + HISTORY_HINT,
        "",
        "QUESTION:",
        ask.question,
    ]
    return "\n".join(lines)


Runner = Callable[[str, str, int], Iterator[str]]


def _default_runner(provider_id: str, prompt: str, timeout: int) -> Iterator[str]:
    return stream(provider_id, prompt, timeout=timeout)


class Bridge:
    """What the handler needs: who may ask, with which code, and how to answer.

    One request at a time. The provider is a subprocess with a subscription
    behind it; two at once is two bills and a confusing panel.
    """

    def __init__(
        self,
        cfg: Config,
        *,
        code: str,
        provider_id: str | None = None,
        origins: frozenset[str] = frozenset(),
        timeout: int = DEFAULT_TIMEOUT,
        runner: Runner | None = None,
    ) -> None:
        self.cfg = cfg
        self.code = normalise_code(code)
        self.provider_id = provider_id or cfg.learner.provider
        self.origins = origins
        self.timeout = timeout
        self.runner = runner or _default_runner
        self.lock = threading.Lock()
        self.failures = 0

    @property
    def locked_out(self) -> bool:
        return self.failures >= MAX_FAILURES

    def check_origin(self, origin: str) -> str:
        if not origin_allowed(origin, self.origins):
            raise Refused(403, "origin not allowed")
        return origin

    def check_token(self, token: str) -> None:
        if self.locked_out:
            raise Refused(403, "too many wrong pairing codes; restart the bridge")
        try:
            given = normalise_code(token or "")
        except ValueError:
            given = ""
        if not secrets.compare_digest(given, self.code):
            self.failures += 1
            raise Refused(401, "wrong pairing code")
        self.failures = 0

    def health(self) -> dict[str, Any]:
        provider = get_provider(self.provider_id)
        return {
            "ok": True,
            "provider": provider.id,
            "label": provider.label,
            "available": provider.available(),
            "install": provider.install,
        }

    def answer(self, ask: Ask) -> Iterator[str]:
        """Yield the answer in the pieces the provider prints it in."""
        prompt = system_prompt(ask, self.cfg)
        yield from self.runner(self.provider_id, prompt, self.timeout)


def _sse(event: str, data: dict[str, Any]) -> bytes:
    return f"event: {event}\ndata: {json.dumps(data)}\n\n".encode()


def handler_for(bridge: Bridge) -> type[http.server.BaseHTTPRequestHandler]:
    """The request handler, closed over one bridge."""

    class Handler(http.server.BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"
        server_version = "vibe-chat"

        def log_message(self, format: str, *args: Any) -> None:  # noqa: A002
            pass

        # -- plumbing ------------------------------------------------------
        def _cors(self, origin: str) -> None:
            self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header("Vary", "Origin")
            self.send_header(
                "Access-Control-Allow-Headers", "content-type, x-vibe-code"
            )
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")

        def _json(self, status: int, payload: dict[str, Any], origin: str = "") -> None:
            body = json.dumps(payload).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            # The answer is data for fetch(); no browser gets to guess it is a page.
            self.send_header("X-Content-Type-Options", "nosniff")
            if origin:
                self._cors(origin)
            self.end_headers()
            self.wfile.write(body)

        def _refuse(self, err: Refused, origin: str = "") -> None:
            self._json(err.status, {"error": err.message}, origin)

        def _origin(self) -> str:
            return bridge.check_origin(self.headers.get("Origin", ""))

        # -- routes --------------------------------------------------------
        def do_OPTIONS(self) -> None:  # noqa: N802
            try:
                origin = self._origin()
            except Refused as err:
                self._refuse(err)
                return
            self.send_response(204)
            self._cors(origin)
            self.send_header("Content-Length", "0")
            self.end_headers()

        def do_GET(self) -> None:  # noqa: N802
            try:
                origin = self._origin()
            except Refused as err:
                self._refuse(err)
                return
            if self.path.split("?")[0] != "/health":
                self._json(404, {"error": "no such endpoint"}, origin)
                return
            self._json(200, bridge.health(), origin)

        def do_POST(self) -> None:  # noqa: N802
            try:
                origin = self._origin()
            except Refused as err:
                self._refuse(err)
                return
            try:
                if self.path.split("?")[0] != "/ask":
                    raise Refused(404, "no such endpoint")
                bridge.check_token(self.headers.get("X-Vibe-Code", ""))
                ask = Ask.from_payload(self._body())
            except Refused as err:
                self._refuse(err, origin)
                return
            except ValueError as err:
                self._json(400, {"error": str(err)}, origin)
                return
            if not bridge.lock.acquire(blocking=False):
                self._json(
                    409, {"error": "a question is already being answered"}, origin
                )
                return
            try:
                self._stream(ask, origin)
            finally:
                bridge.lock.release()

        def _body(self) -> Any:
            # A negative length would make read() wait for the peer to hang
            # up, so a length is a plain count of bytes or the request is over.
            declared = (self.headers.get("Content-Length") or "0").strip()
            if not (declared.isascii() and declared.isdigit()):
                raise Refused(400, "Content-Length is a number of bytes")
            length = int(declared)
            if length > MAX_BODY:
                raise Refused(413, f"the body is at most {MAX_BODY} bytes")
            raw = self.rfile.read(length) if length else b""
            try:
                return json.loads(raw or b"{}")
            except json.JSONDecodeError:
                raise ValueError("the body is not JSON") from None

        def _stream(self, ask: Ask, origin: str) -> None:
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Connection", "close")
            self._cors(origin)
            self.end_headers()
            self.wfile.write(
                _sse(
                    "start",
                    {"context": context_line(ask), "provider": bridge.provider_id},
                )
            )
            self.wfile.flush()
            try:
                for piece in bridge.answer(ask):
                    if not piece:
                        continue
                    self.wfile.write(_sse("delta", {"text": piece}))
                    self.wfile.flush()
            except ProviderMissing as err:
                self.wfile.write(_sse("error", {"message": str(err), "missing": True}))
            except Exception as err:  # noqa: BLE001
                # The page is waiting on this stream, so every failure below
                # becomes one error frame rather than a dropped connection.
                self.wfile.write(_sse("error", {"message": str(err)}))
            else:
                self.wfile.write(_sse("done", {}))
            self.wfile.flush()
            self.close_connection = True

    return Handler


def serve(
    bridge: Bridge, *, port: int = DEFAULT_PORT
) -> http.server.ThreadingHTTPServer:
    """Bind the bridge on loopback and return the server, not yet serving."""
    return http.server.ThreadingHTTPServer((HOST, port), handler_for(bridge))
