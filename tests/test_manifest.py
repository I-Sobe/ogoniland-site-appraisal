"""Tests for docs/sources_manifest.json and docs/SOURCES.md (stdlib only, no network)."""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "docs" / "sources_manifest.json"
SEED = ROOT / "docs" / "sources_seed.yml"
SOURCES_MD = ROOT / "docs" / "SOURCES.md"
RAW = ROOT / "data" / "raw"
SEED_KEYS = ["doc_id", "title", "publisher", "year", "kind", "url", "item_uuid",
             "bitstream_uuid", "local_filename", "discovered_from"]
EXTRA = ["sha256", "bytes", "retrieved_utc"]


def seed_entry_count():
    return sum(1 for l in SEED.read_text(encoding="utf-8").splitlines() if l.startswith("  - "))


@unittest.skipUnless(MANIFEST.is_file(), "docs/sources_manifest.json absent")
class TestManifest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(MANIFEST.read_text(encoding="utf-8"))
        cls.docs = cls.data["documents"]

    def test_1_fields(self):
        self.assertIn("generated_utc", self.data)
        for d in self.docs:
            for k in SEED_KEYS + EXTRA:
                self.assertIn(k, d, d.get("doc_id"))
                if k != "year":
                    self.assertIsNotNone(d[k], f"{d['doc_id']}.{k}")
        self.assertEqual([d["doc_id"] for d in self.docs], sorted(d["doc_id"] for d in self.docs))

    def test_2_hashes_and_sizes(self):
        for d in self.docs:
            self.assertRegex(d["sha256"], r"^[0-9a-f]{64}$")
            self.assertGreater(d["bytes"], 10240, d["doc_id"])

    def test_3_count_matches_seed(self):
        self.assertEqual(len(self.docs), seed_entry_count())

    def test_4_unique(self):
        for k in ("doc_id", "local_filename", "item_uuid", "bitstream_uuid"):
            vals = [d[k] for d in self.docs]
            self.assertEqual(len(vals), len(set(vals)), k)

    def test_5_sources_md_rows(self):
        rows = [l for l in SOURCES_MD.read_text(encoding="utf-8").splitlines()
                if l.startswith("| ") and not l.startswith("| doc_id")]
        self.assertEqual(len(rows), len(self.docs))

    def test_6_files_exist(self):
        for d in self.docs:
            self.assertTrue((RAW / d["local_filename"]).is_file(), d["local_filename"])


if __name__ == "__main__":
    unittest.main()
