"""Tests for model metadata and hardware recommendation heuristics."""

import unittest

from nightygo.model_center import (
    HardwareProfile,
    apply_model_argument,
    classify_model,
    parse_model_catalog,
    recommend_tier,
)


class ModelCatalogTests(unittest.TestCase):
    def test_parses_only_official_gz_network_downloads(self) -> None:
        html = """
        <table><tr><th>Name</th><th>Uploaded At</th><th>Elo Rating</th>
        <th>Network File</th><th>Raw Checkpoint</th></tr>
        <tr><td>kata1-tf3-b10c512-s3203M</td><td>2026-08-25</td>
        <td>14174 ± 12</td><td><a href="https://media.katagotraining.org/uploaded/networks/models/kata1/kata1-tf3-b10c512-s3203M.bin.gz">Download</a></td>
        <td><a href="https://media.katagotraining.org/checkpoint.zip">Download</a></td></tr>
        <tr><td>kata1-b28c512nbt-s1325</td><td>2026-06-07</td><td>14111</td>
        <td><a href="https://example.invalid/model.bin.gz">Download</a></td><td></td></tr></table>
        """
        models = parse_model_catalog(html)
        self.assertEqual(len(models), 1)
        self.assertEqual(models[0].tier, "strong")
        self.assertTrue(models[0].download_url.endswith(".bin.gz"))

    def test_classifies_architectures(self) -> None:
        self.assertEqual(classify_model("kata1-b15c192-s100"), "light")
        self.assertEqual(classify_model("kata1-b18c384nbt-s100"), "balanced")
        self.assertEqual(classify_model("kata1-b28c512nbt-s100"), "strong")
        self.assertEqual(classify_model("kata1-tf3-b11c768-s100"), "maximum")

    def test_recommendation_uses_current_ram_and_gpu_memory(self) -> None:
        cpu = HardwareProfile(total_ram_bytes=32 * 1024**3, available_ram_bytes=10 * 1024**3)
        gpu = HardwareProfile(
            total_ram_bytes=32 * 1024**3,
            available_ram_bytes=10 * 1024**3,
            gpu_name="Test GPU",
            gpu_total_bytes=12 * 1024**3,
            gpu_available_bytes=9 * 1024**3,
        )
        low_memory = HardwareProfile(8 * 1024**3, 2 * 1024**3)
        self.assertEqual(recommend_tier(cpu), "balanced")
        self.assertEqual(recommend_tier(gpu), "maximum")
        self.assertEqual(recommend_tier(low_memory), "light")

    def test_selected_model_is_added_or_replaces_existing_argument(self) -> None:
        self.assertEqual(
            apply_model_argument(("gtp", "-config", "engine.cfg"), "/models/go.bin.gz"),
            ("gtp", "-config", "engine.cfg", "-model", "/models/go.bin.gz"),
        )
        self.assertEqual(
            apply_model_argument(("gtp", "-model", "old.bin.gz"), "new.bin.gz"),
            ("gtp", "-model", "new.bin.gz"),
        )


if __name__ == "__main__":
    unittest.main()
