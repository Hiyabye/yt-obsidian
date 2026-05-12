import argparse
import sys
from pathlib import Path

from dotenv import load_dotenv

from yt_obsidian.files import read_text, write_text
from yt_obsidian.processor import TranscriptProcessor
from yt_obsidian.transcripts import (
    YouTubeTranscriptService,
    parse_video_id,
    slugify,
)

load_dotenv()


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
        "--raw-only", action="store_true", help="Save only the raw transcript."
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
    video_id = parse_video_id(args.video)
    title = args.title or video_id
    slug = slugify(title, fallback=video_id)
    output_dir = Path(args.output_dir)

    transcript = YouTubeTranscriptService().fetch_english_transcript(video_id)
    raw_path = output_dir / f"{slug}.raw.txt"
    write_text(raw_path, transcript)
    print(f"Raw transcript saved to: {raw_path}")

    if args.raw_only:
        return

    processor = TranscriptProcessor()
    markdown = processor.to_obsidian_markdown(
        transcript,
        title=args.title,
    )
    markdown_path = output_dir / f"{slug}.md"
    write_text(markdown_path, markdown)
    print(f"Obsidian Markdown saved to: {markdown_path}")


def process_command(args: argparse.Namespace) -> None:
    transcript = read_text(args.input_file)
    title = args.title or args.input_file.stem
    output_path = args.output or args.input_file.with_suffix(".md")

    processor = TranscriptProcessor()
    markdown = processor.to_obsidian_markdown(
        transcript,
        title=title,
    )
    write_text(output_path, markdown)
    print(f"Obsidian Markdown saved to: {output_path}")
