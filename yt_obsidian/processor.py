import os
from pathlib import Path

SUPPORTED_PROVIDERS = {"openai", "genai"}


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
    def __init__(self, provider: str | None = None) -> None:
        self.provider = normalize_provider(provider)
        if self.provider == "openai":
            self.backend = OpenAIProcessorBackend()
        elif self.provider == "genai":
            self.backend = GenAIProcessorBackend()
        else:
            raise ValueError(f"Unsupported AI provider: {self.provider}")

    def to_obsidian_markdown(
        self,
        transcript: str,
        title: str | None = None,
        chunk_size: int | None = None,
        max_chars: int | None = None,
        input_file: Path | None = None,
    ) -> str:
        transcript = apply_max_chars(transcript, max_chars)
        chunks = split_text(transcript, chunk_size) if chunk_size else [transcript]
        if not chunks:
            return ""

        outputs: list[str] = []
        total_parts = len(chunks)
        for index, chunk in enumerate(chunks):
            allow_title = index == 0
            part_number = index + 1
            instructions = self._instructions(
                title,
                allow_title=allow_title,
                part_number=part_number,
                total_parts=total_parts,
            )
            use_input_file = (
                input_file is not None
                and self.provider == "genai"
                and chunk_size is None
                and max_chars is None
            )
            output = self.backend.generate(
                instructions=instructions,
                transcript=chunk,
                input_file=input_file if use_input_file else None,
            )
            outputs.append(output.strip())

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
            "You format YouTube transcripts for an Obsidian vault. This is formatting, not summarizing.\n"
            f"{title_rule}"
            f"{part_rule}"
            "Add useful Markdown H2 subheadings using the exact '## ' syntax.\n"
            "Preserve every spoken sentence in order. Do not paraphrase, compress, or rewrite.\n"
            "Keep wording as-is; only fix punctuation and paragraph breaks when it improves readability.\n"
            "If something seems unclear or repetitive, keep it anyway.\n"
            "Remove only non-course material from the beginning or end, such as greetings, "
            "channel intro fluff, subscribe reminders, thanks, and sign-offs.\n"
            "Do not replace paragraphs with bullet summaries or shorter lists.\n"
            "DO NOT summarize, shorten, add unsupported facts, or wrap the result in code fences.\n"
            "Return only Markdown."
        )


def normalize_provider(provider: str | None = None) -> str:
    value = provider or os.getenv("AI_PROVIDER", "openai")
    normalized = value.strip().lower()
    if normalized not in SUPPORTED_PROVIDERS:
        supported = ", ".join(sorted(SUPPORTED_PROVIDERS))
        raise ValueError(f"AI provider must be one of: {supported}")
    return normalized


class OpenAIProcessorBackend:
    def __init__(self) -> None:
        from openai import OpenAI

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

    def generate(
        self,
        instructions: str,
        transcript: str,
        input_file: Path | None = None,
    ) -> str:
        response = self.client.responses.create(
            model=self.model,
            instructions=instructions,
            input=transcript,
        )
        return response.output_text


class GenAIProcessorBackend:
    def __init__(self) -> None:
        from google import genai

        api_key = (
            os.getenv("GENAI_API_KEY")
            or os.getenv("GEMINI_API_KEY")
            or os.getenv("GOOGLE_API_KEY")
        )
        if not api_key:
            raise ValueError(
                "GENAI_API_KEY, GEMINI_API_KEY, or GOOGLE_API_KEY is missing. "
                "Add one to your .env file."
            )

        model = os.getenv("GENAI_MODEL")
        if not model:
            raise ValueError("GENAI_MODEL is missing. Add it to your .env file.")

        self.client = genai.Client(api_key=api_key)
        self.model = model

    def generate(
        self,
        instructions: str,
        transcript: str,
        input_file: Path | None = None,
    ) -> str:
        if input_file is not None:
            uploaded_file = self.client.files.upload(file=input_file)
            contents = [
                (
                    f"{instructions}\n\n"
                    "Convert the uploaded transcript file into Obsidian-ready Markdown."
                ),
                uploaded_file,
            ]
        else:
            contents = [instructions, transcript]

        response = self.client.models.generate_content(
            model=self.model,
            contents=contents,
        )
        if response.text is None:
            raise ValueError(
                "GenAI returned an empty response. Check the model and prompt settings."
            )
        return response.text
