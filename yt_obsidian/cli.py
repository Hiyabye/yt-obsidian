import argparse
import sys
from pathlib import Path

from dotenv import load_dotenv

from yt_obsidian.files import read_text, write_text
from yt_obsidian.processor import SUPPORTED_PROVIDERS, TranscriptProcessor
from yt_obsidian.transcripts import (
    DEFAULT_LANGUAGE_CODES,
    YouTubeTranscriptService,
    parse_language_codes,
    parse_video_id,
    slugify,
)

load_dotenv()


def log(message: str, quiet: bool) -> None:
    if not quiet:
        print(message, file=sys.stderr)


def require_positive(name: str, value: int | None) -> None:
    if value is not None and value <= 0:
        raise ValueError(f"{name} must be positive")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="yt-obsidian",
        description="Convert YouTube transcripts into Obsidian-ready notes.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    fetch = subparsers.add_parser(
        "fetch",
        help="Fetch a YouTube transcript and optionally process it.",
    )
    fetch.add_argument("video", help="YouTube video URL or 11-character video id.")
    fetch.add_argument("--title", help="Title to use for the Obsidian note.")
    fetch.add_argument(
        "--output-dir", default="output", help="Directory for generated files."
    )
    fetch.add_argument(
        "--lang",
        default=",".join(DEFAULT_LANGUAGE_CODES),
        help="Comma-separated language codes in priority order (or 'auto').",
    )
    fetch.add_argument(
        "--list-languages",
        action="store_true",
        help="List available transcript languages for the video and exit.",
    )
    fetch.add_argument(
        "--raw-only",
        action="store_true",
        help="Save only the raw transcript (default).",
    )
    fetch.add_argument(
        "--process",
        action="store_true",
        help="Also generate an Obsidian Markdown note.",
    )
    fetch.add_argument(
        "--provider",
        choices=sorted(SUPPORTED_PROVIDERS),
        help="AI provider for processing. Defaults to AI_PROVIDER or openai.",
    )
    fetch.add_argument(
        "--chunk-size",
        type=int,
        help="Max characters per AI request; enables chunking.",
    )
    fetch.add_argument(
        "--max-chars",
        type=int,
        help="Hard cap on transcript length to reduce cost.",
    )
    fetch.add_argument(
        "--quiet", action="store_true", help="Suppress progress messages."
    )

    process = subparsers.add_parser(
        "process",
        help="Process an existing transcript text file.",
    )
    process.add_argument(
        "input_file", type=Path, help="Raw transcript file to process."
    )
    process.add_argument("--title", help="Title to use for the Obsidian note.")
    process.add_argument("--output", type=Path, help="Markdown output path.")
    process.add_argument(
        "--provider",
        choices=sorted(SUPPORTED_PROVIDERS),
        help="AI provider for processing. Defaults to AI_PROVIDER or openai.",
    )
    process.add_argument(
        "--chunk-size",
        type=int,
        help="Max characters per AI request; enables chunking.",
    )
    process.add_argument(
        "--max-chars",
        type=int,
        help="Hard cap on transcript length to reduce cost.",
    )
    process.add_argument(
        "--quiet", action="store_true", help="Suppress progress messages."
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    try:
        if args.command == "fetch":
            fetch_command(args)
        elif args.command == "process":
            process_command(args)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc


def fetch_command(args: argparse.Namespace) -> None:
    require_positive("chunk_size", args.chunk_size)
    require_positive("max_chars", args.max_chars)
    video_id = parse_video_id(args.video)
    title = args.title or video_id
    slug = slugify(title, fallback=video_id)
    output_dir = Path(args.output_dir)

    if args.raw_only and args.process:
        raise ValueError("Use only one of --raw-only or --process.")

    service = YouTubeTranscriptService()
    if args.list_languages:
        log("Fetching available transcript languages...", args.quiet)
        languages = service.list_languages(video_id)
        if not languages:
            print("No transcripts available.")
            return
        for language in languages:
            kind = "generated" if language.is_generated else "manual"
            print(f"{language.code}\t{language.name}\t{kind}")
        return

    lang_value = (args.lang or "").strip()
    if lang_value.lower() == "auto":
        language_codes: list[str] | None = None
        lang_label = "auto"
    else:
        language_codes = parse_language_codes(lang_value)
        lang_label = ", ".join(language_codes) if language_codes else "auto"

    log(f"Fetching transcript ({lang_label})...", args.quiet)
    transcript = service.fetch_transcript(video_id, language_codes)
    raw_path = output_dir / f"{slug}.raw.txt"
    write_text(raw_path, transcript)
    print(f"Raw transcript saved to: {raw_path}")

    if args.raw_only or not args.process:
        return

    processor = TranscriptProcessor(provider=args.provider)
    log(f"Processing transcript with {processor.provider}...", args.quiet)
    markdown = processor.to_obsidian_markdown(
        transcript,
        title=args.title,
        chunk_size=args.chunk_size,
        max_chars=args.max_chars,
        input_file=raw_path,
    )
    markdown_path = output_dir / f"{slug}.md"
    write_text(markdown_path, markdown)
    print(f"Obsidian Markdown saved to: {markdown_path}")


def process_command(args: argparse.Namespace) -> None:
    require_positive("chunk_size", args.chunk_size)
    require_positive("max_chars", args.max_chars)
    log(f"Reading transcript from {args.input_file}...", args.quiet)
    transcript = read_text(args.input_file)
    title = args.title or args.input_file.stem
    output_path = args.output or args.input_file.with_suffix(".md")

    processor = TranscriptProcessor(provider=args.provider)
    log(f"Processing transcript with {processor.provider}...", args.quiet)
    markdown = processor.to_obsidian_markdown(
        transcript,
        title=title,
        chunk_size=args.chunk_size,
        max_chars=args.max_chars,
        input_file=args.input_file,
    )
    write_text(output_path, markdown)
    print(f"Obsidian Markdown saved to: {output_path}")
