import unittest

from nightygo.i18n import LANGUAGES, TRANSLATIONS, translate


class TranslationTests(unittest.TestCase):
    def test_every_source_has_all_five_locales(self):
        self.assertEqual(set(LANGUAGES), {"en", "zh_TW", "zh_CN", "ja", "ko"})
        for source, translations in TRANSLATIONS.items():
            with self.subTest(source=source):
                self.assertEqual(set(translations), set(LANGUAGES))

    def test_translates_core_interface_labels(self):
        self.assertEqual(translate("Game Tree", "zh_TW"), "棋譜樹")
        self.assertEqual(translate("Game Tree", "zh_CN"), "棋谱树")
        self.assertEqual(translate("Game Tree", "ja"), "棋譜ツリー")
        self.assertEqual(translate("Game Tree", "ko"), "기보 트리")

    def test_interpolates_values_after_translation(self):
        self.assertEqual(
            translate("Saved {path}", "ja", path="match.sgf"),
            "保存しました：match.sgf",
        )

    def test_unknown_text_and_unknown_language_fall_back_safely(self):
        self.assertEqual(translate("Uncatalogued text", "ko"), "Uncatalogued text")
        self.assertEqual(translate("Game Tree", "xx"), "Game Tree")


if __name__ == "__main__":
    unittest.main()
