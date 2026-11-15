"""Tests for docs/sources_seed.yml and Session 2 housekeeping (stdlib only, no network)."""
import json
import re
import tomllib
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SEED = ROOT / "docs" / "sources_seed.yml"
KEYS = ["doc_id", "title", "publisher", "year", "kind", "url", "item_uuid",
        "bitstream_uuid", "local_filename", "discovered_from"]


REGULATION_KEYS = ["doc_id", "title", "publisher", "year", "kind", "url", "item_uuid",
                   "bitstream_uuid", "local_filename", "discovered_from",
                   "retrieval_method", "retrieved_date", "provenance_note"]


def read_seed(path):
    """Minimal reader for the seed format: `  - key: <json>` / `    key: <json>`."""
    entries = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.lstrip().startswith("#") or line.startswith("documents:"):
            continue
        m = re.match(r"^(  - |    )([a-z_]+): (.*)$", line)
        if not m:
            raise ValueError(f"unparseable seed line: {line!r}")
        if m.group(1) == "  - ":
            entries.append({})
        entries[-1][m.group(2)] = json.loads(m.group(3))
    return entries


class TestHousekeeping(unittest.TestCase):
    def test_1_gitattributes(self):
        p = ROOT / ".gitattributes"
        self.assertTrue(p.is_file())
        self.assertIn("* text=auto eol=lf", p.read_text(encoding="utf-8").splitlines())

    def test_2_pyproject(self):
        with open(ROOT / "pyproject.toml", "rb") as fh:
            deps = tomllib.load(fh)["project"]["dependencies"]
        self.assertIn("pandas>=3.1", deps)
        self.assertIn("numpy>=2.5", deps)
        names = [re.split(r"[<>=!~ ]", d, maxsplit=1)[0] for d in deps]
        self.assertIn("requests", names)
        self.assertIn("beautifulsoup4", names)
        self.assertFalse([d for d in deps if "==" in d])

    def test_3_lockfile_rename(self):
        self.assertFalse((ROOT / "requirements.txt").exists())
        self.assertTrue((ROOT / "requirements-lock.txt").is_file())

    def test_8_lockfile_utf8_comment_first(self):
        raw = (ROOT / "requirements-lock.txt").read_bytes()
        text = raw.decode("utf-8")
        self.assertNotIn(b"\x00", raw)
        self.assertTrue(text.splitlines()[0].startswith("#"))


@unittest.skipUnless(SEED.is_file(), "docs/sources_seed.yml absent")
class TestSeed(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.entries = read_seed(SEED)

    def test_4_keys_and_nulls(self):
        for e in self.entries:
            if e["kind"] == "regulation":
                for k in REGULATION_KEYS:
                    self.assertIn(k, e, e["doc_id"])
                    if k not in ("item_uuid", "bitstream_uuid"):
                        self.assertIsNotNone(e[k], f"{e['doc_id']}.{k}")
                self.assertIsNone(e["item_uuid"], e["doc_id"])
                self.assertIsNone(e["bitstream_uuid"], e["doc_id"])
                continue
            self.assertEqual(list(e), KEYS, e.get("doc_id"))
            for k, v in e.items():
                if k != "year":
                    self.assertIsNotNone(v, f"{e['doc_id']}.{k}")

    def test_5_urls_and_uuids(self):
        uuid = re.compile(r"^[0-9a-f-]{36}$")
        for e in self.entries:
            self.assertTrue(e["url"].startswith("https://"), e["doc_id"])
            if e["kind"] != "regulation":
                self.assertTrue("/bitstreams/" in e["url"] or e["url"].endswith(".pdf"), e["doc_id"])
                self.assertRegex(e["item_uuid"], uuid)
                self.assertRegex(e["bitstream_uuid"], uuid)

    def test_6_unique(self):
        ids = [e["doc_id"] for e in self.entries]
        self.assertEqual(len(ids), len(set(ids)))

    def test_7_counts(self):
        n = sum(e["kind"] == "factsheet" for e in self.entries)
        print(f"n_factsheets = {n}")
        self.assertGreaterEqual(n, 30)
        self.assertEqual(sum(e["doc_id"] == "report_main" for e in self.entries), 1)

    def test_10_unique_uuids(self):
        for key in ("item_uuid", "bitstream_uuid"):
            vals = [e[key] for e in self.entries if e[key] is not None]
            self.assertEqual(len(vals), len(set(vals)), key)

    def test_9_unique_filenames(self):
        fns = [e["local_filename"] for e in self.entries]
        self.assertEqual(len(fns), len(set(fns)))

    def test_11_unique_urls(self):
        urls = [e["url"] for e in self.entries]
        self.assertEqual(len(urls), len(set(urls)))


if __name__ == "__main__":
    unittest.main()
