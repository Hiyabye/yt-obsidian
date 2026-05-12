import re
from urllib.parse import parse_qs, urlparse

YOUTUBE_ID_RE = re.compile(r"^[A-Za-z0-9_-]{11}$")


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


class YouTubeTranscriptService:
    def __init__(self) -> None:
        from youtube_transcript_api import YouTubeTranscriptApi

        self.client = YouTubeTranscriptApi()

    def fetch_english_transcript(self, video_id: str) -> str:
        transcript = self.client.fetch(video_id, languages=["en", "en-US", "en-GB"])
        return "\n".join(snippet.text for snippet in transcript)
