#!/usr/bin/env python3
"""Cliente minimo da ElevenLabs para locucoes e timings de motion."""

from __future__ import annotations

import argparse
import base64
import json
import os
import re
import sys
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


API_BASE = "https://api.elevenlabs.io"
DEFAULT_MODEL = "eleven_v3"
DEFAULT_FORMAT = "mp3_44100_128"


class ApiError(RuntimeError):
    pass


def find_env_file(explicit: str | None) -> Path | None:
    if explicit:
        path = Path(explicit).expanduser().resolve()
        if not path.is_file():
            raise ValueError(f"Arquivo .env inexistente: {path}")
        return path

    starts = [Path.cwd().resolve(), Path(__file__).resolve().parent]
    visited: set[Path] = set()
    for start in starts:
        for directory in (start, *start.parents):
            if directory in visited:
                continue
            visited.add(directory)
            candidate = directory / ".env"
            if candidate.is_file():
                return candidate
    return None


def load_env(path: Path | None) -> None:
    if path is None:
        return
    for raw_line in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if value and value[0:1] == value[-1:] and value.startswith(("'", '"')):
            value = value[1:-1]
        if key:
            os.environ.setdefault(key, value)


def api_key() -> str:
    value = os.getenv("ELEVENLABS_API_KEY", "").strip()
    if not value:
        raise ValueError("ELEVENLABS_API_KEY nao foi encontrada no ambiente nem no .env.")
    return value


def request_json(
    method: str,
    path: str,
    *,
    timeout: float,
    query: dict[str, Any] | None = None,
    body: dict[str, Any] | None = None,
) -> Any:
    url = f"{API_BASE}{path}"
    if query:
        clean_query = {key: value for key, value in query.items() if value is not None}
        if clean_query:
            url += "?" + urlencode(clean_query, doseq=True)
    data = json.dumps(body, ensure_ascii=False).encode("utf-8") if body is not None else None
    headers = {
        "Accept": "application/json",
        "xi-api-key": api_key(),
        "User-Agent": "skills-library/elevenlabs-motion",
    }
    if data is not None:
        headers["Content-Type"] = "application/json"
    request = Request(url, data=data, headers=headers, method=method)
    try:
        with urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            detail = json.loads(raw)
            message = json.dumps(detail, ensure_ascii=False)
        except json.JSONDecodeError:
            message = raw[:500]
        raise ApiError(f"ElevenLabs respondeu HTTP {exc.code}: {message}") from None
    except URLError as exc:
        raise ApiError(f"Falha de rede ao acessar ElevenLabs: {exc.reason}") from None


def word_timings(alignment: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not alignment:
        return []
    characters = alignment.get("characters") or []
    starts = alignment.get("character_start_times_seconds") or []
    ends = alignment.get("character_end_times_seconds") or []
    size = min(len(characters), len(starts), len(ends))
    text = "".join(str(char) for char in characters[:size])
    words: list[dict[str, Any]] = []
    for match in re.finditer(r"\S+", text):
        first = match.start()
        last = match.end() - 1
        words.append(
            {
                "text": match.group(0),
                "start_seconds": starts[first],
                "end_seconds": ends[last],
            }
        )
    return words


def ensure_new(paths: list[Path], force: bool) -> None:
    existing = [str(path) for path in paths if path.exists()]
    if existing and not force:
        raise ValueError("Destino ja existe; use --force para sobrescrever: " + ", ".join(existing))


def command_status(args: argparse.Namespace) -> None:
    data = request_json("GET", "/v1/user/subscription", timeout=args.timeout)
    result = {
        "tier": data.get("tier"),
        "status": data.get("status"),
        "character_count": data.get("character_count"),
        "character_limit": data.get("character_limit"),
        "next_reset_unix": data.get("next_character_count_reset_unix"),
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


def command_models(args: argparse.Namespace) -> None:
    data = request_json("GET", "/v1/models", timeout=args.timeout)
    models = []
    for model in data:
        if model.get("can_do_text_to_speech"):
            models.append(
                {
                    "model_id": model.get("model_id"),
                    "name": model.get("name"),
                    "languages": len(model.get("languages") or []),
                    "max_characters_request_free_user": model.get("max_characters_request_free_user"),
                    "max_characters_request_subscribed_user": model.get("max_characters_request_subscribed_user"),
                }
            )
    print(json.dumps({"models": models}, ensure_ascii=False, indent=2))


def command_voices(args: argparse.Namespace) -> None:
    query = {
        "page_size": args.page_size,
        "include_total_count": "false",
        "search": args.search,
        "language": args.language,
        "gender": args.gender,
        "use_cases": args.use_case,
    }
    data = request_json("GET", "/v2/voices", timeout=args.timeout, query=query)
    voices = []
    for voice in data.get("voices", []):
        labels = voice.get("labels") or {}
        voices.append(
            {
                "voice_id": voice.get("voice_id"),
                "name": voice.get("name"),
                "category": voice.get("category"),
                "language": labels.get("language"),
                "accent": labels.get("accent"),
                "gender": labels.get("gender"),
                "use_case": labels.get("use_case"),
            }
        )
    result = {"voices": voices, "has_more": data.get("has_more", False)}
    print(json.dumps(result, ensure_ascii=False, indent=2))


def read_text(args: argparse.Namespace) -> str:
    if args.text_file:
        text = Path(args.text_file).read_text(encoding="utf-8-sig").strip()
    else:
        text = (args.text or "").strip()
    if not text:
        raise ValueError("A locucao esta vazia.")
    return text


def command_generate(args: argparse.Namespace) -> None:
    text = read_text(args)
    voice_id = (args.voice_id or os.getenv("ELEVENLABS_VOICE_ID", "")).strip()
    if not voice_id:
        raise ValueError("Informe --voice-id ou configure ELEVENLABS_VOICE_ID.")
    model = (args.model or os.getenv("ELEVENLABS_MODEL_ID") or DEFAULT_MODEL).strip()
    output = Path(args.output).expanduser().resolve()
    timings = (
        Path(args.timings_output).expanduser().resolve()
        if args.timings_output
        else output.with_name(f"{output.stem}-timings.json")
    )
    ensure_new([output, timings], args.force)

    summary = {
        "voice_id": voice_id,
        "model_id": model,
        "language_code": args.language,
        "output_format": args.output_format,
        "characters": len(text),
        "audio_output": str(output),
        "timings_output": str(timings),
    }
    if args.dry_run:
        print(json.dumps({"dry_run": True, **summary}, ensure_ascii=False, indent=2))
        return

    body: dict[str, Any] = {"text": text, "model_id": model}
    if args.language and model != "eleven_multilingual_v2":
        body["language_code"] = args.language
    if args.seed is not None:
        body["seed"] = args.seed

    data = request_json(
        "POST",
        f"/v1/text-to-speech/{voice_id}/with-timestamps",
        timeout=args.timeout,
        query={"output_format": args.output_format},
        body=body,
    )
    encoded = data.get("audio_base64")
    if not encoded:
        raise ApiError("A resposta nao trouxe audio_base64.")
    try:
        audio = base64.b64decode(encoded, validate=True)
    except (ValueError, TypeError) as exc:
        raise ApiError("A resposta trouxe audio_base64 invalido.") from exc

    alignment = data.get("normalized_alignment") or data.get("alignment")
    ends = (alignment or {}).get("character_end_times_seconds") or []
    metadata = {
        **summary,
        "duration_seconds": max(ends) if ends else None,
        "words": word_timings(alignment),
        "alignment": data.get("alignment"),
        "normalized_alignment": data.get("normalized_alignment"),
    }

    output.parent.mkdir(parents=True, exist_ok=True)
    timings.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(audio)
    timings.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    result = {"ok": True, **summary, "duration_seconds": metadata["duration_seconds"]}
    print(json.dumps(result, ensure_ascii=False, indent=2))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--env-file", help="Caminho opcional para o .env")
    parser.add_argument("--timeout", type=float, default=60.0, help="Timeout HTTP em segundos")
    subparsers = parser.add_subparsers(dest="command", required=True)

    status = subparsers.add_parser("status", help="Mostra plano e consumo sem expor a chave")
    status.set_defaults(func=command_status)

    models = subparsers.add_parser("models", help="Lista modelos disponiveis para TTS")
    models.set_defaults(func=command_models)

    voices = subparsers.add_parser("voices", help="Busca vozes disponiveis")
    voices.add_argument("--search")
    voices.add_argument("--language", action="append")
    voices.add_argument("--gender")
    voices.add_argument("--use-case", action="append")
    voices.add_argument("--page-size", type=int, choices=range(1, 101), default=20, metavar="1..100")
    voices.set_defaults(func=command_voices)

    generate = subparsers.add_parser("generate", help="Gera audio e JSON de timings")
    source = generate.add_mutually_exclusive_group(required=True)
    source.add_argument("--text")
    source.add_argument("--text-file")
    generate.add_argument("--voice-id")
    generate.add_argument("--output", required=True)
    generate.add_argument("--timings-output")
    generate.add_argument("--model")
    generate.add_argument("--language", default="pt")
    generate.add_argument("--output-format", default=DEFAULT_FORMAT)
    generate.add_argument("--seed", type=int, choices=range(0, 4294967296), metavar="0..4294967295")
    generate.add_argument("--dry-run", action="store_true")
    generate.add_argument("--force", action="store_true")
    generate.set_defaults(func=command_generate)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        load_env(find_env_file(args.env_file))
        args.func(args)
        return 0
    except (ApiError, OSError, ValueError) as exc:
        print(f"erro: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
