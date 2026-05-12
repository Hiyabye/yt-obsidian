import unittest

from yt_obsidian.processor import apply_max_chars, split_text


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


if __name__ == "__main__":
    unittest.main()
