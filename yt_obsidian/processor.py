import os

from openai import OpenAI


class TranscriptProcessor:
    def __init__(self) -> None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY is missing. Add it to your .env file.")

        base_url = os.getenv("OPENAI_BASE_URL")
        if not base_url:
            raise ValueError("OPENAI_BASE_URL is missing. Add it to your .env file.")

        model = os.getenv("OPENAI_MODEL")
        if not model:
            raise ValueError("OPENAI_MODEL is missing. Add it to your .env file.")

        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model

    def to_obsidian_markdown(self, transcript: str, title: str | None = None) -> str:
        response = self.client.responses.create(
            model=self.model,
            instructions=self._instructions(title),
            input=transcript,
        )
        return response.output_text.strip()

    def _instructions(self, title: str | None) -> str:
        title_rule = (
            f"Start with a single H1 heading exactly like this: # {title}\n"
            if title
            else "Do not add an H1 title unless the transcript clearly states one.\n"
        )

        return (
            "You prepare YouTube transcripts for an Obsidian vault.\n"
            f"{title_rule}"
            "Add useful Markdown H2 subheadings using the exact '## ' syntax.\n"
            "Keep the lecture content faithful and complete.\n"
            "Lightly repair punctuation and paragraph breaks only when it improves readability.\n"
            "Remove only non-course material from the beginning or end, such as greetings, "
            "channel intro fluff, subscribe reminders, thanks, and sign-offs.\n"
            "Do not summarize, shorten, add unsupported facts, or wrap the result in code fences.\n"
            "Return only Markdown."
        )
