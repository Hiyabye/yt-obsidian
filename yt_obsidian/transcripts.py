import re
from dataclasses import dataclass
from urllib.parse import parse_qs, urlparse

YOUTUBE_ID_RE = re.compile(r"^[A-Za-z0-9_-]{11}$")
DEFAULT_LANGUAGE_CODES = ["en", "en-US", "en-GB"]


def parse_video_id(source: str) -> str:
    """Accept a YouTube video id or common YouTube URL formats."""
    value = source.strip()
    if YOUTUBE_ID_RE.fullmatch(value):
        return value

    parsed = urlparse(value)
    host = parsed.netloc.lower().removeprefix("www.")

    if host in {"youtube.com", "m.youtube.com"}:
        if parsed.path == "/watch":
            video_id = parse_qs(parsed.query).get("v", [""])[0]
            if YOUTUBE_ID_RE.fullmatch(video_id):
                return video_id

        parts = [part for part in parsed.path.split("/") if part]
        if len(parts) >= 2 and parts[0] in {"embed", "shorts", "live"}:
            if YOUTUBE_ID_RE.fullmatch(parts[1]):
                return parts[1]

    if host == "youtu.be":
        video_id = parsed.path.strip("/").split("/")[0]
        if YOUTUBE_ID_RE.fullmatch(video_id):
            return video_id

    raise ValueError(f"Could not find a YouTube video id in: {source}")


def slugify(value: str, fallback: str = "transcript") -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.lower()).strip("-")
    return slug or fallback


def parse_language_codes(value: str) -> list[str]:
    codes = [code.strip() for code in value.split(",")]
    return [code for code in codes if code]


@dataclass(frozen=True)
class TranscriptLanguage:
    code: str
    name: str
    is_generated: bool


class YouTubeTranscriptService:
    def __init__(self) -> None:
        from youtube_transcript_api import YouTubeTranscriptApi

        self.client = YouTubeTranscriptApi()

    def list_languages(self, video_id: str) -> list[TranscriptLanguage]:
        transcripts = self.client.list_transcripts(video_id)
        languages: list[TranscriptLanguage] = []
        for transcript in transcripts:
            languages.append(
                TranscriptLanguage(
                    code=transcript.language_code,
                    name=transcript.language,
                    is_generated=transcript.is_generated,
                )
            )
        return languages

    def fetch_transcript(self, video_id: str, language_codes: list[str] | None) -> str:
        from youtube_transcript_api import NoTranscriptFound

        try:
            if language_codes:
                transcript = self.client.fetch(video_id, languages=language_codes)
            else:
                transcript = self.client.fetch(video_id)
        except NoTranscriptFound as exc:
            languages = self.list_languages(video_id)
            available = ", ".join(language.code for language in languages) or "none"
            requested = ", ".join(language_codes or []) or "auto"
            raise ValueError(
                "No transcript found for languages: "
                f"{requested}. Available: {available}"
            ) from exc

        return "\n".join(snippet.text for snippet in transcript)

    def fetch_english_transcript(self, video_id: str) -> str:
        return self.fetch_transcript(video_id, DEFAULT_LANGUAGE_CODES)
