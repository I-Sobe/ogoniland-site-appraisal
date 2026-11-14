"""Discover UNEP Ogoniland source-document URLs via the wedocs REST API.

Route: DSpace REST API (HAL JSON). Every endpoint after the API root is taken
from a ``_links`` entry returned by the server. Nothing is downloaded; only
metadata is read, and the result is written to a seed file for human review.

If the seed file already exists, existing entries are left untouched and only
records not already in it are appended (doc_id numbering continues).
"""
from __future__ import annotations

import datetime as _dt
import json
import re
import sys
import time
from pathlib import Path

import requests

ANCHOR_UI_URL = "https://wedocs.unep.org/items/52908b0a-b39a-4177-b37f-769980ef946d"
MAIN_REPORT_HANDLE = "20.500.11822/7947"
MAIN_REPORT_URL = "https://wedocs.unep.org/20.500.11822/7947"
# The only hardcoded endpoint: the API root, needed to resolve the anchor.
API_ROOT = "https://wedocs.unep.org/server/api"

USER_AGENT = "ogoniland-appraisal-source-discovery/0.1 (research; no downloads)"
SLEEP_SECONDS = 1.0
MIN_COLLECTION_ITEMS = 30
PAGE_SIZE = 100

_UUID_RE = re.compile(r"/items/([0-9a-f-]{36})")
_HASPART_RE = re.compile(r'href="[^"]+/handle/(20\.500\.11822/\d+)"')
_FS_RE = re.compile(r"fact ?sheet", re.I)
# Digit boundaries so that year ranges such as "2024-2029" do not match.
_CODE_RE = re.compile(r"(?<!\d)\d{3}-\d{3}(?!\d)")
_REDIRECTS = (301, 302, 303, 307, 308)

KEYS = ["doc_id", "title", "publisher", "year", "kind", "url", "item_uuid",
        "bitstream_uuid", "local_filename", "discovered_from"]


class DiscoveryStop(RuntimeError):
    """A spec stop rule fired; the message says which."""


class _Client:
    def __init__(self):
        self.s = requests.Session()
        self.s.headers.update({"User-Agent": USER_AGENT, "Accept": "application/hal+json"})
        self.n_requests = 0
        self._last = 0.0

    def _raw(self, url, **kw):
        wait = SLEEP_SECONDS - (time.monotonic() - self._last)
        if wait > 0:
            time.sleep(wait)
        r = self.s.get(url, timeout=60, **kw)
        self._last = time.monotonic()
        self.n_requests += 1
        return r

    def get(self, url):
        r = self._raw(url)
        if r.status_code != 200:
            raise DiscoveryStop(f"{url} returned HTTP {r.status_code}")
        if "json" not in r.headers.get("content-type", ""):
            raise DiscoveryStop(
                f"{url} did not return JSON (content-type "
                f"{r.headers.get('content-type')!r}); HTML browse fallback is not implemented")
        return r.json()

    def resolve_redirect(self, url):
        r = self._raw(url, allow_redirects=False)
        if r.status_code not in _REDIRECTS:
            raise DiscoveryStop(f"{url} did not redirect: HTTP {r.status_code}")
        return r.headers["location"]


def _year(item):
    vals = item.get("metadata", {}).get("dc.date.issued")
    m = re.match(r"\d{4}", vals[0]["value"] if vals else "")
    return int(m.group(0)) if m else None


def _item_page_url(item):
    return f"https://wedocs.unep.org/items/{item['uuid']}"


def _original_pdf(c, item):
    """Return (first PDF bitstream of the ORIGINAL bundle, number of PDFs)."""
    for b in c.get(item["_links"]["bundles"]["href"])["_embedded"]["bundles"]:
        if b.get("name") != "ORIGINAL":
            continue
        bss = c.get(b["_links"]["bitstreams"]["href"])["_embedded"]["bitstreams"]
        pdfs = sorted((x for x in bss if (x.get("name") or "").lower().endswith(".pdf")),
                      key=lambda x: x.get("sequenceId", 0))
        if pdfs:
            return pdfs[0], len(pdfs)
    raise DiscoveryStop("item has no PDF bitstream in its ORIGINAL bundle: "
                        f"{item.get('uuid')} {item.get('name')!r}")


def _is_factsheet(name):
    """Original (narrow) title filter; kept to report what the widening adds."""
    n = (name or "").lower()
    return "fact sheet" in n and "ogoniland" in n


def _is_report_part(name):
    n = (name or "").lower()
    return "ogoniland" in n and any(k in n for k in ("chapter", "appendices", "appendix", "map of"))


def _read_seed(path):
    entries = []
    for line in path.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^(  - |    )([a-z_]+): (.*)$", line)
        if m:
            if m.group(1) == "  - ":
                entries.append({})
            entries[-1][m.group(2)] = json.loads(m.group(3))
    return entries


def _widened_factsheets(c, coll_items, failures):
    """Title has 'fact sheet'/'factsheet' AND ('ogoniland' OR a NNN-NNN code in
    the title or the bitstream name). The bitstream is fetched only for items
    that pass the first clause but not the title part of the second."""
    out = []
    for i in coll_items:
        t = i.get("name") or ""
        if not _FS_RE.search(t):
            continue
        if "ogoniland" in t.lower() or _CODE_RE.search(t):
            out.append(i)
            continue
        try:
            bs, _ = _original_pdf(c, i)
        except DiscoveryStop as exc:
            failures.append(f"not matched; no ORIGINAL PDF to test bitstream name: {exc}")
            continue
        if _CODE_RE.search(bs.get("name") or ""):
            out.append(i)
    return out


def discover(output_path) -> dict:
    out_path = Path(output_path)
    existing = _read_seed(out_path) if out_path.is_file() else []
    have_uuids = {e["item_uuid"] for e in existing}
    used = {e["local_filename"] for e in existing}

    c = _Client()
    failures = []
    root = c.get(API_ROOT)

    # 1. resolve the anchor item; follow its owningCollection link
    uuid = _UUID_RE.search(ANCHOR_UI_URL).group(1)
    anchor = c.get(f"{root['_links']['items']['href']}/{uuid}")
    if "owningCollection" not in anchor.get("_links", {}):
        raise DiscoveryStop("anchor item has no owningCollection")
    coll = c.get(anchor["_links"]["owningCollection"]["href"])

    # 2. enumerate every item of that collection, paging until exhausted
    disc = c.get(root["_links"]["discover"]["href"])
    search = c.get(disc["_links"]["search"]["href"])
    url = f"{search['_links']['objects']['href']}?scope={coll['uuid']}&size={PAGE_SIZE}"
    coll_items = []
    while url:
        res = c.get(url)["_embedded"]["searchResult"]
        coll_items += [o["_embedded"]["indexableObject"] for o in res["_embedded"]["objects"]]
        url = res["_links"].get("next", {}).get("href")
    if len(coll_items) < MIN_COLLECTION_ITEMS:
        raise DiscoveryStop(f"owning collection yielded only {len(coll_items)} items")

    # The owning collection is a general collection (thousands of items), so
    # fact sheets are selected by title.
    narrow_uuids = {i["uuid"] for i in coll_items if _is_factsheet(i.get("name"))}
    factsheets = _widened_factsheets(c, coll_items, failures)
    widened_count = len(factsheets)

    # Main report record and its related parts, resolved through the 'pid' link.
    pid = root["_links"]["pid"]["href"].split("{")[0]
    main = c.get(c.resolve_redirect(f"{pid}?id={MAIN_REPORT_HANDLE}"))
    parts = []
    for v in main["metadata"].get("dc.relation.haspart", []):
        hm = _HASPART_RE.search(v["value"])
        if hm:
            parts.append(c.get(c.resolve_redirect(f"{pid}?id={hm.group(1)}")))
    have = {i["uuid"] for i in factsheets}
    for p in parts:
        if _is_factsheet(p.get("name")) and p["uuid"] not in have:
            factsheets.append(p)
            have.add(p["uuid"])
    report_parts = [p for p in parts if not _is_factsheet(p.get("name"))]
    have = {main["uuid"]} | {p["uuid"] for p in report_parts}
    for i in coll_items:
        if i["uuid"] not in have and _is_report_part(i.get("name")):
            report_parts.append(i)
            have.add(i["uuid"])

    seed_fs_uuids = {e["item_uuid"] for e in existing if e["kind"] == "factsheet"}
    missing_from_filter = sorted(seed_fs_uuids - {i["uuid"] for i in factsheets})

    # 3. ORIGINAL-bundle PDF for each selected item not already in the seed
    entries = []
    new_records = []

    def next_num(prefix):
        nums = [int(e["doc_id"].rsplit("_", 1)[1]) for e in existing + entries
                if re.fullmatch(prefix + r"_\d+", e["doc_id"])]
        return max(nums, default=0) + 1

    def add(doc_id, kind, item):
        bs, npdf = _original_pdf(c, item)
        if npdf > 1:
            failures.append(f"{doc_id}: {npdf} PDFs in ORIGINAL bundle; took lowest sequenceId")
        fn = re.sub(r"[^A-Za-z0-9._-]", "_", bs.get("name") or f"{doc_id}.pdf").lstrip("-")
        if fn in used:
            stem, dot, ext = fn.rpartition(".")
            fn = f"{stem}_{doc_id}.{ext}" if dot else f"{fn}_{doc_id}"
        used.add(fn)
        entries.append({
            "doc_id": doc_id, "title": item.get("name"), "publisher": "UNEP",
            "year": _year(item), "kind": kind, "url": bs["_links"]["content"]["href"],
            "item_uuid": item["uuid"], "bitstream_uuid": bs["uuid"],
            "local_filename": fn, "discovered_from": _item_page_url(item),
        })
        return bs

    if main["uuid"] not in have_uuids:
        add("report_main", "report", main)
    for p in report_parts:
        if p["uuid"] in have_uuids:
            continue
        if "executive summary" in (p.get("name") or "").lower():
            add("report_exec_summary", "report", p)
        else:
            add(f"report_part_{next_num('report_part'):02d}", "report", p)
    for f in factsheets:
        if f["uuid"] in have_uuids:
            continue
        bs = add(f"factsheet_{next_num('factsheet'):02d}", "factsheet", f)
        if f["uuid"] not in narrow_uuids:
            new_records.append({"title": f.get("name"), "item_uuid": f["uuid"],
                                "bitstream_name": bs.get("name")})

    if entries:
        _write_seed(out_path, entries, append=bool(existing))
    return {
        "n_report": sum(e["kind"] == "report" for e in existing + entries),
        "n_factsheets": sum(e["kind"] == "factsheet" for e in existing + entries),
        "n_record_pages_fetched": c.n_requests,
        "failures": failures,
        "route": "rest-api (HAL JSON)",
        "collection": {"name": coll.get("name"), "handle": coll.get("handle"),
                       "n_items": len(coll_items)},
        "widened_filter_count": widened_count,
        "new_records": new_records,
        "n_appended": len(entries),
        "existing_seed_factsheets_missing_from_filter": missing_from_filter,
    }


def _write_seed(path, entries, append=False):
    out = []
    if not append:
        ts = _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        out += [
            "# Source seed for human review. Generated by ogoniland_appraisal.sources.discover.",
            f"# Generated (UTC): {ts}",
            f"# Anchor record: {ANCHOR_UI_URL}",
            f"# Main report record: {MAIN_REPORT_URL}",
            "# Scalars are JSON-quoted; null means absent in the record.",
            "documents:",
        ]
    for e in entries:
        for i, k in enumerate(KEYS):
            out.append(("  - " if i == 0 else "    ") + f"{k}: {json.dumps(e[k], ensure_ascii=False)}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a" if append else "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(out) + "\n")


if __name__ == "__main__":
    dest = sys.argv[1] if len(sys.argv) > 1 else "docs/sources_seed.yml"
    try:
        print(json.dumps(discover(dest), indent=2, ensure_ascii=False))
    except DiscoveryStop as exc:
        print(f"STOP: {exc}", file=sys.stderr)
        sys.exit(2)
