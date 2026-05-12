# yt-obsidian

A tiny, beginner-friendly Python CLI that turns YouTube transcripts into
Obsidian-ready Markdown.

It does only a few things:

- fetch transcripts from YouTube (multi-language)
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

Fetch a transcript (raw only by default):

```bash
python main.py fetch "https://www.youtube.com/watch?v=Unzc731iCUY" --title "How to Speak"
```

Fetch and also create an Obsidian Markdown note:

```bash
python main.py fetch "Unzc731iCUY" --process --title "How to Speak"
```

Fetch a non-English transcript by language priority:

```bash
python main.py fetch "Unzc731iCUY" --lang "ko,en" --title "How to Speak"
```

List available transcript languages:

```bash
python main.py fetch "Unzc731iCUY" --list-languages
```

Process an existing transcript file:

```bash
python main.py process output/how-to-speak.raw.txt --title "How to Speak"
```

Chunk long transcripts or cap length to control cost:

```bash
python main.py process output/how-to-speak.raw.txt --chunk-size 8000 --max-chars 60000
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
