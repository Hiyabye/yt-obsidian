# yt-obsidian

A tiny, beginner-friendly Python CLI that turns YouTube transcripts into
Obsidian-ready Markdown.

It does only a few things:

- fetch English transcripts from YouTube
- save the raw transcript to `output/`
- convert a transcript into Markdown with `##` headings

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Fill in `.env` (required for processing):

```bash
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-5.4-mini
OPENAI_BASE_URL=https://example.com/v1
```

## Usage

Fetch a transcript and create an Obsidian Markdown note:

```bash
python main.py fetch "https://www.youtube.com/watch?v=Unzc731iCUY" --title "Lecture 1"
```

Fetch only the raw English transcript:

```bash
python main.py fetch "Unzc731iCUY" --raw-only
```

Process an existing transcript file:

```bash
python main.py process output/lecture-1.raw.txt --title "Lecture 1"
```

## Project Layout

```text
yt_obsidian/
  cli.py          # command-line interface
  files.py        # small file helpers
  processor.py    # OpenAI Markdown formatting
  transcripts.py  # YouTube transcript fetching and URL parsing
tests/
  test_transcripts.py
main.py           # thin CLI entrypoint
```

## Verify

```bash
python -m unittest discover
```

## License

MIT
