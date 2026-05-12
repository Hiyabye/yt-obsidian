import unittest

from yt_obsidian.transcripts import parse_video_id, slugify


class TranscriptUtilsTest(unittest.TestCase):
    def test_parse_video_id_accepts_id(self) -> None:
        self.assertEqual(parse_video_id("Unzc731iCUY"), "Unzc731iCUY")

    def test_parse_video_id_accepts_watch_url(self) -> None:
        self.assertEqual(
            parse_video_id("https://www.youtube.com/watch?v=Unzc731iCUY"),
            "Unzc731iCUY",
        )

    def test_parse_video_id_accepts_short_url(self) -> None:
        self.assertEqual(parse_video_id("https://youtu.be/Unzc731iCUY"), "Unzc731iCUY")

    def test_parse_video_id_rejects_invalid_value(self) -> None:
        with self.assertRaises(ValueError):
            parse_video_id("not a youtube url")

    def test_slugify(self) -> None:
        self.assertEqual(slugify("Your Success in Life"), "your-success-in-life")


if __name__ == "__main__":
    unittest.main()
