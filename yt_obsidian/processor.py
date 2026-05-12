import os

from openai import OpenAI


def apply_max_chars(text: str, max_chars: int | None) -> str:
    if max_chars is None:
        return text
    if max_chars <= 0:
        raise ValueError("max_chars must be positive")
    if len(text) <= max_chars:
        return text

    trimmed = text[:max_chars]
    newline_pos = trimmed.rfind("\n")
    if newline_pos > 0:
        trimmed = trimmed[:newline_pos]
    return trimmed.rstrip()


def split_text(text: str, chunk_size: int) -> list[str]:
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    if not text.strip():
        return []
    if len(text) <= chunk_size:
        return [text.strip()]

    chunks: list[str] = []
    start = 0
    text_len = len(text)
    while start < text_len:
        end = min(text_len, start + chunk_size)
        newline_pos = text.rfind("\n", start, end)
        if newline_pos > start:
            end = newline_pos
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start = end + 1
    return chunks


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

    def to_obsidian_markdown(
        self,
        transcript: str,
        title: str | None = None,
        chunk_size: int | None = None,
        max_chars: int | None = None,
    ) -> str:
        transcript = apply_max_chars(transcript, max_chars)
        chunks = (
            split_text(transcript, chunk_size) if chunk_size else [transcript]
        )
        if not chunks:
            return ""

        outputs: list[str] = []
        total_parts = len(chunks)
        for index, chunk in enumerate(chunks):
            allow_title = index == 0
            part_number = index + 1
            response = self.client.responses.create(
                model=self.model,
                instructions=self._instructions(
                    title,
                    allow_title=allow_title,
                    part_number=part_number,
                    total_parts=total_parts,
                ),
                input=chunk,
            )
            outputs.append(response.output_text.strip())

        return "\n\n".join(output for output in outputs if output)

    def _instructions(
        self,
        title: str | None,
        allow_title: bool = True,
        part_number: int | None = None,
        total_parts: int | None = None,
    ) -> str:
        if not allow_title:
            title_rule = "Do not add or repeat an H1 title.\n"
        else:
            title_rule = (
                f"Start with a single H1 heading exactly like this: # {title}\n"
                if title
                else "Do not add an H1 title unless the transcript clearly states one.\n"
            )

        part_rule = ""
        if part_number is not None and total_parts is not None and total_parts > 1:
            part_rule = (
                f"This is part {part_number} of {total_parts}. "
                "Continue seamlessly without repeating earlier content.\n"
            )

        return (
            "You prepare YouTube transcripts for an Obsidian vault.\n"
            f"{title_rule}"
            f"{part_rule}"
            "Add useful Markdown H2 subheadings using the exact '## ' syntax.\n"
            "Keep the lecture content faithful and complete.\n"
            "Lightly repair punctuation and paragraph breaks only when it improves readability.\n"
            "Remove only non-course material from the beginning or end, such as greetings, "
            "channel intro fluff, subscribe reminders, thanks, and sign-offs.\n"
            "Do not summarize, shorten, add unsupported facts, or wrap the result in code fences.\n"
            "Return only Markdown."
        )
