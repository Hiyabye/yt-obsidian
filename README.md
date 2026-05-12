# yt-obsidian

A tiny, beginner-friendly Python CLI that turns YouTube transcripts into
Obsidian-ready Markdown.

It does only a few things:

- fetch transcripts from YouTube (multi-language)
- save the raw transcript to `output/`
- convert a transcript into Markdown with `##` headings using OpenAI or Google GenAI

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Fill in `.env` (required for processing). OpenAI remains the default:

```bash
AI_PROVIDER=openai
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-5.4-mini
OPENAI_BASE_URL=https://example.com/v1
```

For Google GenAI, use:

```bash
AI_PROVIDER=genai
GENAI_API_KEY=your_gemini_api_key_here
GENAI_MODEL=gemini-3.1-flash-lite
```

`GEMINI_API_KEY` and `GOOGLE_API_KEY` are also accepted for GenAI.

## Usage

Fetch a transcript (raw only by default):

```bash
python3 main.py fetch "https://www.youtube.com/watch?v=Unzc731iCUY" --title "How to Speak"
```

Fetch and also create an Obsidian Markdown note:

```bash
python3 main.py fetch "Unzc731iCUY" --process --title "How to Speak"
```

Fetch a non-English transcript by language priority:

```bash
python3 main.py fetch "Unzc731iCUY" --lang "ko,en" --title "How to Speak"
```

List available transcript languages:

```bash
python3 main.py fetch "Unzc731iCUY" --list-languages
```

Process an existing transcript file:

```bash
python3 main.py process output/how-to-speak.raw.txt --title "How to Speak"
```

Process with Google GenAI:

```bash
python3 main.py process output/how-to-speak.raw.txt --provider genai --title "How to Speak"
```

Chunk long transcripts or cap length to control cost:

```bash
python3 main.py process output/how-to-speak.raw.txt --chunk-size 8000 --max-chars 60000
```

## Project Layout

```text
yt_obsidian/
  cli.py          # command-line interface
  files.py        # small file helpers
  processor.py    # OpenAI/Google GenAI Markdown formatting
  transcripts.py  # YouTube transcript fetching and URL parsing
tests/
  test_transcripts.py
main.py           # thin CLI entrypoint
```

## Verify

```bash
python3 -m unittest discover
```

## License

MIT
