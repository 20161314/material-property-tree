import gzip
import hashlib
import json
from pathlib import Path
import struct
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from workflow_sources_v3 import read_records, component_records, verify_payload, acquire_asset


class SourceTests(unittest.TestCase):
    def test_gzip_manifest_maps_fields_and_preserves_raw(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "source.csv.gz"
            with gzip.open(path, "wt") as handle:
                handle.write("uid,title,extra\na,Chair,untouched\n")
            row = list(read_records(path, {"source_uid": "uid", "name_en": "title"}))[0]
            self.assertEqual(row["source_uid"], "a")
            self.assertEqual(row["source_raw_fields"]["extra"], "untouched")

    def test_components_do_not_invent_parts(self):
        rows = component_records([{"object_id": "a", "source_locator": "manifest:1"}])
        self.assertEqual(rows[0]["scope"], "WHOLE_OBJECT_FALLBACK")
        with self.assertRaises(ValueError):
            component_records([{"object_id": "a", "source_locator": "m:1", "source_components": [{"component_id": "p", "source_locator": "m:2"}]}])

    def test_valid_glb_and_s3_xml_error(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "asset.glb"
            payload = struct.pack("<4sII", b"glTF", 2, 12)
            path.write_bytes(payload)
            self.assertTrue(verify_payload(path, hashlib.sha256(payload).hexdigest(), "glb")["verified_payload"])
            payload = b'<?xml version="1.0"?><Error><Code>NoSuchKey</Code></Error>'
            path.write_bytes(payload)
            with self.assertRaisesRegex(ValueError, "HTML/XML"):
                verify_payload(path, hashlib.sha256(payload).hexdigest(), "glb")

    def test_zip_escape_and_checksums_fail(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "assets.zip"
            with zipfile.ZipFile(path, "w") as archive:
                archive.writestr("../outside", "data")
            with self.assertRaisesRegex(ValueError, "archive"):
                verify_payload(path, hashlib.sha256(path.read_bytes()).hexdigest(), "zip")
            with self.assertRaisesRegex(ValueError, "SHA"):
                verify_payload(path, "0" * 64)

    def test_acquire_rejects_unbounded_or_undeclared_sources_before_network(self):
        with self.assertRaises(ValueError):
            acquire_asset("http://example.invalid/a", "unused", expected_sha256="0" * 64, license_or_access="CC-BY")
        with self.assertRaises(ValueError):
            acquire_asset("https://example.invalid/a", "unused", expected_sha256="0" * 64, license_or_access="CC-BY", max_bytes=0)


if __name__ == "__main__":
    unittest.main()
