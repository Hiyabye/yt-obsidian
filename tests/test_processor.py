import unittest
from pathlib import Path
from unittest.mock import patch

from yt_obsidian.processor import (
    TranscriptProcessor,
    apply_max_chars,
    normalize_provider,
    split_text,
)


class FakeBackend:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    def generate(
        self,
        instructions: str,
        transcript: str,
        input_file: Path | None = None,
    ) -> str:
        self.calls.append(
            {
                "instructions": instructions,
                "transcript": transcript,
                "input_file": input_file,
            }
        )
        return "markdown"


class ProcessorUtilsTest(unittest.TestCase):
    def test_apply_max_chars_no_limit(self) -> None:
        text = "line1\nline2\nline3"
        self.assertEqual(apply_max_chars(text, None), text)

    def test_apply_max_chars_trims_on_newline(self) -> None:
        text = "line1\nline2\nline3"
        self.assertEqual(apply_max_chars(text, 8), "line1")

    def test_split_text_respects_chunk_size(self) -> None:
        text = "aaa\nbbb\nccc\n"
        chunks = split_text(text, 7)
        self.assertEqual(chunks, ["aaa", "bbb", "ccc"])
        self.assertTrue(all(len(chunk) <= 7 for chunk in chunks))

    def test_normalize_provider_defaults_to_openai(self) -> None:
        with patch.dict("os.environ", {}, clear=True):
            self.assertEqual(normalize_provider(), "openai")

    def test_normalize_provider_reads_environment(self) -> None:
        with patch.dict("os.environ", {"AI_PROVIDER": " genai "}):
            self.assertEqual(normalize_provider(), "genai")

    def test_normalize_provider_rejects_unknown_value(self) -> None:
        with self.assertRaises(ValueError):
            normalize_provider("unknown")

    def test_genai_whole_file_processing_passes_input_file(self) -> None:
        backend = FakeBackend()
        processor = TranscriptProcessor.__new__(TranscriptProcessor)
        processor.provider = "genai"
        processor.backend = backend

        input_file = Path("lecture.txt")
        processor.to_obsidian_markdown("raw transcript", input_file=input_file)

        self.assertEqual(backend.calls[0]["input_file"], input_file)

    def test_genai_chunked_processing_uses_text_chunks(self) -> None:
        backend = FakeBackend()
        processor = TranscriptProcessor.__new__(TranscriptProcessor)
        processor.provider = "genai"
        processor.backend = backend

        processor.to_obsidian_markdown(
            "aaa\nbbb\nccc", chunk_size=7, input_file=Path("lecture.txt")
        )

        self.assertEqual(
            [call["input_file"] for call in backend.calls], [None, None, None]
        )
        self.assertEqual(
            [call["transcript"] for call in backend.calls], ["aaa", "bbb", "ccc"]
        )


if __name__ == "__main__":
    unittest.main()
